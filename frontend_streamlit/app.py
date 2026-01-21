import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
st.set_page_config(page_title="Job Portal AI", page_icon="🚀", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .job-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border: 1px solid #333;
    }
    .job-title {
        font-size: 18px;
        font-weight: bold;
        color: #4da6ff;
    }
    .company-name {
        color: #aaa;
        font-size: 14px;
    }
    .location {
        color: #FFD700;
        font-size: 13px;
    }
    .tag {
        background-color: #333;
        color: #fff;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Filters ---
st.sidebar.title("Filters")

search_query = st.sidebar.text_input("Keywords", "Data Analyst")
locations = st.sidebar.multiselect(
    "Locations", 
    ["Delhi NCR", "Bangalore", "Mumbai", "Hyderabad", "Pune", "Chennai", "Kolkata"],
    default=["Delhi NCR"]
)

experience = st.sidebar.slider("Experience (Years)", 0, 30, (0, 10))
country = st.sidebar.selectbox("Country", ["India", "UAE", "USA"], index=0)

# Resume Upload
st.sidebar.markdown("---")
st.sidebar.subheader("Resume Context")
uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF/DOCX)", type=['pdf', 'docx', 'txt'])

context_id = None
if uploaded_file is not None:
    # Upload logic
    try:
        with st.spinner("Analyzing Resume..."):
            # Streamlit UploadedFile has .name, .type, and .getvalue()
            # requests.post expecting 'files' dictionary
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_URL}/api/context/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                context_id = data.get("context_id")
                st.sidebar.success("Resume Analyzed!")
            else:
                st.sidebar.error("Upload failed")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- Main Area ---
st.title("🚀 AI-Powered Job Search")

if st.button("Search Jobs", type="primary"):
    with st.spinner(f"Searching for '{search_query}' in {', '.join(locations)}..."):
        try:
            params = {
                "query": search_query,
                "country": country,
                "page": 1
            }
            
            # Handle multiple locations for query params
            # requests handles list params as locations=A&locations=B
            if locations:
                params["locations"] = locations
            
            if context_id:
                params["context_id"] = context_id
            
            response = requests.get(f"{API_URL}/api/jobs", params=params)
            
            if response.status_code == 200:
                jobs = response.json()
                st.subheader(f"Found {len(jobs)} Jobs")
                
                if jobs:
                    for job in jobs:
                        # Job Card HTML
                        skills_html = "".join([f"<span class='tag'>{s}</span>" for s in job.get('skills', [])[:4]])
                        
                        card_html = f"""
                        <div class="job-card">
                            <div class="job-title">{job['title']}</div>
                            <div class="company-name">{job['company']}</div>
                            <div class="location">📍 {job.get('location', 'Remote')}</div>
                            <p style="font-size: 13px; color: #ccc; margin-top: 10px;">
                                {job.get('description', '')[:200]}...
                            </p>
                            <div style="margin-top: 10px;">{skills_html}</div>
                            <div style="margin-top: 15px; text-align: right;">
                                <a href="{job.get('apply_link', '#')}" target="_blank" 
                                   style="background-color: #4da6ff; color: white; padding: 6px 12px; border-radius: 5px; text-decoration: none; font-size: 14px;">
                                   Apply Now ↗
                                </a>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.info("No jobs found. Try broadening your location or keywords.")
            else:
                st.error(f"Error fetching jobs: {response.status_code}")
                
        except Exception as e:
            st.error(f"Connection Error: {e}. Is the backend running on port 8000?")

else:
    st.info("Adjust filters on the left and click 'Search Jobs' to begin.")
