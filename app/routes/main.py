from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('main/home.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/guidance-services')
def guidance_services():
    return render_template('main/guidance_services.html')

@main_bp.route('/resources')
def resources():
    return render_template('main/resources.html')

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')

@main_bp.route('/report-tracker')
def report_tracker():
    # Redirect to anonymous report tracker
    return redirect(url_for('anonymous.track_report'))

@main_bp.route('/terms')
def terms():
    return render_template('main/terms.html')

