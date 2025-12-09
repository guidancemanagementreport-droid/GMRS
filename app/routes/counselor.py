from flask import Blueprint, request, jsonify, render_template, session, current_app, redirect, url_for
from app.utils.auth import require_auth, get_current_user

counselor_bp = Blueprint('counselor', __name__)

@counselor_bp.route('/dashboard')
@require_auth(roles=['counselor'])
def dashboard():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    # Get assigned cases
    try:
        cases = supabase.table('cases').select('*, reports(*), users(first_name, last_name)').eq('counselor_id', user['id']).order('created_at', desc=True).execute()
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
    active_cases = len([c for c in cases_data if c.get('status') == 'active'])
    
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
        cases = supabase.table('cases').select('*, reports(*), users(first_name, last_name)').eq('counselor_id', user['id']).execute()
        cases_data = cases.data if cases.data else []
    except:
        cases_data = []
    return render_template('counselor/cases.html', cases=cases_data)

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
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        cases = supabase.table('cases').select('*, reports(*)').eq('student_id', student_id).execute()
        cases_data = cases.data if cases.data else []
    except:
        cases_data = []
    
    try:
        notes = supabase.table('case_notes').select('*').eq('student_id', student_id).order('created_at', desc=True).execute()
        notes_data = notes.data if notes.data else []
    except:
        notes_data = []
    
    return render_template('counselor/student_history.html',
                         cases=cases_data,
                         notes=notes_data)

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

