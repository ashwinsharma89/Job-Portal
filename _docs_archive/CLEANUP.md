# Project File Cleanup Plan

## Files to KEEP (Essential)

### Backend Core (Production)
✅ **Keep** - These are essential for the application:
- `backend/main.py` - FastAPI application
- `backend/database.py` - Database configuration
- `backend/models.py` - SQLAlchemy models
- `backend/services.py` - JobService
- `backend/requirements.txt` - Dependencies
- `backend/pytest.ini` - Test configuration

### API Clients (Production)
✅ **Keep** - External API integrations:
- `backend/jsearch.py` - JSearch API client
- `backend/adzuna.py` - Adzuna API client
- `backend/remotive.py` - Remotive API client
- `backend/jobspy_client.py` - JobSpy integration

### Managers (Production)
✅ **Keep** - Core business logic:
- `backend/managers/matching_engine.py`
- `backend/managers/filter_engine.py`
- `backend/managers/vector_manager.py`
- `backend/managers/scraper_manager.py`

### Scrapers (Production)
✅ **Keep** - All scrapers in `backend/scrapers/`:
- `base_scraper.py`
- `naukri_scraper.py`
- `linkedin_scraper.py`
- `instahyre_scraper.py`
- `foundit_scraper.py`
- `indeed_scraper.py`
- `apna_scraper.py`
- `browser_pool.py`

### Tests (Production)
✅ **Keep** - All files in `backend/tests/`:
- `test_matching_engine_unit.py`
- `test_filter_engine_unit.py`
- `test_vector_manager_unit.py`
- `test_scraper_manager_unit.py`
- `test_services_unit.py`
- `test_services_comprehensive.py`
- `test_edge_cases.py`
- `test_api_integration.py`
- `test_database_integration.py`
- `test_e2e.py`
- `__init__.py`

### Documentation
✅ **Keep**:
- `README.md` - Project documentation
- `TESTING.md` - Test suite documentation
- `.github/copilot-instructions.md` - AI coding guide

---

## Files to DELETE (Old Debug/Test Scripts)

### ❌ Old Debug Scripts (Backend Root)
These were used during development but are no longer needed:
- `backend/debug_db.py` - Database debugging
- `backend/debug_failing_scrapers.py` - Scraper debugging
- `backend/debug_instahyre.py` - Instahyre debugging
- `backend/deep_inspect.py` - Deep inspection tool
- `backend/audit_extraction.py` - Audit tool
- `backend/inspect_priority_sites.py` - Site inspection
- `backend/inspect_sites.py` - Site inspection
- `backend/verify_sqlite.py` - SQLite verification

### ❌ Old Test Scripts (Backend Root)
These were replaced by proper tests in `tests/`:
- `backend/test_db.py` - Replaced by `tests/test_database_integration.py`
- `backend/test_filters.py` - Replaced by `tests/test_filter_engine_unit.py`
- `backend/test_matching_refinements.py` - Replaced by `tests/test_matching_engine_unit.py`
- `backend/test_priority_scrapers.py` - Replaced by `tests/test_scraper_manager_unit.py`
- `backend/test_resume_enrichment.py` - Replaced by `tests/test_services_comprehensive.py`
- `backend/test_scraper_manager.py` - Replaced by `tests/test_scraper_manager_unit.py`
- `backend/test_scrapers_live.py` - Replaced by proper unit tests

### ❌ Old UI (Backend Root)
- `backend/streamlit_app.py` - Old Streamlit UI (replaced by React frontend)

### ❌ Utility Scripts
- `backend/index_existing_jobs.py` - One-time indexing script (can be recreated if needed)

### ⚠️ Optional to Keep
- `TEST_ANALYSIS.md` - Analysis document (can delete after review)

---

## Cleanup Commands

### Safe Cleanup (Recommended)
Move old files to archive folder:
```bash
cd backend
mkdir -p _archive
mv debug_*.py _archive/
mv test_*.py _archive/
mv *_inspect*.py _archive/
mv audit_extraction.py _archive/
mv verify_sqlite.py _archive/
mv streamlit_app.py _archive/
mv index_existing_jobs.py _archive/
```

### Aggressive Cleanup (Delete permanently)
```bash
cd backend
rm -f debug_*.py
rm -f test_*.py  # Be careful - this won't delete tests/ folder
rm -f *_inspect*.py
rm -f audit_extraction.py
rm -f verify_sqlite.py
rm -f streamlit_app.py
rm -f index_existing_jobs.py
```

---

## Summary

### Current File Count
- **Essential files**: ~40 files
- **Old debug/test files**: ~15 files
- **Cleanup potential**: Remove ~27% of files

### After Cleanup
Your project will have:
- ✅ Clean, organized structure
- ✅ Only production-ready code
- ✅ Proper test suite in `tests/`
- ✅ Clear separation of concerns
- ✅ Easier to navigate and maintain

### Recommendation
**Use the safe cleanup** (move to `_archive/`) so you can recover files if needed later.
