from flask import Blueprint, request, jsonify, render_template, session, current_app
from app.utils.auth import require_auth, get_current_user

guest_bp = Blueprint('guest', __name__)

@guest_bp.route('/dashboard')
@require_auth(roles=['guest'])
def dashboard():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    # Get guidance requests
    try:
        requests = supabase.table('guidance_requests').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
        requests_data = requests.data if requests.data else []
    except:
        requests_data = []
    
    # Get notifications
    try:
        notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).limit(10).execute()
        notifications_data = notifications.data if notifications.data else []
    except:
        notifications_data = []
    
    # Get exam schedule
    try:
        exams = supabase.table('exam_schedule').select('*').order('exam_date', desc=True).execute()
        exams_data = exams.data if exams.data else []
    except:
        exams_data = []
    
    return render_template('guest/dashboard.html',
                         requests=requests_data,
                         notifications=notifications_data,
                         exams=exams_data)

@guest_bp.route('/submit-request', methods=['GET', 'POST'])
@require_auth(roles=['guest'])
def submit_request():
    if request.method == 'GET':
        return render_template('guest/submit_request.html')
    
    user = get_current_user()
    data = request.get_json()
    
    try:
        supabase = current_app.supabase
        request_data = supabase.table('guidance_requests').insert({
            'user_id': user['id'],
            'request_type': data.get('request_type'),
            'description': data.get('description'),
            'status': 'pending'
        }).execute()
        
        return jsonify({'success': True, 'request': request_data.data[0] if request_data.data else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@guest_bp.route('/request-status')
@require_auth(roles=['guest'])
def request_status():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        requests = supabase.table('guidance_requests').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
        requests_data = requests.data if requests.data else []
    except:
        requests_data = []
    return render_template('guest/request_status.html', requests=requests_data)

@guest_bp.route('/exam-schedule')
@require_auth(roles=['guest'])
def exam_schedule():
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    try:
        exams = supabase.table('exam_schedule').select('*').order('exam_date', desc=True).execute()
        exams_data = exams.data if exams.data else []
    except:
        exams_data = []
    return render_template('guest/exam_schedule.html', exams=exams_data)

@guest_bp.route('/profile', methods=['GET', 'POST'])
@require_auth(roles=['guest'])
def profile():
    user = get_current_user()
    supabase = getattr(current_app, 'supabase_admin', None) or current_app.supabase
    
    if request.method == 'GET':
        try:
            user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
            user_data_dict = user_data.data if user_data.data else {}
        except:
            user_data_dict = {}
        return render_template('guest/profile.html', user_data=user_data_dict)
    
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
    if 'address' in data:
        update_data['address'] = data.get('address')
    
    try:
        supabase.table('users').update(update_data).eq('id', user['id']).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

