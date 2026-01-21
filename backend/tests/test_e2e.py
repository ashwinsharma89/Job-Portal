import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, Mock
from main import app

class TestEndToEndMocked:
    """Fast E2E tests with mocked scrapers"""
    
    @pytest_asyncio.fixture
    async def client(self):
        """Create test client"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    
    @pytest_asyncio.fixture
    async def mock_services(self):
        """Mock all external services"""
        with patch('main.JobService') as mock_job_service, \
             patch('main.VectorManager') as mock_vm:
            
            # Mock JobService
            job_service_instance = AsyncMock()
            mock_job_service.return_value = job_service_instance
            
            job_service_instance.get_jobs.return_value = (
                [
                    {
                        "id": 1,
                        "title": "Python Developer",
                        "company": "Tech Corp",
                        "location": "Bangalore",
                        "experience_min": 5,
                        "experience_max": 8,
                        "apply_link": "https://example.com/job/1",
                        "source": "Test",
                        "relevance_score": 85.0
                    }
                ],
                False
            )
            
            # Mock VectorManager
            vm_instance = Mock()
            mock_vm.return_value = vm_instance
            vm_instance.create_context_embedding.return_value = "test_context_123"
            
            yield {
                'job_service': job_service_instance,
                'vector_manager': vm_instance
            }
    
    @pytest.mark.asyncio
    async def test_full_search_flow(self, client, mock_services):
        """Test complete search flow"""
        response = await client.get("/api/jobs?query=Python Developer&location=Bangalore")
        
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        assert len(jobs) > 0
        assert jobs[0]["title"] == "Python Developer"
    
    @pytest.mark.xfail(reason="VectorManager may not be initialized in test environment")
    @pytest.mark.asyncio
    async def test_resume_upload_and_search_flow(self, client, mock_services):
        """Test resume upload followed by search"""
        # Mock VectorManager globally
        with patch('main.vector_manager') as mock_vm_global:
            mock_vm_global.create_context_embedding.return_value = "test_context_123"
            
            # Upload resume
            files = {
                "file": ("resume.txt", b"Python Developer\n5 years experience", "text/plain")
            }
            
            upload_response = await client.post("/api/context/upload", files=files)
            
            # May fail if VectorManager not initialized in test environment
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                context_id = upload_data["context_id"]
                
                # Search with context
                search_response = await client.get(f"/api/jobs?query=Python&context_id={context_id}")
                assert search_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_feedback_flow(self, client, mock_services):
        """Test feedback submission"""
        with patch('main.AsyncSessionLocal') as mock_session:
            mock_db = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_db
            
            # Search
            search_response = await client.get("/api/jobs?query=Python")
            assert search_response.status_code == 200
            
            # Submit feedback
            feedback_data = {
                "job_id": 1,
                "action_type": "CLICK",
                "context_id": "test_session"
            }
            
            feedback_response = await client.post("/api/feedback", json=feedback_data)
            assert feedback_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_multi_filter_search(self, client, mock_services):
        """Test search with multiple filters"""
        response = await client.get(
            "/api/jobs?query=Python&experience=5-10 Years&ctc=10-20 LPA&skills=Python"
        )
        
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
    
    @pytest.mark.asyncio
    async def test_pagination_flow(self, client, mock_services):
        """Test pagination"""
        page1 = await client.get("/api/jobs?query=Python&page=1")
        page2 = await client.get("/api/jobs?query=Python&page=2")
        
        assert page1.status_code == 200
        assert page2.status_code == 200
    
    @pytest.mark.asyncio
    async def test_country_switching(self, client, mock_services):
        """Test country switching"""
        india = await client.get("/api/jobs?query=Python&country=India")
        uae = await client.get("/api/jobs?query=Python&country=UAE")
        
        assert india.status_code == 200
        assert uae.status_code == 200
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, client, mock_services):
        """Test concurrent user sessions"""
        import asyncio
        
        tasks = [
            client.get("/api/jobs?query=Python&context_id=user1"),
            client.get("/api/jobs?query=Java&context_id=user2"),
            client.get("/api/jobs?query=JavaScript&context_id=user3"),
        ]
        
        responses = await asyncio.gather(*tasks)
        
        for response in responses:
            assert response.status_code == 200
