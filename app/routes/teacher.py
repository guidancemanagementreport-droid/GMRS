from flask import Blueprint, request, jsonify, render_template, session, current_app, redirect, url_for
from app.utils.auth import require_auth, get_current_user

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
@require_auth(roles=['teacher'])
def dashboard():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    # Get pending reports count (reports in Teacher Review stage)
    pending_reports_count = 0
    try:
        pending_reports = supabase.table('student_reports').select('id', count='exact').eq('stage', 'Teacher Review').execute()
        pending_reports_count = pending_reports.count if hasattr(pending_reports, 'count') else len(pending_reports.data) if pending_reports.data else 0
    except:
        pending_reports_count = 0
    
    # Get recent reports for display
    try:
        reports = supabase.table('student_reports').select(
            '*, users!student_reports_student_id_fkey(first_name, last_name)'
        ).eq('stage', 'Teacher Review').order('created_at', desc=True).limit(5).execute()
        reports_data = reports.data if reports.data else []
    except:
        reports_data = []
    
    try:
        notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).limit(10).execute()
        notifications_data = notifications.data if notifications.data else []
    except:
        notifications_data = []
    
    return render_template('teacher/dashboard.html',
                         pending_reports_count=pending_reports_count,
                         reports=reports_data,
                         notifications=notifications_data)

@teacher_bp.route('/reports')
@require_auth(roles=['teacher'])
def review_reports():
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        # Get all student reports that are in Teacher Review stage
        reports = supabase.table('student_reports').select(
            '*, users!student_reports_student_id_fkey(first_name, last_name, email, user_id)'
        ).eq('stage', 'Teacher Review').order('created_at', desc=True).execute()
        reports_data = reports.data if reports.data else []
        
        # Get existing teacher reviews for these reports
        for report in reports_data:
            try:
                review = supabase.table('teacher_reviews').select('*').eq('report_id', report['id']).order('created_at', desc=True).limit(1).execute()
                report['teacher_review'] = review.data[0] if review.data else None
            except:
                report['teacher_review'] = None
    except Exception as e:
        import traceback
        print(f"Error fetching reports: {str(e)}\n{traceback.format_exc()}")
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

@teacher_bp.route('/reports/<report_id>/review', methods=['GET', 'POST'])
@require_auth(roles=['teacher'])
def review_report_detail(report_id):
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        try:
            # Get the report with student info
            report = supabase.table('student_reports').select(
                '*, users!student_reports_student_id_fkey(first_name, last_name, email, user_id)'
            ).eq('id', report_id).single().execute()
            report_data = report.data if report.data else None
            
            # Get existing teacher review if any
            try:
                review = supabase.table('teacher_reviews').select('*').eq('report_id', report_id).eq('teacher_id', user['id']).order('created_at', desc=True).limit(1).execute()
                review_data = review.data[0] if review.data else None
            except:
                review_data = None
            
            return render_template('teacher/review_report.html', 
                                 report=report_data, 
                                 review=review_data)
        except Exception as e:
            import traceback
            print(f"Error fetching report: {str(e)}\n{traceback.format_exc()}")
            return redirect(url_for('teacher.review_reports'))
    
    # POST - Submit review
    data = request.get_json()
    user = get_current_user()
    
    try:
        # Check if review already exists
        existing_review = supabase.table('teacher_reviews').select('id').eq('report_id', report_id).eq('teacher_id', user['id']).execute()
        
        review_data = {
            'report_id': report_id,
            'teacher_id': user['id'],
            'notes': data.get('notes', ''),
            'action_taken': data.get('action_taken'),
            'recommendation': data.get('recommendation'),
            'status': data.get('status', 'Reviewed')
        }
        
        if existing_review.data:
            # Update existing review
            result = supabase.table('teacher_reviews').update(review_data).eq('id', existing_review.data[0]['id']).execute()
        else:
            # Create new review
            result = supabase.table('teacher_reviews').insert(review_data).execute()
        
        # If forwarding to counselor, update the report status
        if data.get('status') == 'Forwarded to Counselor':
            supabase.table('student_reports').update({
                'stage': 'Counselor Review',
                'status': 'Under Review'
            }).eq('id', report_id).execute()
        else:
            # Update report status based on teacher review
            supabase.table('student_reports').update({
                'status': 'Under Review',
                'teacher_id': user['id']
            }).eq('id', report_id).execute()
        
        return jsonify({'success': True, 'message': 'Review submitted successfully'})
    except Exception as e:
        import traceback
        print(f"Error submitting review: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

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

