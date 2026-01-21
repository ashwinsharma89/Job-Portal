import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Job, SearchQuery, UserInteraction
from datetime import datetime

class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    @pytest_asyncio.fixture
    async def test_db(self):
        """Create test database"""
        # Use in-memory SQLite for testing
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            yield session
        
        await engine.dispose()
    
    @pytest.mark.asyncio
    async def test_job_create(self, test_db):
        """Test creating a job in database"""
        job = Job(
            id=1,
            title="Python Developer",
            company="Tech Corp",
            location="Bangalore",
            experience_min=5,
            experience_max=8,
            ctc_min=1000000,
            ctc_max=2000000,
            apply_link="https://example.com/job/1",
            source="Test",
            description="Test job"
        )
        
        test_db.add(job)
        await test_db.commit()
        
        # Verify it was created
        from sqlalchemy import select
        stmt = select(Job).where(Job.id == 1)
        result = await test_db.execute(stmt)
        retrieved_job = result.scalar_one_or_none()
        
        assert retrieved_job is not None
        assert retrieved_job.title == "Python Developer"
    
    @pytest.mark.asyncio
    async def test_job_update(self, test_db):
        """Test updating a job"""
        job = Job(
            id=2,
            title="Java Developer",
            company="Corp",
            location="Mumbai",
            apply_link="https://example.com/job/2",
            source="Test"
        )
        
        test_db.add(job)
        await test_db.commit()
        
        # Update the job
        from sqlalchemy import select
        stmt = select(Job).where(Job.id == 2)
        result = await test_db.execute(stmt)
        job_to_update = result.scalar_one()
        
        job_to_update.title = "Senior Java Developer"
        await test_db.commit()
        
        # Verify update
        result = await test_db.execute(stmt)
        updated_job = result.scalar_one()
        assert updated_job.title == "Senior Java Developer"
    
    @pytest.mark.asyncio
    async def test_job_delete(self, test_db):
        """Test deleting a job"""
        job = Job(
            id=3,
            title="Test Job",
            company="Test Corp",
            location="Test City",
            apply_link="https://example.com/job/3",
            source="Test"
        )
        
        test_db.add(job)
        await test_db.commit()
        
        # Delete the job
        await test_db.delete(job)
        await test_db.commit()
        
        # Verify deletion
        from sqlalchemy import select
        stmt = select(Job).where(Job.id == 3)
        result = await test_db.execute(stmt)
        deleted_job = result.scalar_one_or_none()
        
        assert deleted_job is None
    
    @pytest.mark.asyncio
    async def test_search_query_cache(self, test_db):
        """Test search query caching"""
        search_query = SearchQuery(
            query_hash="test_hash_123",
            last_fetched=datetime.utcnow(),
            params={"query": "Python", "location": "Bangalore"}
        )
        
        test_db.add(search_query)
        await test_db.commit()
        
        # Retrieve it
        from sqlalchemy import select
        stmt = select(SearchQuery).where(SearchQuery.query_hash == "test_hash_123")
        result = await test_db.execute(stmt)
        cached_query = result.scalar_one_or_none()
        
        assert cached_query is not None
        assert cached_query.params["query"] == "Python"
    
    @pytest.mark.asyncio
    async def test_user_interaction_tracking(self, test_db):
        """Test user interaction tracking"""
        interaction = UserInteraction(
            job_id=1,
            action_type="CLICK",
            context_id="test_context",
            timestamp=datetime.utcnow()
        )
        
        test_db.add(interaction)
        await test_db.commit()
        
        # Retrieve it
        from sqlalchemy import select
        stmt = select(UserInteraction).where(UserInteraction.job_id == 1)
        result = await test_db.execute(stmt)
        tracked_interaction = result.scalar_one_or_none()
        
        assert tracked_interaction is not None
        assert tracked_interaction.action_type == "CLICK"
    
    @pytest.mark.asyncio
    async def test_bulk_job_insert(self, test_db):
        """Test inserting multiple jobs"""
        jobs = [
            Job(
                id=i,
                title=f"Job {i}",
                company="Corp",
                location="City",
                apply_link=f"https://example.com/job/{i}",
                source="Test"
            )
            for i in range(10, 20)
        ]
        
        test_db.add_all(jobs)
        await test_db.commit()
        
        # Verify all were inserted
        from sqlalchemy import select, func
        stmt = select(func.count(Job.id))
        result = await test_db.execute(stmt)
        count = result.scalar()
        
        assert count >= 10
    
    @pytest.mark.asyncio
    async def test_job_query_filtering(self, test_db):
        """Test querying jobs with filters"""
        # Add test jobs
        jobs = [
            Job(
                id=20,
                title="Python Developer",
                company="Corp A",
                location="Bangalore",
                experience_min=5,
                experience_max=8,
                apply_link="https://example.com/job/20",
                source="Naukri"
            ),
            Job(
                id=21,
                title="Java Developer",
                company="Corp B",
                location="Mumbai",
                experience_min=3,
                experience_max=5,
                apply_link="https://example.com/job/21",
                source="LinkedIn"
            )
        ]
        
        test_db.add_all(jobs)
        await test_db.commit()
        
        # Query with filter
        from sqlalchemy import select
        stmt = select(Job).where(Job.location == "Bangalore")
        result = await test_db.execute(stmt)
        bangalore_jobs = result.scalars().all()
        
        assert len(bangalore_jobs) >= 1
        assert all(job.location == "Bangalore" for job in bangalore_jobs)
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, test_db):
        """Test transaction rollback"""
        job = Job(
            id=30,
            title="Test Job",
            company="Test",
            location="Test",
            apply_link="https://example.com/job/30",
            source="Test"
        )
        
        test_db.add(job)
        # Don't commit, rollback instead
        await test_db.rollback()
        
        # Verify it wasn't saved
        from sqlalchemy import select
        stmt = select(Job).where(Job.id == 30)
        result = await test_db.execute(stmt)
        rolled_back_job = result.scalar_one_or_none()
        
        assert rolled_back_job is None
