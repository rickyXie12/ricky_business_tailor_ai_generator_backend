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
        self.max_concurrent = 5

    async def process_single_post(
        self, 
        db: Session,  # The single DB session is now passed in
        post_data: Dict, 
        campaign_id: uuid.UUID, 
        batch_job_id: uuid.UUID
    ):
        """
        Processes a single post using the shared database session.
        """
        post = None
        try:
            # 1. Create the post record
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

            # 2. Generate content concurrently
            caption_task = openai_service.generate_caption(post_data)
            image_task = openai_service.generate_image(post_data)
            results = await asyncio.gather(caption_task, image_task, return_exceptions=True)
            caption_result, image_result = results

            # 3. Process results and update the post object
            caption_failed = isinstance(caption_result, Exception)
            image_failed = isinstance(image_result, Exception)

            if caption_failed:
                post.caption = f"Caption generation failed: {caption_result}"
                print(f"Error generating caption for post '{post.title}': {caption_result}")
            else:
                post.caption = caption_result

            if image_failed:
                # Use a placeholder URL on failure for a better frontend experience
                post.image_url = "https://via.placeholder.com/1024x1024.png?text=Image+Generation+Failed"
                print(f"Error generating image for post '{post.title}': {image_result}")
            else:
                post.image_url = image_result
            
            # 4. Finalize status and update batch job counters atomically
            if caption_failed or image_failed:
                post.generation_status = 'failed'
                db.query(BatchJob).filter(BatchJob.id == batch_job_id).update(
                    {'failed_posts': BatchJob.failed_posts + 1}, synchronize_session=False
                )
            else:
                post.generation_status = 'completed'
                db.query(BatchJob).filter(BatchJob.id == batch_job_id).update(
                    {'completed_posts': BatchJob.completed_posts + 1}, synchronize_session=False
                )
            db.commit()

        except Exception as e:
            # This block catches ANY exception during the process, including DB errors (SQLAlchemyError).
            print(f"An error occurred while processing post '{post_data.get('title')}': {e}")
            if db.is_active:
                db.rollback()

            # If the post was created in the DB, mark it as failed and store the error.
            if post and post.id:
                post.generation_status = 'failed'
                post.caption = f"Post processing failed: {str(e)[:500]}"

            # CRITICAL: No matter the error, increment the failed counter.
            # This ensures progress tracking is always accurate.
            db.query(BatchJob).filter(BatchJob.id == batch_job_id).update(
                {'failed_posts': BatchJob.failed_posts + 1}, synchronize_session=False
            )
            db.commit()

    async def process_batch(self, batch_job_id: uuid.UUID, posts_data: List[Dict]):
        """
        Main batch processing function. Manages a SINGLE database session for all tasks.
        """
        db = SessionLocal() # Create ONE session for the entire batch
        try:
            batch_job = db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
            if not batch_job:
                print(f"Error: Batch job {batch_job_id} not found.")
                return

            batch_job.status = "processing"
            batch_job.started_at = datetime.now(timezone.utc)
            db.commit()

            semaphore = Semaphore(self.max_concurrent)

            async def task_wrapper(post_data: Dict):
                async with semaphore:
                    # Pass the single DB session to the processing function
                    await self.process_single_post(db, post_data, batch_job.campaign_id, batch_job.id)

            print(f"Starting batch generation for {len(posts_data)} posts with a concurrency of {self.max_concurrent}...")
            await asyncio.gather(*[task_wrapper(post) for post in posts_data])

            # Refresh the job object to get the final counts after all tasks are done
            db.refresh(batch_job)

            if batch_job.failed_posts > 0:
                batch_job.status = "failed"
            else:
                batch_job.status = "completed"
            batch_job.completed_at = datetime.now(timezone.utc)
            db.commit()

            print(f"Batch job {batch_job_id} completed. Success: {batch_job.completed_posts}, Failed: {batch_job.failed_posts}")

        finally:
            db.close() # IMPORTANT: Close the single session when the batch is finished
