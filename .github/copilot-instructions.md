# Agentic Job Platform - Copilot Instructions

## Architecture Overview
- **Stack**: React (Vite/Tailwind) Frontend + FastAPI (Python/SQLAlchemy) Backend.
- **Database**: SQLite (`jobplatform.db`) using `aiosqlite` for async access.
- **Search System (Advanced)**:
  - **Hybrid Search**: `JobService` orchestrates Vector Search (ChromaDB) + SQL (SQLite).
  - **Relevance Engine**: `MatchingEngine` (`backend/managers/matching_engine.py`) blends scores using:
    - **Vector Score** (Semantic match)
    - **Keyword Match** (Title/Skills)
    - **Penalties** (Seniority mismatch)
    - **Session Boost** (Rocchio Algorithm for adaptive search)
  - **Resume Context**: `VectorManager` supports `context_id` to enrich user profile from uploaded resumes.

- **Scraping Engine**:
  - `ScraperManager` (`backend/managers/scraper_manager.py`) orchestrates multiple scrapers.
  - Scrapers (`backend/scrapers/`) inherit from `BaseScraper`.
  - Uses Playwright (via `browser_pool.py`) for dynamic sites (Indeed, Naukri, Bayt) and `httpx` for APIs (JSearch, Adzuna).

## Core Patterns & Conventions

### Backend (FastAPI)
- **Service Layer**: Business logic resides in `backend/services.py` (`JobService`) and `backend/managers/`.
- **Managers**: Logic is split into `MatchingEngine`, `VectorManager`, `FilterEngine`, `ScraperManager`.
- **Scraper Implementation**:
  - New scrapers MUST inherit `BaseScraper`.
  - MUST call `self.normalize_job_data(raw_job, source, country)` to ensure consistent schema and filtering.
  - Handle `country` explicitly to prevent data leakage (e.g., India jobs appearing in UAE).
- **Database Access**: Use `AsyncSession` dependency `get_db` from `backend/database.py`.
- **Environment**: Load vars using `dotenv` from the root `.env` file.

### Frontend (React)
- **State Management**: Primary search state (query, location, filters, contextId) is centralized in `App.tsx`.
- **Components**: Functional components using Tailwind for styling.
- **API Client**: All backend calls are typed and centralized in `src/api.ts`.
- **Feedback Loop**: `JobCard` triggers `sendFeedback` on Click/Apply to train the Session Booster.

## Developer Workflows
- **Start All Services**: Run `./start.sh` from the root.
- **Debug Scrapers**: Use `python backend/debug_failing_scrapers.py` to test individual scrapers without running the full server.
- **Database Inspection**: `jobplatform.db` is the local SQLite file. Use `backend/debug_db.py` to inspect contents.

## Key Files
- `backend/main.py`: App entry point and lifecycle management.
- `backend/managers/matching_engine.py`: Scoring logic (Weights, Penalties, Breakdown).
- `backend/managers/vector_manager.py`: ChromaDB interaction, Embedding generation, Rocchio Boost.
- `backend/services.py`: `JobService.get_jobs` handles the core search/filter/cache/enrichment logic.
- `backend/scrapers/base_scraper.py`: Base class with shared utilities (browser pool, normalization).
