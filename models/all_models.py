import uuid
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    campaigns = relationship("Campaign", back_populates="user")
    batch_jobs = relationship("BatchJob", back_populates="user")

class ContentTone(Base):
    __tablename__ = "content_tones"
    id = Column(String(20), primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    prompt_modifier = Column(Text)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    brand_name = Column(String(255), nullable=False)
    target_audience = Column(Text)
    tone_id = Column(String(20), ForeignKey('content_tones.id'), nullable=False)
    status = Column(String(20), default='draft')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="campaigns")
    posts = relationship("CampaignPost", back_populates="campaign", cascade="all, delete-orphan")

class BatchJob(Base):
    __tablename__ = "batch_jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id', ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    total_posts = Column(Integer, default=0)
    completed_posts = Column(Integer, default=0)
    failed_posts = Column(Integer, default=0)
    status = Column(String(20), default='pending', index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="batch_jobs")
    posts = relationship("CampaignPost", back_populates="batch_job", cascade="all, delete-orphan")

class CampaignPost(Base):
    __tablename__ = "campaign_posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id', ondelete="CASCADE"), nullable=False)
    batch_job_id = Column(UUID(as_uuid=True), ForeignKey('batch_jobs.id', ondelete="SET NULL"), index=True)
    title = Column(String(255))
    topic = Column(String(255))
    brief = Column(Text)
    caption = Column(Text)
    image_url = Column(String(500))
    generation_status = Column(String(20), default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    campaign = relationship("Campaign", back_populates="posts")
    batch_job = relationship("BatchJob", back_populates="posts")