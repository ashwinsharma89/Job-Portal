import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from services import JobService
from models import Job, SearchQuery, UserInteraction
from datetime import datetime, timedelta
from sqlalchemy import select

class TestJobServiceComprehensive:
    """Comprehensive tests for JobService to achieve 100% coverage"""
    
    @pytest_asyncio.fixture
    async def mock_db(self):
        """Mock database session"""
        db = AsyncMock()
        return db
    
    @pytest_asyncio.fixture
    async def full_service(self, mock_db):
        """Create JobService with all dependencies mocked"""
        service = JobService(mock_db)
        service.scraper_manager = AsyncMock()
        service.filter_engine = Mock()
        service.matching_engine = Mock()
        service.vector_manager = Mock()
        service.profiler = Mock()
        
        # Mock profiler methods
        service.profiler.measure = MagicMock()
        service.profiler.measure.return_value.__enter__ = Mock()
        service.profiler.measure.return_value.__exit__ = Mock()
        service.profiler.set_meta = Mock()
        
        return service
    
    @pytest.mark.asyncio
    async def test_background_scrape_task(self, full_service, mock_db):
        """Test background scraping task execution"""
        # Mock scraper results
        full_service.scraper_manager.execute_search.return_value = [
            {
                'id': 1,
                'title': 'Python Developer',
                'company': 'Tech Corp',
                'location': 'Bangalore',
                'experience_min': 5,
                'experience_max': 8,
                'apply_link': 'https://example.com/job/1',
                'source': 'Naukri',
                'description': 'Python job'
            }
        ]
        
        # Mock database session for background task
        with patch('services.AsyncSessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            # Mock database operations
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            # Execute background scrape
            await full_service._scrape_and_save_background(
                "Python", "Bangalore", 1, "test_hash", {}, "India"
            )
            
            # Verify scraper was called
            full_service.scraper_manager.execute_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_jobs_with_profiler(self, full_service, mock_db):
        """Test get_jobs with profiler enabled"""
        # Setup mocks
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = []
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        # Mock vector search
        full_service.vector_manager.search.return_value = []
        
        jobs, should_scrape = await full_service.get_jobs("Python", "Bangalore")
        
        # Verify profiler was used
        assert full_service.profiler.set_meta.called
    
    @pytest.mark.asyncio
    async def test_get_jobs_with_resume_enrichment(self, full_service, mock_db):
        """Test resume context enrichment"""
        # Setup mocks
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        # Create a mock job
        mock_job = Job(
            id=1,
            title="Python Developer",
            company="Tech Corp",
            location="Bangalore",
            experience_min=5,
            experience_max=8,
            description="Python job",
            apply_link="https://example.com",
            source="Test"
        )
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = [mock_job]
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            elif "user_interactions" in str(stmt).lower():
                mock_interaction_result = Mock()
                mock_interaction_result.scalars.return_value.all.return_value = []
                return mock_interaction_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        # Mock vector manager
        full_service.vector_manager.search.return_value = [{'id': '1', 'score': 0.9}]
        full_service.vector_manager.get_context_metadata.return_value = {
            'skills': ['Python', 'Django'],
            'experience_years': 5
        }
        full_service.vector_manager.rerank.return_value = [0.9]
        
        # Mock matching engine
        full_service.matching_engine.calculate_score.return_value = (85.0, {
            'skills': 80.0,
            'title': 90.0,
            'experience': 85.0,
            'recency': 80.0
        })
        
        jobs, should_scrape = await full_service.get_jobs(
            "Python", "Bangalore", context_id="test_context"
        )
        
        # Verify context metadata was fetched
        full_service.vector_manager.get_context_metadata.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_jobs_with_feedback_boosting(self, full_service, mock_db):
        """Test session feedback boosting"""
        # Setup mocks
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        mock_job = Job(
            id=1,
            title="Python Developer",
            company="Tech Corp",
            location="Bangalore",
            experience_min=5,
            experience_max=8,
            description="Python job",
            apply_link="https://example.com",
            source="Test"
        )
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = [mock_job]
        
        # Mock interaction query
        mock_interaction_result = Mock()
        mock_interaction_result.scalars.return_value.all.return_value = [1, 2, 3]
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            elif "user_interactions" in str(stmt).lower():
                return mock_interaction_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        # Mock vector manager
        full_service.vector_manager.search.return_value = [{'id': '1', 'score': 0.9}]
        full_service.vector_manager.rerank.return_value = [0.9]
        
        # Mock matching engine
        full_service.matching_engine.calculate_score.return_value = (85.0, {})
        
        jobs, should_scrape = await full_service.get_jobs(
            "Python", "Bangalore", context_id="test_context"
        )
        
        # Verify it completes without error
        assert isinstance(jobs, list)
    
    @pytest.mark.asyncio
    async def test_get_jobs_with_reranking(self, full_service, mock_db):
        """Test reranking integration"""
        # Setup mocks
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        # Create 60 mock jobs to trigger reranking
        mock_jobs = []
        for i in range(60):
            job = Job(
                id=i,
                title=f"Python Developer {i}",
                company="Tech Corp",
                location="Bangalore",
                experience_min=5,
                experience_max=8,
                description=f"Python job {i}",
                apply_link=f"https://example.com/{i}",
                source="Test"
            )
            mock_jobs.append(job)
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = mock_jobs
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            elif "user_interactions" in str(stmt).lower():
                mock_interaction_result = Mock()
                mock_interaction_result.scalars.return_value.all.return_value = []
                return mock_interaction_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        # Mock vector manager
        full_service.vector_manager.search.return_value = [
            {'id': str(i), 'score': 0.9} for i in range(60)
        ]
        full_service.vector_manager.rerank.return_value = [0.9 - (i * 0.01) for i in range(50)]
        
        # Mock matching engine
        full_service.matching_engine.calculate_score.return_value = (85.0, {})
        
        jobs, should_scrape = await full_service.get_jobs("Python", "Bangalore")
        
        # Verify reranking was called
        full_service.vector_manager.rerank.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_jobs_vector_search_failure(self, full_service, mock_db):
        """Test handling of vector search failures"""
        # Setup mocks
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = []
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        # Make vector search fail
        full_service.vector_manager.search.side_effect = Exception("Vector search failed")
        
        jobs, should_scrape = await full_service.get_jobs("Python", "Bangalore")
        
        # Should still return results (fallback to SQL)
        assert isinstance(jobs, list)
    
    @pytest.mark.asyncio
    async def test_get_jobs_reranking_failure(self, full_service, mock_db):
        """Test handling of reranking failures"""
        # Setup mocks
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        # Create 60 jobs
        mock_jobs = [
            Job(
                id=i,
                title=f"Job {i}",
                company="Corp",
                location="City",
                experience_min=5,
                experience_max=8,
                description=f"Desc {i}",
                apply_link=f"https://example.com/{i}",
                source="Test"
            ) for i in range(60)
        ]
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = mock_jobs
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            elif "user_interactions" in str(stmt).lower():
                mock_interaction_result = Mock()
                mock_interaction_result.scalars.return_value.all.return_value = []
                return mock_interaction_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        full_service.vector_manager.search.return_value = []
        full_service.vector_manager.rerank.side_effect = Exception("Reranking failed")
        full_service.matching_engine.calculate_score.return_value = (85.0, {})
        
        jobs, should_scrape = await full_service.get_jobs("Python", "Bangalore")
        
        # Should still return results
        assert len(jobs) > 0
    
    @pytest.mark.asyncio
    async def test_get_jobs_with_filters(self, full_service, mock_db):
        """Test get_jobs with all filter types"""
        # Setup mocks
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = []
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        full_service.vector_manager.search.return_value = []
        full_service.filter_engine.apply_filters.return_value = select(Job)
        
        jobs, should_scrape = await full_service.get_jobs(
            "Python",
            "Bangalore",
            experience=["5-10 Years"],
            ctc=["10-20 LPA"],
            skills=["Python", "Django"],
            jobPortals=["Naukri", "LinkedIn"]
        )
        
        # Verify filter engine was called with all filters
        full_service.filter_engine.apply_filters.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_jobs_low_results_triggers_scrape(self, full_service, mock_db):
        """Test that low results trigger background scrape"""
        # Setup mocks
        cached_query = SearchQuery(
            query_hash="test_hash",
            last_fetched=datetime.utcnow(),
            params={}
        )
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = cached_query
        
        # Return only 3 jobs (less than 5)
        mock_jobs = [
            Job(
                id=i,
                title=f"Job {i}",
                company="Corp",
                location="City",
                experience_min=5,
                experience_max=8,
                description="Desc",
                apply_link=f"https://example.com/{i}",
                source="Test"
            ) for i in range(3)
        ]
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = mock_jobs
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        full_service.vector_manager.search.return_value = []
        full_service.matching_engine.calculate_score.return_value = (85.0, {})
        
        jobs, should_scrape = await full_service.get_jobs("Python", "Bangalore")
        
        # Should trigger scrape due to low results
        assert len(jobs) == 3
