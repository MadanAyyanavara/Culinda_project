"""
AI-powered content summarization and generation
"""
from typing import Optional
import logging
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class SummarizerService:
    """Service for AI-powered content summarization"""
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def summarize(self, text: str, max_length: int = 200) -> Optional[str]:
        """Generate a concise summary of the text"""
        if not self.client:
            logger.warning("OpenAI client not configured")
            return None
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant that summarizes AI news. Create a concise summary in {max_length} characters or less."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this AI news:\n\n{text[:2000]}"
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            return None
    
    async def generate_linkedin_post(
        self, 
        title: str, 
        summary: str, 
        url: str,
        tone: str = "professional"
    ) -> str:
        """Generate a LinkedIn post for sharing news"""
        if not self.client:
            # Fallback template if no OpenAI
            return self._fallback_linkedin_post(title, summary, url)
        
        try:
            tone_instructions = {
                "professional": "Write in a professional, insightful tone suitable for industry leaders.",
                "casual": "Write in a friendly, conversational tone that's engaging.",
                "enthusiastic": "Write with excitement and enthusiasm about the topic."
            }
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a social media expert creating LinkedIn posts about AI news.
                        {tone_instructions.get(tone, tone_instructions['professional'])}
                        Include relevant hashtags.
                        Keep it under 280 characters for optimal engagement.
                        Do not include the URL in the post - it will be added separately."""
                    },
                    {
                        "role": "user",
                        "content": f"Create a LinkedIn post for:\n\nTitle: {title}\n\nSummary: {summary}"
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            post = response.choices[0].message.content.strip()
            return f"{post}\n\n🔗 {url}"
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn post: {e}")
            return self._fallback_linkedin_post(title, summary, url)
    
    def _fallback_linkedin_post(self, title: str, summary: str, url: str) -> str:
        """Fallback LinkedIn post template"""
        truncated_summary = summary[:150] + "..." if len(summary) > 150 else summary
        return f"""🤖 {title}

{truncated_summary}

#AI #MachineLearning #Technology #Innovation

🔗 {url}"""
    
    async def generate_email_content(
        self,
        title: str,
        summary: str,
        url: str,
        recipient_name: Optional[str] = None
    ) -> dict:
        """Generate email subject and body for sharing news"""
        greeting = f"Hi {recipient_name}," if recipient_name else "Hi,"
        
        if not self.client:
            return self._fallback_email(title, summary, url, greeting)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an assistant helping share interesting AI news via email.
                        Generate a subject line and email body.
                        Be concise but informative.
                        Response format:
                        SUBJECT: [subject line]
                        BODY: [email body]"""
                    },
                    {
                        "role": "user",
                        "content": f"Create an email to share this AI news:\n\nTitle: {title}\n\nSummary: {summary}\n\nURL: {url}"
                    }
                ],
                max_tokens=300,
                temperature=0.6
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse response
            lines = content.split('\n')
            subject = ""
            body = ""
            
            for line in lines:
                if line.startswith("SUBJECT:"):
                    subject = line.replace("SUBJECT:", "").strip()
                elif line.startswith("BODY:"):
                    body = content.split("BODY:")[1].strip()
                    break
            
            if not subject:
                subject = f"Interesting AI News: {title}"
            if not body:
                body = f"{greeting}\n\nI thought you might find this interesting:\n\n{summary}\n\nRead more: {url}"
            else:
                body = f"{greeting}\n\n{body}"
            
            return {"subject": subject, "body": body}
            
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return self._fallback_email(title, summary, url, greeting)
    
    def _fallback_email(self, title: str, summary: str, url: str, greeting: str) -> dict:
        """Fallback email template"""
        return {
            "subject": f"Interesting AI News: {title}",
            "body": f"""{greeting}

I wanted to share this interesting AI news with you:

{title}

{summary}

Read the full article here: {url}

Best regards"""
        }
    
    async def generate_whatsapp_message(
        self,
        title: str,
        summary: str,
        url: str
    ) -> str:
        """Generate a WhatsApp message for sharing"""
        # WhatsApp messages should be concise
        truncated = summary[:100] + "..." if len(summary) > 100 else summary
        
        return f"""🤖 *{title}*

{truncated}

👉 {url}"""
    
    async def extract_key_insights(self, text: str) -> list:
        """Extract key insights from article text"""
        if not self.client:
            return []
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract 3-5 key insights from the AI news. Return as a bullet list."
                    },
                    {
                        "role": "user",
                        "content": text[:3000]
                    }
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            content = response.choices[0].message.content.strip()
            # Parse bullet points
            insights = [
                line.lstrip('•-* ').strip()
                for line in content.split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            
            return insights[:5]
            
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return []
