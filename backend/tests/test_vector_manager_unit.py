import pytest
from unittest.mock import Mock, patch, MagicMock
from managers.vector_manager import VectorManager
import numpy as np

class TestVectorManager:
    """Unit tests for VectorManager with mocked ChromaDB"""
    
    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client"""
        with patch('managers.vector_manager.chromadb') as mock_chromadb:
            mock_client = Mock()
            mock_collection = Mock()
            mock_context_collection = Mock()
            
            mock_client.get_or_create_collection.side_effect = [
                mock_collection,
                mock_context_collection
            ]
            
            mock_chromadb.PersistentClient.return_value = mock_client
            
            yield {
                'chromadb': mock_chromadb,
                'client': mock_client,
                'collection': mock_collection,
                'context_collection': mock_context_collection
            }
    
    @pytest.fixture
    def mock_models(self):
        """Mock SentenceTransformer and CrossEncoder"""
        with patch('managers.vector_manager.SentenceTransformer') as mock_st, \
             patch('managers.vector_manager.CrossEncoder') as mock_ce:
            
            mock_encoder = Mock()
            mock_encoder.encode.return_value = np.array([0.1, 0.2, 0.3])
            mock_st.return_value = mock_encoder
            
            mock_reranker = Mock()
            mock_reranker.predict.return_value = [0.8, 0.6, 0.4]
            mock_ce.return_value = mock_reranker
            
            yield {
                'encoder': mock_encoder,
                'reranker': mock_reranker
            }
    
    def test_init_embedded_mode(self, mock_chroma_client, mock_models):
        """Test VectorManager initialization in embedded mode"""
        vm = VectorManager(persist_path="./test_chroma")
        
        assert vm.client is not None
        assert vm.collection is not None
        assert vm.context_collection is not None
        assert vm.model is not None
        assert vm.reranker is not None
    
    def test_generate_embedding(self, mock_chroma_client, mock_models):
        """Test embedding generation"""
        vm = VectorManager()
        embedding = vm._generate_embedding("test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 3
        mock_models['encoder'].encode.assert_called_once()
    
    def test_create_context_embedding(self, mock_chroma_client, mock_models):
        """Test resume context embedding creation"""
        vm = VectorManager()
        context_id = vm.create_context_embedding("Sample resume text")
        
        assert isinstance(context_id, str)
        assert len(context_id) == 32  # MD5 hash length
        vm.context_collection.upsert.assert_called_once()
    
    def test_upsert_jobs(self, mock_chroma_client, mock_models):
        """Test job indexing"""
        vm = VectorManager()
        jobs = [
            {
                'id': 1,
                'title': 'Python Developer',
                'company': 'Tech Corp',
                'description': 'Looking for Python dev',
                'skills': ['Python', 'Django'],
                'location': 'Bangalore',
                'source': 'Naukri',
                'experience_min': 5,
                'ctc_min': 1000000
            }
        ]
        
        vm.upsert_jobs(jobs)
        
        vm.collection.upsert.assert_called_once()
        call_args = vm.collection.upsert.call_args
        assert len(call_args.kwargs['ids']) == 1
        assert len(call_args.kwargs['embeddings']) == 1
        assert len(call_args.kwargs['metadatas']) == 1
    
    def test_upsert_jobs_empty(self, mock_chroma_client, mock_models):
        """Test upsert with empty job list"""
        vm = VectorManager()
        vm.upsert_jobs([])
        
        vm.collection.upsert.assert_not_called()
    
    def test_search_basic(self, mock_chroma_client, mock_models):
        """Test basic vector search"""
        vm = VectorManager()
        
        # Mock search results
        vm.collection.query.return_value = {
            'ids': [['1', '2', '3']],
            'distances': [[0.1, 0.2, 0.3]],
            'metadatas': [[
                {'title': 'Job 1'},
                {'title': 'Job 2'},
                {'title': 'Job 3'}
            ]]
        }
        
        results = vm.search("Python Developer", top_k=3)
        
        assert len(results) == 3
        assert results[0]['id'] == '1'
        assert results[0]['score'] == 0.9  # 1 - 0.1
        vm.collection.query.assert_called_once()
    
    def test_search_with_context(self, mock_chroma_client, mock_models):
        """Test search with resume context"""
        vm = VectorManager()
        
        # Mock context retrieval
        vm.context_collection.get.return_value = {
            'embeddings': [[0.5, 0.6, 0.7]]
        }
        
        vm.collection.query.return_value = {
            'ids': [['1']],
            'distances': [[0.1]],
            'metadatas': [[{'title': 'Job 1'}]]
        }
        
        results = vm.search("Python", context_id="test_context_id")
        
        assert len(results) == 1
        vm.context_collection.get.assert_called_once()
    
    def test_search_with_feedback(self, mock_chroma_client, mock_models):
        """Test search with feedback boosting"""
        vm = VectorManager()
        
        # Mock embeddings retrieval
        vm.collection.get.return_value = {
            'embeddings': [[0.4, 0.5, 0.6], [0.3, 0.4, 0.5]]
        }
        
        vm.collection.query.return_value = {
            'ids': [['1']],
            'distances': [[0.1]],
            'metadatas': [[{'title': 'Job 1'}]]
        }
        
        results = vm.search("Python", feedback_job_ids=[1, 2])
        
        assert len(results) == 1
        vm.collection.get.assert_called_once()
    
    def test_get_context_metadata(self, mock_chroma_client, mock_models):
        """Test context metadata retrieval"""
        vm = VectorManager()
        
        vm.context_collection.get.return_value = {
            'metadatas': [{'skills': ['Python'], 'experience_years': 5}]
        }
        
        metadata = vm.get_context_metadata("test_id")
        
        assert 'skills' in metadata
        assert metadata['experience_years'] == 5
    
    def test_get_context_metadata_not_found(self, mock_chroma_client, mock_models):
        """Test context metadata when not found"""
        vm = VectorManager()
        
        vm.context_collection.get.return_value = {'metadatas': []}
        
        metadata = vm.get_context_metadata("invalid_id")
        
        assert metadata == {}
    
    def test_rerank(self, mock_chroma_client, mock_models):
        """Test reranking functionality"""
        vm = VectorManager()
        
        docs = ["Doc 1", "Doc 2", "Doc 3"]
        scores = vm.rerank("Python Developer", docs)
        
        assert len(scores) == 3
        assert all(0 <= score <= 1 for score in scores)
        mock_models['reranker'].predict.assert_called_once()
    
    def test_rerank_empty(self, mock_chroma_client, mock_models):
        """Test reranking with empty docs"""
        vm = VectorManager()
        
        scores = vm.rerank("Python", [])
        
        assert scores == []
        mock_models['reranker'].predict.assert_not_called()
    
    def test_get_embeddings_by_ids(self, mock_chroma_client, mock_models):
        """Test fetching embeddings by job IDs"""
        vm = VectorManager()
        
        vm.collection.get.return_value = {
            'embeddings': [[0.1, 0.2], [0.3, 0.4]]
        }
        
        embeddings = vm.get_embeddings_by_ids([1, 2])
        
        assert len(embeddings) == 2
        vm.collection.get.assert_called_once()
