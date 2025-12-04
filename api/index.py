"""
Vercel serverless function entry point for Flask app
"""
from app import create_app
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = create_app()

# Export the app for Vercel
if __name__ == "__main__":
    app.run()

