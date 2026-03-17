"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sources table
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('feed_url', sa.String(500), nullable=True),
        sa.Column('type', sa.Enum('rss', 'api', 'scraper', 'youtube', name='sourcetype'), nullable=True),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('last_fetched', sa.DateTime(), nullable=True),
        sa.Column('fetch_interval_minutes', sa.Integer(), default=15),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_sources_id', 'sources', ['id'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), default='user'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('email_notifications', sa.Boolean(), default=True),
        sa.Column('preferred_sources', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create news_items table
    op.create_table(
        'news_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('url', sa.String(1000), nullable=False),
        sa.Column('author', sa.String(255), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('fetched_at', sa.DateTime(), nullable=True),
        sa.Column('image_url', sa.String(1000), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('is_duplicate', sa.Boolean(), default=False),
        sa.Column('duplicate_of_id', sa.Integer(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('cluster_id', sa.Integer(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id']),
        sa.ForeignKeyConstraint(['duplicate_of_id'], ['news_items.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    op.create_index('ix_news_items_id', 'news_items', ['id'])
    op.create_index('ix_news_items_source_id', 'news_items', ['source_id'])
    op.create_index('ix_news_items_published_at', 'news_items', ['published_at'])
    op.create_index('ix_news_items_content_hash', 'news_items', ['content_hash'])
    op.create_index('idx_news_published_source', 'news_items', ['published_at', 'source_id'])
    op.create_index('idx_news_not_duplicate', 'news_items', ['is_duplicate', 'published_at'])

    # Create favorites table
    op.create_table(
        'favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('news_item_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['news_item_id'], ['news_items.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_favorites_id', 'favorites', ['id'])
    op.create_index('ix_favorites_user_id', 'favorites', ['user_id'])
    op.create_index('ix_favorites_news_item_id', 'favorites', ['news_item_id'])
    op.create_index('idx_unique_favorite', 'favorites', ['user_id', 'news_item_id'], unique=True)

    # Create broadcast_logs table
    op.create_table(
        'broadcast_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('favorite_id', sa.Integer(), nullable=True),
        sa.Column('news_item_id', sa.Integer(), nullable=True),
        sa.Column('platform', sa.Enum('email', 'linkedin', 'whatsapp', 'blog', 'newsletter', name='broadcastplatform'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'sent', 'failed', name='broadcaststatus'), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('recipient', sa.String(500), nullable=True),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['favorite_id'], ['favorites.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_broadcast_logs_id', 'broadcast_logs', ['id'])
    op.create_index('ix_broadcast_logs_user_id', 'broadcast_logs', ['user_id'])

    # Create fetch_logs table
    op.create_table(
        'fetch_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('success', sa.Boolean(), default=False),
        sa.Column('items_fetched', sa.Integer(), default=0),
        sa.Column('items_new', sa.Integer(), default=0),
        sa.Column('items_duplicate', sa.Integer(), default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_fetch_logs_id', 'fetch_logs', ['id'])
    op.create_index('ix_fetch_logs_source_id', 'fetch_logs', ['source_id'])


def downgrade() -> None:
    op.drop_table('fetch_logs')
    op.drop_table('broadcast_logs')
    op.drop_table('favorites')
    op.drop_table('news_items')
    op.drop_table('users')
    op.drop_table('sources')
    op.execute('DROP TYPE IF EXISTS sourcetype')
    op.execute('DROP TYPE IF EXISTS broadcastplatform')
    op.execute('DROP TYPE IF EXISTS broadcaststatus')
