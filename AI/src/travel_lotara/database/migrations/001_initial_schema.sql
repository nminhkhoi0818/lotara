-- ============================================
-- Travel Lotara Database Schema
-- Supabase PostgreSQL Migrations
-- ============================================
-- 
-- Run this SQL in your Supabase SQL Editor:
-- 1. Go to Supabase Dashboard
-- 2. Select your project
-- 3. Navigate to SQL Editor
-- 4. Paste and run this script
--
-- For free tier optimization:
-- - Using JSONB for flexible schemas
-- - Indexes on frequently queried columns
-- - Soft deletes where appropriate
-- ============================================


-- ============================================
-- EXTENSIONS
-- ============================================
-- Enable UUID generation (usually enabled by default)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ============================================
-- SESSIONS TABLE (create first - referenced by jobs)
-- ============================================
-- Stores conversation context
CREATE TABLE IF NOT EXISTS public.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    
    -- Session state
    is_active BOOLEAN DEFAULT TRUE,
    context JSONB DEFAULT '{}',
    
    -- Conversation history (limited for free tier)
    messages JSONB DEFAULT '[]',
    
    -- Captured preferences
    captured_preferences JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON public.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON public.sessions(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON public.sessions(last_activity_at DESC);


-- ============================================
-- JOBS TABLE
-- ============================================
-- Stores workflow execution records
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    session_id UUID REFERENCES public.sessions(id) ON DELETE SET NULL,
    
    -- Job configuration
    mode TEXT NOT NULL DEFAULT 'reactive' CHECK (mode IN ('reactive', 'proactive')),
    status TEXT NOT NULL DEFAULT 'started' CHECK (status IN (
        'started', 'planning', 'executing', 'waiting_approval', 
        'completed', 'failed', 'cancelled'
    )),
    query TEXT,
    constraints JSONB DEFAULT '{}',
    trigger_context JSONB,
    
    -- Execution state
    current_state TEXT DEFAULT 'monitoring',
    tasks JSONB DEFAULT '[]',
    
    -- Outputs
    partial_outputs JSONB DEFAULT '{}',
    final_result JSONB,
    
    -- Error tracking
    error JSONB,
    
    -- Observability
    opik_trace_id TEXT,
    opik_trace_url TEXT,
    
    -- Human-in-the-loop
    awaiting_approval BOOLEAN DEFAULT FALSE,
    approval_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Indexes for jobs
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON public.jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON public.jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_user_status ON public.jobs(user_id, status);


-- ============================================
-- FEEDBACK TABLE
-- ============================================
-- Stores user ratings and comments
CREATE TABLE IF NOT EXISTS public.feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    
    -- Feedback content
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    helpful_aspects JSONB DEFAULT '[]',
    improvement_areas JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one feedback per job
    UNIQUE(job_id)
);

-- Indexes for feedback
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON public.feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON public.feedback(rating);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON public.feedback(created_at DESC);


-- ============================================
-- USER PREFERENCES TABLE
-- ============================================
-- Stores persistent user preferences
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL UNIQUE,
    
    -- Travel preferences
    preferred_destinations JSONB DEFAULT '[]',
    budget_range JSONB,  -- {min: 0, max: 5000}
    travel_style TEXT,   -- luxury, budget, adventure, etc.
    dietary_restrictions JSONB DEFAULT '[]',
    accessibility_needs JSONB DEFAULT '[]',
    
    -- Communication preferences
    preferred_language TEXT DEFAULT 'en',
    notification_settings JSONB DEFAULT '{"price_alerts": true, "trip_reminders": true, "proactive_suggestions": true}',
    
    -- Historical data
    past_destinations JSONB DEFAULT '[]',
    favorite_activities JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for user preferences
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON public.user_preferences(user_id);


-- ============================================
-- ITINERARIES TABLE
-- ============================================
-- Stores saved/booked travel itineraries
CREATE TABLE IF NOT EXISTS public.itineraries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    
    -- Itinerary details
    title TEXT NOT NULL,
    destination TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    
    -- Full itinerary data
    itinerary_data JSONB DEFAULT '{}',
    
    -- Status
    is_booked BOOLEAN DEFAULT FALSE,
    booking_references JSONB DEFAULT '[]',
    
    -- Costs
    estimated_total_cost DECIMAL(10, 2),
    currency TEXT DEFAULT 'USD',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for itineraries
CREATE INDEX IF NOT EXISTS idx_itineraries_user_id ON public.itineraries(user_id);
CREATE INDEX IF NOT EXISTS idx_itineraries_destination ON public.itineraries(destination);
CREATE INDEX IF NOT EXISTS idx_itineraries_dates ON public.itineraries(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_itineraries_booked ON public.itineraries(user_id, is_booked);


-- ============================================
-- HEALTH CHECK TABLE (for connectivity tests)
-- ============================================
CREATE TABLE IF NOT EXISTS public.health_check (
    id SERIAL PRIMARY KEY,
    status TEXT DEFAULT 'ok',
    checked_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert initial health check record
INSERT INTO public.health_check (status) VALUES ('ok') ON CONFLICT DO NOTHING;


-- ============================================
-- UPDATED_AT TRIGGER FUNCTION
-- ============================================
-- Automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================
-- APPLY TRIGGERS
-- ============================================
-- Jobs table
DROP TRIGGER IF EXISTS update_jobs_updated_at ON public.jobs;
CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON public.jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Sessions table
DROP TRIGGER IF EXISTS update_sessions_updated_at ON public.sessions;
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON public.sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- User preferences table
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON public.user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Itineraries table
DROP TRIGGER IF EXISTS update_itineraries_updated_at ON public.itineraries;
CREATE TRIGGER update_itineraries_updated_at
    BEFORE UPDATE ON public.itineraries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================
-- Enable RLS on all tables
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.itineraries ENABLE ROW LEVEL SECURITY;

-- Note: For MVP with service role key, RLS policies are bypassed.
-- Add proper RLS policies when implementing user authentication:
--
-- Example policy (uncomment and modify as needed):
-- CREATE POLICY "Users can view own jobs"
--     ON public.jobs FOR SELECT
--     USING (auth.uid()::text = user_id);
--
-- CREATE POLICY "Users can insert own jobs"
--     ON public.jobs FOR INSERT
--     WITH CHECK (auth.uid()::text = user_id);


-- ============================================
-- SERVICE ROLE ACCESS
-- ============================================
-- Grant full access to service role (for backend API)
-- This allows bypassing RLS when using the service role key
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;


-- ============================================
-- ANON ROLE ACCESS (for authenticated users)
-- ============================================
-- Grant limited access to anon role
GRANT SELECT, INSERT, UPDATE ON public.jobs TO anon;
GRANT SELECT, INSERT, UPDATE ON public.sessions TO anon;
GRANT SELECT, INSERT ON public.feedback TO anon;
GRANT SELECT, INSERT, UPDATE ON public.user_preferences TO anon;
GRANT SELECT, INSERT, UPDATE ON public.itineraries TO anon;
GRANT SELECT ON public.health_check TO anon;


-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Get user's recent jobs with pagination
CREATE OR REPLACE FUNCTION get_user_jobs(
    p_user_id TEXT,
    p_limit INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0,
    p_status TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    status TEXT,
    mode TEXT,
    query TEXT,
    created_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    final_result JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        j.id,
        j.status,
        j.mode,
        j.query,
        j.created_at,
        j.completed_at,
        j.final_result
    FROM public.jobs j
    WHERE j.user_id = p_user_id
        AND (p_status IS NULL OR j.status = p_status)
    ORDER BY j.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Get user statistics
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id TEXT)
RETURNS TABLE (
    total_jobs BIGINT,
    completed_jobs BIGINT,
    avg_rating NUMERIC,
    total_itineraries BIGINT,
    booked_itineraries BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM public.jobs WHERE user_id = p_user_id),
        (SELECT COUNT(*) FROM public.jobs WHERE user_id = p_user_id AND status = 'completed'),
        (SELECT COALESCE(AVG(rating), 0) FROM public.feedback WHERE user_id = p_user_id),
        (SELECT COUNT(*) FROM public.itineraries WHERE user_id = p_user_id),
        (SELECT COUNT(*) FROM public.itineraries WHERE user_id = p_user_id AND is_booked = TRUE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Cleanup old sessions (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_sessions(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.sessions
    WHERE is_active = FALSE
        AND last_activity_at < NOW() - (days_old || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ============================================
-- SUCCESS MESSAGE
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✓ Travel Lotara database schema created successfully!';
    RAISE NOTICE 'Tables created: jobs, sessions, feedback, user_preferences, itineraries, health_check';
    RAISE NOTICE 'Remember to set up RLS policies for production use.';
END $$;
