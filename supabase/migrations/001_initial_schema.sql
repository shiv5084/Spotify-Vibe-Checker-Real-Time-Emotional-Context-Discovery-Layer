-- =============================================
-- Users & Auth (managed by Supabase Auth)
-- =============================================

-- User Profiles
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    prompts_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Track Metadata (from Spotify Dataset)
-- =============================================

CREATE TABLE IF NOT EXISTS tracks (
    id TEXT PRIMARY KEY,                    -- Spotify track ID from dataset
    track_name TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    valence REAL,                          -- 0.0–1.0
    energy REAL,                           -- 0.0–1.0
    danceability REAL,                     -- 0.0–1.0
    tempo REAL,                            -- BPM
    acousticness REAL,                     -- 0.0–1.0
    instrumentalness REAL,                 -- 0.0–1.0
    loudness REAL,                         -- dB
    speechiness REAL,                      -- 0.0–1.0
    liveness REAL,                         -- 0.0–1.0
    mode INTEGER,                          -- 0 (minor) or 1 (major)
    duration_ms INTEGER,
    popularity INTEGER,                    -- 0–100
    track_genre TEXT,
    embedding_text TEXT,                   -- Generated description for embedding
    indexed_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Prompt History
-- =============================================

CREATE TABLE IF NOT EXISTS prompt_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    prompt_text TEXT NOT NULL,
    emotional_profile JSONB,              -- Extracted emotional profile
    queue_result JSONB,                   -- Generated Vibe Queue
    confidence REAL,                      -- LLM confidence score
    latency_ms INTEGER,                   -- End-to-end pipeline latency
    cache_hit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Audit Log (Pipeline Observability)
-- =============================================

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id TEXT NOT NULL,
    component TEXT NOT NULL,               -- input_processor | emotion_extraction | retrieval | ranking | assembler
    action TEXT NOT NULL,                  -- validate | extract | search | rank | assemble
    input_data JSONB,
    output_data JSONB,
    latency_ms INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Row Level Security
-- =============================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_history ENABLE ROW LEVEL SECURITY;

-- Drop policies if they already exist
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can view own prompt history" ON prompt_history;
DROP POLICY IF EXISTS "Users can insert own prompts" ON prompt_history;

-- Create RLS Policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own prompt history" ON prompt_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own prompts" ON prompt_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Tracks are publicly readable (no RLS needed)
-- Audit log is admin-only (default deny for non-admin)
