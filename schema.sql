-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users (simple auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content tones lookup
CREATE TABLE content_tones (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    prompt_modifier TEXT
);

-- Insert default tones
INSERT INTO content_tones (id, name, description, prompt_modifier) VALUES
('friendly', 'Friendly', 'Warm and approachable', 'Use warm, welcoming language'),
('casual', 'Casual', 'Relaxed and informal', 'Keep it conversational'),
('modern', 'Modern', 'Contemporary and innovative', 'Use trendy language'),
('professional', 'Professional', 'Formal and business-like', 'Maintain professional tone'),
('humorous', 'Humorous', 'Funny and entertaining', 'Add humor and playfulness');

-- Campaigns (organizing content)
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    brand_name VARCHAR(255) NOT NULL,
    target_audience TEXT,
    tone_id VARCHAR(20) NOT NULL REFERENCES content_tones(id),
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Batch jobs (track bulk operations) 
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    total_posts INTEGER NOT NULL DEFAULT 0,
    completed_posts INTEGER NOT NULL DEFAULT 0,
    failed_posts INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaign posts (individual content)
CREATE TABLE campaign_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    batch_job_id UUID REFERENCES batch_jobs(id) ON DELETE SET NULL,
    title VARCHAR(255),
    topic VARCHAR(255),
    brief TEXT,
    caption TEXT,
    image_url VARCHAR(500),
    generation_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_batch_jobs_status ON batch_jobs(status);
CREATE INDEX idx_campaign_posts_batch_job_id ON campaign_posts(batch_job_id);