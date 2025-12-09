-- ============================
-- COUNSELOR CASES TABLE
-- ============================
-- This table stores counselor case records for student reports
-- Run this in Supabase SQL Editor after student_reports and teacher_reviews tables exist

-- First, add final_status column to student_reports table
ALTER TABLE student_reports
ADD COLUMN IF NOT EXISTS final_status VARCHAR(50) DEFAULT 'Pending'
    CHECK (final_status IN (
        'Pending',
        'In Process',
        'Waiting for Counselor',
        'Resolved',
        'Closed'
    ));

-- Create counselor_cases table
CREATE TABLE IF NOT EXISTS counselor_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    report_id UUID NOT NULL,      -- link to student_reports
    counselor_id UUID NOT NULL,   -- counselor handling the case

    summary TEXT,                 -- short assessment summary
    counselor_notes TEXT NOT NULL, -- counselor's full notes
    action_taken TEXT,            -- what actions were taken
    recommendation TEXT,          -- final advice or guidance
    meeting_date TIMESTAMP WITH TIME ZONE,     -- counseling session date
    follow_up_date TIMESTAMP WITH TIME ZONE,   -- optional

    status VARCHAR(50) DEFAULT 'In Review'
        CHECK (status IN (
            'In Review',
            'Processing',
            'Pending Meeting',
            'Confirmed',
            'Returned',
            'Resolved',
            'Settled',
            'Closed'
        )),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_report
        FOREIGN KEY (report_id)
        REFERENCES student_reports(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_counselor
        FOREIGN KEY (counselor_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- Auto-update timestamp trigger
CREATE TRIGGER update_counselor_cases_timestamp
BEFORE UPDATE ON counselor_cases
FOR EACH ROW
EXECUTE FUNCTION moddatetime(updated_at);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_counselor_cases_report_id ON counselor_cases(report_id);
CREATE INDEX IF NOT EXISTS idx_counselor_cases_counselor_id ON counselor_cases(counselor_id);
CREATE INDEX IF NOT EXISTS idx_counselor_cases_status ON counselor_cases(status);
CREATE INDEX IF NOT EXISTS idx_student_reports_final_status ON student_reports(final_status);

-- Enable Row Level Security
ALTER TABLE counselor_cases ENABLE ROW LEVEL SECURITY;

-- ============================
-- TRIGGER: Auto-update Student Report when Counselor Resolves/Closes
-- ============================
CREATE OR REPLACE FUNCTION update_report_final_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IN ('Resolved', 'Closed') THEN
        UPDATE student_reports
        SET 
            final_status = NEW.status,
            stage = 'Resolved',
            status = NEW.status
        WHERE id = NEW.report_id;
    ELSIF NEW.status = 'In Review' THEN
        UPDATE student_reports
        SET 
            final_status = 'In Process',
            status = 'Under Review'
        WHERE id = NEW.report_id;
    ELSIF NEW.status = 'Processing' THEN
        UPDATE student_reports
        SET 
            final_status = 'In Process',
            status = 'In Progress'
        WHERE id = NEW.report_id;
    ELSIF NEW.status = 'Pending Meeting' THEN
        UPDATE student_reports
        SET 
            final_status = 'In Process',
            status = 'Under Review'
        WHERE id = NEW.report_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for INSERT (when counselor creates case with Resolved/Closed status)
CREATE TRIGGER trg_counselor_status_insert
AFTER INSERT ON counselor_cases
FOR EACH ROW
WHEN (NEW.status IN ('Resolved', 'Closed'))
EXECUTE FUNCTION update_report_final_status();

-- Trigger for UPDATE (when counselor updates case to Resolved/Closed status)
CREATE TRIGGER trg_counselor_status_update
AFTER UPDATE ON counselor_cases
FOR EACH ROW
WHEN (NEW.status IN ('Resolved', 'Closed') AND (OLD.status IS NULL OR OLD.status NOT IN ('Resolved', 'Closed')))
EXECUTE FUNCTION update_report_final_status();

-- Trigger for status updates (In Review, Processing, Pending Meeting)
CREATE TRIGGER trg_counselor_status_intermediate
AFTER INSERT OR UPDATE ON counselor_cases
FOR EACH ROW
WHEN (NEW.status IN ('In Review', 'Processing', 'Pending Meeting'))
EXECUTE FUNCTION update_report_final_status();

-- Trigger for Confirmed status - allows student to request counseling
CREATE OR REPLACE FUNCTION update_report_confirmed()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'Confirmed' THEN
        UPDATE student_reports
        SET 
            final_status = 'In Process',
            status = 'Under Review'
        WHERE id = NEW.report_id;
    ELSIF NEW.status = 'Returned' THEN
        UPDATE student_reports
        SET 
            final_status = 'Pending',
            status = 'Submitted',
            stage = 'Teacher Review'
        WHERE id = NEW.report_id;
    ELSIF NEW.status = 'Settled' THEN
        UPDATE student_reports
        SET 
            final_status = 'Closed',
            stage = 'Closed',
            status = 'Closed'
        WHERE id = NEW.report_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_counselor_confirmed
AFTER INSERT OR UPDATE ON counselor_cases
FOR EACH ROW
WHEN (NEW.status IN ('Confirmed', 'Returned', 'Settled'))
EXECUTE FUNCTION update_report_confirmed();

-- ============================
-- RLS POLICIES
-- ============================
-- Note: Since we use custom authentication with Flask sessions,
-- most operations use the service_role key which bypasses RLS.
-- These policies are for additional security when using anon key.

-- Allow service role full access (for backend operations with Flask)
CREATE POLICY "service_role_full_access_counselor_cases"
ON counselor_cases
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Allow anon role to insert (for backend operations)
CREATE POLICY "allow_insert_counselor_cases"
ON counselor_cases
FOR INSERT
TO anon
WITH CHECK (true);

-- Allow anon role to select (for backend operations)
CREATE POLICY "allow_select_counselor_cases"
ON counselor_cases
FOR SELECT
TO anon
USING (true);

-- Allow anon role to update (for backend operations)
CREATE POLICY "allow_update_counselor_cases"
ON counselor_cases
FOR UPDATE
TO anon
USING (true)
WITH CHECK (true);

