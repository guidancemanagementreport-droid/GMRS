from flask import Blueprint, request, jsonify, render_template, session, current_app
from app.utils.auth import require_auth, get_current_user

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
@require_auth(roles=['teacher'])
def dashboard():
    user = get_current_user()
    supabase = request.app.supabase
    
    reports = supabase.table('reports').select('*, users(full_name, email)').order('created_at', desc=True).limit(20).execute()
    notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).limit(10).execute()
    
    return render_template('teacher/dashboard.html',
                         reports=reports.data if reports.data else [],
                         notifications=notifications.data if notifications.data else [])

@teacher_bp.route('/reports')
@require_auth(roles=['teacher'])
def review_reports():
    supabase = request.app.supabase
    reports = supabase.table('reports').select('*, users(full_name, email)').execute()
    return render_template('teacher/reports.html', reports=reports.data if reports.data else [])

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

@teacher_bp.route('/cases')
@require_auth(roles=['teacher'])
def monitor_cases():
    supabase = request.app.supabase
    cases = supabase.table('cases').select('*, reports(*), users(full_name)').execute()
    return render_template('teacher/cases.html', cases=cases.data if cases.data else [])

@teacher_bp.route('/profile', methods=['GET', 'POST'])
@require_auth(roles=['teacher'])
def profile():
    user = get_current_user()
    supabase = request.app.supabase
    
    if request.method == 'GET':
        user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
        return render_template('teacher/profile.html', user_data=user_data.data if user_data.data else {})
    
    data = request.get_json()
    supabase.table('users').update({
        'full_name': data.get('full_name'),
        'phone': data.get('phone')
    }).eq('id', user['id']).execute()
    
    return jsonify({'success': True})

