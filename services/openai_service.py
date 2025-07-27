import asyncio
import openai
import os
import random
from typing import Dict

class OpenAIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.max_retries = 4  # Lowered for speed

    async def generate_caption(self, campaign_data: Dict) -> str:
        prompt = f"""
        Create an engaging Instagram caption for the brand '{campaign_data['brand_name']}'.
        Topic: {campaign_data.get('topic', 'General brand content')}
        Key message or brief: {campaign_data.get('brief', '')}
        Target Audience: {campaign_data.get('target_audience', 'a general audience')}
        Required Tone: {campaign_data['tone']}
        
        Requirements:
        - The caption must be under 2000 characters.
        - It must include 5 to 8 relevant hashtags.
        - It must include 2-4 appropriate emojis.
        - It must end with a clear call-to-action.
        - Do NOT include quotation marks around the final caption.
        """
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=os.getenv("OPENAI_CAPTION_MODEL", "gpt-4o-mini"),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,  # Lowered for speed
                    temperature=0.4
                )
                await asyncio.sleep(0.5)  # Add a small delay after success
                return response.choices[0].message.content.strip()
            except openai.RateLimitError as e:
                base = 2 ** attempt
                jitter = random.uniform(0, 1)
                wait_time = min(60, base + jitter)
                print(f"Rate limit hit for caption. Retrying in {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                print(f"Caption generation failed: {e}")
                raise
        raise Exception("Caption generation failed after retries.")

    async def generate_image(self, campaign_data: Dict) -> str:
        image_prompt = f"""
        A professional, high-quality, vibrant Instagram post image for the brand '{campaign_data['brand_name']}'.
        The image should visually represent the topic: '{campaign_data.get('topic', 'Brand content')}'
        The style should be {campaign_data['tone']} and visually appealing to {campaign_data.get('target_audience', 'a general audience')}.
        Brief: {campaign_data.get('brief', '')}
        Key elements to include: High quality, 1:1 aspect ratio. No text on the image.
        """
        for attempt in range(self.max_retries):
            try:
                response = await self.client.images.generate(
                    model=os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3"),
                    prompt=image_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                await asyncio.sleep(1)  # Add a small delay after success
                return response.data[0].url
            except openai.RateLimitError as e:
                base = 2 ** attempt
                jitter = random.uniform(0, 2)
                wait_time = min(90, base + jitter)
                print(f"Rate limit hit for image. Retrying in {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                print(f"Image generation failed: {e}")
                raise
        raise Exception("Image generation failed after retries.")

# Global instance to be used across the application
openai_service = OpenAIService()