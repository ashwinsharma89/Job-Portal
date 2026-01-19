# Agentic Job Platform
> **AI-Powered "Enterprise Grade" Search Engine**
> *Hybrid Search • Vector Intelligence • Autonomous Scraping • Agentic Feedback Loop*

A personalized job portal aggregating tech jobs from multiple Indian platforms, featuring smart filtering and caching.

## Tech Stack
- **Frontend:** React (Vite) + Tailwind CSS
- **Backend:** FastAPI (Python) + SQLAlchemy
- **Database:** PostgreSQL (Supabase) + AsyncPG
- **API:** JSearch (RapidAPI)

## Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Supabase Database URL
- RapidAPI Key (JSearch)

## Setup Instructions

### 1. Database & Environment
Ensure you have a `.env` file in the root directory with the following variables:
```env
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:[port]/[db]
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=jsearch.p.rapidapi.com
```

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start Backend (Port 8000)
uvicorn main:app --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install

# Start Frontend (Port 5173)
npm run dev
```
Open `http://localhost:5173` to view the app.

## Features
- **Job Search:** Search by query and location.
- **Filters:** Client-side filtering for Experience and CTC.
- **Caching:** API results are cached in PostgreSQL for 24 hours to save API calls.
