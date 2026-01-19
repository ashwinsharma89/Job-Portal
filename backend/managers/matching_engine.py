from typing import List, Dict
import re
from datetime import datetime

class MatchingEngine:
    def __init__(self):
        # Weight Config
        self.weights = {
            "skills": 0.40,
            "title": 0.30,
            "experience": 0.20,
            "recency": 0.10
        }

    def calculate_score(self, job: object, user_profile: Dict) -> tuple[float, Dict[str, float]]:
        """
        Calculate a 0-100 relevance score for a job against a user profile.
        Returns: (score, breakdown_dict)
        """
        if not user_profile:
            return 0.0, {}

        # --- Dynamic Config based on Query Complexity ---
        query = user_profile.get("query", "")
        q_words = len(query.split())
        
        # Default Weights
        weights = self.weights.copy()
        
        # If query is complex (e.g. "Senior Python Backend Developer"), boost Title weight
        if q_words > 2:
            weights = {
                "skills": 0.30,
                "title": 0.50, # Boost Title
                "experience": 0.10,
                "recency": 0.10
            }
        
        score = 0.0
        breakdown = {}
        
        # 1. Skill Match
        skill_score = self._calculate_skill_score(job, user_profile.get("skills", []))
        score += skill_score * weights["skills"]
        breakdown["skills"] = round(skill_score, 1)
        
        # 2. Title Match
        title_score = self._calculate_title_score(job.title, query)
        score += title_score * weights["title"]
        breakdown["title"] = round(title_score, 1)
        
        # 3. Experience Match
        target_exp = user_profile.get("experience_years", 0)
        exp_score = self._calculate_experience_score(job.experience_min, job.experience_max, target_exp)
        score += exp_score * weights["experience"]
        breakdown["experience"] = round(exp_score, 1)
        
        # 4. Recency
        rec_score = self._calculate_recency_score(job.posted_at)
        score += rec_score * weights["recency"]
        breakdown["recency"] = round(rec_score, 1)
        
        # --- Negative Filtering (Penalty) ---
        penalty_factor = 1.0
        job_title_lower = job.title.lower() if job.title else ""
        query_lower = query.lower()
        
        # Seniority Map: Query Term -> Negative Terms
        negative_map = {
            "senior": ["junior", "intern", "entry level", "fresher"],
            "lead": ["junior", "intern", "entry level"],
            "principal": ["junior", "intern", "senior"],
            "junior": ["senior", "lead", "principal", "manager", "architect"],
            "intern": ["senior", "lead", "principal", "manager"],
        }
        
        for q_term, neg_terms in negative_map.items():
            if q_term in query_lower:
                for neg in neg_terms:
                    # strict word boundary check to avoid "lead" in "leader" (which is fine)
                    if f" {neg} " in f" {job_title_lower} ":
                        penalty_factor = 0.5 # 50% Penalty
                        break
        
        if penalty_factor != 1.0:
            score *= penalty_factor
            breakdown["seniority_penalty"] = penalty_factor
            
        final_score = round(min(score, 100.0), 1)
        breakdown["final_score"] = final_score
        
        return final_score, breakdown

    def _calculate_skill_score(self, job, user_skills: List[str]) -> float:
        if not user_skills:
            return 50.0 # Neural if no skills specified
            
        full_text = (job.title + " " + job.description + " " + (str(job.skills) if job.skills else "")).lower()
        
        matches = 0
        for skill in user_skills:
            # Simple boundary check to avoid substring matches like "Go" in "Good"
            # Using simple text check for speed for now, regex ideal but slower
            if skill.lower() in full_text:
                matches += 1
                
        # Score = (matches / total_user_skills) * 100
        # But cap it, usually 50-80% match is great
        if len(user_skills) == 0: return 0
        
        ratio = matches / len(user_skills)
        return min(ratio * 100, 100.0)

    def _calculate_title_score(self, job_title: str, query: str) -> float:
        if not query: return 50.0
        
        job_title = job_title.lower()
        query = query.lower()
        
        # Exact match
        if query == job_title:
            return 100.0
            
        # Contains match
        if query in job_title:
            return 90.0
            
        # Word overlap
        q_words = set(query.split())
        t_words = set(job_title.split())
        overlap = len(q_words.intersection(t_words))
        
        if len(q_words) > 0:
            return (overlap / len(q_words)) * 80.0
            
        return 0.0

    def _calculate_experience_score(self, job_min: int, job_max: int, user_exp: int) -> float:
        # If job has no exp data, return neutral score
        if job_min == 0 and job_max == 0:
            return 50.0
            
        # Check if user exp falls within range
        # Assume job_max 0 means "min+" (e.g. 5+ years) -> consider max as min+5
        effective_max = job_max if job_max > 0 else job_min + 5
        
        if job_min <= user_exp <= effective_max:
            return 100.0
        
        # Distance penalty
        # Distance to nearest boundary
        if user_exp < job_min:
            dist = job_min - user_exp
        else:
            dist = user_exp - effective_max
            
        # Decay: -20 points per year of mismatch
        score = 100.0 - (dist * 20)
        return max(score, 0.0)

    def _calculate_recency_score(self, posted_at) -> float:
        if not posted_at:
            return 50.0 # Neutral
            
        if isinstance(posted_at, str):
             # Try parse or return neutral
             return 50.0
             
        # Check delta days
        try:
            delta = datetime.now() - posted_at
            days = delta.days
            
            if days <= 1: return 100.0
            if days <= 3: return 90.0
            if days <= 7: return 80.0
            if days <= 14: return 60.0
            if days <= 30: return 40.0
            return 20.0
        except:
            return 50.0
