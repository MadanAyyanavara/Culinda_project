"""
News API routes
"""
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user, get_optional_user_id
from app.models.models import NewsItem, Source, Favorite, User
from app.schemas.schemas import (
    NewsItemResponse, NewsItemDetail, NewsListResponse,
    RefreshRequest, RefreshResponse, DashboardStats
)
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=NewsListResponse)
async def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_ids: Optional[str] = Query(None, description="Comma-separated source IDs"),
    search: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    include_duplicates: bool = Query(False),
    sort_by: str = Query("published_at", regex="^(published_at|fetched_at|title)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    """List news items with filtering, pagination, and sorting"""
    
    # Build query
    query = select(NewsItem).options(selectinload(NewsItem.source))
    
    # Filter duplicates
    if not include_duplicates:
        query = query.where(NewsItem.is_duplicate == False)
    
    # Filter by source
    if source_ids:
        ids = [int(id.strip()) for id in source_ids.split(",") if id.strip().isdigit()]
        if ids:
            query = query.where(NewsItem.source_id.in_(ids))
    
    # Search in title and summary
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                NewsItem.title.ilike(search_term),
                NewsItem.summary.ilike(search_term)
            )
        )
    
    # Filter by tags
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
        if tag_list:
            # SQLite: use OR conditions for tag matching
            tag_conditions = []
            for tag in tag_list:
                tag_conditions.append(NewsItem.tags.ilike(f"%{tag}%"))
            if tag_conditions:
                query = query.where(or_(*tag_conditions))
    
    # Filter by date
    if start_date:
        query = query.where(NewsItem.published_at >= start_date)
    if end_date:
        query = query.where(NewsItem.published_at <= end_date)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply sorting
    sort_column = getattr(NewsItem, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Get user's favorites
    fav_result = await db.execute(
        select(Favorite.news_item_id).where(Favorite.user_id == user_id)
    )
    favorite_ids = set(fav_result.scalars().all())
    
    # Build response
    response_items = []
    for item in items:
        item_dict = NewsItemResponse.model_validate(item)
        item_dict.is_favorited = item.id in favorite_ids
        response_items.append(item_dict)
    
    return NewsListResponse(
        items=response_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db), user_id: int = Depends(get_optional_user_id)):
    """Get dashboard statistics"""
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    # Total news (non-duplicate)
    total_news = await db.execute(
        select(func.count()).where(NewsItem.is_duplicate == False)
    )
    
    # Total sources
    total_sources = await db.execute(select(func.count()).select_from(Source))
    
    # Active sources
    active_sources = await db.execute(
        select(func.count()).where(Source.active == True)
    )
    
    # User favorites
    total_favorites = await db.execute(
        select(func.count()).where(Favorite.user_id == user_id)
    )
    
    # Broadcasts (would come from broadcast_logs)
    from app.models.models import BroadcastLog
    total_broadcasts = await db.execute(
        select(func.count()).where(BroadcastLog.user_id == user_id)
    )
    
    # News today
    news_today = await db.execute(
        select(func.count()).where(
            and_(
                NewsItem.is_duplicate == False,
                NewsItem.published_at >= today_start
            )
        )
    )
    
    # News this week
    news_week = await db.execute(
        select(func.count()).where(
            and_(
                NewsItem.is_duplicate == False,
                NewsItem.published_at >= week_start
            )
        )
    )
    
    return DashboardStats(
        total_news=total_news.scalar() or 0,
        total_sources=total_sources.scalar() or 0,
        active_sources=active_sources.scalar() or 0,
        total_favorites=total_favorites.scalar() or 0,
        total_broadcasts=total_broadcasts.scalar() or 0,
        news_today=news_today.scalar() or 0,
        news_this_week=news_week.scalar() or 0
    )


@router.get("/{news_id}", response_model=NewsItemDetail)
async def get_news_item(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    """Get a single news item by ID"""
    
    result = await db.execute(
        select(NewsItem)
        .options(selectinload(NewsItem.source))
        .where(NewsItem.id == news_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")
    
    # Check if favorited
    fav_result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == user_id,
                Favorite.news_item_id == news_id
            )
        )
    )
    is_favorited = fav_result.scalar_one_or_none() is not None
    
    response = NewsItemDetail.model_validate(item)
    response.is_favorited = is_favorited
    
    return response


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_news(
    request: RefreshRequest = None,
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger news refresh"""
    
    ingestion = IngestionService(db)
    
    # Initialize sources if needed
    await ingestion.initialize_sources()
    
    if request and request.source_ids:
        result = await ingestion.fetch_sources_by_ids(request.source_ids)
    else:
        result = await ingestion.fetch_all_sources()
    
    # Run deduplication
    await ingestion.run_deduplication()
    
    return RefreshResponse(
        message="News refresh completed",
        sources_refreshed=result["sources_fetched"],
        new_items=result["new_items"],
        duplicates_found=result["duplicates_found"],
        errors=result.get("errors", [])
    )
