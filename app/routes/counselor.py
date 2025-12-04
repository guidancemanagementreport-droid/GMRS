from flask import Blueprint, request, jsonify, render_template, session, current_app
from app.utils.auth import require_auth, get_current_user

counselor_bp = Blueprint('counselor', __name__)

@counselor_bp.route('/dashboard')
@require_auth(roles=['counselor'])
def dashboard():
    user = get_current_user()
    supabase = current_app.supabase
    
    # Get assigned cases
    cases = supabase.table('cases').select('*, reports(*), users(full_name)').eq('counselor_id', user['id']).order('created_at', desc=True).execute()
    
    # Get notifications
    notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).limit(10).execute()
    
    # Get statistics
    total_cases = len(cases.data) if cases.data else 0
    active_cases = len([c for c in (cases.data or []) if c.get('status') == 'active'])
    
    return render_template('counselor/dashboard.html',
                         cases=cases.data if cases.data else [],
                         notifications=notifications.data if notifications.data else [],
                         total_cases=total_cases,
                         active_cases=active_cases)

@counselor_bp.route('/cases')
@require_auth(roles=['counselor'])
def assigned_cases():
    user = get_current_user()
    supabase = current_app.supabase
    cases = supabase.table('cases').select('*, reports(*), users(full_name)').eq('counselor_id', user['id']).execute()
    return render_template('counselor/cases.html', cases=cases.data if cases.data else [])

@counselor_bp.route('/case/<case_id>/notes', methods=['GET', 'POST'])
@require_auth(roles=['counselor'])
def case_notes(case_id):
    supabase = current_app.supabase
    
    if request.method == 'GET':
        notes = supabase.table('case_notes').select('*').eq('case_id', case_id).order('created_at', desc=True).execute()
        case = supabase.table('cases').select('*').eq('id', case_id).single().execute()
        return render_template('counselor/case_notes.html', 
                             notes=notes.data if notes.data else [],
                             case=case.data if case.data else {})
    
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
    supabase = current_app.supabase
    cases = supabase.table('cases').select('*, reports(*)').eq('student_id', student_id).execute()
    notes = supabase.table('case_notes').select('*').eq('student_id', student_id).order('created_at', desc=True).execute()
    return render_template('counselor/student_history.html',
                         cases=cases.data if cases.data else [],
                         notes=notes.data if notes.data else [])

@counselor_bp.route('/analytics')
@require_auth(roles=['counselor'])
def analytics():
    supabase = current_app.supabase
    
    # Get case statistics
    all_cases = supabase.table('cases').select('*').execute()
    cases_data = all_cases.data if all_cases.data else []
    
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
    supabase = current_app.supabase
    
    if request.method == 'GET':
        resources = supabase.table('resources').select('*').order('created_at', desc=True).execute()
        return render_template('counselor/manage_guidance.html', resources=resources.data if resources.data else [])
    
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
    supabase = current_app.supabase
    
    if request.method == 'GET':
        user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
        return render_template('counselor/profile.html', user_data=user_data.data if user_data.data else {})
    
    data = request.get_json()
    supabase.table('users').update({
        'full_name': data.get('full_name'),
        'phone': data.get('phone'),
        'specialization': data.get('specialization')
    }).eq('id', user['id']).execute()
    
    return jsonify({'success': True})

