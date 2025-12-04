from functools import wraps
from flask import request, jsonify, session, redirect, url_for, current_app
from supabase import Client

def get_current_user():
    """Get current user from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    supabase: Client = current_app.supabase
    try:
        user = supabase.table('users').select('*').eq('id', user_id).single().execute()
        return user.data if user.data else None
    except:
        return None

def require_auth(roles=None):
    """Decorator to require authentication and optionally specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login'))
            
            if roles:
                user = get_current_user()
                if not user or user.get('role') not in roles:
                    if request.is_json:
                        return jsonify({'error': 'Insufficient permissions'}), 403
                    return redirect(url_for('main.home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

