"""
API dependencies
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.core.database import AsyncSessionLocal
from app.models.models import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# For MVP, we'll use a simple user system
# In production, this would use JWT tokens or OAuth
DEFAULT_USER_ID = 1


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    """Get or create default user for MVP"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(User).where(User.id == DEFAULT_USER_ID)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create default user
        user = User(
            id=DEFAULT_USER_ID,
            email="demo@example.com",
            name="Demo User",
            role="admin"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return user


def get_optional_user_id() -> int:
    """Get user ID for operations that don't require full user object"""
    return DEFAULT_USER_ID
