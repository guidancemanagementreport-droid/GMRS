-- ============================
-- UPDATE COUNSELING_REQUESTS TABLE
-- ============================
-- Add report_id column to link counseling requests to confirmed reports
-- Add scheduled_date and update status values

-- Add report_id column if it doesn't exist
ALTER TABLE counseling_requests
ADD COLUMN IF NOT EXISTS report_id UUID REFERENCES student_reports(id) ON DELETE SET NULL;

-- Add scheduled_date column if it doesn't exist
ALTER TABLE counseling_requests
ADD COLUMN IF NOT EXISTS scheduled_date TIMESTAMP WITH TIME ZONE;

-- Update status check constraint to include new statuses
ALTER TABLE counseling_requests
DROP CONSTRAINT IF EXISTS counseling_requests_status_check;

ALTER TABLE counseling_requests
ADD CONSTRAINT counseling_requests_status_check
CHECK (status IN ('pending', 'approved', 'rescheduled', 'rejected', 'completed', 'cancelled'));

-- Create index for report_id
CREATE INDEX IF NOT EXISTS idx_counseling_requests_report_id ON counseling_requests(report_id);

