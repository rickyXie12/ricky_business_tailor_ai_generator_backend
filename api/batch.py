import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from models.all_models import BatchJob, Campaign, CampaignPost
from schemas.main import BatchGenerationRequest
from services.batch_service import BatchGenerationService
from api.campaigns import get_current_user_id

router = APIRouter(tags=["Batch Generation"])

@router.post("/campaigns/{campaign_id}/generate-batch")
async def start_batch_generation(
    campaign_id: uuid.UUID,
    batch_request: BatchGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.user_id == user_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or access denied")

    new_batch_job = BatchJob(
        user_id=user_id,
        campaign_id=campaign_id,
        name=batch_request.name,
        total_posts=len(batch_request.posts),
        status='pending',
        started_at=datetime.now(timezone.utc)  # Track start time
    )
    db.add(new_batch_job)
    db.commit()
    db.refresh(new_batch_job)

    batch_service = BatchGenerationService()
    background_tasks.add_task(
        batch_service.process_batch,
        batch_job_id=new_batch_job.id,
        posts_data=[p.dict() for p in batch_request.posts]
    )
    return {"message": "Batch generation started.", "job_id": new_batch_job.id}


@router.get("/batch-jobs/{job_id}/status")
def get_batch_status(job_id: uuid.UUID, db: Session = Depends(get_db)):
    batch_job = db.query(BatchJob).filter(BatchJob.id == job_id).first()
    if not batch_job:
        raise HTTPException(status_code=404, detail="Batch job not found")

    percentage = 0
    if batch_job.total_posts > 0:
        percentage = ((batch_job.completed_posts + batch_job.failed_posts) / batch_job.total_posts) * 100

    # Calculate elapsed time
    started_at = batch_job.started_at
    completed_at = batch_job.completed_at
    now = datetime.now(timezone.utc)
    elapsed = None
    if started_at:
        if completed_at:
            elapsed = (completed_at - started_at).total_seconds()
        else:
            elapsed = (now - started_at).total_seconds()

    return {
        'id': str(batch_job.id),
        'status': batch_job.status,
        'progress': {
            'total': batch_job.total_posts,
            'completed': batch_job.completed_posts,
            'failed': batch_job.failed_posts,
            'percentage': round(percentage, 1)
        },
        'started_at': started_at.isoformat() if started_at else None,
        'completed_at': completed_at.isoformat() if completed_at else None,
        'elapsed_seconds': round(elapsed, 2) if elapsed is not None else None
    }

@router.get("/batch-jobs/{job_id}/results")
def get_batch_results(job_id: uuid.UUID, db: Session = Depends(get_db)):
    posts = db.query(CampaignPost).filter(CampaignPost.batch_job_id == job_id).all()
    if not posts:
        raise HTTPException(status_code=404, detail="No posts found for this job or job does not exist.")

    return [{
        "id": str(post.id),
        "title": post.title,
        "caption": post.caption,
        "image_url": post.image_url,
        "status": post.generation_status
    } for post in posts]