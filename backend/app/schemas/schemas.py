"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator
from enum import Enum


# Enums matching database enums
class SourceTypeEnum(str, Enum):
    RSS = "rss"
    API = "api"
    SCRAPER = "scraper"
    YOUTUBE = "youtube"


class BroadcastPlatformEnum(str, Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    BLOG = "blog"
    NEWSLETTER = "newsletter"


class BroadcastStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


# ============ Source Schemas ============

class SourceBase(BaseModel):
    name: str
    url: str
    feed_url: Optional[str] = None
    type: SourceTypeEnum = SourceTypeEnum.RSS
    active: bool = True
    icon_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    feed_url: Optional[str] = None
    type: Optional[SourceTypeEnum] = None
    active: Optional[bool] = None
    icon_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class SourceResponse(SourceBase):
    id: int
    last_fetched: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ News Item Schemas ============

class NewsItemBase(BaseModel):
    title: str
    summary: Optional[str] = None
    url: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    tags: List[str] = []
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            # Handle comma-separated string from database
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v or []


class NewsItemCreate(NewsItemBase):
    source_id: int
    content: Optional[str] = None


class NewsItemResponse(NewsItemBase):
    id: int
    source_id: int
    source: Optional[SourceResponse] = None
    content: Optional[str] = None
    is_duplicate: bool = False
    ai_summary: Optional[str] = None
    impact_score: Optional[float] = None
    cluster_id: Optional[int] = None
    fetched_at: datetime
    created_at: datetime
    is_favorited: bool = False  # Will be populated based on user context
    
    class Config:
        from_attributes = True


class NewsItemDetail(NewsItemResponse):
    content: Optional[str] = None
    duplicate_of_id: Optional[int] = None
    similarity_score: Optional[float] = None


class NewsListResponse(BaseModel):
    items: List[NewsItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============ User Schemas ============

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    email_notifications: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Favorite Schemas ============

class FavoriteCreate(BaseModel):
    news_item_id: int
    notes: Optional[str] = None


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    news_item_id: int
    news_item: NewsItemResponse
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    items: List[FavoriteResponse]
    total: int


# ============ Broadcast Schemas ============

class BroadcastRequest(BaseModel):
    news_item_id: Optional[int] = None
    favorite_id: Optional[int] = None
    platform: BroadcastPlatformEnum
    recipient: Optional[str] = None  # Email address for email, etc.
    custom_message: Optional[str] = None
    generate_ai_content: bool = False  # Use AI to generate LinkedIn caption, etc.


class BroadcastResponse(BaseModel):
    id: int
    platform: BroadcastPlatformEnum
    status: BroadcastStatusEnum
    content: Optional[str] = None
    recipient: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class BroadcastLogListResponse(BaseModel):
    items: List[BroadcastResponse]
    total: int


# ============ Content Generation Schemas ============

class GenerateContentRequest(BaseModel):
    news_item_id: int
    platform: BroadcastPlatformEnum
    tone: Optional[str] = "professional"  # professional, casual, enthusiastic


class GenerateContentResponse(BaseModel):
    content: str
    platform: BroadcastPlatformEnum
    character_count: int


# ============ Filter/Query Schemas ============

class NewsFilterParams(BaseModel):
    source_ids: Optional[List[int]] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_duplicates: bool = False
    sort_by: str = "published_at"  # published_at, fetched_at, impact_score
    sort_order: str = "desc"  # asc, desc


# ============ Stats Schemas ============

class DashboardStats(BaseModel):
    total_news: int
    total_sources: int
    active_sources: int
    total_favorites: int
    total_broadcasts: int
    news_today: int
    news_this_week: int


class SourceStats(BaseModel):
    source_id: int
    source_name: str
    total_items: int
    items_today: int
    last_fetched: Optional[datetime]


# ============ Refresh/Admin Schemas ============

class RefreshRequest(BaseModel):
    source_ids: Optional[List[int]] = None  # None means refresh all


class RefreshResponse(BaseModel):
    message: str
    sources_refreshed: int
    new_items: int
    duplicates_found: int
    errors: List[str] = []


# ============ Health Check ============

class HealthCheck(BaseModel):
    status: str
    database: str
    version: str = "1.0.0"
