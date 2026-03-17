"""
SQLAlchemy database models for AI News Dashboard
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, Enum, Index, Float
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class SourceType(str, enum.Enum):
    RSS = "rss"
    API = "api"
    SCRAPER = "scraper"
    YOUTUBE = "youtube"


class BroadcastPlatform(str, enum.Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    BLOG = "blog"
    NEWSLETTER = "newsletter"


class BroadcastStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Source(Base):
    """News sources configuration"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    url = Column(String(500), nullable=False)
    feed_url = Column(String(500), nullable=True)  # RSS feed URL if applicable
    type = Column(Enum(SourceType), default=SourceType.RSS)
    active = Column(Boolean, default=True)
    icon_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "blog", "research", "news"
    last_fetched = Column(DateTime, nullable=True)
    fetch_interval_minutes = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    news_items = relationship("NewsItem", back_populates="source")
    
    def __repr__(self):
        return f"<Source {self.name}>"


class NewsItem(Base):
    """Aggregated news items"""
    __tablename__ = "news_items"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # Full content if available
    url = Column(String(1000), nullable=False, unique=True)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String(1000), nullable=True)
    tags = Column(Text, default="")  # Comma-separated tags for SQLite compatibility
    
    # Deduplication fields
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer, ForeignKey("news_items.id"), nullable=True)
    similarity_score = Column(Float, nullable=True)  # Similarity to duplicate
    content_hash = Column(String(64), nullable=True, index=True)  # For quick dedup
    
    # Clustering
    cluster_id = Column(Integer, nullable=True, index=True)
    
    # AI-generated fields
    ai_summary = Column(Text, nullable=True)
    impact_score = Column(Float, nullable=True)  # 0-1 score for importance
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source = relationship("Source", back_populates="news_items")
    favorites = relationship("Favorite", back_populates="news_item")
    duplicate_of = relationship("NewsItem", remote_side=[id])
    
    # Indexes for better query performance
    __table_args__ = (
        Index("idx_news_published_source", "published_at", "source_id"),
        Index("idx_news_not_duplicate", "is_duplicate", "published_at"),
    )
    
    def __repr__(self):
        return f"<NewsItem {self.title[:50]}>"


class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)  # Optional for MVP
    role = Column(String(50), default="user")  # user, admin
    is_active = Column(Boolean, default=True)
    
    # Preferences - stored as comma-separated string for SQLite
    email_notifications = Column(Boolean, default=True)
    preferred_sources = Column(Text, default="")  # Comma-separated source IDs
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    favorites = relationship("Favorite", back_populates="user")
    broadcast_logs = relationship("BroadcastLog", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Favorite(Base):
    """User favorites"""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    news_item_id = Column(Integer, ForeignKey("news_items.id"), nullable=False, index=True)
    notes = Column(Text, nullable=True)  # User notes about the favorite
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    news_item = relationship("NewsItem", back_populates="favorites")
    broadcast_logs = relationship("BroadcastLog", back_populates="favorite")
    
    # Unique constraint to prevent duplicate favorites
    __table_args__ = (
        Index("idx_unique_favorite", "user_id", "news_item_id", unique=True),
    )
    
    def __repr__(self):
        return f"<Favorite user={self.user_id} news={self.news_item_id}>"


class BroadcastLog(Base):
    """Broadcast/sharing history"""
    __tablename__ = "broadcast_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    favorite_id = Column(Integer, ForeignKey("favorites.id"), nullable=True, index=True)
    news_item_id = Column(Integer, ForeignKey("news_items.id"), nullable=True)
    
    platform = Column(Enum(BroadcastPlatform), nullable=False)
    status = Column(Enum(BroadcastStatus), default=BroadcastStatus.PENDING)
    
    # Content that was broadcast
    content = Column(Text, nullable=True)  # The actual message/post content
    recipient = Column(String(500), nullable=True)  # Email address, etc.
    
    # Response/tracking
    external_id = Column(String(255), nullable=True)  # ID from external platform
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="broadcast_logs")
    favorite = relationship("Favorite", back_populates="broadcast_logs")
    
    def __repr__(self):
        return f"<BroadcastLog {self.platform} {self.status}>"


class FetchLog(Base):
    """Log of fetch operations for monitoring"""
    __tablename__ = "fetch_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    success = Column(Boolean, default=False)
    items_fetched = Column(Integer, default=0)
    items_new = Column(Integer, default=0)
    items_duplicate = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Relationship
    source = relationship("Source")
    
    def __repr__(self):
        return f"<FetchLog source={self.source_id} success={self.success}>"
