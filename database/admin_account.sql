-- ============================
-- ADMIN ACCOUNT CREATION
-- ============================
-- Guidance Management Reporting System
-- For Supabase PostgreSQL
-- 
-- This file creates the initial admin account
-- Default credentials (CHANGE AFTER FIRST LOGIN):
-- Username: admin
-- Password: Admin123!
--
-- IMPORTANT: Change the password immediately after first login!

-- Insert admin account
INSERT INTO users (
    user_id,
    email,
    role,
    username,
    password_hash,
    is_active,
    first_name,
    last_name,
    contact_number,
    position,
    created_at,
    updated_at
) VALUES (
    'ADMIN001',                                    -- user_id
    'admin@gmrs.local',                           -- email (optional, can be changed)
    'admin',                                      -- role
    'admin',                                      -- username (based on user_id)
    '$2b$12$wn4DBh9UPwi3Qr8POvul5.K6SjusKIZeWAcTl7huqgkMxtW/aEhYK',  -- password_hash for "Admin123!" (bcrypt)
    TRUE,                                         -- is_active
    'System',                                     -- first_name
    'Administrator',                              -- last_name
    NULL,                                         -- contact_number (optional)
    'System Administrator',                       -- position
    NOW(),                                        -- created_at
    NOW()                                         -- updated_at
) ON CONFLICT (user_id) DO NOTHING;

-- Note: The password hash above is for "Admin123!"
-- To generate a new password hash, use bcrypt in your application:
-- from bcrypt import hashpw, gensalt
-- password_hash = hashpw(password.encode('utf-8'), gensalt()).decode()
--
-- Or use an online bcrypt generator:
-- https://bcrypt-generator.com/

