import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
import logging
import math
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)

class VectorManager:
    def __init__(self, persist_path: str = "./chroma_db"):
        self.persist_path = persist_path
        
        # Initialize ChromaDB Client
        chroma_host = os.getenv("CHROMA_SERVER_HOST")
        chroma_port = os.getenv("CHROMA_SERVER_PORT")

        if chroma_host and chroma_port:
            logger.info(f"Connecting to ChromaDB Server at http://{chroma_host}:{chroma_port}")
            self.client = chromadb.HttpClient(host=chroma_host, port=int(chroma_port))
        else:
            logger.info(f"Initializing Embedded ChromaDB at {persist_path}")
            self.client = chromadb.PersistentClient(path=persist_path)
        
        # Get or Create Collections
        self.collection = self.client.get_or_create_collection(
            name="job_listings",
            metadata={"hnsw:space": "cosine"}
        )
        
        # New: User Context Collection (Resumes/Bios)
        self.context_collection = self.client.get_or_create_collection(
            name="user_contexts",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize Embedding Model (Bi-Encoder)
        logger.info("Loading Embedding Model: all-MiniLM-L6-v2")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Reranker (Cross-Encoder)
        logger.info("Loading Reranker: ms-marco-MiniLM-L-6-v2")
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
    def _generate_embedding(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
        
    def create_context_embedding(self, text: str) -> str:
        """
        Embeds a resume or bio and stores it.
        Returns the context_id (hash of text).
        """
        import hashlib
        # truncated text for hash to avoid huge filenames/ids if used elsewhere
        context_id = hashlib.md5(text.encode()).hexdigest()
        
        # Generate Embedding
        # Truncate to first 1000 chars for embedding to capture key skills/experience
        # or use the model's max seq length logic (SentenceTransformers handles it mostly, but good to be safe)
        embedding = self._generate_embedding(text[:4000]) 
        
        self.context_collection.upsert(
            ids=[context_id],
            embeddings=[embedding],
            documents=[text], # Store full text for retrieval if needed
            metadatas=[{"type": "resume"}]
        )
        
        return context_id

    def upsert_jobs(self, jobs: List[Dict[str, Any]]):
        """
        Vectorize and Index a batch of jobs.
        """
        if not jobs:
            return

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for job in jobs:
            # Create Rich Text Representation for Embedding
            job_id = str(job['id'])
            
            # Safe get
            title = job.get('title', '')
            company = job.get('company', '')
            desc = job.get('description', '')
            skills = job.get('skills', [])
            location = job.get('location', '')
            
            skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
            
            # Optimization: Focus embedding on the most import parts
            embed_text = f"{title} at {company}. Skills: {skills_str}. Location: {location}. {desc[:500]}"
            
            ids.append(job_id)
            documents.append(embed_text)
            embeddings.append(self._generate_embedding(embed_text))
            
            # Store metadata for Filtering before vector search
            metadatas.append({
                "title": title,
                "company": company,
                "location": location,
                "source": job.get('source', 'unknown'),
                "experience_min": job.get('experience_min', 0),
                "ctc_min": job.get('ctc_min', 0)
            })
            
        # Upsert to Chroma
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        logger.info(f"Indexed {len(jobs)} jobs in ChromaDB")

    def get_embeddings_by_ids(self, job_ids: List[int]) -> List[List[float]]:
        """Fetch embeddings for specific job IDs."""
        try:
            results = self.collection.get(ids=[str(jid) for jid in job_ids], include=["embeddings"])
            return results.get("embeddings", [])
        except Exception as e:
            logger.error(f"Failed to fetch embeddings for jobs {job_ids}: {e}")
            return []

    def search(self, query: str, top_k: int = 50, filters: Dict = None, context_id: str = None, feedback_job_ids: List[int] = None) -> List[Dict]:
        """
        Semantic Search with optional feedback boosting (Rocchio Algorithm).
        """
        query_embedding = None
        
        # 1. Base Embedding Source
        if context_id:
            try:
                ctx_data = self.context_collection.get(ids=[context_id], include=["embeddings"])
                if ctx_data and ctx_data['embeddings']:
                    query_embedding = ctx_data['embeddings'][0]
                    logger.info(f"Using Resume Context: {context_id}")
            except Exception: pass
            
        if not query_embedding:
            # Fallback to text query
            query_embedding = self._generate_embedding(query)

        # 2. Apply Feedback (Session Booster)
        if feedback_job_ids:
            try:
                feedback_vecs = self.get_embeddings_by_ids(feedback_job_ids)
                if feedback_vecs:
                    import numpy as np
                    base = np.array(query_embedding)
                    feedback = np.mean([np.array(v) for v in feedback_vecs], axis=0)
                    
                    # Rocchio: q_new = alpha * q_old + beta * avg(relevant)
                    # We use alpha=0.8, beta=0.2
                    adapted_vec = (0.8 * base) + (0.2 * feedback)
                    query_embedding = adapted_vec.tolist()
                    logger.info(f"Applied Session Boost using {len(feedback_vecs)} interactions")
            except Exception as e:
                logger.error(f"Failed to apply feedback boost: {e}")
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters 
        )
        
        # Format results
        formatted_results = []
        if results['ids']:
            ids = results['ids'][0]
            distances = results['distances'][0]
            metadatas = results['metadatas'][0]
            
            for i in range(len(ids)):
                formatted_results.append({
                    "id": ids[i],
                    "score": 1 - distances[i], # Convert distance to similarity score
                    "metadata": metadatas[i]
                })
                
        return formatted_results

    def get_context_metadata(self, context_id: str) -> Dict:
        """
        Retrieve metadata (skills, experience, etc.) associated with a resume context.
        """
        try:
            ctx_data = self.context_collection.get(ids=[context_id], include=["metadatas"])
            if ctx_data and ctx_data['metadatas'] and len(ctx_data['metadatas']) > 0:
                return ctx_data['metadatas'][0]
        except Exception as e:
            logger.error(f"Failed to fetch context metadata: {e}")
        return {}

    def rerank(self, query: str, docs: List[str]) -> List[float]:
        """
        Rerank a list of documents against a query.
        Returns list of scores (0-1).
        """
        if not docs:
            return []
        
        # If query is short, fine. If it's a resume replacement query, might be long?
        # CrossEncoder usually expects (Query, Document).
        pairs = [[query[:500], doc] for doc in docs] # Truncate query for Reranker speed
        scores = self.reranker.predict(pairs)
        
        # Apply Sigmoid to convert logits to 0-1 probability
        # 1 / (1 + exp(-x))
        sigmoid_scores = []
        
        # Handle single float return
        if isinstance(scores, float):
             return [1 / (1 + math.exp(-scores))]
             
        for s in scores:
            sigmoid_scores.append(1 / (1 + math.exp(-float(s))))
            
        return sigmoid_scores
