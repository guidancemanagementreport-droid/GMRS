from flask import Blueprint, request, jsonify, render_template, session, current_app
from app.utils.auth import require_auth, get_current_user

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@require_auth(roles=['student'])
def dashboard():
    user = get_current_user()
    supabase = request.app.supabase
    
    # Get user's reports
    reports = supabase.table('reports').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
    
    # Get counseling requests
    counseling = supabase.table('counseling_requests').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
    
    # Get notifications
    notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).limit(10).execute()
    
    return render_template('student/dashboard.html',
                         reports=reports.data if reports.data else [],
                         counseling=counseling.data if counseling.data else [],
                         notifications=notifications.data if notifications.data else [])

@student_bp.route('/submit-report', methods=['GET', 'POST'])
@require_auth(roles=['student'])
def submit_report():
    if request.method == 'GET':
        return render_template('student/submit_report.html')
    
    user = get_current_user()
    data = request.get_json()
    
    try:
        supabase = current_app.supabase
        report = supabase.table('reports').insert({
            'user_id': user['id'],
            'title': data.get('title'),
            'description': data.get('description'),
            'category': data.get('category'),
            'status': 'pending',
            'reported_by': 'student'
        }).execute()
        
        return jsonify({'success': True, 'report': report.data[0] if report.data else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@student_bp.route('/report-status')
@require_auth(roles=['student'])
def report_status():
    user = get_current_user()
    supabase = request.app.supabase
    reports = supabase.table('reports').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
    return render_template('student/report_status.html', reports=reports.data if reports.data else [])

@student_bp.route('/request-counseling', methods=['GET', 'POST'])
@require_auth(roles=['student'])
def request_counseling():
    if request.method == 'GET':
        return render_template('student/request_counseling.html')
    
    user = get_current_user()
    data = request.get_json()
    
    try:
        supabase = current_app.supabase
        request_data = supabase.table('counseling_requests').insert({
            'user_id': user['id'],
            'reason': data.get('reason'),
            'preferred_date': data.get('preferred_date'),
            'urgency': data.get('urgency', 'normal'),
            'status': 'pending'
        }).execute()
        
        return jsonify({'success': True, 'request': request_data.data[0] if request_data.data else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@student_bp.route('/counseling-status')
@require_auth(roles=['student'])
def counseling_status():
    user = get_current_user()
    supabase = request.app.supabase
    requests = supabase.table('counseling_requests').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
    return render_template('student/counseling_status.html', requests=requests.data if requests.data else [])

@student_bp.route('/profile', methods=['GET', 'POST'])
@require_auth(roles=['student'])
def profile():
    user = get_current_user()
    supabase = request.app.supabase
    
    if request.method == 'GET':
        user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
        return render_template('student/profile.html', user_data=user_data.data if user_data.data else {})
    
    data = request.get_json()
    supabase.table('users').update({
        'full_name': data.get('full_name'),
        'phone': data.get('phone'),
        'student_id': data.get('student_id')
    }).eq('id', user['id']).execute()
    
    return jsonify({'success': True})

