"""
News ingestion orchestrator
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.models.models import Source, NewsItem, FetchLog, SourceType
from app.services.ingestion.fetchers import get_fetcher_for_source, SOURCE_CONFIGS
from app.services.deduplication import DeduplicationService

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates news fetching from all sources"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dedup_service = DeduplicationService()
    
    async def initialize_sources(self) -> int:
        """Initialize sources in database from config"""
        count = 0
        for config in SOURCE_CONFIGS:
            # Check if source already exists
            result = await self.db.execute(
                select(Source).where(Source.name == config["name"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                source = Source(
                    name=config["name"],
                    url=config["url"],
                    feed_url=config.get("feed_url"),
                    type=SourceType(config.get("type", "rss")),
                    category=config.get("category"),
                    icon_url=config.get("icon_url"),
                    description=config.get("description"),
                    active=True
                )
                self.db.add(source)
                count += 1
        
        await self.db.commit()
        logger.info(f"Initialized {count} new sources")
        return count
    
    async def fetch_all_sources(self) -> Dict[str, Any]:
        """Fetch news from all active sources"""
        result = await self.db.execute(
            select(Source).where(Source.active == True)
        )
        sources = result.scalars().all()
        
        total_new = 0
        total_duplicate = 0
        errors = []
        
        # Fetch from each source
        for source in sources:
            try:
                new_count, dup_count = await self.fetch_source(source)
                total_new += new_count
                total_duplicate += dup_count
            except Exception as e:
                error_msg = f"Error fetching {source.name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return {
            "sources_fetched": len(sources),
            "new_items": total_new,
            "duplicates_found": total_duplicate,
            "errors": errors
        }
    
    async def fetch_source(self, source: Source) -> tuple[int, int]:
        """Fetch news from a single source"""
        fetch_log = FetchLog(source_id=source.id)
        self.db.add(fetch_log)
        
        try:
            # Get appropriate fetcher
            config = {
                "name": source.name,
                "url": source.url,
                "feed_url": source.feed_url,
                "type": source.type.value if source.type else "rss"
            }
            fetcher = get_fetcher_for_source(config)
            
            # Fetch items
            items = await fetcher.fetch()
            await fetcher.close()
            
            new_count = 0
            dup_count = 0
            
            for item in items:
                # Check if URL already exists
                existing = await self.db.execute(
                    select(NewsItem).where(NewsItem.url == item["url"])
                )
                if existing.scalar_one_or_none():
                    dup_count += 1
                    continue
                
                # Check content hash for duplicates
                if item.get("content_hash"):
                    hash_check = await self.db.execute(
                        select(NewsItem).where(
                            NewsItem.content_hash == item["content_hash"]
                        )
                    )
                    if hash_check.scalar_one_or_none():
                        dup_count += 1
                        continue
                
                # Create new news item
                news_item = NewsItem(
                    source_id=source.id,
                    title=item["title"],
                    summary=item.get("summary"),
                    url=item["url"],
                    author=item.get("author"),
                    published_at=item.get("published_at"),
                    image_url=item.get("image_url"),
                    tags=item.get("tags", []),
                    content_hash=item.get("content_hash"),
                    fetched_at=datetime.utcnow()
                )
                self.db.add(news_item)
                new_count += 1
            
            # Update source last_fetched
            source.last_fetched = datetime.utcnow()
            
            # Update fetch log
            fetch_log.completed_at = datetime.utcnow()
            fetch_log.success = True
            fetch_log.items_fetched = len(items)
            fetch_log.items_new = new_count
            fetch_log.items_duplicate = dup_count
            
            await self.db.commit()
            logger.info(f"Fetched {source.name}: {new_count} new, {dup_count} duplicates")
            
            return new_count, dup_count
            
        except Exception as e:
            fetch_log.completed_at = datetime.utcnow()
            fetch_log.success = False
            fetch_log.error_message = str(e)
            await self.db.commit()
            raise
    
    async def fetch_sources_by_ids(self, source_ids: List[int]) -> Dict[str, Any]:
        """Fetch news from specific sources"""
        result = await self.db.execute(
            select(Source).where(
                and_(Source.id.in_(source_ids), Source.active == True)
            )
        )
        sources = result.scalars().all()
        
        total_new = 0
        total_duplicate = 0
        errors = []
        
        for source in sources:
            try:
                new_count, dup_count = await self.fetch_source(source)
                total_new += new_count
                total_duplicate += dup_count
            except Exception as e:
                errors.append(f"Error fetching {source.name}: {str(e)}")
        
        return {
            "sources_fetched": len(sources),
            "new_items": total_new,
            "duplicates_found": total_duplicate,
            "errors": errors
        }
    
    async def run_deduplication(self) -> int:
        """Run deduplication on recent items"""
        # Get recent non-duplicate items
        result = await self.db.execute(
            select(NewsItem)
            .where(NewsItem.is_duplicate == False)
            .order_by(NewsItem.published_at.desc())
            .limit(500)
        )
        items = result.scalars().all()
        
        if len(items) < 2:
            return 0
        
        # Build list of titles for comparison
        titles = [item.title for item in items]
        
        # Find duplicates using similarity
        duplicates_found = 0
        duplicate_pairs = self.dedup_service.find_duplicates(titles)
        
        for idx1, idx2, score in duplicate_pairs:
            # Mark the newer item as duplicate
            item1, item2 = items[idx1], items[idx2]
            
            # Determine which is newer (mark newer as duplicate)
            if item1.published_at and item2.published_at:
                if item1.published_at > item2.published_at:
                    item1.is_duplicate = True
                    item1.duplicate_of_id = item2.id
                    item1.similarity_score = score
                else:
                    item2.is_duplicate = True
                    item2.duplicate_of_id = item1.id
                    item2.similarity_score = score
            else:
                # If no dates, mark item1 as duplicate
                item1.is_duplicate = True
                item1.duplicate_of_id = item2.id
                item1.similarity_score = score
            
            duplicates_found += 1
        
        await self.db.commit()
        logger.info(f"Deduplication found {duplicates_found} duplicate pairs")
        
        return duplicates_found
