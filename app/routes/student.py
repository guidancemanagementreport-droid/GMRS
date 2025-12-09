from flask import Blueprint, request, jsonify, render_template, session, current_app
from app.utils.auth import require_auth, get_current_user

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@require_auth(roles=['student'])
def dashboard():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    # Get user's reports
    try:
        reports = supabase.table('reports').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
        reports_data = reports.data if reports.data else []
    except:
        reports_data = []
    
    # Get counseling requests
    try:
        counseling = supabase.table('counseling_requests').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
        counseling_data = counseling.data if counseling.data else []
    except:
        counseling_data = []
    
    # Get notifications
    try:
        notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).limit(10).execute()
        notifications_data = notifications.data if notifications.data else []
    except:
        notifications_data = []
    
    return render_template('student/dashboard.html',
                         reports=reports_data,
                         counseling=counseling_data,
                         notifications=notifications_data)

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
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        reports = supabase.table('reports').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
        reports_data = reports.data if reports.data else []
    except:
        reports_data = []
    return render_template('student/report_status.html', reports=reports_data)

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
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        requests = supabase.table('counseling_requests').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
        requests_data = requests.data if requests.data else []
    except:
        requests_data = []
    return render_template('student/counseling_status.html', requests=requests_data)

@student_bp.route('/help-support')
@require_auth(roles=['student'])
def help_support():
    return render_template('student/help_support.html')

@student_bp.route('/notifications')
@require_auth(roles=['student'])
def notifications():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
    return render_template('student/notifications.html', notifications=notifications.data if notifications.data else [])

@student_bp.route('/resources')
@require_auth(roles=['student'])
def resources():
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        resources_data = supabase.table('resources').select('*').order('created_at', desc=True).execute()
        resources_list = resources_data.data if resources_data.data else []
    except Exception as e:
        print(f"Error fetching resources: {e}")
        # If table doesn't exist or there's an error, return empty list
        resources_list = []
    
    return render_template('student/resources.html', resources=resources_list)

@student_bp.route('/profile', methods=['GET', 'POST'])
@require_auth(roles=['student'])
def profile():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
        return render_template('student/profile.html', user_data=user_data.data if user_data.data else {})
    
    data = request.get_json()
    supabase.table('users').update({
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'contact_number': data.get('contact_number'),
        'year_level': data.get('year_level')
    }).eq('id', user['id']).execute()
    
    return jsonify({'success': True})

