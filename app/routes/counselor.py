from flask import Blueprint, request, jsonify, render_template, session, current_app, redirect, url_for
from app.utils.auth import require_auth, get_current_user

counselor_bp = Blueprint('counselor', __name__)

@counselor_bp.route('/dashboard')
@require_auth(roles=['counselor'])
def dashboard():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    # Get assigned cases (reports in Counselor Review stage)
    try:
        cases = supabase.table('student_reports').select(
            '*, users!student_reports_student_id_fkey(first_name, last_name)'
        ).eq('stage', 'Counselor Review').order('created_at', desc=True).execute()
        cases_data = cases.data if cases.data else []
    except:
        cases_data = []
    
    # Get notifications
    try:
        notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).limit(10).execute()
        notifications_data = notifications.data if notifications.data else []
    except:
        notifications_data = []
    
    # Get statistics
    total_cases = len(cases_data)
    active_cases = len([c for c in cases_data if c.get('final_status') in ('Pending', 'In Process', 'Waiting for Counselor')])
    
    return render_template('counselor/dashboard.html',
                         cases=cases_data,
                         notifications=notifications_data,
                         total_cases=total_cases,
                         active_cases=active_cases)

@counselor_bp.route('/case-record')
@require_auth(roles=['counselor'])
def case_record():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        # Get all student reports in Counselor Review stage (forwarded by teachers)
        reports = supabase.table('student_reports').select(
            '*, users!student_reports_student_id_fkey(first_name, last_name, email, user_id), counselor_cases(*)'
        ).eq('stage', 'Counselor Review').order('created_at', desc=True).execute()
        reports_data = reports.data if reports.data else []
        
        # Get existing counselor cases for these reports
        for report in reports_data:
            try:
                case = supabase.table('counselor_cases').select('*').eq('report_id', report['id']).eq('counselor_id', user['id']).order('created_at', desc=True).limit(1).execute()
                report['counselor_case'] = case.data[0] if case.data else None
            except:
                report['counselor_case'] = None
            
            # Get teacher review if exists
            try:
                teacher_review = supabase.table('teacher_reviews').select('*').eq('report_id', report['id']).order('created_at', desc=True).limit(1).execute()
                report['teacher_review'] = teacher_review.data[0] if teacher_review.data else None
            except:
                report['teacher_review'] = None
    except Exception as e:
        import traceback
        print(f"Error fetching case records: {str(e)}\n{traceback.format_exc()}")
        reports_data = []
    return render_template('counselor/cases.html', cases=reports_data)

@counselor_bp.route('/cases')
@require_auth(roles=['counselor'])
def assigned_cases():
    # Redirect to case-record for consistency
    return redirect(url_for('counselor.case_record'))

@counselor_bp.route('/notifications')
@require_auth(roles=['counselor'])
def notifications():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
        notifications_data = notifications.data if notifications.data else []
    except:
        notifications_data = []
    return render_template('counselor/notifications.html', notifications=notifications_data)

@counselor_bp.route('/case-record/<report_id>/review', methods=['GET', 'POST'])
@require_auth(roles=['counselor'])
def review_case(report_id):
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        try:
            # Get the student report with student info
            report = supabase.table('student_reports').select(
                '*, users!student_reports_student_id_fkey(first_name, last_name, email, user_id)'
            ).eq('id', report_id).single().execute()
            report_data = report.data if report.data else None
            
            # Get teacher review if exists
            try:
                teacher_review = supabase.table('teacher_reviews').select('*').eq('report_id', report_id).order('created_at', desc=True).limit(1).execute()
                teacher_review_data = teacher_review.data[0] if teacher_review.data else None
            except:
                teacher_review_data = None
            
            # Get existing counselor case if any
            try:
                counselor_case = supabase.table('counselor_cases').select('*').eq('report_id', report_id).eq('counselor_id', user['id']).order('created_at', desc=True).limit(1).execute()
                counselor_case_data = counselor_case.data[0] if counselor_case.data else None
            except:
                counselor_case_data = None
            
            return render_template('counselor/review_case.html', 
                                 report=report_data,
                                 teacher_review=teacher_review_data,
                                 counselor_case=counselor_case_data)
        except Exception as e:
            import traceback
            print(f"Error fetching case: {str(e)}\n{traceback.format_exc()}")
            return redirect(url_for('counselor.case_record'))
    
    # POST - Submit/Update counselor case
    data = request.get_json()
    user = get_current_user()
    
    try:
        # Check if case already exists
        existing_case = supabase.table('counselor_cases').select('id').eq('report_id', report_id).eq('counselor_id', user['id']).execute()
        
        case_data = {
            'report_id': report_id,
            'counselor_id': user['id'],
            'summary': data.get('summary'),
            'counselor_notes': data.get('counselor_notes', ''),
            'action_taken': data.get('action_taken'),
            'recommendation': data.get('recommendation'),
            'meeting_date': data.get('meeting_date'),
            'follow_up_date': data.get('follow_up_date'),
            'status': data.get('status', 'In Review')
        }
        
        if existing_case.data:
            # Update existing case
            result = supabase.table('counselor_cases').update(case_data).eq('id', existing_case.data[0]['id']).execute()
        else:
            # Create new case
            result = supabase.table('counselor_cases').insert(case_data).execute()
        
        return jsonify({'success': True, 'message': 'Case record updated successfully'})
    except Exception as e:
        import traceback
        print(f"Error submitting case: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@counselor_bp.route('/case/<case_id>/notes', methods=['GET', 'POST'])
@require_auth(roles=['counselor'])
def case_notes(case_id):
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        try:
            notes = supabase.table('case_notes').select('*').eq('case_id', case_id).order('created_at', desc=True).execute()
            notes_data = notes.data if notes.data else []
        except:
            notes_data = []
        
        try:
            case = supabase.table('cases').select('*').eq('id', case_id).single().execute()
            case_data = case.data if case.data else {}
        except:
            case_data = {}
        
        return render_template('counselor/case_notes.html', 
                             notes=notes_data,
                             case=case_data)
    
    user = get_current_user()
    data = request.get_json()
    
    try:
        note = supabase.table('case_notes').insert({
            'case_id': case_id,
            'counselor_id': user['id'],
            'note': data.get('note'),
            'note_type': data.get('note_type', 'general')
        }).execute()
        
        return jsonify({'success': True, 'note': note.data[0] if note.data else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@counselor_bp.route('/student-history/<student_id>')
@require_auth(roles=['counselor'])
def student_history(student_id):
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        # Get student reports with counselor cases
        reports = supabase.table('student_reports').select(
            '*, counselor_cases!inner(*), users!student_reports_student_id_fkey(first_name, last_name)'
        ).eq('student_id', student_id).execute()
        cases_data = reports.data if reports.data else []
    except:
        cases_data = []
    
    # Get counseling requests for this student
    try:
        counseling_requests = supabase.table('counseling_requests').select(
            '*, student_reports(tracking_code, subject)'
        ).eq('user_id', student_id).order('created_at', desc=True).execute()
        counseling_requests_data = counseling_requests.data if counseling_requests.data else []
    except:
        counseling_requests_data = []
    
    return render_template('counselor/student_history.html',
                         cases=cases_data,
                         counseling_requests=counseling_requests_data,
                         student_id=student_id)

@counselor_bp.route('/counseling-requests', methods=['GET', 'POST'])
@require_auth(roles=['counselor'])
def counseling_requests():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        try:
            # Get all pending counseling requests
            requests = supabase.table('counseling_requests').select(
                '*, users!counseling_requests_user_id_fkey(first_name, last_name, user_id), student_reports(tracking_code, subject)'
            ).eq('status', 'pending').order('created_at', desc=True).execute()
            requests_data = requests.data if requests.data else []
        except Exception as e:
            import traceback
            print(f"Error fetching counseling requests: {str(e)}\n{traceback.format_exc()}")
            requests_data = []
        
        return render_template('counselor/counseling_requests.html', requests=requests_data)
    
    # POST - Update counseling request status
    data = request.get_json()
    request_id = data.get('request_id')
    action = data.get('action')  # approve, reschedule, reject
    
    try:
        if action == 'approve':
            update_data = {
                'status': 'approved',
                'scheduled_date': data.get('scheduled_date')
            }
        elif action == 'reschedule':
            update_data = {
                'status': 'rescheduled',
                'scheduled_date': data.get('scheduled_date')
            }
        elif action == 'reject':
            update_data = {
                'status': 'rejected'
            }
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        result = supabase.table('counseling_requests').update(update_data).eq('id', request_id).execute()
        
        return jsonify({'success': True, 'message': f'Counseling request {action}d successfully'})
    except Exception as e:
        import traceback
        print(f"Error updating counseling request: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@counselor_bp.route('/counseling-requests/<request_id>/complete', methods=['POST'])
@require_auth(roles=['counselor'])
def complete_counseling(request_id):
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    data = request.get_json()
    
    try:
        # Get the counseling request
        counseling_request = supabase.table('counseling_requests').select('*').eq('id', request_id).single().execute()
        if not counseling_request.data:
            return jsonify({'error': 'Counseling request not found'}), 404
        
        report_id = counseling_request.data.get('report_id')
        
        # Mark counseling as completed
        supabase.table('counseling_requests').update({
            'status': 'completed'
        }).eq('id', request_id).execute()
        
        # If report_id exists, settle the report
        if report_id:
            supabase.table('counselor_cases').update({
                'status': 'Settled'
            }).eq('report_id', report_id).execute()
        
        return jsonify({'success': True, 'message': 'Counseling session completed and report settled'})
    except Exception as e:
        import traceback
        print(f"Error completing counseling: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 400

@counselor_bp.route('/analytics')
@require_auth(roles=['counselor'])
def analytics():
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    # Get case statistics
    try:
        all_cases = supabase.table('cases').select('*').execute()
        cases_data = all_cases.data if all_cases.data else []
    except:
        cases_data = []
    
    stats = {
        'total': len(cases_data),
        'active': len([c for c in cases_data if c.get('status') == 'active']),
        'closed': len([c for c in cases_data if c.get('status') == 'closed']),
        'pending': len([c for c in cases_data if c.get('status') == 'pending'])
    }
    
    return render_template('counselor/analytics.html', stats=stats)

@counselor_bp.route('/manage-guidance', methods=['GET', 'POST'])
@require_auth(roles=['counselor'])
def manage_guidance():
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        try:
            resources = supabase.table('resources').select('*').order('created_at', desc=True).execute()
            resources_data = resources.data if resources.data else []
        except:
            resources_data = []
        return render_template('counselor/manage_guidance.html', resources=resources_data)
    
    user = get_current_user()
    data = request.get_json()
    
    try:
        resource = supabase.table('resources').insert({
            'title': data.get('title'),
            'description': data.get('description'),
            'resource_type': data.get('resource_type'),
            'created_by': user['id']
        }).execute()
        
        return jsonify({'success': True, 'resource': resource.data[0] if resource.data else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@counselor_bp.route('/profile', methods=['GET', 'POST'])
@require_auth(roles=['counselor'])
def profile():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        try:
            user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
            user_data_dict = user_data.data if user_data.data else {}
        except:
            user_data_dict = {}
        return render_template('counselor/profile.html', user_data=user_data_dict)
    
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
    if 'specialization' in data:
        update_data['specialization'] = data.get('specialization')
    
    try:
        supabase.table('users').update(update_data).eq('id', user['id']).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

