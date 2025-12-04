from flask import Blueprint, request, jsonify, render_template, session, current_app
from app.utils.auth import require_auth, get_current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@require_auth(roles=['admin'])
def dashboard():
    supabase = current_app.supabase
    
    # Get statistics
    users_count = supabase.table('users').select('id', count='exact').execute()
    reports_count = supabase.table('reports').select('id', count='exact').execute()
    cases_count = supabase.table('cases').select('id', count='exact').execute()
    
    # Get recent activity
    recent_reports = supabase.table('reports').select('*').order('created_at', desc=True).limit(10).execute()
    recent_users = supabase.table('users').select('*').order('created_at', desc=True).limit(10).execute()
    
    return render_template('admin/dashboard.html',
                         users_count=users_count.count if hasattr(users_count, 'count') else 0,
                         reports_count=reports_count.count if hasattr(reports_count, 'count') else 0,
                         cases_count=cases_count.count if hasattr(cases_count, 'count') else 0,
                         recent_reports=recent_reports.data if recent_reports.data else [],
                         recent_users=recent_users.data if recent_users.data else [])

@admin_bp.route('/users')
@require_auth(roles=['admin'])
def manage_users():
    supabase = current_app.supabase
    users = supabase.table('users').select('*').order('created_at', desc=True).execute()
    return render_template('admin/users.html', users=users.data if users.data else [])

@admin_bp.route('/users/<user_id>', methods=['PUT', 'DELETE'])
@require_auth(roles=['admin'])
def user_actions(user_id):
    supabase = current_app.supabase
    
    if request.method == 'PUT':
        data = request.get_json()
        supabase.table('users').update({
            'role': data.get('role'),
            'full_name': data.get('full_name'),
            'is_active': data.get('is_active', True)
        }).eq('id', user_id).execute()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        supabase.table('users').update({'is_active': False}).eq('id', user_id).execute()
        return jsonify({'success': True})

@admin_bp.route('/analytics')
@require_auth(roles=['admin'])
def analytics():
    supabase = current_app.supabase
    
    # Get all reports
    all_reports = supabase.table('reports').select('*').execute()
    reports_data = all_reports.data if all_reports.data else []
    
    # Get all cases
    all_cases = supabase.table('cases').select('*').execute()
    cases_data = all_cases.data if all_cases.data else []
    
    # Calculate statistics
    stats = {
        'total_reports': len(reports_data),
        'pending_reports': len([r for r in reports_data if r.get('status') == 'pending']),
        'resolved_reports': len([r for r in reports_data if r.get('status') == 'resolved']),
        'total_cases': len(cases_data),
        'active_cases': len([c for c in cases_data if c.get('status') == 'active']),
        'closed_cases': len([c for c in cases_data if c.get('status') == 'closed'])
    }
    
    return render_template('admin/analytics.html', stats=stats)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@require_auth(roles=['admin'])
def settings():
    supabase = current_app.supabase
    
    if request.method == 'GET':
        settings_data = supabase.table('system_settings').select('*').execute()
        settings_dict = {s['key']: s['value'] for s in (settings_data.data or [])}
        return render_template('admin/settings.html', settings=settings_dict)
    
    data = request.get_json()
    for key, value in data.items():
        supabase.table('system_settings').upsert({
            'key': key,
            'value': value
        }).execute()
    
    return jsonify({'success': True})

@admin_bp.route('/backup')
@require_auth(roles=['admin'])
def backup():
    return render_template('admin/backup.html')

@admin_bp.route('/security')
@require_auth(roles=['admin'])
def security():
    supabase = current_app.supabase
    # Get access logs
    logs = supabase.table('analytics_logs').select('*').order('created_at', desc=True).limit(100).execute()
    return render_template('admin/security.html', logs=logs.data if logs.data else [])

@admin_bp.route('/profile', methods=['GET', 'POST'])
@require_auth(roles=['admin'])
def profile():
    user = get_current_user()
    supabase = current_app.supabase
    
    if request.method == 'GET':
        user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute()
        return render_template('admin/profile.html', user_data=user_data.data if user_data.data else {})
    
    data = request.get_json()
    supabase.table('users').update({
        'full_name': data.get('full_name'),
        'phone': data.get('phone')
    }).eq('id', user['id']).execute()
    
    return jsonify({'success': True})

