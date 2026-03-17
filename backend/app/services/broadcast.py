"""
Broadcast service for sharing news via email, LinkedIn, WhatsApp
"""
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import urllib.parse
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings
from app.services.summarizer import SummarizerService

logger = logging.getLogger(__name__)


class BroadcastService:
    """Service for broadcasting/sharing news to various platforms"""
    
    def __init__(self):
        self.summarizer = SummarizerService()
    
    async def broadcast_email(
        self,
        title: str,
        summary: str,
        url: str,
        recipient_email: str,
        recipient_name: Optional[str] = None,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send news via email"""
        try:
            if custom_message:
                subject = f"AI News: {title}"
                body = f"{custom_message}\n\n---\n\n{title}\n\n{summary}\n\nRead more: {url}"
            else:
                # Generate email content using AI
                email_content = await self.summarizer.generate_email_content(
                    title, summary, url, recipient_name
                )
                subject = email_content["subject"]
                body = email_content["body"]
            
            # Check if SMTP is configured
            if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
                # Return mock response for demo
                logger.info(f"Email would be sent to {recipient_email} (SMTP not configured)")
                return {
                    "success": True,
                    "platform": "email",
                    "recipient": recipient_email,
                    "content": body,
                    "subject": subject,
                    "mock": True,
                    "message": "Email simulated (SMTP not configured)"
                }
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["From"] = settings.EMAIL_FROM
            message["To"] = recipient_email
            message["Subject"] = subject
            
            # Plain text version
            message.attach(MIMEText(body, "plain"))
            
            # HTML version
            html_body = f"""
            <html>
            <body>
                <h2>{title}</h2>
                <p>{body.replace(chr(10), '<br>')}</p>
                <p><a href="{url}">Read the full article</a></p>
            </body>
            </html>
            """
            message.attach(MIMEText(html_body, "html"))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True
            )
            
            return {
                "success": True,
                "platform": "email",
                "recipient": recipient_email,
                "content": body,
                "subject": subject,
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                "success": False,
                "platform": "email",
                "error": str(e)
            }
    
    async def broadcast_linkedin(
        self,
        title: str,
        summary: str,
        url: str,
        generate_ai_content: bool = True,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Generate LinkedIn post content and sharing URL"""
        try:
            if generate_ai_content:
                content = await self.summarizer.generate_linkedin_post(
                    title, summary, url, tone
                )
            else:
                content = f"""🤖 {title}

{summary[:200]}{'...' if len(summary) > 200 else ''}

#AI #MachineLearning #Technology

🔗 {url}"""
            
            # Generate LinkedIn share URL
            # LinkedIn share URL format
            encoded_url = urllib.parse.quote(url, safe='')
            share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}"
            
            return {
                "success": True,
                "platform": "linkedin",
                "content": content,
                "share_url": share_url,
                "character_count": len(content),
                "instructions": "Click the share URL to post on LinkedIn, or copy the generated content."
            }
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn post: {e}")
            return {
                "success": False,
                "platform": "linkedin",
                "error": str(e)
            }
    
    async def broadcast_whatsapp(
        self,
        title: str,
        summary: str,
        url: str,
        phone_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate WhatsApp message and sharing URL"""
        try:
            # Generate message
            message = await self.summarizer.generate_whatsapp_message(
                title, summary, url
            )
            
            # URL encode the message
            encoded_message = urllib.parse.quote(message)
            
            # Generate WhatsApp Web URL
            if phone_number:
                # Remove any non-numeric characters
                clean_number = ''.join(filter(str.isdigit, phone_number))
                share_url = f"https://wa.me/{clean_number}?text={encoded_message}"
            else:
                # General share URL (opens WhatsApp to select contact)
                share_url = f"https://wa.me/?text={encoded_message}"
            
            return {
                "success": True,
                "platform": "whatsapp",
                "content": message,
                "share_url": share_url,
                "phone_number": phone_number,
                "instructions": "Click the share URL to open WhatsApp with the pre-filled message."
            }
            
        except Exception as e:
            logger.error(f"Error generating WhatsApp message: {e}")
            return {
                "success": False,
                "platform": "whatsapp",
                "error": str(e)
            }
    
    async def broadcast_blog(
        self,
        title: str,
        summary: str,
        url: str,
        author: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate blog post content"""
        try:
            # Generate a more detailed blog-style content
            content = f"""# {title}

*Source: [{url}]({url})*
{f'*Author: {author}*' if author else ''}

## Summary

{summary}

## Key Takeaways

This article discusses important developments in AI technology. Read the full article for complete details.

---

*This post was curated by AI News Dashboard*
"""
            
            return {
                "success": True,
                "platform": "blog",
                "content": content,
                "format": "markdown",
                "instructions": "Copy this content to your blog platform."
            }
            
        except Exception as e:
            logger.error(f"Error generating blog content: {e}")
            return {
                "success": False,
                "platform": "blog",
                "error": str(e)
            }
    
    async def broadcast_newsletter(
        self,
        items: list,  # List of news items
    ) -> Dict[str, Any]:
        """Generate newsletter content from multiple items"""
        try:
            # Build newsletter content
            newsletter = """# AI News Weekly Digest

Here are the top AI news stories this week:

---

"""
            for i, item in enumerate(items[:10], 1):
                newsletter += f"""## {i}. {item.get('title', 'Untitled')}

{item.get('summary', 'No summary available.')}

🔗 [Read more]({item.get('url', '#')})

---

"""
            
            newsletter += """
*This newsletter was generated by AI News Dashboard*

To unsubscribe, update your preferences in the dashboard.
"""
            
            return {
                "success": True,
                "platform": "newsletter",
                "content": newsletter,
                "format": "markdown",
                "items_included": len(items[:10]),
                "instructions": "Send this content via your newsletter platform."
            }
            
        except Exception as e:
            logger.error(f"Error generating newsletter: {e}")
            return {
                "success": False,
                "platform": "newsletter",
                "error": str(e)
            }
