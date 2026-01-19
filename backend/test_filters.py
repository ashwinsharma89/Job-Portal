import unittest
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from models import Job
from managers.filter_engine import FilterEngine
from database import Base, engine
import asyncio

# Mock Job Object for SQL Expression testing
# Since FilterEngine generates SQL expressions, we effectively need a real SQL execution 
# or a way to compile the expression. Best to use an in-memory SQLite DB for logic test.

class TestFilterEngine(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # We need an async setup, but unittest is sync. 
        # We will use a helper to run async code.
        cls.loop = asyncio.new_event_loop()
        
    def run_async(self, coro):
        return self.loop.run_until_complete(coro)

    def test_ctc_overlap_logic(self):
        # This test documents the CURRENT behavior vs DESIRED behavior
        
        # Scenario: Job pays 10-50 LPA. User asks for 40-50 LPA.
        # Job.ctc_min = 1000000
        # Job.ctc_max = 5000000
        # Filter: min=4000000, max=5000000
        
        # Current Logic in Code:
        # ctc_conditions.append(and_(Job.ctc_min >= min_val, Job.ctc_min <= max_val))
        
        job_min = 1000000
        filter_min = 4000000
        filter_max = 5000000
        
        # Test Current Implementation Logic Manually
        # 10L >= 40L ? False.
        passes_current = (job_min >= filter_min) and (job_min <= filter_max)
        print(f"\n[Scenario: Wide Job (10-50L) vs Specific Query (40-50L)]")
        print(f"Current Logic (Min In Range): {passes_current}")
        
        # Desired Logic (Overlap)
        # Job.min <= Filter.max AND Job.max >= Filter.min
        job_max = 5000000
        passes_desired = (job_min <= filter_max) and (job_max >= filter_min)
        print(f"Desired Logic (Overlap): {passes_desired}")
        
        self.assertFalse(passes_current, "Current logic should fail this case")
        self.assertTrue(passes_desired, "Desired logic should pass this case")

    def test_ctc_partial_overlap(self):
        # Scenario: Job pays 10-15 LPA. User asks for 12-18 LPA.
        # Job is a valid candidate for the lower end of the user's range.
        
        job_min = 10 * 100000
        job_max = 15 * 100000
        filter_min = 12 * 100000
        filter_max = 18 * 100000
        
        # Current Logic
        # 10L >= 12L ? False
        passes_current = (job_min >= filter_min) and (job_min <= filter_max)
        
        # Desired Logic
        passes_desired = (job_min <= filter_max) and (job_max >= filter_min)
        
        print(f"\n[Scenario: Partial Overlap (10-15L) vs (12-18L)]")
        print(f"Current Logic: {passes_current}")
        print(f"Desired Logic: {passes_desired}")
        
        self.assertFalse(passes_current)
        self.assertTrue(passes_desired)

if __name__ == '__main__':
    unittest.main()
