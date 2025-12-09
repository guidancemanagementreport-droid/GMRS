from flask import Flask
from supabase import create_client, Client
import os

def create_app():
    import os
    # Get the absolute path to the static folder for Vercel compatibility
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(base_dir, 'static')
    app = Flask(__name__, 
                static_folder=static_folder, 
                static_url_path='/static',
                template_folder='templates')
    # Require env vars in production; no defaults to avoid wrong project/keys
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SUPABASE_URL'] = os.environ['SUPABASE_URL']
    app.config['SUPABASE_KEY'] = os.environ['SUPABASE_KEY']
    app.config['SUPABASE_SERVICE_KEY'] = os.environ['SUPABASE_SERVICE_KEY']  # Service role key for admin operations
    
    # Initialize Supabase client (anon key for regular operations)
    try:
        supabase: Client = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])
        app.supabase = supabase
        
        # Initialize service role client for login and admin operations
        if app.config['SUPABASE_SERVICE_KEY']:
            app.supabase_admin = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_SERVICE_KEY'])
        else:
            app.supabase_admin = supabase  # Fallback to anon key if service key not set
    except Exception as e:
        print(f"Warning: Supabase initialization error: {e}")
        app.supabase = None
        app.supabase_admin = None
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.guest import guest_bp
    from app.routes.teacher import teacher_bp
    from app.routes.counselor import counselor_bp
    from app.routes.admin import admin_bp
    from app.routes.anonymous import anonymous_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(guest_bp, url_prefix='/guest')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(counselor_bp, url_prefix='/counselor')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(anonymous_bp, url_prefix='/anonymous')
    app.register_blueprint(main_bp)
    
    return app

