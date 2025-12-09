from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, current_app
from app.utils.auth import get_current_user
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    data = request.get_json()
    username = data.get('username') or data.get('email')  # Support both for backward compatibility
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    try:
        # Use admin client (service role) for login queries to bypass RLS
        supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
        if not supabase:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Query user by username only
        try:
            print(f"Attempting to find user with username: {username}")  # Debug
            user_query = supabase.table('users').select('*').eq('username', username).eq('is_active', True).execute()
            print(f"Query result: {user_query.data if user_query else 'None'}")  # Debug
        except Exception as e:
            print(f"Database query error: {str(e)}")  # Debug
            return jsonify({'error': f'Database query failed: {str(e)}'}), 401
        
        if not user_query or not user_query.data or len(user_query.data) == 0:
            print(f"No user found with username: {username}")  # Debug
            return jsonify({'error': 'User not found or account is inactive'}), 401
        
        user_data = user_query.data[0]
        print(f"User found: {user_data.get('username')}, role: {user_data.get('role')}")  # Debug
        
        # Verify password using bcrypt
        password_hash = user_data.get('password_hash', '')
        if not password_hash:
            print("No password hash found for user")  # Debug
            return jsonify({'error': 'User account has no password set'}), 401
        
        try:
            # Check password - bcrypt.checkpw expects bytes
            print("Verifying password...")  # Debug
            password_valid = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            print(f"Password valid: {password_valid}")  # Debug
        except Exception as e:
            print(f"Password verification exception: {str(e)}")  # Debug
            return jsonify({'error': f'Password verification error: {str(e)}'}), 401
        
        if not password_valid:
            print("Password verification failed")  # Debug
            return jsonify({'error': 'Invalid password'}), 401
        
        # Set session data
        role = user_data.get('role', 'student')
        session['user_id'] = str(user_data.get('id'))
        session['user_role'] = role
        session['user_name'] = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or user_data.get('username', 'User')
        session['username'] = user_data.get('username', '')
        
        # Ensure session is saved
        session.permanent = True
        
        # Redirect based on role
        redirect_map = {
            'student': '/student/dashboard',
            'guest': '/guest/dashboard',
            'teacher': '/teacher/dashboard',
            'counselor': '/counselor/dashboard',
            'admin': '/admin/dashboard'
        }
        
        redirect_url = redirect_map.get(role, '/')
        print(f"Login successful for user: {user_data.get('username')}, role: {role}, redirecting to: {redirect_url}")  # Debug
        
        return jsonify({
            'success': True,
            'redirect': redirect_url,
            'role': role
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        trace = traceback.format_exc()
        print(f"Login error: {error_msg}\n{trace}")  # Log to console for debugging
        return jsonify({'error': f'Login failed: {error_msg}'}), 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

