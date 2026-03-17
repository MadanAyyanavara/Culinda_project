"""
News fetchers for various AI news sources
"""
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import feedparser
import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import logging

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    """Base class for all news fetchers"""
    
    def __init__(self, source_name: str, source_url: str, feed_url: Optional[str] = None):
        self.source_name = source_name
        self.source_url = source_url
        self.feed_url = feed_url
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "AI-News-Aggregator/1.0 (Educational Project)"
            }
        )
    
    @abstractmethod
    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch news items from the source"""
        pass
    
    def generate_content_hash(self, title: str, url: str) -> str:
        """Generate a hash for deduplication"""
        content = f"{title.lower().strip()}:{url.lower().strip()}"
        return hashlib.sha256(content.encode()).hexdigest()[:64]
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None
        try:
            return date_parser.parse(date_str)
        except Exception:
            return None
    
    def clean_html(self, html: str) -> str:
        """Remove HTML tags from text"""
        if not html:
            return ""
        soup = BeautifulSoup(html, "lxml")
        return soup.get_text(separator=" ", strip=True)
    
    def truncate_summary(self, text: str, max_length: int = 500) -> str:
        """Truncate summary to max length"""
        if not text:
            return ""
        text = self.clean_html(text)
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(" ", 1)[0] + "..."
    
    async def close(self):
        await self.client.aclose()


class RSSFetcher(BaseFetcher):
    """Fetcher for RSS/Atom feeds"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        items = []
        try:
            response = await self.client.get(self.feed_url or self.source_url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries[:50]:  # Limit to 50 items per fetch
                published = None
                if hasattr(entry, 'published'):
                    published = self.parse_date(entry.published)
                elif hasattr(entry, 'updated'):
                    published = self.parse_date(entry.updated)
                
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = self.truncate_summary(entry.summary)
                elif hasattr(entry, 'description'):
                    summary = self.truncate_summary(entry.description)
                
                # Extract image
                image_url = None
                if hasattr(entry, 'media_content') and entry.media_content:
                    image_url = entry.media_content[0].get('url')
                elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                    image_url = entry.media_thumbnail[0].get('url')
                
                # Extract tags
                tags = []
                if hasattr(entry, 'tags'):
                    tags = [tag.term for tag in entry.tags[:5]]
                
                item = {
                    "title": entry.get('title', 'No Title'),
                    "url": entry.get('link', ''),
                    "summary": summary,
                    "author": entry.get('author', None),
                    "published_at": published,
                    "image_url": image_url,
                    "tags": tags,
                    "content_hash": self.generate_content_hash(
                        entry.get('title', ''), 
                        entry.get('link', '')
                    )
                }
                
                if item['url']:  # Only add if we have a URL
                    items.append(item)
                    
        except Exception as e:
            logger.error(f"Error fetching RSS from {self.source_name}: {e}")
        
        return items


class HackerNewsFetcher(BaseFetcher):
    """Fetcher for Hacker News AI-related posts"""
    
    API_BASE = "https://hacker-news.firebaseio.com/v0"
    AI_KEYWORDS = ['ai', 'artificial intelligence', 'machine learning', 'ml', 
                   'deep learning', 'neural network', 'gpt', 'llm', 'chatgpt',
                   'openai', 'anthropic', 'claude', 'gemini', 'transformer']
    
    async def fetch(self) -> List[Dict[str, Any]]:
        items = []
        try:
            # Get top stories
            response = await self.client.get(f"{self.API_BASE}/topstories.json")
            story_ids = response.json()[:100]  # Check top 100
            
            # Fetch story details in parallel
            tasks = [self._fetch_story(sid) for sid in story_ids[:30]]
            stories = await asyncio.gather(*tasks, return_exceptions=True)
            
            for story in stories:
                if isinstance(story, dict) and story:
                    items.append(story)
                    
        except Exception as e:
            logger.error(f"Error fetching from Hacker News: {e}")
        
        return items[:20]  # Return top 20 AI-related
    
    async def _fetch_story(self, story_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = await self.client.get(f"{self.API_BASE}/item/{story_id}.json")
            data = response.json()
            
            if not data or data.get('type') != 'story':
                return None
            
            title = data.get('title', '').lower()
            # Filter for AI-related content
            if not any(kw in title for kw in self.AI_KEYWORDS):
                return None
            
            return {
                "title": data.get('title', 'No Title'),
                "url": data.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                "summary": f"Score: {data.get('score', 0)} | Comments: {data.get('descendants', 0)}",
                "author": data.get('by'),
                "published_at": datetime.fromtimestamp(data.get('time', 0)),
                "image_url": None,
                "tags": ["hacker-news"],
                "content_hash": self.generate_content_hash(
                    data.get('title', ''),
                    data.get('url', str(story_id))
                )
            }
        except Exception:
            return None


class RedditFetcher(BaseFetcher):
    """Fetcher for Reddit ML subreddit"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        items = []
        try:
            headers = {"User-Agent": "AI-News-Bot/1.0"}
            response = await self.client.get(
                "https://www.reddit.com/r/MachineLearning/hot.json?limit=30",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                
                if post_data.get('stickied'):
                    continue
                
                published = datetime.fromtimestamp(post_data.get('created_utc', 0))
                
                items.append({
                    "title": post_data.get('title', 'No Title'),
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "summary": self.truncate_summary(post_data.get('selftext', '')),
                    "author": post_data.get('author'),
                    "published_at": published,
                    "image_url": post_data.get('thumbnail') if post_data.get('thumbnail', '').startswith('http') else None,
                    "tags": ["reddit", "machine-learning"],
                    "content_hash": self.generate_content_hash(
                        post_data.get('title', ''),
                        post_data.get('permalink', '')
                    )
                })
                
        except Exception as e:
            logger.error(f"Error fetching from Reddit: {e}")
        
        return items


class ArxivFetcher(BaseFetcher):
    """Fetcher for arXiv AI/ML papers"""
    
    ARXIV_API = "http://export.arxiv.org/api/query"
    
    async def fetch(self) -> List[Dict[str, Any]]:
        items = []
        try:
            params = {
                "search_query": "cat:cs.AI OR cat:cs.CL OR cat:cs.LG",
                "start": 0,
                "max_results": 30,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }
            
            response = await self.client.get(self.ARXIV_API, params=params)
            response.raise_for_status()
            
            # Parse Atom feed
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries:
                # Extract authors
                authors = ", ".join([a.get('name', '') for a in entry.get('authors', [])[:3]])
                if len(entry.get('authors', [])) > 3:
                    authors += " et al."
                
                # Extract categories as tags
                tags = [tag.get('term', '') for tag in entry.get('tags', [])[:5]]
                
                items.append({
                    "title": entry.get('title', 'No Title').replace('\n', ' '),
                    "url": entry.get('link', ''),
                    "summary": self.truncate_summary(entry.get('summary', '')),
                    "author": authors,
                    "published_at": self.parse_date(entry.get('published')),
                    "image_url": None,
                    "tags": tags,
                    "content_hash": self.generate_content_hash(
                        entry.get('title', ''),
                        entry.get('id', '')
                    )
                })
                
        except Exception as e:
            logger.error(f"Error fetching from arXiv: {e}")
        
        return items


class YouTubeFetcher(BaseFetcher):
    """Fetcher for YouTube AI channels (using RSS feeds)"""
    
    async def fetch(self) -> List[Dict[str, Any]]:
        items = []
        try:
            response = await self.client.get(self.feed_url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries[:10]:
                # Extract video ID for thumbnail
                video_id = entry.get('yt_videoid', '')
                thumbnail = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else None
                
                items.append({
                    "title": entry.get('title', 'No Title'),
                    "url": entry.get('link', ''),
                    "summary": self.truncate_summary(entry.get('summary', '')),
                    "author": entry.get('author', self.source_name),
                    "published_at": self.parse_date(entry.get('published')),
                    "image_url": thumbnail,
                    "tags": ["youtube", "video"],
                    "content_hash": self.generate_content_hash(
                        entry.get('title', ''),
                        entry.get('link', '')
                    )
                })
                
        except Exception as e:
            logger.error(f"Error fetching from YouTube {self.source_name}: {e}")
        
        return items


# Predefined source configurations with their fetchers
SOURCE_CONFIGS = [
    # ===== Blogs =====
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog",
        "feed_url": "https://openai.com/blog/rss.xml",
        "type": "rss",
        "category": "blog",
        "icon_url": "https://openai.com/favicon.ico",
        "description": "Official OpenAI research and announcements"
    },
    {
        "name": "Google AI Blog",
        "url": "https://ai.googleblog.com",
        "feed_url": "https://ai.googleblog.com/feeds/posts/default?alt=rss",
        "type": "rss",
        "category": "blog",
        "icon_url": "https://www.google.com/favicon.ico",
        "description": "Google AI research updates"
    },
    {
        "name": "Meta AI",
        "url": "https://ai.meta.com/blog",
        "feed_url": "https://ai.meta.com/blog/rss/",
        "type": "rss",
        "category": "blog",
        "icon_url": "https://ai.meta.com/favicon.ico",
        "description": "Meta AI research and updates"
    },
    {
        "name": "Anthropic",
        "url": "https://www.anthropic.com",
        "feed_url": "https://www.anthropic.com/rss.xml",
        "type": "rss",
        "category": "blog",
        "icon_url": "https://www.anthropic.com/favicon.ico",
        "description": "Anthropic AI safety research"
    },
    {
        "name": "DeepMind",
        "url": "https://deepmind.google",
        "feed_url": "https://deepmind.google/blog/rss.xml",
        "type": "rss",
        "category": "blog",
        "icon_url": "https://deepmind.google/favicon.ico",
        "description": "DeepMind research publications"
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog",
        "feed_url": "https://huggingface.co/blog/feed.xml",
        "type": "rss",
        "category": "blog",
        "icon_url": "https://huggingface.co/favicon.ico",
        "description": "Hugging Face ML community updates"
    },
    {
        "name": "Microsoft AI Blog",
        "url": "https://blogs.microsoft.com/ai",
        "feed_url": "https://blogs.microsoft.com/ai/feed/",
        "type": "rss",
        "category": "blog",
        "icon_url": "https://microsoft.com/favicon.ico",
        "description": "Microsoft AI announcements"
    },
    {
        "name": "Stability AI Blog",
        "url": "https://stability.ai/blog",
        "feed_url": "https://stability.ai/blog/rss.xml",
        "type": "rss",
        "category": "blog",
        "icon_url": "https://stability.ai/favicon.ico",
        "description": "Stability AI open source updates"
    },
    # ===== Tech News =====
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/",
        "feed_url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "type": "rss",
        "category": "news",
        "icon_url": "https://techcrunch.com/favicon.ico",
        "description": "TechCrunch AI news coverage"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/",
        "feed_url": "https://venturebeat.com/category/ai/feed/",
        "type": "rss",
        "category": "news",
        "icon_url": "https://venturebeat.com/favicon.ico",
        "description": "VentureBeat AI industry news"
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/ai-artificial-intelligence",
        "feed_url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "type": "rss",
        "category": "news",
        "icon_url": "https://www.theverge.com/favicon.ico",
        "description": "The Verge AI coverage"
    },
    {
        "name": "Wired AI",
        "url": "https://www.wired.com/tag/artificial-intelligence/",
        "feed_url": "https://www.wired.com/feed/tag/ai/latest/rss",
        "type": "rss",
        "category": "news",
        "icon_url": "https://www.wired.com/favicon.ico",
        "description": "Wired magazine AI articles"
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/",
        "feed_url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "type": "rss",
        "category": "news",
        "icon_url": "https://www.technologyreview.com/favicon.ico",
        "description": "MIT Tech Review AI coverage"
    },
    {
        "name": "Ars Technica AI",
        "url": "https://arstechnica.com/ai/",
        "feed_url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "type": "rss",
        "category": "news",
        "icon_url": "https://arstechnica.com/favicon.ico",
        "description": "Ars Technica technology news"
    },
    # ===== Research =====
    {
        "name": "arXiv AI",
        "url": "https://arxiv.org/list/cs.AI/recent",
        "feed_url": None,
        "type": "api",
        "category": "research",
        "icon_url": "https://arxiv.org/favicon.ico",
        "description": "arXiv AI/ML research papers"
    },
    {
        "name": "Papers With Code",
        "url": "https://paperswithcode.com",
        "feed_url": "https://paperswithcode.com/rss",
        "type": "rss",
        "category": "research",
        "icon_url": "https://paperswithcode.com/favicon.ico",
        "description": "ML papers with code implementations"
    },
    # ===== Community =====
    {
        "name": "Hacker News AI",
        "url": "https://news.ycombinator.com",
        "feed_url": None,
        "type": "api",
        "category": "community",
        "icon_url": "https://news.ycombinator.com/favicon.ico",
        "description": "Hacker News AI-related posts"
    },
    {
        "name": "Reddit r/MachineLearning",
        "url": "https://www.reddit.com/r/MachineLearning/",
        "feed_url": None,
        "type": "api",
        "category": "community",
        "icon_url": "https://www.reddit.com/favicon.ico",
        "description": "Reddit ML community discussions"
    },
    # ===== YouTube Channels =====
    {
        "name": "Two Minute Papers",
        "url": "https://www.youtube.com/c/K%C3%A1rolyZsolnai",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCbfYPyITQ-7l4upoX8nvctg",
        "type": "youtube",
        "category": "youtube",
        "icon_url": "https://www.youtube.com/favicon.ico",
        "description": "AI research explained in 2 minutes"
    },
    {
        "name": "Yannic Kilcher",
        "url": "https://www.youtube.com/c/YannicKilcher",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCZHmQk67mSJgfCCTn7xBfew",
        "type": "youtube",
        "category": "youtube",
        "icon_url": "https://www.youtube.com/favicon.ico",
        "description": "Deep learning paper explanations"
    },
    # ===== Startup/Product =====
    {
        "name": "Y Combinator Blog",
        "url": "https://www.ycombinator.com/blog",
        "feed_url": "https://www.ycombinator.com/blog/rss/",
        "type": "rss",
        "category": "startup",
        "icon_url": "https://www.ycombinator.com/favicon.ico",
        "description": "YC startup insights"
    },
    {
        "name": "Product Hunt AI",
        "url": "https://www.producthunt.com/topics/artificial-intelligence",
        "feed_url": "https://www.producthunt.com/feed?category=artificial-intelligence",
        "type": "rss",
        "category": "product",
        "icon_url": "https://www.producthunt.com/favicon.ico",
        "description": "New AI product launches"
    },
]


def get_fetcher_for_source(source_config: Dict[str, Any]) -> BaseFetcher:
    """Factory function to get appropriate fetcher for a source"""
    source_type = source_config.get("type", "rss")
    name = source_config["name"]
    url = source_config["url"]
    feed_url = source_config.get("feed_url")
    
    if "Hacker News" in name:
        return HackerNewsFetcher(name, url, feed_url)
    elif "Reddit" in name:
        return RedditFetcher(name, url, feed_url)
    elif "arXiv" in name:
        return ArxivFetcher(name, url, feed_url)
    elif source_type == "youtube":
        return YouTubeFetcher(name, url, feed_url)
    else:
        return RSSFetcher(name, url, feed_url)
