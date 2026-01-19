from managers.matching_engine import MatchingEngine

def test_dynamic_weights():
    engine = MatchingEngine()
    
    job_perfect = type('Job', (), {
        'title': 'Senior Python Developer', 
        'description': 'Python', 
        'skills': ['Python'],
        'experience_min': 5, 'experience_max': 8,
        'posted_at': None
    })
    
    # 1. Short Query (Standard Weights)
    profile_short = {"query": "Python", "skills": ["Python"], "experience_years": 5}
    score_short = engine.calculate_score(job_perfect, profile_short)
    print(f"Short Query Score: {score_short}")
    
    # 2. Complex Query (Boosted Title)
    # The title match is 100%. In complex query, Title weight is 0.5 (vs 0.3).
    # So score should be higher if title match is high.
    profile_complex = {"query": "Senior Python Developer", "skills": ["Python"], "experience_years": 5}
    score_complex = engine.calculate_score(job_perfect, profile_complex)
    print(f"Complex Query Score: {score_complex}")
    
    assert score_complex >= score_short, "Complex query should weight title match higher"

def test_negative_filtering():
    engine = MatchingEngine()
    
    # Job is "Junior", User is "Senior"
    job_junior = type('Job', (), {
        'title': 'Junior Python Developer', 
        'description': 'Python', 
        'skills': ['Python'],
        'experience_min': 1, 'experience_max': 3,
        'posted_at': None
    })
    
    profile_senior = {"query": "Senior Python Developer", "skills": ["Python"], "experience_years": 5}
    
    score = engine.calculate_score(job_junior, profile_senior)
    print(f"Negative Filtering Score (Senior query vs Junior job): {score}")
    
    # Expected penalty: 50%. 
    # Without penalty: might be ~60% (due to title overlap 'Python Developer').
    # With penalty: ~30%.
    assert score < 50.0, "Negative filtering should penalize mismatches"

if __name__ == "__main__":
    test_dynamic_weights()
    test_negative_filtering()
    print("ALL TESTS PASSED")
