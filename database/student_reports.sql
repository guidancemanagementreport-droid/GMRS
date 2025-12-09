-- ============================
-- STUDENT REPORTS TABLE
-- ============================
-- This table stores all reports submitted by students
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS student_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Linked to student account
    student_id UUID NOT NULL,
    
    -- Basic report details
    report_type VARCHAR(100) NOT NULL,   -- e.g., bullying, harassment, academic concern, etc.
    category VARCHAR(100),               -- optional category
    subject VARCHAR(255),                -- short title
    description TEXT NOT NULL,           -- full description
    
    -- Optional details
    incident_location VARCHAR(255),
    incident_date DATE,
    persons_involved TEXT,               -- comma-separated or JSON list
    attachments TEXT[],                  -- array of file paths stored in Supabase Storage
    
    -- Tracking details
    tracking_code VARCHAR(20) NOT NULL UNIQUE, -- auto-generated code given to student
    status VARCHAR(50) DEFAULT 'Submitted'
        CHECK (status IN ('Submitted', 'Under Review', 'In Progress', 'Resolved', 'Closed')),
    
    -- Internal processing
    counselor_id UUID,                   -- assigned counselor
    teacher_id UUID,                     -- optional reviewer
    priority VARCHAR(20) DEFAULT 'Normal'
        CHECK (priority IN ('Low', 'Normal', 'High', 'Critical')),
    
    -- Workflow stage
    stage VARCHAR(50) DEFAULT 'Teacher Review'
        CHECK (stage IN (
            'Teacher Review', 
            'Counselor Review', 
            'Resolved', 
            'Closed'
        )),
    
    -- System metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign keys
    CONSTRAINT fk_student
        FOREIGN KEY (student_id) 
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_counselor
        FOREIGN KEY (counselor_id)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- Auto-update timestamp trigger
CREATE TRIGGER update_student_reports_timestamp
BEFORE UPDATE ON student_reports
FOR EACH ROW
EXECUTE FUNCTION moddatetime(updated_at);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_student_reports_student_id ON student_reports(student_id);
CREATE INDEX IF NOT EXISTS idx_student_reports_status ON student_reports(status);
CREATE INDEX IF NOT EXISTS idx_student_reports_tracking_code ON student_reports(tracking_code);
CREATE INDEX IF NOT EXISTS idx_student_reports_counselor_id ON student_reports(counselor_id);
CREATE INDEX IF NOT EXISTS idx_student_reports_created_at ON student_reports(created_at);

-- Enable Row Level Security
ALTER TABLE student_reports ENABLE ROW LEVEL SECURITY;

-- ============================
-- RLS POLICIES
-- ============================
-- Note: Since we use custom authentication with Flask sessions,
-- most operations use the service_role key which bypasses RLS.
-- These policies are for additional security when using anon key.

-- Allow service role full access (for backend operations with Flask)
CREATE POLICY "service_role_full_access"
ON student_reports
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Allow anon role to insert (for backend operations)
-- This allows the Flask app to insert reports when using anon key
CREATE POLICY "allow_insert_reports"
ON student_reports
FOR INSERT
TO anon
WITH CHECK (true);

-- Allow anon role to select (for backend operations)
-- This allows the Flask app to query reports when using anon key
CREATE POLICY "allow_select_reports"
ON student_reports
FOR SELECT
TO anon
USING (true);

-- Allow anon role to update (for backend operations)
-- This allows the Flask app to update reports when using anon key
CREATE POLICY "allow_update_reports"
ON student_reports
FOR UPDATE
TO anon
USING (true)
WITH CHECK (true);

