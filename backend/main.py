from fastapi import FastAPI, Depends, HTTPException, Query
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine, Base, AsyncSessionLocal
from services import JobService
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from models import UserInteraction
# Load environment variables from parent directory's .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from managers.vector_manager import VectorManager

# Global Vector Manager Instance
vector_manager_instance = None

# --- Pydantic Schemas ---
class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    ctc_min: Optional[float] = None
    ctc_max: Optional[float] = None
    posted_at: Optional[datetime] = None
    apply_link: Optional[str] = None
    source: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    relevance_score: float = 0.0
    match_breakdown: Optional[Dict[str, float]] = None
    
    class Config:
        from_attributes = True

class FeedbackRequest(BaseModel):
    job_id: int
    action_type: str # CLICK, APPLY, DISMISS
    context_id: Optional[str] = None

# --- Lifespan for DB Init ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load DB tables on startup
    try:
        # Enforce a 5-second timeout on DB connection
        async with asyncio.timeout(5): 
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        print("Database connected successfully.")
    except Exception as e:
        print(f"WARNING: Database connection failed (Timeout/Error): {e}")
        print("Running in stateless mode (Caching disabled).")
        
    # Initialize Vector Manager (Load Models)
    try:
        global vector_manager_instance
        print("Initializing Vector Manager (Loading AI Models)...")
        vector_manager_instance = VectorManager()
        print("Vector Manager Ready 🧠")
    except Exception as e:
        print(f"Failed to load Vector Manager: {e}")

    yield



app = FastAPI(title="Job Portal API", version="1.0.0", lifespan=lifespan)

# --- CORS ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:8501", 
    "*"  # Allow all for development/sharing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Debug-Info", "X-Background-Scrape"],
)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from utils.profiler import RequestProfiler

class ProfilerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        profiler = RequestProfiler()
        request.state.profiler = profiler
        
        response = await call_next(request)
        
        # Inject Debug Header
        response.headers["X-Debug-Info"] = profiler.get_header_json()
        return response

app.add_middleware(ProfilerMiddleware)

# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "Job Portal API is running"}

from fastapi import Response, Request, File, UploadFile
from utils.resume_parser import ResumeParser

@app.post("/api/context/upload")
async def upload_context(file: UploadFile = File(...)):
    """
    Parses a resume/doc, stores embedding in Chroma, and returns a Context ID.
    """
    try:
        text = await ResumeParser.extract_text(file)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from file")
            
        # Create Embedding & Store
        if not vector_manager_instance:
             raise HTTPException(status_code=503, detail="Vector Database not initialized")
             
        context_id = vector_manager_instance.create_context_embedding(text)
        
        return {
            "context_id": context_id,
            "filename": file.filename,
            "preview": text[:200] + "..."
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/api/feedback")
async def log_feedback(feedback: FeedbackRequest, db: AsyncSession = Depends(get_db)):
    """
    Log user interaction (Click, Apply, Dismiss) for future personalization.
    """
    try:
        interaction = UserInteraction(
            job_id=feedback.job_id,
            action_type=feedback.action_type,
            context_id=feedback.context_id
        )
        db.add(interaction)
        await db.commit()
        return {"status": "logged", "job_id": feedback.job_id}
    except Exception as e:
        # Don't fail the request, just log error
        print(f"Feedback logging failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(
    response: Response,
    request: Request,
    query: str = Query(..., description="Job title or keyword"),
    locations: List[str] = Query(None, description="Locations to filter by (e.g., 'Bangalore', 'Mumbai')"),
    page: int = Query(1, ge=1, description="Page number"),
    experience: List[str] = Query(None, description="Experience ranges (e.g., '0-2 Years')"),
    ctc: List[str] = Query(None, description="CTC ranges (e.g., '0-6 LPA')"),
    skills: List[str] = Query(None, description="Skills to filter by"),
    jobPortals: List[str] = Query(None, description="Job Portals to filter by (e.g., 'LinkedIn', 'Naukri')"),
    context_id: Optional[str] = Query(None, description="Context ID from uploaded resume"),
    country: Optional[str] = Query("India", description="Market Region (India, UAE)"),
    db: AsyncSession = Depends(get_db)
):
    profiler = getattr(request.state, "profiler", None)
    service = JobService(db, vector_manager=vector_manager_instance, profiler=profiler)
    jobs, triggered = await service.get_jobs(
        query=query, 
        locations=locations, 
        page=page,
        experience=experience,
        ctc=ctc,
        skills=skills,
        jobPortals=jobPortals,
        context_id=context_id,
        country=country
    )
    
    if triggered:
        response.headers["X-Background-Scrape"] = "true"
        
    return jobs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
