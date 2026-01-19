from typing import List, Dict, Any

# Mock VectorManager
class MockVectorManager:
    def get_context_metadata(self, context_id: str) -> Dict:
        if context_id == "valid_ctx":
            return {
                "skills": ["Python", "Django", "Machine Learning"],
                "experience_years": 8
            }
        return {}

# Mock JobService logic for testing
def test_profile_enrichment():
    vector_manager = MockVectorManager()
    
    # Scene 1: User search "Python", no context
    user_profile = {
        "query": "Python",
        "skills": ["Python"],
        "experience_years": 0
    }
    
    print("Base Profile:", user_profile)
    
    # Scene 2: Enrich with Context
    context_id = "valid_ctx"
    ctx_meta = vector_manager.get_context_metadata(context_id)
    
    if ctx_meta:
        # 1. Skills Merge
        resume_skills = ctx_meta.get("skills", [])
        current_skills = user_profile.get("skills", [])
        user_profile["skills"] = list(set(current_skills + resume_skills))
        
        # 2. Experience Override (since base is 0)
        if user_profile["experience_years"] == 0 and "experience_years" in ctx_meta:
            user_profile["experience_years"] = int(ctx_meta["experience_years"])
            
    print("Enriched Profile:", user_profile)
    
    assert "Django" in user_profile["skills"]
    assert user_profile["experience_years"] == 8
    print("TEST PASSED: Profile enriched correctly.")

if __name__ == "__main__":
    test_profile_enrichment()
