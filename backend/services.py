from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from models import Job, SearchQuery
from managers.scraper_manager import ScraperManager
from managers.filter_engine import FilterEngine
from managers.matching_engine import MatchingEngine
from database import AsyncSessionLocal
from hashlib import md5
import json
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, db: AsyncSession, vector_manager=None, profiler=None):
        self.db = db
        self.scraper_manager = ScraperManager()
        self.filter_engine = FilterEngine()
        self.matching_engine = MatchingEngine()
        self.vector_manager = vector_manager
        self.profiler = profiler

    def _generate_query_hash(self, params: dict) -> str:
        """Create a deterministic hash from search parameters."""
        query_string = json.dumps(params, sort_keys=True)
        return md5(query_string.encode()).hexdigest()

    async def _scrape_and_save_background(self, query: str, location: str, page: int, query_hash: str, cache_params: dict, country: str = "India"):
        """Background task to scrape and update DB/Vector index."""
        logger.info(f"Background Scrape Triggered: {query} in {country}")
        try:
             # Use a fresh DB session for background task
             async with AsyncSessionLocal() as session:
                 # Re-instantiate manager with new session if needed, or just use it
                 # ScraperManager doesn't hold DB state, it returns data
                 jobs_data = await self.scraper_manager.execute_search(query, location, page, country=country)
                 
                 if jobs_data:
                     # Upsert Logic
                     valid_jobs = []
                     for job_dict in jobs_data:
                         try:
                             # Add extra metadata
                             job_dict["query_hash"] = query_hash
                             job_dict["country"] = country # Tag with country
                             job = Job(**job_dict)
                             await session.merge(job)
                             valid_jobs.append(job_dict)
                         except Exception as e:
                             continue
                     
                     # Update Cache Entry
                     # Need to fetch or create SearchQuery in this session
                     stmt = select(SearchQuery).where(SearchQuery.query_hash == query_hash)
                     res = await session.execute(stmt)
                     cached = res.scalar_one_or_none()
                     
                     if not cached:
                         cached = SearchQuery(query_hash=query_hash, params=cache_params)
                         session.add(cached)
                     cached.last_fetched = datetime.utcnow()
                     
                     await session.commit()
                     
                     # Index to Vector DB (real-time update)
                     if self.vector_manager:
                         self.vector_manager.upsert_jobs(jobs_data)
                     
                     logger.info(f"Background Scrape Complete: {len(valid_jobs)} jobs added.")
                 else:
                     logger.info("Background Scrape: No jobs found.")
                     
        except Exception as e:
            logger.error(f"Background task failed: {e}")

    async def get_jobs(
        self,
        query: str,
        location: str = None,
        page: int = 1,
        experience: list[str] = None, 
        ctc: list[str] = None,
        skills: list[str] = None,

        jobPortals: list[str] = None,
        context_id: str = None,
        country: str = "India"
    ):
        search_term = query.strip() or "Job"
        if location: full_term = f"{search_term} in {location}"
        else: full_term = search_term

        # 1. Check Cache Status
        cache_params = {
            "q": full_term, 
            "page": page,
            "orig_q": query,
            "skills": skills,
            "portals": jobPortals,
            "exp": experience,
            "ctx": context_id,
            "country": country
        }
        query_hash = self._generate_query_hash(cache_params)
        
        stmt = select(SearchQuery).where(SearchQuery.query_hash == query_hash)
        result = await self.db.execute(stmt)
        cached_query = result.scalar_one_or_none()
        
        should_scrape = False
        if not cached_query:
            should_scrape = True
        elif cached_query.last_fetched < datetime.utcnow() - timedelta(hours=24):
            should_scrape = True
            
        if self.profiler:
            self.profiler.set_meta("cache_hit", not should_scrape)

        # 2. INSTANT SEARCH (Vector + SQL)
        vector_ids = []
        if self.vector_manager:
            try:
                # Semantic Search
                if self.profiler:
                    with self.profiler.measure("vector_search"):
                        # FEATURE: Session Boosting
                        feedback_ids = []
                        if context_id:
                            # Verify with DB for recent interactions
                            stmt = select(UserInteraction.job_id).where(
                                UserInteraction.context_id == context_id,
                                UserInteraction.action_type.in_(['CLICK', 'APPLY']),
                                UserInteraction.timestamp > datetime.utcnow() - timedelta(hours=1) # Last hour only
                            ).limit(10)
                            res = await self.db.execute(stmt)
                            feedback_ids = res.scalars().all()

                        vector_results = self.vector_manager.search(
                            search_term, 
                            top_k=50, 
                            context_id=context_id,
                            feedback_job_ids=feedback_ids
                        )
                        vector_ids = [int(r['id']) for r in vector_results]
                        self.profiler.set_meta("vector_hits", len(vector_ids))
                else:
                    vector_results = self.vector_manager.search(search_term, top_k=50, context_id=context_id)
                    vector_ids = [int(r['id']) for r in vector_results]
            except Exception as e:
                logger.error(f"Vector search failed: {e}")

        # Build Hybrid Query
        stmt = select(Job)
        
        # Combining Logic: ID in Vector OR Title matches Keyword
        conditions = []
        if vector_ids:
            conditions.append(Job.id.in_(vector_ids))
        
        # Keyword Fallback (SQL LIKE)
        conditions.append(Job.title.ilike(f"%{search_term}%"))
        
        # Keyword Fallback (SQL LIKE)
        conditions.append(Job.title.ilike(f"%{search_term}%"))
        

        
        if conditions:
            # (Matches Vector) OR (Matches Keyword) AND (Matches Country)
            # Re-structuring: (Vector OR Keyword) AND Country
            # SQLAlchemy `or_` applies to the list. We need AND for country.
            
            # Correct Logic:
            # WHERE (id IN vector_ids OR title LIKE kw) AND country = val
            combined_match = or_(
                Job.id.in_(vector_ids) if vector_ids else False, 
                Job.title.ilike(f"%{search_term}%")
            )
            stmt = stmt.where(combined_match)
            
            # Strict Country Filter
            if country:
                stmt = stmt.where(Job.country == country)

            # Strict Location Filter (if provided)
            # We use ilike for case-insensitive partial match (e.g. "Bangalore" matches "Bengaluru, Bangalore")
            if location:
                stmt = stmt.where(Job.location.ilike(f"%{location}%"))
            
        # 3. Apply Filters (using Engine)
        stmt = self.filter_engine.apply_filters(stmt, experience, ctc, skills, jobPortals)
        
        # Execute DB Query
        if self.profiler:
             with self.profiler.measure("sql_query"):
                result = await self.db.execute(stmt)
                jobs = result.scalars().all()
                self.profiler.set_meta("total_candidates", len(jobs))
        else:
            result = await self.db.execute(stmt)
            jobs = result.scalars().all()
        
        # 4. Trigger Background Scrape if needed (or if DB empty)
        if should_scrape or len(jobs) < 5:
            # Fire and forget
            asyncio.create_task(self._scrape_and_save_background(
                search_term, location, page, query_hash, cache_params, country
            ))
        
        # 5. Score & Sort (Relevance Engine)
        user_exp = 0
        if experience:
             try:
                 parts = experience[0].replace(" Years", "").split("-")
                 user_exp = int(parts[0])
             except: pass
        
        # Base User Profile from Search Inputs
        user_profile = {
            "query": search_term,
            "skills": skills if skills else [],
            "experience_years": user_exp
        }
        
        # --- RESUME CONTEXT ENRICHMENT ---
        if context_id and self.vector_manager:
            try:
                # Fetch detailed metadata from Resume Context (Chromadb)
                ctx_meta = self.vector_manager.get_context_metadata(context_id)
                if ctx_meta:
                    # Enrich/Override profile
                    # 1. Skills: Merge query skills with resume skills
                    resume_skills = ctx_meta.get("skills", [])
                    if isinstance(resume_skills, str): 
                        # Handle stored string representation if any
                        try: resume_skills = eval(resume_skills) 
                        except: resume_skills = [resume_skills]
                        
                    current_skills = user_profile.get("skills", [])
                    user_profile["skills"] = list(set(current_skills + list(resume_skills)))
                    
                    # 2. Experience: If context has experience, prefer it? 
                    # Actually, if user strictly filtered by filter panel, keep that.
                    # But if no filter, use resume experience.
                    if not experience and "experience_years" in ctx_meta:
                        user_profile["experience_years"] = int(ctx_meta["experience_years"])
                        
                    logger.info(f"Enriched User Profile with Context {context_id}: {len(user_profile['skills'])} skills")
            except Exception as e:
                logger.error(f"Failed to enrich profile with context: {e}")
        
        scored_jobs = []
        for job in jobs:
            score, breakdown = self.matching_engine.calculate_score(job, user_profile)
            
            # Boost score if present in Vector Search results
            if self.vector_manager and str(job.id) in [str(id) for id in vector_ids]:
                # Add semantic boost (e.g. +10%)
                score = min(score + 10, 100)
                breakdown["semantic_boost"] = 10.0
                
            setattr(job, "relevance_score", score) 
            setattr(job, "match_breakdown", breakdown)
            scored_jobs.append(job)
            
        # Initial Sort by Basic Relevance
        scored_jobs.sort(key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)
        
        # --- RERANKING STEP (Cross-Encoder) ---
        # Rerank the top 50 jobs for maximum precision
        if self.vector_manager and len(scored_jobs) > 0:
            top_n = 50
            candidates = scored_jobs[:top_n]
            others = scored_jobs[top_n:]
            
            try:
                descriptions = [job.description or "" for job in candidates]
                # Pass query + descriptions to reranker
                
                rerank_scores = []
                if self.profiler:
                    with self.profiler.measure("reranking"):
                        rerank_scores = self.vector_manager.rerank(search_term, descriptions)
                        self.profiler.set_meta("reranked_count", len(candidates))
                else:
                     rerank_scores = self.vector_manager.rerank(search_term, descriptions)
                
                for i, job in enumerate(candidates):
                    # Rerank score is 0-1. Scale to 0-100.
                    # We blend it with the implementation score: 70% Rerank + 30% Rule
                    ai_score = rerank_scores[i] * 100
                    rule_score = job.relevance_score
                    
                    final_score = (ai_score * 0.7) + (rule_score * 0.3)
                    job.relevance_score = final_score
                    
                # Re-sort candidates
                candidates.sort(key=lambda x: x.relevance_score, reverse=True)
                
                # Merge back
                scored_jobs = candidates + others
                
            except Exception as e:
                logger.error(f"Reranking failed: {e}")
                
        if self.profiler:
            self.profiler.set_meta("final_results", len(scored_jobs))
        
        # Return jobs AND whether background scrape was triggered
        return scored_jobs, should_scrape
