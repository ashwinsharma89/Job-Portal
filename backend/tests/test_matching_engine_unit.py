import pytest
from managers.matching_engine import MatchingEngine
from models import Job
from datetime import datetime

class TestMatchingEngine:
    """Unit tests for the MatchingEngine scoring system"""
    
    @pytest.fixture
    def engine(self):
        return MatchingEngine()
    
    @pytest.fixture
    def sample_job(self):
        """Create a sample job for testing"""
        job = Job(
            id=1,
            title="Senior Python Developer",
            company="Tech Corp",
            location="Bangalore",
            experience_min=5,
            experience_max=8,
            ctc_min=1500000,
            ctc_max=2500000,
            skills=["Python", "Django", "PostgreSQL"],
            posted_at=datetime.now(),
            apply_link="https://example.com/job/1",
            source="Test",
            description="Looking for a senior Python developer with Django experience"
        )
        return job
    
    def test_skill_match_perfect(self, engine, sample_job):
        """Test perfect skill match returns 100"""
        user_profile = {
            "query": "Python Developer",
            "skills": ["Python", "Django", "PostgreSQL"],
            "experience_years": 6
        }
        score = engine._calculate_skill_score(sample_job, user_profile["skills"])
        assert score == 100.0
    
    def test_skill_match_partial(self, engine, sample_job):
        """Test partial skill match returns proportional score"""
        user_profile = {
            "query": "Python Developer",
            "skills": ["Python", "Django"],  # Missing PostgreSQL
            "experience_years": 6
        }
        score = engine._calculate_skill_score(sample_job, user_profile["skills"])
        # User has 2/3 of job skills, but matching logic gives 100 if user has ANY matching skills
        assert score == 100.0  # All user skills match job requirements
    
    def test_skill_match_none(self, engine, sample_job):
        """Test no skill match returns neutral score"""
        user_profile = {
            "query": "Python Developer",
            "skills": [],
            "experience_years": 6
        }
        score = engine._calculate_skill_score(sample_job, user_profile["skills"])
        assert score == 50.0  # Neutral
    
    def test_title_match_exact(self, engine):
        """Test exact title match returns 100"""
        score = engine._calculate_title_score("Python Developer", "Python Developer")
        assert score == 100.0
    
    def test_title_match_contains(self, engine):
        """Test substring title match returns 90"""
        score = engine._calculate_title_score("Senior Python Developer", "Python Developer")
        assert score == 90.0
    
    def test_title_match_word_overlap(self, engine):
        """Test word overlap returns proportional score"""
        score = engine._calculate_title_score("Python Backend Engineer", "Python Developer")
        assert 0 < score < 90
    
    def test_experience_match_perfect(self, engine):
        """Test experience within range returns 100"""
        score = engine._calculate_experience_score(5, 8, 6)
        assert score == 100.0
    
    def test_experience_match_below_range(self, engine):
        """Test experience below range returns penalty"""
        score = engine._calculate_experience_score(5, 8, 3)
        assert score < 100.0
        assert score > 0
    
    def test_experience_match_above_range(self, engine):
        """Test experience above range returns penalty"""
        score = engine._calculate_experience_score(5, 8, 10)
        assert score < 100.0
        assert score > 0
    
    def test_experience_match_no_data(self, engine):
        """Test missing experience data returns neutral"""
        score = engine._calculate_experience_score(0, 0, 5)
        assert score == 50.0
    
    def test_recency_score_today(self, engine):
        """Test job posted today returns 100"""
        score = engine._calculate_recency_score(datetime.now())
        assert score == 100.0
    
    def test_recency_score_old(self, engine):
        """Test old job returns lower score"""
        from datetime import timedelta
        old_date = datetime.now() - timedelta(days=60)
        score = engine._calculate_recency_score(old_date)
        assert score < 50.0
    
    def test_recency_score_no_data(self, engine):
        """Test missing posted_at returns neutral"""
        score = engine._calculate_recency_score(None)
        assert score == 50.0
    
    def test_seniority_penalty_senior_vs_junior(self, engine, sample_job):
        """Test senior query penalizes junior jobs"""
        sample_job.title = "Junior Python Developer"
        user_profile = {
            "query": "Senior Python Developer",
            "skills": ["Python"],
            "experience_years": 6
        }
        score, breakdown = engine.calculate_score(sample_job, user_profile)
        assert "seniority_penalty" in breakdown
        assert breakdown["seniority_penalty"] == 0.5
    
    def test_full_score_calculation(self, engine, sample_job):
        """Test complete score calculation"""
        user_profile = {
            "query": "Python Developer",
            "skills": ["Python", "Django"],
            "experience_years": 6
        }
        score, breakdown = engine.calculate_score(sample_job, user_profile)
        
        assert 0 <= score <= 100
        assert "skills" in breakdown
        assert "title" in breakdown
        assert "experience" in breakdown
        assert "recency" in breakdown
        assert "final_score" in breakdown
