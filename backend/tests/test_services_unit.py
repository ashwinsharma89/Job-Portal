import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from services import JobService
from models import Job, SearchQuery
from datetime import datetime, timedelta

class TestJobService:
    """Unit tests for JobService"""
    
    @pytest_asyncio.fixture
    async def mock_db(self):
        """Mock database session"""
        db = AsyncMock()
        return db
    
    @pytest_asyncio.fixture
    async def service(self, mock_db):
        """Create JobService with mocked dependencies"""
        service = JobService(mock_db)
        service.scraper_manager = Mock()
        service.filter_engine = Mock()
        service.matching_engine = Mock()
        service.vector_manager = Mock()
        return service
    
    def test_generate_query_hash(self, service):
        """Test query hash generation is deterministic"""
        params1 = {"q": "Python", "page": 1}
        params2 = {"q": "Python", "page": 1}
        params3 = {"q": "Java", "page": 1}
        
        hash1 = service._generate_query_hash(params1)
        hash2 = service._generate_query_hash(params2)
        hash3 = service._generate_query_hash(params3)
        
        assert hash1 == hash2  # Same params = same hash
        assert hash1 != hash3  # Different params = different hash
    
    @pytest.mark.asyncio
    async def test_get_jobs_cache_hit(self, service, mock_db):
        """Test that cached queries don't trigger scraping"""
        from datetime import datetime
        
        # Mock cached query with actual datetime
        cached_query = Mock()
        cached_query.query_hash = "test_hash"
        cached_query.last_fetched = datetime.utcnow()
        cached_query.params = {}
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = cached_query
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = []
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        jobs, should_scrape = await service.get_jobs("Python", "Bangalore")
        
        assert should_scrape == False  # Should not scrape
    
    @pytest.mark.asyncio
    async def test_get_jobs_cache_miss(self, service, mock_db):
        """Test that missing cache triggers scraping"""
        # Mock no cached query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = []
        
        # Set up mock to return different results for different queries
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        jobs, should_scrape = await service.get_jobs("Python", "Bangalore")
        
        assert should_scrape == True  # Should trigger scrape
    
    @pytest.mark.asyncio
    async def test_get_jobs_stale_cache(self, service, mock_db):
        """Test that stale cache triggers scraping"""
        # Mock stale cached query (>24 hours old)
        cached_query = SearchQuery(
            query_hash="test_hash",
            last_fetched=datetime.utcnow() - timedelta(hours=25),
            params={}
        )
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = cached_query
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = []
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        jobs, should_scrape = await service.get_jobs("Python", "Bangalore")
        
        assert should_scrape == True  # Should trigger scrape
    
    @pytest.mark.asyncio
    async def test_get_jobs_with_vector_search(self, service, mock_db):
        """Test vector search integration"""
        service.vector_manager.search.return_value = [
            {"id": "1", "score": 0.9},
            {"id": "2", "score": 0.8}
        ]
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        mock_jobs_result = Mock()
        mock_jobs_result.scalars.return_value.all.return_value = []
        
        async def mock_execute(stmt):
            if "search_queries" in str(stmt).lower():
                return mock_result
            return mock_jobs_result
        
        mock_db.execute.side_effect = mock_execute
        
        jobs, should_scrape = await service.get_jobs("Python", "Bangalore")
        
        # Verify vector search was called
        service.vector_manager.search.assert_called_once()
