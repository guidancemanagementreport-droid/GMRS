-- ============================
-- GUIDANCE MANAGEMENT REPORTING SYSTEM
-- COMPLETE DATABASE SCHEMA
-- ============================
-- For Supabase PostgreSQL
-- Run this file in Supabase SQL Editor to create the complete database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable moddatetime extension for auto-updating timestamps
CREATE EXTENSION IF NOT EXISTS "moddatetime";

-- ============================
-- USERS TABLE (MAIN ACCOUNTS)
-- ============================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identification fields
    user_id VARCHAR(50) NOT NULL UNIQUE,     -- student/teacher/counselor/admin ID
    email VARCHAR(255) UNIQUE,             -- optional (some may not use email)
    role VARCHAR(20) NOT NULL 
        CHECK (role IN ('student', 'teacher', 'counselor', 'admin')),
    
    -- Auth fields
    username VARCHAR(100) NOT NULL UNIQUE,  -- based on user_id
    password_hash TEXT NOT NULL,           -- bcrypt or pbkdf2 hashed password
    is_active BOOLEAN NOT NULL DEFAULT TRUE, -- soft disable instead of delete
    
    -- Profile fields
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    middle_name VARCHAR(150),
    contact_number VARCHAR(20),
    gender VARCHAR(20),
    birthdate DATE,
    department VARCHAR(255),
    year_level VARCHAR(50),                -- for students
    position VARCHAR(255),                 -- for teachers/counselors/admins
    address TEXT,
    specialization TEXT,
    
    -- System metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,                       -- admin ID who created the account
    
    -- Foreign keys
    CONSTRAINT fk_created_by
        FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE SET NULL
);

-- ============================
-- REPORTS TABLE
-- ============================
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_review', 'resolved', 'closed')),
    reported_by TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    student_id TEXT,
    tracking_code TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- CASES TABLE
-- ============================
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES reports(id) ON DELETE SET NULL,
    student_id UUID REFERENCES users(id) ON DELETE SET NULL,
    counselor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'closed', 'resolved')),
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- CASE NOTES TABLE
-- ============================
CREATE TABLE IF NOT EXISTS case_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    counselor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    student_id UUID REFERENCES users(id) ON DELETE SET NULL,
    note TEXT NOT NULL,
    note_type TEXT DEFAULT 'general' CHECK (note_type IN ('general', 'session', 'followup', 'other')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- COUNSELING REQUESTS TABLE
-- ============================
CREATE TABLE IF NOT EXISTS counseling_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    preferred_date DATE,
    urgency TEXT DEFAULT 'normal' CHECK (urgency IN ('low', 'normal', 'high', 'urgent')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'scheduled', 'completed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- GUIDANCE REQUESTS TABLE (for guests/applicants)
-- ============================
CREATE TABLE IF NOT EXISTS guidance_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    request_type TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- NOTIFICATIONS TABLE
-- ============================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info' CHECK (type IN ('info', 'warning', 'error', 'success')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- RESOURCES TABLE
-- ============================
CREATE TABLE IF NOT EXISTS resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    resource_type TEXT CHECK (resource_type IN ('document', 'link', 'video', 'other')),
    file_url TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- EXAM SCHEDULE TABLE
-- ============================
CREATE TABLE IF NOT EXISTS exam_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_name TEXT NOT NULL,
    exam_date DATE NOT NULL,
    exam_time TIME,
    location TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- SYSTEM SETTINGS TABLE
-- ============================
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- ANALYTICS LOGS TABLE
-- ============================
CREATE TABLE IF NOT EXISTS analytics_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================
-- INDEXES FOR PERFORMANCE
-- ============================
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_by ON users(created_by);
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_tracking_code ON reports(tracking_code);
CREATE INDEX IF NOT EXISTS idx_cases_counselor_id ON cases(counselor_id);
CREATE INDEX IF NOT EXISTS idx_cases_student_id ON cases(student_id);
CREATE INDEX IF NOT EXISTS idx_case_notes_case_id ON case_notes(case_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_counseling_requests_user_id ON counseling_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_guidance_requests_user_id ON guidance_requests(user_id);

-- ============================
-- ROW LEVEL SECURITY (RLS)
-- ============================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE counseling_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE guidance_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_logs ENABLE ROW LEVEL SECURITY;

-- ============================
-- USERS TABLE RLS POLICIES
-- ============================
-- Allow login queries (anon role can read for authentication)
CREATE POLICY "Allow login queries"
    ON users FOR SELECT
    TO anon
    USING (TRUE);

-- Allow authenticated users to view their own profile
CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    TO authenticated
    USING (id::text = auth.uid()::text);

-- Allow authenticated users to update their own profile
CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    TO authenticated
    USING (id::text = auth.uid()::text);

-- Helper function to check if user is admin (avoids recursion)
CREATE OR REPLACE FUNCTION is_admin(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM users
        WHERE id = user_uuid AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Allow admins to view all users
CREATE POLICY "Admins can view all users"
    ON users FOR SELECT
    TO authenticated
    USING (is_admin(auth.uid()));

-- Allow admins to manage all users
CREATE POLICY "Admins can manage all users"
    ON users
    FOR ALL
    TO authenticated
    USING (is_admin(auth.uid()));

-- ============================
-- REPORTS TABLE RLS POLICIES
-- ============================
CREATE POLICY "Users can view their own reports"
    ON reports FOR SELECT
    USING (user_id = auth.uid() OR is_anonymous = TRUE);

CREATE POLICY "Users can create reports"
    ON reports FOR INSERT
    WITH CHECK (user_id = auth.uid() OR is_anonymous = TRUE);

CREATE POLICY "Teachers and counselors can view all reports"
    ON reports FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role IN ('teacher', 'counselor', 'admin')
        )
    );

-- ============================
-- CASES TABLE RLS POLICIES
-- ============================
CREATE POLICY "Counselors can view assigned cases"
    ON cases FOR SELECT
    USING (
        counselor_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role IN ('admin', 'teacher')
        )
    );

-- ============================
-- NOTIFICATIONS TABLE RLS POLICIES
-- ============================
CREATE POLICY "Users can view their own notifications"
    ON notifications FOR SELECT
    USING (user_id = auth.uid());

-- ============================
-- RESOURCES TABLE RLS POLICIES
-- ============================
CREATE POLICY "Anyone can view resources"
    ON resources FOR SELECT
    USING (TRUE);

CREATE POLICY "Counselors and admins can create resources"
    ON resources FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role IN ('counselor', 'admin')
        )
    );

-- ============================
-- EXAM SCHEDULE TABLE RLS POLICIES
-- ============================
CREATE POLICY "Anyone can view exam schedule"
    ON exam_schedule FOR SELECT
    USING (TRUE);

-- ============================
-- SYSTEM SETTINGS TABLE RLS POLICIES
-- ============================
CREATE POLICY "Admins can manage settings"
    ON system_settings FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================
-- FUNCTIONS FOR UPDATED_AT TIMESTAMPS
-- ============================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================
-- TRIGGERS FOR AUTO-UPDATE TIMESTAMPS
-- ============================
-- Users table uses moddatetime
CREATE TRIGGER update_users_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW 
    EXECUTE FUNCTION moddatetime(updated_at);

-- Other tables use custom function
CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_counseling_requests_updated_at BEFORE UPDATE ON counseling_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_guidance_requests_updated_at BEFORE UPDATE ON guidance_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exam_schedule_updated_at BEFORE UPDATE ON exam_schedule
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
