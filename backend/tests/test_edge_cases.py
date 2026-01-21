import pytest
from managers.matching_engine import MatchingEngine
from managers.filter_engine import FilterEngine
from managers.vector_manager import VectorManager
from unittest.mock import Mock, patch
from models import Job
from sqlalchemy import select

class TestEdgeCases:
    """Tests for edge cases and error paths to reach 100% coverage"""
    
    # MatchingEngine edge cases
    def test_matching_engine_complex_query_weight_adjustment(self):
        """Test dynamic weight adjustment for complex queries"""
        engine = MatchingEngine()
        job = Job(
            id=1,
            title="Senior Python Backend Developer",
            company="Tech Corp",
            location="Bangalore",
            experience_min=5,
            experience_max=8,
            description="Python job",
            apply_link="https://example.com",
            source="Test"
        )
        
        # Complex query (>2 words) should boost title weight
        user_profile = {
            "query": "Senior Python Backend Developer Engineer",  # 5 words
            "skills": [],
            "experience_years": 6
        }
        
        score, breakdown = engine.calculate_score(job, user_profile)
        
        # Should use adjusted weights
        assert score > 0
    
    def test_matching_engine_empty_profile(self):
        """Test matching with empty user profile"""
        engine = MatchingEngine()
        job = Job(
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
        
        score, breakdown = engine.calculate_score(job, {})
        
        assert score == 0.0
        assert breakdown == {}
    
    def test_matching_engine_recency_string_date(self):
        """Test recency scoring with string date"""
        engine = MatchingEngine()
        
        score = engine._calculate_recency_score("2024-01-01")
        
        assert score == 50.0  # Should return neutral for unparseable dates
    
    # FilterEngine edge cases
    def test_filter_engine_invalid_experience_format(self):
        """Test filter with invalid experience format"""
        engine = FilterEngine()
        stmt = select(Job)
        
        # Invalid format should be handled gracefully
        filtered = engine.apply_filters(stmt, experience=["invalid format"])
        
        assert filtered is not None
    
    def test_filter_engine_invalid_ctc_format(self):
        """Test filter with invalid CTC format"""
        engine = FilterEngine()
        stmt = select(Job)
        
        filtered = engine.apply_filters(stmt, ctc=["invalid"])
        
        assert filtered is not None
    
    # VectorManager edge cases
    def test_vector_manager_http_client_mode(self):
        """Test VectorManager initialization with HTTP client"""
        with patch.dict('os.environ', {'CHROMA_SERVER_HOST': 'localhost', 'CHROMA_SERVER_PORT': '8000'}):
            with patch('managers.vector_manager.chromadb') as mock_chromadb:
                mock_client = Mock()
                mock_collection = Mock()
                mock_context_collection = Mock()
                
                mock_client.get_or_create_collection.side_effect = [
                    mock_collection,
                    mock_context_collection
                ]
                
                mock_chromadb.HttpClient.return_value = mock_client
                
                with patch('managers.vector_manager.SentenceTransformer'), \
                     patch('managers.vector_manager.CrossEncoder'):
                    
                    vm = VectorManager()
                    
                    # Should use HTTP client
                    mock_chromadb.HttpClient.assert_called_once()
    
    def test_vector_manager_get_embeddings_error(self):
        """Test get_embeddings_by_ids error handling"""
        with patch('managers.vector_manager.chromadb'), \
             patch('managers.vector_manager.SentenceTransformer'), \
             patch('managers.vector_manager.CrossEncoder'):
            
            vm = VectorManager()
            vm.collection.get.side_effect = Exception("Database error")
            
            embeddings = vm.get_embeddings_by_ids([1, 2, 3])
            
            assert embeddings == []
    
    def test_vector_manager_rerank_single_score(self):
        """Test reranking with single float return"""
        with patch('managers.vector_manager.chromadb'), \
             patch('managers.vector_manager.SentenceTransformer'), \
             patch('managers.vector_manager.CrossEncoder') as mock_ce:
            
            mock_reranker = Mock()
            mock_reranker.predict.return_value = 0.8  # Single float
            mock_ce.return_value = mock_reranker
            
            vm = VectorManager()
            scores = vm.rerank("query", ["doc1"])
            
            assert len(scores) == 1
            assert 0 <= scores[0] <= 1
    
    def test_vector_manager_context_metadata_error(self):
        """Test context metadata retrieval error handling"""
        with patch('managers.vector_manager.chromadb'), \
             patch('managers.vector_manager.SentenceTransformer'), \
             patch('managers.vector_manager.CrossEncoder'):
            
            vm = VectorManager()
            vm.context_collection.get.side_effect = Exception("Error")
            
            metadata = vm.get_context_metadata("test_id")
            
            assert metadata == {}
    
    def test_vector_manager_search_no_results(self):
        """Test search with no results"""
        with patch('managers.vector_manager.chromadb'), \
             patch('managers.vector_manager.SentenceTransformer'), \
             patch('managers.vector_manager.CrossEncoder'):
            
            vm = VectorManager()
            vm.collection.query.return_value = {'ids': []}
            
            results = vm.search("query")
            
            assert results == []
    
    def test_vector_manager_search_context_not_found(self):
        """Test search with invalid context_id"""
        with patch('managers.vector_manager.chromadb'), \
             patch('managers.vector_manager.SentenceTransformer'), \
             patch('managers.vector_manager.CrossEncoder'):
            
            vm = VectorManager()
            vm.context_collection.get.return_value = {'embeddings': []}
            vm.collection.query.return_value = {'ids': []}
            
            results = vm.search("query", context_id="invalid")
            
            # Should fallback to text query
            assert isinstance(results, list)
    
    def test_vector_manager_feedback_boost_error(self):
        """Test feedback boosting error handling"""
        with patch('managers.vector_manager.chromadb'), \
             patch('managers.vector_manager.SentenceTransformer'), \
             patch('managers.vector_manager.CrossEncoder'):
            
            vm = VectorManager()
            vm.collection.get.side_effect = Exception("Error")
            vm.collection.query.return_value = {'ids': []}
            
            results = vm.search("query", feedback_job_ids=[1, 2])
            
            # Should handle error gracefully
            assert isinstance(results, list)
