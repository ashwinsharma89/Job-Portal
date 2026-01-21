# Project Reorganization Plan

## Current Structure Issues

### Backend Root (Too Many Files)
```
backend/
├── main.py              # API entry point
├── database.py          # Database config
├── models.py            # SQLAlchemy models
├── services.py          # JobService
├── adzuna.py           # API client
├── jsearch.py          # API client
├── remotive.py         # API client
├── jobspy_client.py    # API client
├── requirements.txt    # Dependencies
└── pytest.ini          # Test config
```

**Issues**:
- ❌ API clients scattered in root
- ❌ Config files mixed with code
- ❌ No clear separation of concerns

---

## Proposed Reorganization

### Option 1: Standard Python Package Structure (Recommended)

```
backend/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI app
│   ├── database.py        # Database config
│   ├── models.py          # SQLAlchemy models
│   └── services.py        # JobService
│
├── clients/               # External API clients
│   ├── __init__.py
│   ├── adzuna.py
│   ├── jsearch.py
│   ├── remotive.py
│   └── jobspy_client.py
│
├── managers/              # Business logic (already organized)
│   ├── __init__.py
│   ├── matching_engine.py
│   ├── filter_engine.py
│   ├── vector_manager.py
│   └── scraper_manager.py
│
├── scrapers/              # Web scrapers (already organized)
│   ├── __init__.py
│   ├── base_scraper.py
│   └── ...
│
├── utils/                 # Utilities (already exists)
│   ├── __init__.py
│   ├── profiler.py
│   └── resume_parser.py
│
├── tests/                 # Test suite (already organized)
│   └── ...
│
├── config/                # Configuration files
│   ├── __init__.py
│   └── settings.py        # Environment variables, settings
│
├── data/                  # Data files (databases, etc.)
│   └── jobs.db
│
├── requirements.txt       # Dependencies
├── pytest.ini            # Test config
└── README.md             # Backend docs
```

### Option 2: Minimal Reorganization (Quick Win)

```
backend/
├── main.py               # Keep in root (entry point)
├── database.py           # Keep in root (core)
├── models.py             # Keep in root (core)
├── services.py           # Keep in root (core)
│
├── api_clients/          # NEW: Group API clients
│   ├── __init__.py
│   ├── adzuna.py
│   ├── jsearch.py
│   ├── remotive.py
│   └── jobspy_client.py
│
├── managers/             # Already organized ✅
├── scrapers/             # Already organized ✅
├── utils/                # Already organized ✅
├── tests/                # Already organized ✅
│
├── data/                 # NEW: Data files
│   └── jobs.db
│
├── requirements.txt
└── pytest.ini
```

---

## Recommended Actions

### 1. Create `api_clients/` folder
Move API client files:
```bash
mkdir -p api_clients
touch api_clients/__init__.py
mv adzuna.py jsearch.py remotive.py jobspy_client.py api_clients/
```

### 2. Create `data/` folder
Move database files:
```bash
mkdir -p data
mv *.db *.sqlite data/ 2>/dev/null || true
```

### 3. Update imports in affected files
- `main.py` - Update API client imports
- `services.py` - Update API client imports
- `managers/scraper_manager.py` - Update API client imports

### 4. Create `__init__.py` files
```bash
# api_clients/__init__.py
from .adzuna import AdzunaClient
from .jsearch import JSearchClient
from .remotive import RemotiveClient
from .jobspy_client import JobSpyClient

__all__ = ['AdzunaClient', 'JSearchClient', 'RemotiveClient', 'JobSpyClient']
```

---

## Root Directory Organization

### Project Root
```
Jobs/
├── backend/              # Backend application
├── frontend/             # React frontend
├── .github/              # GitHub configs
├── README.md            # Project overview
├── TESTING.md           # Test documentation
└── .gitignore           # Git ignore rules
```

**Clean up root**:
- ✅ Keep: `README.md`, `TESTING.md`
- ❌ Archive: `CLEANUP.md`, `CLEANUP_COMPLETE.md`, `TEST_ANALYSIS.md`

---

## Benefits

### Before
- 📁 8 files in backend root
- ❌ API clients scattered
- ❌ Database files in root

### After (Option 2)
- 📁 4 core files in backend root
- ✅ API clients organized in `api_clients/`
- ✅ Data files in `data/`
- ✅ Clear folder structure
- ✅ Easy to navigate

---

## Migration Checklist

- [ ] Create `api_clients/` folder
- [ ] Move API client files
- [ ] Create `api_clients/__init__.py`
- [ ] Create `data/` folder
- [ ] Move database files
- [ ] Update imports in `main.py`
- [ ] Update imports in `services.py`
- [ ] Update imports in `managers/scraper_manager.py`
- [ ] Test that everything still works
- [ ] Archive cleanup docs from root

**Recommendation**: Start with **Option 2** (Minimal Reorganization) as it's a quick win with minimal risk.
