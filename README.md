# 🚀 Job Portal - AI-Powered Job Search Platform

A full-stack job search platform with intelligent matching, semantic search, and multi-source job aggregation.

## ✨ Features

### 🎯 Smart Job Matching
- **AI-powered relevance scoring** - Matches jobs based on skills, experience, and preferences
- **Semantic search** - Vector-based search using sentence transformers
- **Resume-aware recommendations** - Upload resume for personalized results
- **Session-based learning** - Improves recommendations based on your interactions

### 🌐 Multi-Source Aggregation
- **10+ job portals** - Naukri, LinkedIn, Indeed, Instahyre, and more
- **API integrations** - JSearch, Adzuna, Remotive for remote jobs
- **Real-time scraping** - Playwright-based web scrapers
- **Intelligent caching** - 24-hour cache to reduce redundant scraping

### 🔍 Advanced Filtering
- Experience range (e.g., 5-10 years)
- Salary range (CTC)
- Skills matching
- Location filtering
- Job portal selection
- Country support (India, UAE)

### 📊 Smart Features
- **Hybrid search** - Combines vector search with SQL filtering
- **Reranking** - Cross-encoder for improved result ordering
- **Seniority detection** - Identifies senior/junior roles
- **Recency scoring** - Prioritizes recent job postings

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[TESTING.md](TESTING.md)** | Complete test suite documentation (91 tests, 96% coverage) |
| **[DOCKER.md](DOCKER.md)** | Docker deployment guide and containerization |
| **[DOCS.md](DOCS.md)** | Documentation index and quick links |
| **[.github/copilot-instructions.md](.github/copilot-instructions.md)** | AI coding assistant guide |

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone and setup
git clone <repository-url>
cd Jobs

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run with Docker
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

See **[DOCKER.md](DOCKER.md)** for detailed deployment instructions.

### Option 2: Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

---

## 🧪 Testing

We have **91 comprehensive tests** with **96% code coverage**!

```bash
cd backend

# Run all tests
PYTHONPATH=/Users/ashwin/Desktop/Jobs/backend ./venv/bin/pytest tests/ -v

# Run with coverage
./venv/bin/pytest tests/ --cov=managers --cov=services --cov-report=html

# View coverage report
open htmlcov/index.html
```

See **[TESTING.md](TESTING.md)** for complete testing documentation.

---

## 🏗️ Architecture

### Tech Stack

**Backend**:
- FastAPI (Python 3.13)
- SQLAlchemy + SQLite
- ChromaDB (vector database)
- Playwright (web scraping)
- Sentence Transformers (embeddings)
- pytest (testing)

**Frontend**:
- React 19
- TypeScript
- Vite
- TailwindCSS
- Axios

**Infrastructure**:
- Docker & Docker Compose
- Nginx (reverse proxy)
- Multi-stage builds

### Project Structure

```
Jobs/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── services.py          # JobService
│   ├── models.py            # Database models
│   ├── managers/            # Business logic
│   │   ├── matching_engine.py
│   │   ├── filter_engine.py
│   │   ├── vector_manager.py
│   │   └── scraper_manager.py
│   ├── scrapers/            # Web scrapers
│   ├── tests/               # Test suite (91 tests)
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   └── lib/             # Utilities
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml       # Orchestration
└── README.md               # This file
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=jsearch.p.rapidapi.com

ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_APP_KEY=your_adzuna_app_key_here

# Database
DATABASE_URL=sqlite:///data/jobs.db
```

Get API keys from:
- **JSearch**: [RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
- **Adzuna**: [Adzuna Developer](https://developer.adzuna.com/)

---

## 📊 API Endpoints

### Job Search
```http
GET /api/jobs?query=Python&location=Bangalore&page=1
```

**Query Parameters**:
- `query` - Search term (required)
- `location` - Job location
- `page` - Page number (default: 1)
- `experience` - Experience range (e.g., "5-10 Years")
- `ctc` - Salary range (e.g., "10-20 LPA")
- `skills` - Required skills (comma-separated)
- `jobPortals` - Filter by portals (e.g., "Naukri,LinkedIn")
- `context_id` - Resume context ID for personalized results
- `country` - Country filter (India, UAE)

### Resume Upload
```http
POST /api/context/upload
Content-Type: multipart/form-data

file: <resume.pdf>
```

### Feedback
```http
POST /api/feedback
Content-Type: application/json

{
  "job_id": 123,
  "action_type": "CLICK",
  "context_id": "optional_session_id"
}
```

**Interactive API Docs**: http://localhost:8000/docs

---

## 🎯 Key Features Explained

### 1. Hybrid Search
Combines vector similarity search with SQL filtering for optimal results:
- Vector search finds semantically similar jobs
- SQL filters apply experience, salary, skills constraints
- Results are merged and reranked

### 2. Resume Enrichment
Upload your resume to get personalized recommendations:
- Extracts skills and experience using NLP
- Creates vector embedding of your profile
- Boosts relevant job matches

### 3. Session Learning
The system learns from your interactions:
- Tracks clicks and applications
- Boosts similar jobs in future searches
- Improves over time

### 4. Smart Caching
Intelligent caching reduces redundant scraping:
- 24-hour cache per query
- Background refresh for stale data
- Immediate results for cached queries

---

## 🧪 Test Coverage

| Module | Coverage | Tests |
|--------|----------|-------|
| FilterEngine | 100% | 7 tests |
| MatchingEngine | 97% | 15 tests |
| VectorManager | 97% | 17 tests |
| ScraperManager | 95% | 7 tests |
| JobService | 93% | 14 tests |
| **Overall** | **96%** | **91 tests** |

See **[TESTING.md](TESTING.md)** for detailed test documentation.

---

## 🐳 Docker Deployment

Full containerized deployment with Docker Compose:

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Features:
- ✅ Multi-stage builds (optimized images)
- ✅ Health checks
- ✅ Auto-restart on failure
- ✅ Data persistence (volumes)
- ✅ Nginx reverse proxy
- ✅ Production-ready

See **[DOCKER.md](DOCKER.md)** for complete deployment guide.

---

## 🛠️ Development

### Running Tests
```bash
cd backend
./venv/bin/pytest tests/ -v
```

### Code Quality
```bash
# Type checking
mypy backend/

# Linting
pylint backend/
```

### Database Management
```bash
# View database
sqlite3 backend/data/jobs.db

# Reset database
rm backend/data/jobs.db
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Scrapers**: Naukri, LinkedIn, Indeed, Instahyre, Foundit, Apna
- **APIs**: JSearch, Adzuna, Remotive
- **AI Models**: Sentence Transformers, Cross-Encoders
- **Frameworks**: FastAPI, React, Playwright

---

## 📞 Support

For issues or questions:
- Check **[DOCS.md](DOCS.md)** for documentation index
- Review **[TESTING.md](TESTING.md)** for test details
- See **[DOCKER.md](DOCKER.md)** for deployment help

---

**Built with ❤️ using FastAPI, React, and AI**
