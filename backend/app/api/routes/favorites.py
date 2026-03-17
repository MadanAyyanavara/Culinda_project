"""
Favorites API routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user, get_optional_user_id
from app.models.models import Favorite, NewsItem, User
from app.schemas.schemas import (
    FavoriteCreate, FavoriteResponse, FavoriteListResponse, NewsItemResponse
)

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=FavoriteListResponse)
async def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    """List user's favorited news items"""
    
    # Get total count
    count_result = await db.execute(
        select(func.count()).where(Favorite.user_id == user_id)
    )
    total = count_result.scalar()
    
    # Get favorites with news items
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Favorite)
        .options(
            selectinload(Favorite.news_item).selectinload(NewsItem.source)
        )
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    favorites = result.scalars().all()
    
    # Build response
    items = []
    for fav in favorites:
        news_response = NewsItemResponse.model_validate(fav.news_item)
        news_response.is_favorited = True
        
        items.append(FavoriteResponse(
            id=fav.id,
            user_id=fav.user_id,
            news_item_id=fav.news_item_id,
            news_item=news_response,
            notes=fav.notes,
            created_at=fav.created_at
        ))
    
    return FavoriteListResponse(items=items, total=total)


@router.post("", response_model=FavoriteResponse)
async def add_favorite(
    request: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    """Add a news item to favorites"""
    
    # Check if news item exists
    news_result = await db.execute(
        select(NewsItem)
        .options(selectinload(NewsItem.source))
        .where(NewsItem.id == request.news_item_id)
    )
    news_item = news_result.scalar_one_or_none()
    
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")
    
    # Check if already favorited
    existing = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == user_id,
                Favorite.news_item_id == request.news_item_id
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already in favorites")
    
    # Create favorite
    favorite = Favorite(
        user_id=user_id,
        news_item_id=request.news_item_id,
        notes=request.notes
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    
    # Build response
    news_response = NewsItemResponse.model_validate(news_item)
    news_response.is_favorited = True
    
    return FavoriteResponse(
        id=favorite.id,
        user_id=favorite.user_id,
        news_item_id=favorite.news_item_id,
        news_item=news_response,
        notes=favorite.notes,
        created_at=favorite.created_at
    )


@router.delete("/{favorite_id}")
async def remove_favorite(
    favorite_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    """Remove a news item from favorites"""
    
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.id == favorite_id,
                Favorite.user_id == user_id
            )
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    await db.delete(favorite)
    await db.commit()
    
    return {"message": "Removed from favorites"}


@router.delete("/news/{news_item_id}")
async def remove_favorite_by_news_id(
    news_item_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    """Remove a news item from favorites by news item ID"""
    
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.news_item_id == news_item_id,
                Favorite.user_id == user_id
            )
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    await db.delete(favorite)
    await db.commit()
    
    return {"message": "Removed from favorites"}


@router.patch("/{favorite_id}")
async def update_favorite_notes(
    favorite_id: int,
    notes: str,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    """Update notes on a favorite"""
    
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.id == favorite_id,
                Favorite.user_id == user_id
            )
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    favorite.notes = notes
    await db.commit()
    
    return {"message": "Notes updated"}
