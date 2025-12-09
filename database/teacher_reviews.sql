-- ============================
-- TEACHER REVIEWS TABLE
-- ============================
-- This table stores teacher reviews and feedback on student reports
-- Run this in Supabase SQL Editor after student_reports table exists

-- First, add stage column to student_reports table
ALTER TABLE student_reports
ADD COLUMN IF NOT EXISTS stage VARCHAR(50) DEFAULT 'Teacher Review'
    CHECK (stage IN (
        'Teacher Review', 
        'Counselor Review', 
        'Resolved', 
        'Closed'
    ));

-- Create teacher_reviews table
CREATE TABLE IF NOT EXISTS teacher_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    report_id UUID NOT NULL,      -- linked to student_reports
    teacher_id UUID NOT NULL,     -- teacher reviewing the report

    notes TEXT NOT NULL,          -- teacher's feedback/comments
    action_taken TEXT,            -- optional actions performed
    recommendation VARCHAR(255),  -- e.g. "Forward to counselor", "Monitor", etc.

    status VARCHAR(50) DEFAULT 'Reviewed'
        CHECK (status IN ('Reviewed', 'Monitoring', 'Forwarded to Counselor')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_report
        FOREIGN KEY (report_id)
        REFERENCES student_reports(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- Auto-update timestamp trigger
CREATE TRIGGER update_teacher_reviews_timestamp
BEFORE UPDATE ON teacher_reviews
FOR EACH ROW
EXECUTE FUNCTION moddatetime(updated_at);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_teacher_reviews_report_id ON teacher_reviews(report_id);
CREATE INDEX IF NOT EXISTS idx_teacher_reviews_teacher_id ON teacher_reviews(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_reviews_status ON teacher_reviews(status);
CREATE INDEX IF NOT EXISTS idx_student_reports_stage ON student_reports(stage);

-- Enable Row Level Security
ALTER TABLE teacher_reviews ENABLE ROW LEVEL SECURITY;

-- ============================
-- TRIGGER: Auto-move to Counselor Review when Teacher Forwards
-- ============================
CREATE OR REPLACE FUNCTION move_to_counselor_stage()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'Forwarded to Counselor' THEN
        UPDATE student_reports
        SET stage = 'Counselor Review',
            status = 'Under Review',
            counselor_id = (
                SELECT id FROM users 
                WHERE role = 'counselor' 
                LIMIT 1
            )
        WHERE id = NEW.report_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for INSERT (when teacher creates review with Forwarded status)
CREATE TRIGGER trg_teacher_forward_insert
AFTER INSERT ON teacher_reviews
FOR EACH ROW
WHEN (NEW.status = 'Forwarded to Counselor')
EXECUTE FUNCTION move_to_counselor_stage();

-- Trigger for UPDATE (when teacher updates review to Forwarded status)
CREATE TRIGGER trg_teacher_forward_update
AFTER UPDATE ON teacher_reviews
FOR EACH ROW
WHEN (NEW.status = 'Forwarded to Counselor' AND (OLD.status IS NULL OR OLD.status != 'Forwarded to Counselor'))
EXECUTE FUNCTION move_to_counselor_stage();

-- ============================
-- RLS POLICIES
-- ============================
-- Note: Since we use custom authentication with Flask sessions,
-- most operations use the service_role key which bypasses RLS.
-- These policies are for additional security when using anon key.

-- Allow service role full access (for backend operations with Flask)
CREATE POLICY "service_role_full_access_teacher_reviews"
ON teacher_reviews
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Allow anon role to insert (for backend operations)
CREATE POLICY "allow_insert_teacher_reviews"
ON teacher_reviews
FOR INSERT
TO anon
WITH CHECK (true);

-- Allow anon role to select (for backend operations)
CREATE POLICY "allow_select_teacher_reviews"
ON teacher_reviews
FOR SELECT
TO anon
USING (true);

-- Allow anon role to update (for backend operations)
CREATE POLICY "allow_update_teacher_reviews"
ON teacher_reviews
FOR UPDATE
TO anon
USING (true)
WITH CHECK (true);

