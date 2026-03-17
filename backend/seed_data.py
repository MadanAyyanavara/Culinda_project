"""
Seed script to populate the database with demo data
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.models.models import Source, NewsItem, User, Favorite, BroadcastLog
from app.services.deduplication import ContentHasher

# Demo news articles
DEMO_ARTICLES = [
    {
        "title": "OpenAI Announces GPT-5: Revolutionary Multimodal AI System",
        "summary": "OpenAI has unveiled GPT-5, featuring unprecedented capabilities in reasoning, code generation, and multimodal understanding. The new model demonstrates 40% improvement in complex problem-solving tasks.",
        "content": "Full article content here...",
        "author": "Sarah Chen",
        "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800",
        "category": "Research",
    },
    {
        "title": "Google DeepMind's AlphaFold 3 Predicts Protein Structures with 99% Accuracy",
        "summary": "The latest iteration of AlphaFold achieves near-perfect accuracy in protein structure prediction, opening new frontiers in drug discovery and understanding diseases.",
        "content": "Full article content here...",
        "author": "Dr. James Wilson",
        "image_url": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=800",
        "category": "Research",
    },
    {
        "title": "Microsoft Copilot Surpasses 10 Million Daily Active Users",
        "summary": "Microsoft's AI assistant reaches major milestone, becoming the fastest-growing productivity tool in the company's history. Enterprise adoption up 300%.",
        "content": "Full article content here...",
        "author": "Michael Roberts",
        "image_url": "https://images.unsplash.com/photo-1633419461186-7d40a38105ec?w=800",
        "category": "Industry",
    },
    {
        "title": "Anthropic's Claude 3 Opus Outperforms GPT-4 on Benchmarks",
        "summary": "Claude 3 Opus demonstrates superior performance in reasoning, mathematics, and coding tasks. The model shows particular strength in analysis and creative writing.",
        "content": "Full article content here...",
        "author": "Emily Zhang",
        "image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800",
        "category": "Research",
    },
    {
        "title": "Tesla's Full Self-Driving V12 Uses End-to-End Neural Networks",
        "summary": "Tesla releases FSD V12 with revolutionary end-to-end neural network approach, eliminating over 300,000 lines of explicit C++ code.",
        "content": "Full article content here...",
        "author": "David Martinez",
        "image_url": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800",
        "category": "Automotive",
    },
    {
        "title": "Meta Releases Llama 3: Open Source Model Rivals GPT-4",
        "summary": "Meta's latest open-source LLM achieves competitive performance with proprietary models while maintaining open weights for research and commercial use.",
        "content": "Full article content here...",
        "author": "Lisa Anderson",
        "image_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800",
        "category": "Open Source",
    },
    {
        "title": "NVIDIA H200 GPUs Enable 2x Faster AI Training",
        "summary": "New H200 Tensor Core GPUs with HBM3e memory deliver unprecedented performance for large language model training and inference.",
        "content": "Full article content here...",
        "author": "Robert Kim",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=800",
        "category": "Hardware",
    },
    {
        "title": "Stability AI Releases Stable Diffusion 3 with Improved Typography",
        "summary": "Latest version of Stable Diffusion shows remarkable improvement in text rendering within images, addressing a major limitation of previous versions.",
        "content": "Full article content here...",
        "author": "Anna Kowalski",
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800",
        "category": "Creative AI",
    },
    {
        "title": "Amazon's Alexa Gets Major AI Upgrade with Large Language Models",
        "summary": "Amazon announces comprehensive AI overhaul for Alexa, enabling more natural conversations and complex task completion.",
        "content": "Full article content here...",
        "author": "Tom Johnson",
        "image_url": "https://images.unsplash.com/photo-1543512214-318c77a07298?w=800",
        "category": "Consumer",
    },
    {
        "title": "AI-Generated Code Now 40% of All Code on GitHub",
        "summary": "GitHub report reveals AI pair programming tools like Copilot are fundamentally changing how developers write and maintain code.",
        "content": "Full article content here...",
        "author": "Rachel Green",
        "image_url": "https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=800",
        "category": "Development",
    },
    {
        "title": "Boston Dynamics' Atlas Robot Demonstrates Parkour Skills",
        "summary": "Latest demonstration shows Atlas performing complex parkour maneuvers autonomously, showcasing advances in robotics and balance control.",
        "content": "Full article content here...",
        "author": "Chris Taylor",
        "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800",
        "category": "Robotics",
    },
    {
        "title": "AI Drug Discovery Platform Identifies New Antibiotic",
        "summary": "Machine learning system discovers novel antibiotic compound effective against drug-resistant bacteria, marking breakthrough in pharmaceutical AI.",
        "content": "Full article content here...",
        "author": "Dr. Maria Santos",
        "image_url": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=800",
        "category": "Healthcare",
    },
]

async def seed_sources(db):
    """Create demo sources"""
    sources_data = [
        {"name": "OpenAI Blog", "url": "https://openai.com/blog", "category": "Research"},
        {"name": "Google AI", "url": "https://ai.googleblog.com", "category": "Research"},
        {"name": "DeepMind", "url": "https://deepmind.com", "category": "Research"},
        {"name": "Anthropic", "url": "https://anthropic.com", "category": "Research"},
        {"name": "Microsoft AI", "url": "https://blogs.microsoft.com/ai", "category": "Industry"},
        {"name": "Meta AI", "url": "https://ai.meta.com", "category": "Open Source"},
        {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com", "category": "Hardware"},
        {"name": "Stability AI", "url": "https://stability.ai", "category": "Creative AI"},
        {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence", "category": "News"},
        {"name": "MIT Technology Review", "url": "https://technologyreview.com", "category": "Research"},
    ]
    
    sources = []
    for data in sources_data:
        source = Source(
            name=data["name"],
            url=data["url"],
            feed_url=f"{data['url']}/rss",
            type="rss",
            active=True,
            category=data["category"],
            last_fetched=datetime.utcnow(),
        )
        db.add(source)
        sources.append(source)
    
    await db.commit()
    return sources

async def seed_news(db, sources):
    """Create demo news articles"""
    for i, article_data in enumerate(DEMO_ARTICLES):
        source = sources[i % len(sources)]
        content_hash = ContentHasher.compute_hash(article_data["title"])
        
        # Vary the published dates
        hours_ago = i * 2 + (i % 5)
        published_at = datetime.utcnow() - timedelta(hours=hours_ago)
        
        news_item = NewsItem(
            source_id=source.id,
            title=article_data["title"],
            summary=article_data["summary"],
            content=article_data["content"],
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
    
    await db.commit()

async def seed_user(db):
    """Create demo user"""
    user = User(
        email="demo@ainews.com",
        name="Demo User",
        role="admin",
        is_active=True,
        email_notifications=True,
    )
    db.add(user)
    await db.commit()
    return user

async def seed_favorites(db, user_id, news_items):
    """Create some favorite articles"""
    for i in [0, 2, 5, 8]:  # Favorite a few articles
        favorite = Favorite(
            user_id=user_id,
            news_item_id=news_items[i].id,
            notes=f"Interesting article about {news_items[i].title[:30]}...",
        )
        db.add(favorite)
    
    await db.commit()

async def seed_broadcasts(db, user_id, news_items):
    """Create some broadcast history"""
    platforms = ["email", "linkedin", "whatsapp", "blog"]
    
    for i, platform in enumerate(platforms):
        broadcast = BroadcastLog(
            user_id=user_id,
            news_item_id=news_items[i].id,
            platform=platform,
            status="sent" if i % 2 == 0 else "pending",
            content=f"Check out this article: {news_items[i].title}",
            recipient="demo@example.com" if platform == "email" else None,
            sent_at=datetime.utcnow() - timedelta(hours=i*3) if i % 2 == 0 else None,
        )
        db.add(broadcast)
    
    await db.commit()

async def main():
    """Main seeding function"""
    print("Initializing database...")
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # Check if data already exists
        result = await db.execute(select(NewsItem))
        if result.scalars().first():
            print("Database already seeded!")
            return
        
        print("Seeding sources...")
        sources = await seed_sources(db)
        
        print("Seeding news articles...")
        await seed_news(db, sources)
        
        print("Seeding user...")
        user = await seed_user(db)
        
        # Get news items for favorites and broadcasts
        result = await db.execute(select(NewsItem))
        news_items = result.scalars().all()
        
        print("Seeding favorites...")
        await seed_favorites(db, user.id, news_items)
        
        print("Seeding broadcasts...")
        await seed_broadcasts(db, user.id, news_items)
        
        print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(main())
