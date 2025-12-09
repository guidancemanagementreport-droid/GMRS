from flask import Blueprint, request, jsonify, render_template, current_app
import secrets
import string

anonymous_bp = Blueprint('anonymous', __name__)

def generate_tracking_code():
    """Generate a unique 8-character tracking code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))

@anonymous_bp.route('/report', methods=['GET', 'POST'])
def submit_report():
    if request.method == 'GET':
        return render_template('anonymous/report.html')
    
    data = request.get_json()
    
    try:
        supabase = current_app.supabase
        
        # Generate unique tracking code
        tracking_code = generate_tracking_code()
        
        # Ensure tracking code is unique
        max_attempts = 10
        for _ in range(max_attempts):
            existing = supabase.table('reports').select('id').eq('tracking_code', tracking_code).execute()
            if not existing.data:
                break
            tracking_code = generate_tracking_code()
        
        report = supabase.table('reports').insert({
            'title': data.get('title'),
            'description': data.get('description'),
            'category': data.get('category'),
            'status': 'pending',
            'reported_by': 'anonymous',
            'is_anonymous': True,
            'tracking_code': tracking_code
        }).execute()
        
        if report.data:
            return jsonify({
                'success': True,
                'report_id': report.data[0]['id'],
                'tracking_code': tracking_code,
                'message': 'Report submitted successfully'
            })
        else:
            return jsonify({'error': 'Failed to create report'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@anonymous_bp.route('/track', methods=['GET', 'POST'])
def track_report():
    if request.method == 'GET':
        return render_template('anonymous/track.html')
    
    data = request.get_json()
    tracking_code = data.get('tracking_code', '').upper().strip()
    
    if not tracking_code:
        return jsonify({'error': 'Tracking code is required'}), 400
    
    supabase = current_app.supabase
    try:
        report = supabase.table('reports').select('*').eq('tracking_code', tracking_code).single().execute()
        if report.data:
            return jsonify({
                'success': True,
                'report': report.data
            })
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Report not found'}), 404

@anonymous_bp.route('/track/<tracking_code>')
def track_report_by_code(tracking_code):
    supabase = current_app.supabase
    try:
        report = supabase.table('reports').select('*').eq('tracking_code', tracking_code.upper()).single().execute()
        return render_template('anonymous/track.html', report=report.data if report.data else {}, tracking_code=tracking_code.upper())
    except:
        return render_template('anonymous/track.html', report={}, error='Report not found', tracking_code=tracking_code.upper())

