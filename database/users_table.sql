-- ============================
-- USERS TABLE (MAIN ACCOUNTS)
-- ============================
-- Guidance Management Reporting System
-- For Supabase PostgreSQL
-- Admin-only creation, ID-based usernames, Auto-generated 6-digit password

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable moddatetime extension for auto-updating timestamps
CREATE EXTENSION IF NOT EXISTS "moddatetime";

-- Users table (Main Accounts)
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_by ON users(created_by);

-- Row Level Security (RLS) Policies
-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users policies
-- Only Admin can insert new users
CREATE POLICY "Admin can create users"
    ON users FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Users can view their own profile
CREATE POLICY "Users can view own data"
    ON users FOR SELECT
    USING (
        id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (id = auth.uid());

-- Admin can view/manage all users
CREATE POLICY "Admin can manage all users"
    ON users
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Auto-update timestamp for users table using moddatetime
CREATE TRIGGER update_users_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW 
    EXECUTE FUNCTION moddatetime(updated_at);

