import streamlit as st
import asyncio
import os
import sys

# Ensure backend directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import AsyncSessionLocal
from services import JobService
from managers.vector_manager import VectorManager

# Page Config
st.set_page_config(
    page_title="Agentic Job Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Cards
st.markdown("""
<style>
    .job-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .card-title {
        color: #1a73e8;
        font-size: 1.2rem;
        font-weight: 600;
        text-decoration: none;
    }
    .card-company {
        color: #5f6368;
        font-weight: 500;
    }
    .card-meta {
        font-size: 0.9rem;
        color: #70757a;
        margin-top: 0.5rem;
    }
    .score-badge {
        background-color: #e6f4ea;
        color: #137333;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Async Helper
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

async def search_jobs(query, location, experience_year, ctc_range, skills, context_id=None):
    async with AsyncSessionLocal() as db:
        vector_manager = VectorManager() # Will use default Chroma settings
        service = JobService(db, vector_manager=vector_manager)
        
        # filters construction
        exp_filter = [f"{experience_year} Years"] if experience_year else None
        ctc_filter = [ctc_range] if ctc_range else None
        
        jobs = await service.get_jobs(
            query=query,
            location=location,
            page=1,
            experience=exp_filter,
            ctc=ctc_filter,
            skills=skills,
            context_id=context_id,
            country="India" # Default for now, can make dynamic
        )
        return jobs

# --- Sidebar ---
st.sidebar.title("🤖 Agent Filters")

# Resume Upload Section
st.sidebar.subheader("📄 Dynamic Context")
uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF/DOCX)", type=['pdf', 'docx', 'doc'])

if uploaded_file and "context_id" not in st.session_state:
    with st.spinner("Analyzing Resume..."):
        try:
            # Save temp file
            import tempfile
            from utils.resume_parser import ResumeParser
            
            # Create a mock upload file object or read content directly
            # Since ResumeParser expects parsing logic, let's just do it inline or adapt
            # Streamlit UploadedFile -> bytes
            bytes_data = uploaded_file.getvalue()
            
            # Simple Text Extraction (Inline for Streamlit simplicity)
            text = ""
            if uploaded_file.name.endswith(".pdf"):
                import pypdf
                pdf = pypdf.PdfReader(uploaded_file)
                text = "\n".join(page.extract_text() for page in pdf.pages)
            elif uploaded_file.name.endswith(".docx"):
                import docx
                doc = docx.Document(uploaded_file)
                text = "\n".join(para.text for para in doc.paragraphs)
            else:
                text = str(bytes_data, "utf-8")
                
            # Embed
            vm = VectorManager()
            context_id = vm.create_context_embedding(text)
            st.session_state["context_id"] = context_id
            st.sidebar.success("Resume Analyzed! Agent will prioritize matching jobs.")
            
        except Exception as e:
            st.sidebar.error(f"Failed to parse resume: {e}")

if "context_id" in st.session_state:
    st.sidebar.info(f"Active Context: {st.session_state['context_id'][:8]}...")
    if st.sidebar.button("Clear Context"):
        del st.session_state["context_id"]
        st.rerun()

st.sidebar.markdown("---")

query = st.sidebar.text_input("Job Role", "Python Developer", placeholder="e.g. Data Scientist")
location = st.sidebar.text_input("City", "Bangalore", placeholder="e.g. Bangalore")

st.sidebar.markdown("### Refine Search")
exp_options = ["0-3 Years", "3-6 Years", "6-10 Years", "10-14 Years", "14+ Years"]
selected_exp = st.sidebar.selectbox("Experience Level", ["Any"] + exp_options)
real_exp = selected_exp if selected_exp != "Any" else None

ctc_options = ["0-10 LPA", "10-20 LPA", "20-30 LPA", "30-50 LPA", "50+ LPA"]
selected_ctc = st.sidebar.selectbox("Salary Range (CTC)", ["Any"] + ctc_options)
real_ctc = selected_ctc if selected_ctc != "Any" else None

skills_input = st.sidebar.text_area("Key Skills (Comma separated)", "Python, SQL, FastAPI")
skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]

search_btn = st.sidebar.button("Find Jobs", type="primary")

# --- Main Content ---
st.title("Agentic Job Platform")
st.markdown("> **AI-Powered Search Engine** • *Hybrid Vector Search + Autonomous Scraping*")

if search_btn or query: 
    with st.spinner(f"Agent is searching for '{query}' in '{location}'..."):
        try:
            context_id = st.session_state.get("context_id")
            jobs, should_scrape = run_async(search_jobs(query, location, real_exp, real_ctc, skills_list, context_id))
            
            if should_scrape:
                st.info("📡 **AI Agent Active**: Searching for more fresh results in background...")
            
            st.success(f"Found {len(jobs)} relevant jobs.")
            
            for job in jobs:
                # Calculate display values
                salary = f"₹{int(job.ctc_min/100000)}L - ₹{int(job.ctc_max/100000)}L" if job.ctc_min else "Not Disclosed"
                exp = f"{job.experience_min}-{job.experience_max} Yrs" if job.experience_min is not None else "Entry Level"
                score = int(job.relevance_score * 100) if hasattr(job, 'relevance_score') else 0
                
                with st.container():
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.markdown(f"""
                        <div class="job-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <a href="{job.apply_link}" target="_blank" class="card-title">{job.title}</a>
                                <span class="score-badge">Match: {score}%</span>
                            </div>
                            <div class="card-company">{job.company} • {job.location or 'Remote'}</div>
                            <div class="card-meta">
                                💼 {exp} &nbsp; | &nbsp; 💰 {salary} &nbsp; | &nbsp; 📅 {job.posted_at.strftime('%d %b') if job.posted_at else 'Recent'}
                            </div>
                            <div style="margin-top:0.5rem; font-size:0.85rem; color:#444;">
                                {job.description[:200] + "..." if job.description else "No description available."}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Debug Info / Breakdown
                        if hasattr(job, 'match_breakdown') and job.match_breakdown:
                             st.json(job.match_breakdown, expanded=False)
                        st.link_button("Apply Now", job.apply_link if job.apply_link else "#")

        except Exception as e:
            st.error(f"Search Failed: {e}")
            st.exception(e)
