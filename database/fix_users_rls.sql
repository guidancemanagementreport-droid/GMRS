-- ============================
-- FIX USERS TABLE RLS POLICIES
-- ============================
-- This fixes the infinite recursion issue in RLS policies
-- Run this in Supabase SQL Editor after creating the users table

-- Drop existing policies that cause recursion
DROP POLICY IF EXISTS "Admin can create users" ON users;
DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Admin can manage all users" ON users;
DROP POLICY IF EXISTS "Allow login queries" ON users;

-- IMPORTANT: For login to work, we need to allow anon role to read users
-- OR use service role key in your Flask app
-- This policy allows reading users for login authentication
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

-- Allow admins to view all users (using a function to avoid recursion)
CREATE OR REPLACE FUNCTION is_admin(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM users
        WHERE id = user_uuid AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

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

