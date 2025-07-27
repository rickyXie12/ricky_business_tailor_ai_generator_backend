import asyncio
import uuid
from asyncio import Semaphore
from typing import List, Dict
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from database import SessionLocal
from models.all_models import BatchJob, CampaignPost
from services.openai_service import openai_service

class BatchGenerationService:
    def __init__(self):
        self.caption_concurrent = 3  # Lower concurrency for captions
        self.image_concurrent = 3

    async def process_single_post(self, db: Session, post_data: Dict, campaign_id: uuid.UUID, batch_job_id: uuid.UUID,
                                 caption_semaphore: Semaphore, image_semaphore: Semaphore):
        post = None
        try:
            post = CampaignPost(
                campaign_id=campaign_id,
                batch_job_id=batch_job_id,
                title=post_data.get('title'),
                topic=post_data.get('topic'),
                brief=post_data.get('brief'),
                generation_status='generating'
            )
            db.add(post)
            db.commit()
            db.refresh(post)

            # Caption generation (rate-limited, with retry and delay)
            caption = None
            async with caption_semaphore:
                for attempt in range(8):
                    try:
                        await asyncio.sleep(2)
                        caption = await openai_service.generate_caption(post_data)
                        break
                    except Exception as e:
                        if "RateLimitError" in str(type(e)) or "rate limit" in str(e).lower():
                            wait_time = min(90, 5 * (attempt + 1))
                            print(f"Rate limit hit for caption. Waiting {wait_time}s before retry...")
                            await asyncio.sleep(wait_time)
                        else:
                            raise
                if caption is None:
                    caption = "Caption generation failed after retries."

            # Image generation (low concurrency, with retry)
            image_url = None
            for attempt in range(6):
                try:
                    async with image_semaphore:
                        image_url = await openai_service.generate_image(post_data)
                    break
                except Exception as e:
                    if "RateLimitError" in str(type(e)) or "rate limit" in str(e).lower():
                        wait_time = min(60, 2 ** attempt)
                        print(f"Rate limit hit for image. Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
            if image_url is None:
                raise Exception("Image generation failed after retries.")

            post.caption = caption
            post.image_url = image_url
            post.generation_status = 'completed'
            db.commit()

            db.query(BatchJob).filter(BatchJob.id == batch_job_id).update(
                {'completed_posts': BatchJob.completed_posts + 1}, synchronize_session=False
            )
            db.commit()

        except Exception as e:
            print(f"Error processing post '{post_data.get('title')}': {str(e)}")
            if post:
                post.generation_status = 'failed'
                db.commit()

            db.query(BatchJob).filter(BatchJob.id == batch_job_id).update(
                {'failed_posts': BatchJob.failed_posts + 1}, synchronize_session=False
            )
            db.commit()

    async def process_batch(self, batch_job_id: uuid.UUID, posts_data: List[Dict]):
        db = SessionLocal()
        try:
            batch_job = db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
            if not batch_job:
                print(f"Error: Batch job {batch_job_id} not found.")
                return

            batch_job.status = "processing"
            batch_job.started_at = datetime.now(timezone.utc)
            db.commit()

            caption_semaphore = Semaphore(self.caption_concurrent)
            image_semaphore = Semaphore(self.image_concurrent)

            async def task_wrapper(post_data: Dict):
                await self.process_single_post(
                    db, post_data, batch_job.campaign_id, batch_job.id,
                    caption_semaphore, image_semaphore
                )

            print(f"Starting batch generation for {len(posts_data)} posts...")
            await asyncio.gather(*[task_wrapper(post) for post in posts_data])

            db.refresh(batch_job)

            if batch_job.failed_posts > 0:
                batch_job.status = "completed_w_errors"
            else:
                batch_job.status = "completed"
            batch_job.completed_at = datetime.now(timezone.utc)
            db.commit()

            print(f"Batch job {batch_job_id} completed. Success: {batch_job.completed_posts}, Failed: {batch_job.failed_posts}")

        finally:
            db.close()