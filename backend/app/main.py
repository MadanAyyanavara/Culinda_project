"""
AI News Aggregation Dashboard - FastAPI Backend
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.api.routes import news, favorites, broadcast, sources
from app.schemas.schemas import HealthCheck

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Scheduler for periodic tasks
scheduler = AsyncIOScheduler()


async def scheduled_news_fetch():
    """Background task to fetch news periodically"""
    from app.services.ingestion import IngestionService
    
    logger.info("Starting scheduled news fetch...")
    async with AsyncSessionLocal() as db:
        try:
            ingestion = IngestionService(db)
            result = await ingestion.fetch_all_sources()
            await ingestion.run_deduplication()
            logger.info(f"Scheduled fetch complete: {result['new_items']} new items")
        except Exception as e:
            logger.error(f"Scheduled fetch error: {e}")


async def seed_demo_data():
    """Seed demo data for the application"""
    from sqlalchemy import select
    from datetime import datetime, timedelta
    from app.models.models import Source, NewsItem, User, Favorite, BroadcastLog
    from app.services.deduplication import ContentHasher
    
    async with AsyncSessionLocal() as db:
        # Check if news data already exists
        result = await db.execute(select(NewsItem))
        if result.scalars().first():
            logger.info("Demo data already exists, skipping seed")
            return
        
        logger.info("Seeding demo data...")
        
        # Get existing sources
        result = await db.execute(select(Source))
        sources = result.scalars().all()
        
        if not sources:
            logger.warning("No sources found, cannot seed news data")
            return
        
        # Demo articles
        demo_articles = [
            {
                "title": "OpenAI Announces GPT-5: Revolutionary Multimodal AI System",
                "summary": "OpenAI has unveiled GPT-5, featuring unprecedented capabilities in reasoning, code generation, and multimodal understanding. The new model demonstrates 40% improvement in complex problem-solving tasks.",
                "author": "Sarah Chen",
                "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800",
                "category": "Research",
            },
            {
                "title": "Google DeepMind's AlphaFold 3 Predicts Protein Structures with 99% Accuracy",
                "summary": "The latest iteration of AlphaFold achieves near-perfect accuracy in protein structure prediction, opening new frontiers in drug discovery and understanding diseases.",
                "author": "Dr. James Wilson",
                "image_url": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=800",
                "category": "Research",
            },
            {
                "title": "Microsoft Copilot Surpasses 10 Million Daily Active Users",
                "summary": "Microsoft's AI assistant reaches major milestone, becoming the fastest-growing productivity tool in the company's history. Enterprise adoption up 300%.",
                "author": "Michael Roberts",
                "image_url": "https://images.unsplash.com/photo-1633419461186-7d40a38105ec?w=800",
                "category": "Industry",
            },
            {
                "title": "Anthropic's Claude 3 Opus Outperforms GPT-4 on Benchmarks",
                "summary": "Claude 3 Opus demonstrates superior performance in reasoning, mathematics, and coding tasks. The model shows particular strength in analysis and creative writing.",
                "author": "Emily Zhang",
                "image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800",
                "category": "Research",
            },
            {
                "title": "Tesla's Full Self-Driving V12 Uses End-to-End Neural Networks",
                "summary": "Tesla releases FSD V12 with revolutionary end-to-end neural network approach, eliminating over 300,000 lines of explicit C++ code.",
                "author": "David Martinez",
                "image_url": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800",
                "category": "Automotive",
            },
            {
                "title": "Meta Releases Llama 3: Open Source Model Rivals GPT-4",
                "summary": "Meta's latest open-source LLM achieves competitive performance with proprietary models while maintaining open weights for research and commercial use.",
                "author": "Lisa Anderson",
                "image_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800",
                "category": "Open Source",
            },
            {
                "title": "NVIDIA H200 GPUs Enable 2x Faster AI Training",
                "summary": "New H200 Tensor Core GPUs with HBM3e memory deliver unprecedented performance for large language model training and inference.",
                "author": "Robert Kim",
                "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=800",
                "category": "Hardware",
            },
            {
                "title": "AI-Generated Code Now 40% of All Code on GitHub",
                "summary": "GitHub report reveals AI pair programming tools like Copilot are fundamentally changing how developers write and maintain code.",
                "author": "Rachel Green",
                "image_url": "https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=800",
                "category": "Development",
            },
            {
                "title": "Boston Dynamics' Atlas Robot Demonstrates Parkour Skills",
                "summary": "Latest demonstration shows Atlas performing complex parkour maneuvers autonomously, showcasing advances in robotics and balance control.",
                "author": "Chris Taylor",
                "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800",
                "category": "Robotics",
            },
            {
                "title": "AI Drug Discovery Platform Identifies New Antibiotic",
                "summary": "Machine learning system discovers novel antibiotic compound effective against drug-resistant bacteria, marking breakthrough in pharmaceutical AI.",
                "author": "Dr. Maria Santos",
                "image_url": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=800",
                "category": "Healthcare",
            },
        ]
        
        news_items = []
        for i, article_data in enumerate(demo_articles):
            source = sources[i % len(sources)]
            content_hash = ContentHasher.compute_hash(article_data["title"])
            hours_ago = i * 2 + (i % 5)
            published_at = datetime.utcnow() - timedelta(hours=hours_ago)
            
            news_item = NewsItem(
                source_id=source.id,
                title=article_data["title"],
                summary=article_data["summary"],
                content=article_data["summary"],
                url=f"https://example.com/article/{i+1}",
                author=article_data["author"],
                published_at=published_at,
                fetched_at=datetime.utcnow(),
                image_url=article_data.get("image_url"),
                tags=",".join([article_data["category"], "AI", "Technology"]),
                is_duplicate=False,
                content_hash=content_hash,
                ai_summary=f"Key takeaway: {article_data['summary'][:100]}..." if i % 3 == 0 else None,
                impact_score=85 + (i % 15),
            )
            db.add(news_item)
            news_items.append(news_item)
        
        await db.flush()
        
        # Create demo user
        result = await db.execute(select(User))
        if not result.scalars().first():
            user = User(
                email="demo@ainews.com",
                name="Demo User",
                role="admin",
                is_active=True,
                email_notifications=True,
            )
            db.add(user)
            await db.flush()
            
            # Create favorites
            for i in [0, 2, 5]:
                if i < len(news_items):
                    favorite = Favorite(
                        user_id=user.id,
                        news_item_id=news_items[i].id,
                        notes=f"Interesting article about {news_items[i].title[:30]}...",
                    )
                    db.add(favorite)
            
            # Create broadcasts
            platforms = ["email", "linkedin", "whatsapp"]
            for i, platform in enumerate(platforms):
                if i < len(news_items):
                    broadcast = BroadcastLog(
                        user_id=user.id,
                        news_item_id=news_items[i].id,
                        platform=platform,
                        status="sent",
                        content=f"Check out: {news_items[i].title}",
                        recipient="demo@example.com" if platform == "email" else None,
                        sent_at=datetime.utcnow() - timedelta(hours=i*3),
                    )
                    db.add(broadcast)
        
        await db.commit()
        logger.info("Demo data seeded successfully!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI News Dashboard API...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize sources on startup
    async with AsyncSessionLocal() as db:
        from app.services.ingestion import IngestionService
        ingestion = IngestionService(db)
        await ingestion.initialize_sources()
        logger.info("Sources initialized")
    
    # Seed demo data after sources are created
    await seed_demo_data()
    
    # Start scheduler
    scheduler.add_job(
        scheduled_news_fetch,
        IntervalTrigger(minutes=settings.FETCH_INTERVAL_MINUTES),
        id="news_fetch",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Scheduler started (interval: {settings.FETCH_INTERVAL_MINUTES} minutes)")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("Scheduler stopped")


# Create FastAPI application
app = FastAPI(
    title="AI News Aggregation Dashboard",
    description="API for aggregating and broadcasting AI news from 20+ sources",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(news.router, prefix="/api")
app.include_router(favorites.router, prefix="/api")
app.include_router(broadcast.router, prefix="/api")
app.include_router(sources.router, prefix="/api")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI News Aggregation Dashboard API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }


@app.get("/api/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """Health check endpoint"""
    from sqlalchemy import text
    
    db_status = "healthy"
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text("SELECT 1"))
        except Exception:
            db_status = "unhealthy"
    
    return HealthCheck(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
        version="1.0.0"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
