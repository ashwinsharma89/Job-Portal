import pytest
from managers.filter_engine import FilterEngine
from models import Job
from sqlalchemy import select

class TestFilterEngine:
    """Unit tests for the FilterEngine"""
    
    @pytest.fixture
    def engine(self):
        return FilterEngine()
    
    def test_experience_filter_single_range(self, engine):
        """Test experience filter with single range"""
        stmt = select(Job)
        filtered = engine.apply_filters(stmt, experience=["5-10 Years"])
        
        # Check that WHERE clause was added
        assert "experience_min" in str(filtered)
    
    def test_experience_filter_multiple_ranges(self, engine):
        """Test experience filter with multiple ranges"""
        stmt = select(Job)
        filtered = engine.apply_filters(stmt, experience=["0-2 Years", "5-10 Years"])
        
        # Should create OR conditions
        assert "experience_min" in str(filtered)
    
    def test_ctc_filter_single_range(self, engine):
        """Test CTC filter with single range"""
        stmt = select(Job)
        filtered = engine.apply_filters(stmt, ctc=["10-20 LPA"])
        
        assert "ctc_min" in str(filtered)
    
    def test_skills_filter(self, engine):
        """Test skills filter"""
        stmt = select(Job)
        filtered = engine.apply_filters(stmt, skills=["Python", "Django"])
        
        # Should add description LIKE conditions
        assert "description" in str(filtered).lower() or "skills" in str(filtered).lower()
    
    def test_portal_filter(self, engine):
        """Test job portal filter"""
        stmt = select(Job)
        filtered = engine.apply_filters(stmt, jobPortals=["Naukri", "LinkedIn"])
        
        assert "source" in str(filtered)
    
    def test_no_filters(self, engine):
        """Test that no filters returns original statement"""
        stmt = select(Job)
        filtered = engine.apply_filters(stmt)
        
        # Should be unchanged
        assert str(stmt) == str(filtered)
    
    def test_combined_filters(self, engine):
        """Test multiple filters applied together"""
        stmt = select(Job)
        filtered = engine.apply_filters(
            stmt,
            experience=["5-10 Years"],
            ctc=["10-20 LPA"],
            skills=["Python"],
            jobPortals=["Naukri"]
        )
        
        # Should have all conditions
        query_str = str(filtered)
        assert "experience_min" in query_str
        assert "ctc_min" in query_str
        assert "source" in query_str
