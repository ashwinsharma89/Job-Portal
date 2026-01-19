from sqlalchemy import or_, and_, select
from models import Job
from typing import List

class FilterEngine:
    def apply_filters(self, stmt, experience: List[str] = None, ctc: List[str] = None, 
                      skills: List[str] = None, jobPortals: List[str] = None):
        """
        Apply complex filters to the SQLAlchemy statement.
        """
        
        # 1. Experience Filter (Range Overlap Logic)
        if experience:
            exp_conditions = []
            for exp_range in experience:
                try:
                    parts = exp_range.replace(" Years", "").replace("+", "").split("-")
                    min_exp = int(parts[0])
                    max_exp = int(parts[1]) if len(parts) > 1 else 99
                    
                    # Logic: Job.min <= Filter.max AND (Job.max >= Filter.min OR Job.max == 0/Null)
                    exp_conditions.append(and_(
                        Job.experience_min <= max_exp,
                        or_(
                            Job.experience_max >= min_exp,
                            Job.experience_max == 0,
                            Job.experience_max == None
                        )
                    ))
                except ValueError:
                    continue
            
            if exp_conditions:
                stmt = stmt.where(or_(*exp_conditions))

        # 2. CTC Filter (Range Overlap Logic)
        if ctc:
            ctc_conditions = []
            for ctc_range in ctc:
                try:
                    parts = ctc_range.replace(" LPA", "").replace("+", "").split("-")
                    # Convert LPA to absolute number if needed. Assuming stored as raw number 500000.
                    # If JSearch returns 500000, we should filter by 500000.
                    # Format: 0-6 LPA -> 0 to 600000
                    
                    min_val = float(parts[0]) * 100000
                    max_val = float(parts[1]) * 100000 if len(parts) > 1 else 999999999
                    
                    # Logic: Range Overlap
                    # Job.min <= Filter.max AND (Job.max >= Filter.min OR Job.max is None/0)
                    ctc_conditions.append(and_(
                        Job.ctc_min <= max_val,
                        or_(
                            Job.ctc_max >= min_val,
                            Job.ctc_max == 0,
                            Job.ctc_max == None
                        )
                    ))
                except ValueError:
                    continue
            
            if ctc_conditions:
                 stmt = stmt.where(or_(*ctc_conditions))

        # 3. Skills Filter (Text Match)
        if skills:
            skill_conditions = []
            for skill in skills:
                term = f"%{skill}%"
                skill_conditions.append(or_(
                    Job.title.ilike(term),
                    Job.description.ilike(term)
                ))
            
            if skill_conditions:
                stmt = stmt.where(or_(*skill_conditions))

        # 4. Portals/Source Filter
        if jobPortals:
            portal_conditions = []
            for portal in jobPortals:
                portal_conditions.append(Job.source.ilike(f"%{portal}%"))
            
            if portal_conditions:
                stmt = stmt.where(or_(*portal_conditions))
                
        return stmt
