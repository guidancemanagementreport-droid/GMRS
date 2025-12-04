from flask import Blueprint, request, jsonify, render_template, session, current_app
from app.utils.auth import require_auth, get_current_user

guest_bp = Blueprint('guest', __name__)

@guest_bp.route('/dashboard')
@require_auth(roles=['guest'])
def dashboard():
    user = get_current_user()
    supabase = request.app.supabase
    
    # Get guidance requests
    requests = supabase.table('guidance_requests').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
    
    # Get notifications
    notifications = supabase.table('notifications').select('*').eq('user_id', user['id']).order('created_at', desc=True).limit(10).execute()
    
    # Get exam schedule
    exams = supabase.table('exam_schedule').select('*').order('exam_date', desc=True).execute()
    
    return render_template('guest/dashboard.html',
                         requests=requests.data if requests.data else [],
                         notifications=notifications.data if notifications.data else [],
                         exams=exams.data if exams.data else [])

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
    supabase = request.app.supabase
    requests = supabase.table('guidance_requests').select('*').eq('user_id', user['id']).order('created_at', desc=True).execute()
    return render_template('guest/request_status.html', requests=requests.data if requests.data else [])

@guest_bp.route('/exam-schedule')
@require_auth(roles=['guest'])
def exam_schedule():
    supabase = request.app.supabase
    exams = supabase.table('exam_schedule').select('*').order('exam_date', desc=True).execute()
    return render_template('guest/exam_schedule.html', exams=exams.data if exams.data else [])

@guest_bp.route('/profile', methods=['GET', 'POST'])
@require_auth(roles=['guest'])
def profile():
    user = get_current_user()
    supabase = request.app.supabase
    
    if request.method == 'GET':
        user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
        return render_template('guest/profile.html', user_data=user_data.data if user_data.data else {})
    
    data = request.get_json()
    supabase.table('users').update({
        'full_name': data.get('full_name'),
        'phone': data.get('phone'),
        'address': data.get('address')
    }).eq('id', user['id']).execute()
    
    return jsonify({'success': True})

