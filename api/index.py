"""
Vercel serverless function entry point for Flask app
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and create Flask app
try:
    from app import create_app
    app = create_app()
except Exception as e:
    # For debugging - this will show in Vercel logs
    import traceback
    print(f"Error creating app: {e}")
    print(traceback.format_exc())
    raise
