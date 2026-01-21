import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from managers.scraper_manager import ScraperManager

class TestScraperManager:
    """Unit tests for ScraperManager"""
    
    @pytest.fixture
    def manager(self):
        """Create ScraperManager with mocked scrapers"""
        with patch('managers.scraper_manager.JSearchClient'), \
             patch('managers.scraper_manager.AdzunaClient'), \
             patch('managers.scraper_manager.RemotiveClient'), \
             patch('managers.scraper_manager.NaukriScraper'), \
             patch('managers.scraper_manager.LinkedInScraper'), \
             patch('managers.scraper_manager.InstahyreScraper'):
            
            manager = ScraperManager()
            return manager
    
    @pytest.mark.asyncio
    async def test_run_wrapper_success(self, manager):
        """Test successful scraper execution"""
        async def mock_scraper():
            return [{'title': 'Job 1'}, {'title': 'Job 2'}]
        
        result = await manager._run_wrapper(mock_scraper(), "TestScraper", 10)
        
        assert len(result) == 2
        assert result[0]['title'] == 'Job 1'
    
    @pytest.mark.asyncio
    async def test_run_wrapper_timeout(self, manager):
        """Test scraper timeout handling"""
        async def slow_scraper():
            import asyncio
            await asyncio.sleep(20)
            return []
        
        result = await manager._run_wrapper(slow_scraper(), "SlowScraper", 1)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_run_wrapper_exception(self, manager):
        """Test scraper exception handling"""
        async def failing_scraper():
            raise Exception("Scraper failed")
        
        result = await manager._run_wrapper(failing_scraper(), "FailingScraper", 10)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_run_wrapper_non_list_return(self, manager):
        """Test handling of non-list return values"""
        async def bad_scraper():
            return "not a list"
        
        result = await manager._run_wrapper(bad_scraper(), "BadScraper", 10)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_execute_search_india(self, manager):
        """Test search execution for India"""
        # Mock all scrapers to return empty lists
        manager.jsearch_client.search_jobs = AsyncMock(return_value=[])
        manager.adzuna_client.search_jobs = AsyncMock(return_value=[])
        manager.remotive_client.search_jobs = AsyncMock(return_value=[])
        
        for scraper in manager.scrapers.values():
            scraper.search_jobs = AsyncMock(return_value=[])
        
        results = await manager.execute_search("Python", "Bangalore", 1, "India")
        
        assert isinstance(results, list)
        # Verify API clients were called
        manager.jsearch_client.search_jobs.assert_called_once()
        manager.remotive_client.search_jobs.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_search_uae(self, manager):
        """Test search execution for UAE"""
        manager.jsearch_client.search_jobs = AsyncMock(return_value=[])
        manager.remotive_client.search_jobs = AsyncMock(return_value=[])
        
        for scraper in manager.scrapers.values():
            scraper.search_jobs = AsyncMock(return_value=[])
        
        results = await manager.execute_search("Python", "Dubai", 1, "UAE")
        
        assert isinstance(results, list)
        # Verify UAE-specific scrapers would be called
        manager.jsearch_client.search_jobs.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_search_aggregates_results(self, manager):
        """Test that results from multiple scrapers are aggregated"""
        manager.jsearch_client.search_jobs = AsyncMock(return_value=[
            {'id': 1, 'title': 'Job 1'}
        ])
        manager.adzuna_client.search_jobs = AsyncMock(return_value=[
            {'id': 2, 'title': 'Job 2'}
        ])
        manager.remotive_client.search_jobs = AsyncMock(return_value=[
            {'id': 3, 'title': 'Job 3'}
        ])
        
        for scraper in manager.scrapers.values():
            scraper.search_jobs = AsyncMock(return_value=[])
        
        results = await manager.execute_search("Python", "Bangalore", 1, "India")
        
        assert len(results) >= 3  # At least 3 from API clients
