import asyncio
import uuid
from asyncio import Semaphore
from typing import List, Dict
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal
from models.all_models import BatchJob, CampaignPost
from services.openai_service import openai_service

class BatchGenerationService:
    def __init__(self):
        # Concurrency limits for OpenAI API calls.
        # DALL-E 3 often has stricter rate limits, so its concurrency is lower.
        self.caption_concurrent = 10
        self.image_concurrent = 5

    async def process_single_post(self, post_data: Dict, campaign_id: uuid.UUID, batch_job_id: uuid.UUID,
                                  caption_semaphore: Semaphore, image_semaphore: Semaphore):
        """
        Processes a single post: creates a DB record, generates content concurrently,
        and updates the status in a single, isolated database session.
        """
        db = SessionLocal()
        post = None
        try:
            # 1. Create the post record to get an ID and set initial status
            post = CampaignPost(
                campaign_id=campaign_id,
                batch_job_id=batch_job_id,
                title=post_data.get('title'),
                topic=post_data.get('topic'),
                brief=post_data.get('brief'),
                generation_status='generating',
            )
            db.add(post)
            db.commit()
            db.refresh(post)

            # 2. Generate content in parallel, relying on the service's retry logic
            async def get_caption():
                async with caption_semaphore:
                    return await openai_service.generate_caption(post_data)

            async def get_image():
                async with image_semaphore:
                    return await openai_service.generate_image(post_data)

            results = await asyncio.gather(get_caption(), get_image(), return_exceptions=True)
            caption_result, image_result = results

            # 3. Process results and update the post object
            is_success = True
            if isinstance(caption_result, Exception):
                is_success = False
                post.caption = f"Caption generation failed: {caption_result}"
                print(f"Error generating caption for post '{post.title}': {caption_result}")
            else:
                post.caption = caption_result

            if isinstance(image_result, Exception):
                is_success = False
                post.image_url = None
                print(f"Error generating image for post '{post.title}': {image_result}")
            else:
                post.image_url = image_result

            # 4. Finalize status and update batch job counters in one transaction
            if is_success:
                post.generation_status = 'completed'
                db.query(BatchJob).filter(BatchJob.id == batch_job_id).update(
                    {'completed_posts': BatchJob.completed_posts + 1}, synchronize_session=False
                )
            else:
                post.generation_status = 'failed'
                db.query(BatchJob).filter(BatchJob.id == batch_job_id).update(
                    {'failed_posts': BatchJob.failed_posts + 1}, synchronize_session=False
                )
            db.commit()
        except SQLAlchemyError as e:
            print(f"Database error processing post '{post_data.get('title')}': {e}")
            db.rollback()
        except Exception as e:
            print(f"Unexpected error processing post '{post_data.get('title')}': {e}")
            if post and db.is_active:
                db.rollback()
                post.generation_status = 'failed'
                db.query(BatchJob).filter(BatchJob.id == batch_job_id).update(
                    {'failed_posts': BatchJob.failed_posts + 1}, synchronize_session=False
                )
                db.commit()
        finally:
            db.close()

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
                    post_data, batch_job.campaign_id, batch_job.id,
                    caption_semaphore, image_semaphore,
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