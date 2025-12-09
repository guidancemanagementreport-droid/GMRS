from flask import Blueprint, request, jsonify, render_template, session, current_app, redirect, url_for
from app.utils.auth import require_auth, get_current_user

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
@require_auth(roles=['teacher'])
def dashboard():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    try:
        reports = supabase.table('reports').select('*, users(first_name, last_name, email)').order('created_at', desc=True).limit(20).execute()
        reports_data = reports.data if reports.data else []
    except:
        reports_data = []
    
    try:
        notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).limit(10).execute()
        notifications_data = notifications.data if notifications.data else []
    except:
        notifications_data = []
    
    return render_template('teacher/dashboard.html',
                         reports=reports_data,
                         notifications=notifications_data)

@teacher_bp.route('/reports')
@require_auth(roles=['teacher'])
def review_reports():
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        reports = supabase.table('reports').select('*, users(first_name, last_name, email)').execute()
        reports_data = reports.data if reports.data else []
    except:
        reports_data = []
    return render_template('teacher/reports.html', reports=reports_data)

@teacher_bp.route('/submit-incident', methods=['GET', 'POST'])
@require_auth(roles=['teacher'])
def submit_incident():
    if request.method == 'GET':
        return render_template('teacher/submit_incident.html')
    
    user = get_current_user()
    data = request.get_json()
    
    try:
        supabase = current_app.supabase
        report = supabase.table('reports').insert({
            'user_id': user['id'],
            'title': data.get('title'),
            'description': data.get('description'),
            'category': data.get('category'),
            'student_id': data.get('student_id'),
            'status': 'pending',
            'reported_by': 'teacher'
        }).execute()
        
        return jsonify({'success': True, 'report': report.data[0] if report.data else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@teacher_bp.route('/communication-tools')
@require_auth(roles=['teacher'])
def communication_tools():
    return render_template('teacher/communication_tools.html')

@teacher_bp.route('/notifications')
@require_auth(roles=['teacher'])
def notifications():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
    return render_template('teacher/notifications.html', notifications=notifications.data if notifications.data else [])

@teacher_bp.route('/monitor-case-program')
@require_auth(roles=['teacher'])
def monitor_case_program():
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        cases = supabase.table('cases').select('*, reports(*), users(first_name, last_name)').execute()
        cases_data = cases.data if cases.data else []
    except:
        cases_data = []
    return render_template('teacher/cases.html', cases=cases_data)

@teacher_bp.route('/cases')
@require_auth(roles=['teacher'])
def monitor_cases():
    # Redirect to monitor-case-program for consistency
    return redirect(url_for('teacher.monitor_case_program'))

@teacher_bp.route('/profile', methods=['GET', 'POST'])
@require_auth(roles=['teacher'])
def profile():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        try:
            user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
            user_data_dict = user_data.data if user_data.data else {}
        except:
            user_data_dict = {}
        return render_template('teacher/profile.html', user_data=user_data_dict)
    
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
    
    try:
        supabase.table('users').update(update_data).eq('id', user['id']).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

