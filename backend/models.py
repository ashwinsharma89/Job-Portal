from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ARRAY, Text, func
from database import Base
from datetime import datetime

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    experience_min = Column(Integer, nullable=True)
    experience_max = Column(Integer, nullable=True)
    ctc_min = Column(Float, nullable=True)
    ctc_max = Column(Float, nullable=True)
    skills = Column(JSON, default=[])
    posted_at = Column(DateTime)
    apply_link = Column(String)
    source = Column(String)
    logo_url = Column(String, nullable=True)
    
    description = Column(Text, nullable=True)
    country = Column(String, default="India", index=True)
    
    # Store the query hash that fetched this job to associate it with search params
    # This allows us to retrieve relevant jobs for a cached query
    query_hash = Column(String, index=True) 
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SearchQuery(Base):
    __tablename__ = "search_queries"

    query_hash = Column(String, primary_key=True, index=True)
    last_fetched = Column(DateTime, default=datetime.utcnow)
    params = Column(JSON) # Store raw params for debugging/logging

class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, index=True)
    action_type = Column(String) # CLICK, APPLY, DISMISS
    context_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
