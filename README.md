# AI News Aggregation & Broadcasting Dashboard

A full-stack application that aggregates AI news from 20+ sources, provides deduplication, favorites management, and multi-platform broadcasting capabilities.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Architecture                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                    │
│   │   OpenAI    │     │  TechCrunch │     │   arXiv     │    ... 20+ Sources │
│   │   Blog      │     │     AI      │     │   Papers    │                    │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                    │
│          │                   │                   │                            │
│          └───────────────────┼───────────────────┘                            │
│                              ▼                                                │
│                    ┌─────────────────┐                                        │
│                    │  Ingestion      │                                        │
│                    │  Service        │                                        │
│                    │  (RSS/API/      │                                        │
│                    │   Scraper)      │                                        │
│                    └────────┬────────┘                                        │
│                             ▼                                                 │
│                    ┌─────────────────┐                                        │
│                    │  Deduplication  │                                        │
│                    │  (TF-IDF +      │                                        │
│                    │   Cosine Sim)   │                                        │
│                    └────────┬────────┘                                        │
│                             ▼                                                 │
│   ┌─────────────────────────────────────────────────────────────┐            │
│   │                     PostgreSQL                               │            │
│   │  ┌─────────┐  ┌───────────┐  ┌──────────┐  ┌─────────────┐  │            │
│   │  │ sources │  │news_items │  │favorites │  │broadcast_log│  │            │
│   │  └─────────┘  └───────────┘  └──────────┘  └─────────────┘  │            │
│   └─────────────────────────────────────────────────────────────┘            │
│                             ▲                                                 │
│                             │                                                 │
│                    ┌────────┴────────┐                                        │
│                    │    FastAPI      │                                        │
│                    │    Backend      │                                        │
│                    │   (REST API)    │                                        │
│                    └────────┬────────┘                                        │
│                             │                                                 │
│              ┌──────────────┼──────────────┐                                  │
│              ▼              ▼              ▼                                  │
│       ┌───────────┐  ┌───────────┐  ┌───────────┐                            │
│       │   Email   │  │ LinkedIn  │  │ WhatsApp  │  Broadcast Services        │
│       └───────────┘  └───────────┘  └───────────┘                            │
│                             ▲                                                 │
│                             │                                                 │
│                    ┌────────┴────────┐                                        │
│                    │    Next.js      │                                        │
│                    │    Frontend     │                                        │
│                    │   Dashboard     │                                        │
│                    └─────────────────┘                                        │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Features

- **News Aggregation**: Collects AI news from 20+ high-quality sources
- **Deduplication**: TF-IDF + cosine similarity based duplicate detection
- **Favorites System**: Save and manage favorite articles
- **Multi-Platform Broadcasting**: Share via Email, LinkedIn, WhatsApp, Blog, Newsletter
- **AI-Powered Content Generation**: OpenAI integration for summaries and captions
- **Scheduled Fetching**: Automatic news updates every 15 minutes
- **Responsive Dashboard**: Modern UI with filtering, sorting, and search

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| AI/LLM | OpenAI API (optional) |
| Deployment | Docker, Docker Compose |
| Ingestion | feedparser, httpx, BeautifulSoup |

## Project Structure

```
Culinda_project/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── news.py        # News endpoints
│   │   │   │   ├── favorites.py   # Favorites endpoints
│   │   │   │   ├── broadcast.py   # Broadcast endpoints
│   │   │   │   └── sources.py     # Sources endpoints
│   │   │   └── deps.py            # Dependencies
│   │   ├── core/
│   │   │   ├── config.py          # Settings
│   │   │   └── database.py        # DB connection
│   │   ├── models/
│   │   │   └── models.py          # SQLAlchemy models
│   │   ├── schemas/
│   │   │   └── schemas.py         # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ingestion/         # News fetchers
│   │   │   ├── deduplication.py   # Dedup service
│   │   │   ├── broadcast.py       # Broadcast service
│   │   │   └── summarizer.py      # AI summarization
│   │   └── main.py                # FastAPI app
│   ├── alembic/                   # Migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Home/News Feed
│   │   ├── favorites/page.tsx     # Favorites page
│   │   └── layout.tsx             # Layout
│   ├── components/
│   │   ├── layout/                # Navbar, Sidebar
│   │   ├── news/                  # NewsCard, FilterBar
│   │   ├── dashboard/             # StatsCards
│   │   └── ui/                    # Toast components
│   ├── lib/
│   │   ├── api.ts                 # API client
│   │   ├── types.ts               # TypeScript types
│   │   └── utils.ts               # Utilities
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start

### Using Docker (Recommended)

1. **Clone and navigate to project:**
   ```bash
   cd Culinda_project
   ```

2. **Set environment variables (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start all services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

### Manual Setup

#### Backend

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL:**
   - Create database: `ai_news_db`
   - Update `.env` with connection string

4. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

5. **Start backend:**
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Create env file:**
   ```bash
   cp .env.local.example .env.local
   ```

3. **Start frontend:**
   ```bash
   npm run dev
   ```

## API Endpoints

### News
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/news` | List news with filters |
| GET | `/api/news/{id}` | Get single news item |
| GET | `/api/news/stats` | Dashboard statistics |
| POST | `/api/news/refresh` | Trigger news refresh |

### Favorites
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/favorites` | List favorites |
| POST | `/api/favorites` | Add to favorites |
| DELETE | `/api/favorites/{id}` | Remove from favorites |

### Broadcast
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/broadcast` | Broadcast to platform |
| GET | `/api/broadcast/logs` | Get broadcast history |
| POST | `/api/broadcast/generate-content` | Generate AI content |

### Sources
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sources` | List all sources |
| POST | `/api/sources/initialize` | Initialize default sources |

## News Sources (20+)

### Blogs
- OpenAI Blog
- Google AI Blog
- Meta AI
- Anthropic
- DeepMind
- Hugging Face Blog
- Microsoft AI Blog
- Stability AI Blog

### Tech News
- TechCrunch AI
- VentureBeat AI
- The Verge AI
- Wired AI
- MIT Technology Review
- Ars Technica

### Research
- arXiv (cs.AI, cs.CL, cs.LG)
- Papers With Code

### Community
- Hacker News (AI filtered)
- Reddit r/MachineLearning

### YouTube
- Two Minute Papers
- Yannic Kilcher

### Startup/Product
- Y Combinator Blog
- Product Hunt AI

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `OPENAI_API_KEY` | OpenAI API key (for AI features) | Optional |
| `SMTP_HOST` | Email server host | smtp.gmail.com |
| `SMTP_USER` | Email username | - |
| `SMTP_PASSWORD` | Email password/app password | - |
| `CORS_ORIGINS` | Allowed CORS origins | localhost:3000 |
| `FETCH_INTERVAL_MINUTES` | News fetch interval | 15 |

## Design Decisions

1. **Async Architecture**: FastAPI with async SQLAlchemy for high-performance I/O operations
2. **TF-IDF Deduplication**: Efficient similarity-based deduplication without external ML models
3. **Scheduled Fetching**: APScheduler for reliable background task scheduling
4. **Modular Fetchers**: Factory pattern for extensible source support
5. **Type Safety**: Full Pydantic/TypeScript typing for robust data validation
6. **Docker-First**: Complete containerization for easy deployment

## Future Improvements

- [ ] User authentication with JWT
- [ ] Real-time notifications via WebSockets
- [ ] Advanced AI clustering with embeddings
- [ ] Custom RSS feed addition
- [ ] Mobile app with React Native
- [ ] Analytics dashboard with charts

## License

MIT License
