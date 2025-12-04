from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, current_app
from app.utils.auth import get_current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        supabase = current_app.supabase
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if auth_response.user:
            # Get user role from users table
            user = supabase.table('users').select('*').eq('id', auth_response.user.id).single().execute()
            
            session['user_id'] = auth_response.user.id
            session['user_role'] = user.data.get('role') if user.data else 'student'
            session['access_token'] = auth_response.session.access_token
            
            # Redirect based on role
            role = session['user_role']
            redirect_map = {
                'student': '/student/dashboard',
                'guest': '/guest/dashboard',
                'teacher': '/teacher/dashboard',
                'counselor': '/counselor/dashboard',
                'admin': '/admin/dashboard'
            }
            
            return jsonify({
                'success': True,
                'redirect': redirect_map.get(role, '/')
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 401
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    role = data.get('role', 'student')
    
    if not email or not password or not full_name:
        return jsonify({'error': 'All fields required'}), 400
    
    try:
        supabase = current_app.supabase
        # Create auth user
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password
        })
        
        if auth_response.user:
            # Create user record
            supabase.table('users').insert({
                'id': auth_response.user.id,
                'email': email,
                'full_name': full_name,
                'role': role
            }).execute()
            
            return jsonify({'success': True, 'message': 'Registration successful'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify({'error': 'Registration failed'}), 400

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

