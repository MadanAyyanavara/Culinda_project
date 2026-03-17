"""
Broadcast API routes for sharing news
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.api.deps import get_db, get_optional_user_id
from app.models.models import (
    NewsItem, Favorite, BroadcastLog, 
    BroadcastPlatform, BroadcastStatus
)
from app.schemas.schemas import (
    BroadcastRequest, BroadcastResponse, BroadcastLogListResponse,
    GenerateContentRequest, GenerateContentResponse,
    BroadcastPlatformEnum
)
from app.services.broadcast import BroadcastService
from app.services.summarizer import SummarizerService

router = APIRouter(prefix="/broadcast", tags=["broadcast"])


@router.post("", response_model=BroadcastResponse)
async def broadcast_news(
    request: BroadcastRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    """Broadcast/share a news item to a platform"""
    
    # Get the news item
    news_item = None
    favorite_id = None
    
    if request.favorite_id:
        fav_result = await db.execute(
            select(Favorite)
            .options(selectinload(Favorite.news_item))
            .where(Favorite.id == request.favorite_id)
        )
        favorite = fav_result.scalar_one_or_none()
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")
        news_item = favorite.news_item
        favorite_id = favorite.id
    elif request.news_item_id:
        news_result = await db.execute(
            select(NewsItem).where(NewsItem.id == request.news_item_id)
        )
        news_item = news_result.scalar_one_or_none()
        if not news_item:
            raise HTTPException(status_code=404, detail="News item not found")
    else:
        raise HTTPException(
            status_code=400, 
            detail="Either news_item_id or favorite_id is required"
        )
    
    # Initialize broadcast service
    broadcast_service = BroadcastService()
    
    # Perform broadcast based on platform
    platform = request.platform
    result = None
    
    if platform == BroadcastPlatformEnum.EMAIL:
        if not request.recipient:
            raise HTTPException(
                status_code=400, 
                detail="Recipient email is required for email broadcast"
            )
        result = await broadcast_service.broadcast_email(
            title=news_item.title,
            summary=news_item.summary or "",
            url=news_item.url,
            recipient_email=request.recipient,
            custom_message=request.custom_message
        )
    
    elif platform == BroadcastPlatformEnum.LINKEDIN:
        result = await broadcast_service.broadcast_linkedin(
            title=news_item.title,
            summary=news_item.summary or "",
            url=news_item.url,
            generate_ai_content=request.generate_ai_content
        )
    
    elif platform == BroadcastPlatformEnum.WHATSAPP:
        result = await broadcast_service.broadcast_whatsapp(
            title=news_item.title,
            summary=news_item.summary or "",
            url=news_item.url,
            phone_number=request.recipient
        )
    
    elif platform == BroadcastPlatformEnum.BLOG:
        result = await broadcast_service.broadcast_blog(
            title=news_item.title,
            summary=news_item.summary or "",
            url=news_item.url,
            author=news_item.author
        )
    
    elif platform == BroadcastPlatformEnum.NEWSLETTER:
        # For newsletter, we'll just format a single item
        result = await broadcast_service.broadcast_blog(
            title=news_item.title,
            summary=news_item.summary or "",
            url=news_item.url,
            author=news_item.author
        )
    
    # Create broadcast log
    status = BroadcastStatus.SENT if result.get("success") else BroadcastStatus.FAILED
    
    broadcast_log = BroadcastLog(
        user_id=user_id,
        favorite_id=favorite_id,
        news_item_id=news_item.id,
        platform=BroadcastPlatform(platform.value),
        status=status,
        content=result.get("content"),
        recipient=request.recipient,
        error_message=result.get("error"),
        sent_at=datetime.utcnow() if status == BroadcastStatus.SENT else None
    )
    db.add(broadcast_log)
    await db.commit()
    await db.refresh(broadcast_log)
    
    return BroadcastResponse(
        id=broadcast_log.id,
        platform=platform,
        status=BroadcastStatusEnum(status.value) if hasattr(status, 'value') else status,
        content=result.get("content"),
        recipient=request.recipient,
        created_at=broadcast_log.created_at,
        sent_at=broadcast_log.sent_at,
        error_message=result.get("error")
    )


# Import for status enum
from app.schemas.schemas import BroadcastStatusEnum


@router.get("/logs", response_model=BroadcastLogListResponse)
async def list_broadcast_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[BroadcastPlatformEnum] = None,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_optional_user_id)
):
    """Get broadcast history"""
    
    # Build query
    query = select(BroadcastLog).where(BroadcastLog.user_id == user_id)
    
    if platform:
        query = query.where(BroadcastLog.platform == BroadcastPlatform(platform.value))
    
    # Get total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()
    
    # Get logs
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(BroadcastLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    logs = result.scalars().all()
    
    return BroadcastLogListResponse(
        items=[
            BroadcastResponse(
                id=log.id,
                platform=BroadcastPlatformEnum(log.platform.value),
                status=BroadcastStatusEnum(log.status.value),
                content=log.content,
                recipient=log.recipient,
                created_at=log.created_at,
                sent_at=log.sent_at,
                error_message=log.error_message
            )
            for log in logs
        ],
        total=total
    )


@router.post("/generate-content", response_model=GenerateContentResponse)
async def generate_broadcast_content(
    request: GenerateContentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate AI content for a specific platform"""
    
    # Get news item
    result = await db.execute(
        select(NewsItem).where(NewsItem.id == request.news_item_id)
    )
    news_item = result.scalar_one_or_none()
    
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")
    
    summarizer = SummarizerService()
    content = ""
    
    if request.platform == BroadcastPlatformEnum.LINKEDIN:
        content = await summarizer.generate_linkedin_post(
            title=news_item.title,
            summary=news_item.summary or "",
            url=news_item.url,
            tone=request.tone or "professional"
        )
    elif request.platform == BroadcastPlatformEnum.WHATSAPP:
        content = await summarizer.generate_whatsapp_message(
            title=news_item.title,
            summary=news_item.summary or "",
            url=news_item.url
        )
    elif request.platform == BroadcastPlatformEnum.EMAIL:
        email_content = await summarizer.generate_email_content(
            title=news_item.title,
            summary=news_item.summary or "",
            url=news_item.url
        )
        content = f"Subject: {email_content['subject']}\n\n{email_content['body']}"
    else:
        content = f"{news_item.title}\n\n{news_item.summary}\n\nRead more: {news_item.url}"
    
    return GenerateContentResponse(
        content=content,
        platform=request.platform,
        character_count=len(content)
    )
