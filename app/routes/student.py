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
        reports = supabase.table('student_reports').select('*').eq('student_id', user['id']).order('created_at', desc=True).execute()
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
    
    import random
    import string
    
    user = get_current_user()
    data = request.get_json()
    
    # Generate unique tracking code (8 characters: 2 letters + 6 digits)
    def generate_tracking_code():
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        numbers = ''.join(random.choices(string.digits, k=6))
        return f"{letters}{numbers}"
    
    try:
        supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
        
        # Generate unique tracking code
        tracking_code = generate_tracking_code()
        max_attempts = 10
        attempts = 0
        
        # Ensure tracking code is unique
        while attempts < max_attempts:
            existing = supabase.table('student_reports').select('tracking_code').eq('tracking_code', tracking_code).execute()
            if not existing.data:
                break
            tracking_code = generate_tracking_code()
            attempts += 1
        
        # Prepare report data
        report_data = {
            'student_id': user['id'],
            'report_type': data.get('report_type', 'General'),
            'category': data.get('category'),
            'subject': data.get('subject', data.get('title', '')),
            'description': data.get('description'),
            'incident_location': data.get('incident_location'),
            'incident_date': data.get('incident_date'),
            'persons_involved': data.get('persons_involved'),
            'tracking_code': tracking_code,
            'status': 'Submitted',
            'stage': 'Teacher Review',  # Automatically goes to teacher review
            'priority': data.get('priority', 'Normal')
        }
        
        # Add attachments if provided
        if data.get('attachments'):
            report_data['attachments'] = data.get('attachments')
        
        # Insert report
        report = supabase.table('student_reports').insert(report_data).execute()
        
        if report.data:
            return jsonify({
                'success': True, 
                'report': report.data[0],
                'tracking_code': tracking_code
            })
        else:
            return jsonify({'error': 'Failed to create report'}), 400
            
    except Exception as e:
        import traceback
        print(f"Error submitting report: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@student_bp.route('/report-status')
@require_auth(roles=['student'])
def report_status():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        reports = supabase.table('student_reports').select('*').eq('student_id', user['id']).order('created_at', desc=True).execute()
        reports_data = reports.data if reports.data else []
        
        # Get counselor cases and recommendations for each report
        for report in reports_data:
            try:
                counselor_case = supabase.table('counselor_cases').select('*').eq('report_id', report['id']).order('created_at', desc=True).limit(1).execute()
                report['counselor_case'] = counselor_case.data[0] if counselor_case.data else None
            except:
                report['counselor_case'] = None
    except:
        reports_data = []
    return render_template('student/report_status.html', reports=reports_data)

@student_bp.route('/request-counseling', methods=['GET', 'POST'])
@require_auth(roles=['student'])
def request_counseling():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        # Get confirmed reports that allow counseling requests
        try:
            confirmed_reports = supabase.table('student_reports').select(
                '*, counselor_cases!inner(status)'
            ).eq('student_id', user['id']).eq('counselor_cases.status', 'Confirmed').execute()
            confirmed_reports_data = confirmed_reports.data if confirmed_reports.data else []
        except:
            confirmed_reports_data = []
        
        return render_template('student/request_counseling.html', confirmed_reports=confirmed_reports_data)
    
    data = request.get_json()
    report_id = data.get('report_id')
    
    # Verify that the report is confirmed by counselor
    try:
        counselor_case = supabase.table('counselor_cases').select('*').eq('report_id', report_id).eq('status', 'Confirmed').single().execute()
        if not counselor_case.data:
            return jsonify({'error': 'This report must be confirmed by a counselor before requesting counseling'}), 400
    except:
        return jsonify({'error': 'Invalid report or report not confirmed'}), 400
    
    try:
        request_data = supabase.table('counseling_requests').insert({
            'user_id': user['id'],
            'report_id': report_id,  # Link to the confirmed report
            'reason': data.get('reason'),
            'preferred_date': data.get('preferred_date'),
            'urgency': data.get('urgency', 'normal'),
            'status': 'pending'
        }).execute()
        
        return jsonify({'success': True, 'request': request_data.data[0] if request_data.data else None})
    except Exception as e:
        import traceback
        print(f"Error creating counseling request: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@student_bp.route('/counseling-status')
@require_auth(roles=['student'])
def counseling_status():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        requests = supabase.table('counseling_requests').select(
            '*, student_reports(tracking_code, subject)'
        ).eq('user_id', user['id']).order('created_at', desc=True).execute()
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

