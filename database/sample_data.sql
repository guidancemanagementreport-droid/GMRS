-- Sample Data for Testing
-- Run this after creating the schema

-- Insert sample users (Note: These require actual Supabase auth users first)
-- You'll need to create auth users in Supabase Auth, then update these IDs

-- Sample system settings
INSERT INTO system_settings (key, value, description) VALUES
('site_name', 'Guidance Management Reporting System', 'Name of the application'),
('maintenance_mode', 'false', 'Enable/disable maintenance mode'),
('max_file_size', '10', 'Maximum file upload size in MB')
ON CONFLICT (key) DO NOTHING;

-- Sample exam schedule
INSERT INTO exam_schedule (exam_name, exam_date, exam_time, location, description) VALUES
('Midterm Exams', '2024-03-15', '09:00:00', 'Main Hall', 'Midterm examination period'),
('Final Exams', '2024-06-10', '09:00:00', 'Main Hall', 'Final examination period'),
('Entrance Exam', '2024-04-20', '08:00:00', 'Auditorium', 'College entrance examination')
ON CONFLICT DO NOTHING;

-- Sample resources
INSERT INTO resources (title, description, resource_type) VALUES
('Academic Support Guide', 'Comprehensive guide for academic support services', 'document'),
('Career Planning Resources', 'Resources for career planning and exploration', 'link'),
('Mental Health Support', 'Information about mental health resources', 'document'),
('College Application Tips', 'Tips and guidelines for college applications', 'document')
ON CONFLICT DO NOTHING;

-- Note: To create sample users, reports, and cases:
-- 1. First create users through Supabase Auth
-- 2. Then insert corresponding records in the users table
-- 3. Then create reports and cases linked to those users

