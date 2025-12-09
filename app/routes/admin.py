from flask import Blueprint, request, jsonify, render_template, session, current_app
from app.utils.auth import require_auth, get_current_user
from app.utils.auth import require_auth, get_current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@require_auth(roles=['admin'])
def dashboard():
    # Use admin client to bypass RLS for admin operations
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    # Initialize default values
    users_count = 0
    reports_count = 0
    cases_count = 0
    recent_reports = []
    recent_users = []
    
    # Get statistics with error handling
    try:
        users_result = supabase.table('users').select('id', count='exact').execute()
        users_count = users_result.count if hasattr(users_result, 'count') else 0
    except Exception as e:
        print(f"Error getting users count: {str(e)}")
        users_count = 0
    
    try:
        reports_result = supabase.table('reports').select('id', count='exact').execute()
        reports_count = reports_result.count if hasattr(reports_result, 'count') else 0
    except Exception as e:
        print(f"Error getting reports count: {str(e)}")
        reports_count = 0
    
    try:
        cases_result = supabase.table('cases').select('id', count='exact').execute()
        cases_count = cases_result.count if hasattr(cases_result, 'count') else 0
    except Exception as e:
        print(f"Error getting cases count: {str(e)}")
        cases_count = 0
    
    # Get recent activity with error handling
    try:
        recent_reports_result = supabase.table('reports').select('*').order('created_at', desc=True).limit(10).execute()
        recent_reports = recent_reports_result.data if recent_reports_result.data else []
    except Exception as e:
        print(f"Error getting recent reports: {str(e)}")
        recent_reports = []
    
    try:
        recent_users_result = supabase.table('users').select('*').order('created_at', desc=True).limit(10).execute()
        recent_users = recent_users_result.data if recent_users_result.data else []
    except Exception as e:
        print(f"Error getting recent users: {str(e)}")
        recent_users = []
    
    return render_template('admin/dashboard.html',
                         users_count=users_count,
                         reports_count=reports_count,
                         cases_count=cases_count,
                         recent_reports=recent_reports,
                         recent_users=recent_users)

@admin_bp.route('/users')
@require_auth(roles=['admin'])
def manage_users():
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    users = supabase.table('users').select('*').order('created_at', desc=True).execute()
    return render_template('admin/users.html', users=users.data if users.data else [])

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@require_auth(roles=['admin'])
def create_user():
    if request.method == 'GET':
        return render_template('admin/create_user.html')
    
    import random
    import string
    import bcrypt
    
    data = request.get_json()
    email = data.get('email')
    full_name = data.get('full_name', '').strip()
    role = data.get('role', 'student')
    id_number = data.get('id_number', '').strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    if not full_name:
        return jsonify({'error': 'Full name is required'}), 400
    
    # Parse full name into first_name and last_name
    name_parts = full_name.split(maxsplit=1)
    first_name = name_parts[0] if len(name_parts) > 0 else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    # Generate user_id if not provided
    if not id_number:
        if role == 'student':
            id_number = email.split('@')[0].upper()
        elif role == 'teacher':
            id_number = f"T{random.randint(1000, 9999)}"
        elif role == 'counselor':
            id_number = f"C{random.randint(1000, 9999)}"
        elif role == 'admin':
            id_number = f"ADMIN{random.randint(100, 999)}"
    
    # Generate username (based on user_id)
    username = id_number.lower()
    
    # Ensure username is unique - check if it exists and append number if needed
    try:
        supabase_check = getattr(current_app, 'supabase_admin', None) or current_app.supabase
        existing_user = supabase_check.table('users').select('username').eq('username', username).execute()
        if existing_user.data:
            # Username exists, append random number
            username = f"{id_number.lower()}{random.randint(100, 999)}"
    except:
        pass  # If check fails, proceed with original username
    
    # Generate 6-digit random password
    password = ''.join(random.choices(string.digits, k=6))
    
    # Hash password using bcrypt
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        # Use admin client (service role) to bypass RLS
        supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
        
        # Get current admin user for created_by field
        current_user = get_current_user()
        created_by = current_user.get('id') if current_user else None
        
        # Create user record in users table
        user_data = {
            'user_id': id_number,
            'email': email,
            'role': role,
            'username': username,
            'password_hash': password_hash,
            'first_name': first_name,
            'last_name': last_name,
            'is_active': True,
            'created_by': created_by
        }
        
        # Add role-specific fields
        if role == 'student':
            user_data['year_level'] = data.get('year_level', '')
        elif role in ['teacher', 'counselor', 'admin']:
            user_data['position'] = data.get('position', f'{role.title()} Position')
        
        # Insert user
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            new_user = result.data[0]
            return jsonify({
                'success': True,
                'user_id': new_user.get('id'),
                'email': email,
                'username': username,
                'password': password,
                'message': 'User created successfully'
            })
        else:
            return jsonify({'error': 'Failed to create user record'}), 400
            
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error creating user: {error_msg}\n{traceback.format_exc()}")
        return jsonify({'error': f'Failed to create user: {error_msg}'}), 400

@admin_bp.route('/users/<user_id>', methods=['PUT', 'DELETE'])
@require_auth(roles=['admin'])
def user_actions(user_id):
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'PUT':
        data = request.get_json()
        update_data = {}
        
        # Handle full_name split into first_name and last_name
        if 'full_name' in data:
            full_name = data.get('full_name', '').strip()
            name_parts = full_name.split(maxsplit=1)
            update_data['first_name'] = name_parts[0] if len(name_parts) > 0 else ''
            update_data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
        
        if 'first_name' in data:
            update_data['first_name'] = data.get('first_name')
        if 'last_name' in data:
            update_data['last_name'] = data.get('last_name')
        if 'email' in data:
            update_data['email'] = data.get('email')
        if 'role' in data:
            update_data['role'] = data.get('role')
        if 'contact_number' in data:
            update_data['contact_number'] = data.get('contact_number')
        if 'is_active' in data:
            update_data['is_active'] = data.get('is_active')
        
        supabase.table('users').update(update_data).eq('id', user_id).execute()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        supabase.table('users').update({'is_active': False}).eq('id', user_id).execute()
        return jsonify({'success': True})

@admin_bp.route('/analytics')
@require_auth(roles=['admin'])
def analytics():
    supabase = current_app.supabase
    
    # Get all reports
    all_reports = supabase.table('reports').select('*').execute()
    reports_data = all_reports.data if all_reports.data else []
    
    # Get all cases
    all_cases = supabase.table('cases').select('*').execute()
    cases_data = all_cases.data if all_cases.data else []
    
    # Calculate statistics
    stats = {
        'total_reports': len(reports_data),
        'pending_reports': len([r for r in reports_data if r.get('status') == 'pending']),
        'resolved_reports': len([r for r in reports_data if r.get('status') == 'resolved']),
        'total_cases': len(cases_data),
        'active_cases': len([c for c in cases_data if c.get('status') == 'active']),
        'closed_cases': len([c for c in cases_data if c.get('status') == 'closed'])
    }
    
    return render_template('admin/analytics.html', stats=stats)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@require_auth(roles=['admin'])
def settings():
    supabase = current_app.supabase
    
    if request.method == 'GET':
        settings_data = supabase.table('system_settings').select('*').execute()
        settings_dict = {s['key']: s['value'] for s in (settings_data.data or [])}
        return render_template('admin/settings.html', settings=settings_dict)
    
    data = request.get_json()
    for key, value in data.items():
        supabase.table('system_settings').upsert({
            'key': key,
            'value': value
        }).execute()
    
    return jsonify({'success': True})

@admin_bp.route('/backup')
@require_auth(roles=['admin'])
def backup():
    return render_template('admin/backup.html')

@admin_bp.route('/security')
@require_auth(roles=['admin'])
def security():
    supabase = current_app.supabase
    # Get access logs
    logs = supabase.table('analytics_logs').select('*').order('created_at', desc=True).limit(100).execute()
    return render_template('admin/security.html', logs=logs.data if logs.data else [])

@admin_bp.route('/profile', methods=['GET', 'POST'])
@require_auth(roles=['admin'])
def profile():
    user = get_current_user()
    supabase = current_app.supabase
    
    if request.method == 'GET':
        user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
        return render_template('admin/profile.html', user_data=user_data.data if user_data.data else {})
    
    data = request.get_json()
    update_data = {}
    
    # Handle full_name split into first_name and last_name
    if 'full_name' in data:
        full_name = data.get('full_name', '').strip()
        name_parts = full_name.split(maxsplit=1)
        update_data['first_name'] = name_parts[0] if len(name_parts) > 0 else ''
        update_data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
    
    if 'first_name' in data:
        update_data['first_name'] = data.get('first_name')
    if 'last_name' in data:
        update_data['last_name'] = data.get('last_name')
    if 'contact_number' in data:
        update_data['contact_number'] = data.get('contact_number')
    
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    supabase.table('users').update(update_data).eq('id', user['id']).execute()
    
    return jsonify({'success': True})

