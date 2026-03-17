"""
Sources API routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db
from app.models.models import Source, NewsItem
from app.schemas.schemas import (
    SourceResponse, SourceCreate, SourceUpdate, SourceStats
)
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=List[SourceResponse])
async def list_sources(
    active_only: bool = Query(False),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all news sources"""
    
    query = select(Source)
    
    if active_only:
        query = query.where(Source.active == True)
    
    if category:
        query = query.where(Source.category == category)
    
    query = query.order_by(Source.name)
    
    result = await db.execute(query)
    sources = result.scalars().all()
    
    return [SourceResponse.model_validate(s) for s in sources]


@router.get("/stats", response_model=List[SourceStats])
async def get_source_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for each source"""
    
    from datetime import datetime, timedelta
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get all sources
    sources_result = await db.execute(select(Source).where(Source.active == True))
    sources = sources_result.scalars().all()
    
    stats = []
    for source in sources:
        # Total items for this source
        total_result = await db.execute(
            select(func.count()).where(NewsItem.source_id == source.id)
        )
        total = total_result.scalar()
        
        # Items today
        today_result = await db.execute(
            select(func.count()).where(
                NewsItem.source_id == source.id,
                NewsItem.fetched_at >= today_start
            )
        )
        today_count = today_result.scalar()
        
        stats.append(SourceStats(
            source_id=source.id,
            source_name=source.name,
            total_items=total or 0,
            items_today=today_count or 0,
            last_fetched=source.last_fetched
        ))
    
    return stats


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single source by ID"""
    
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return SourceResponse.model_validate(source)


@router.post("", response_model=SourceResponse)
async def create_source(
    request: SourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new news source"""
    
    # Check if source with same name exists
    existing = await db.execute(
        select(Source).where(Source.name == request.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Source with this name already exists")
    
    source = Source(**request.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    
    return SourceResponse.model_validate(source)


@router.patch("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    request: SourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a news source"""
    
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)
    
    await db.commit()
    await db.refresh(source)
    
    return SourceResponse.model_validate(source)


@router.delete("/{source_id}")
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a news source (soft delete by setting inactive)"""
    
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    source.active = False
    await db.commit()
    
    return {"message": "Source deactivated"}


@router.post("/initialize")
async def initialize_sources(db: AsyncSession = Depends(get_db)):
    """Initialize default sources from configuration"""
    
    ingestion = IngestionService(db)
    count = await ingestion.initialize_sources()
    
    return {"message": f"Initialized {count} new sources"}


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Get list of unique source categories"""
    
    result = await db.execute(
        select(Source.category).distinct().where(Source.category.isnot(None))
    )
    categories = [r[0] for r in result.all() if r[0]]
    
    return {"categories": sorted(categories)}
