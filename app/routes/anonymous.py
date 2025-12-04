from flask import Blueprint, request, jsonify, render_template, current_app

anonymous_bp = Blueprint('anonymous', __name__)

@anonymous_bp.route('/report', methods=['GET', 'POST'])
def submit_report():
    if request.method == 'GET':
        return render_template('anonymous/report.html')
    
    data = request.get_json()
    
    try:
        supabase = current_app.supabase
        report = supabase.table('reports').insert({
            'title': data.get('title'),
            'description': data.get('description'),
            'category': data.get('category'),
            'status': 'pending',
            'reported_by': 'anonymous',
            'is_anonymous': True
        }).execute()
        
        return jsonify({'success': True, 'report_id': report.data[0]['id'] if report.data else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@anonymous_bp.route('/track/<report_id>')
def track_report(report_id):
    supabase = current_app.supabase
    try:
        report = supabase.table('reports').select('*').eq('id', report_id).single().execute()
        return render_template('anonymous/track.html', report=report.data if report.data else {})
    except:
        return render_template('anonymous/track.html', report={}, error='Report not found')

