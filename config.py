import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    CONVERTED_FOLDER = os.path.join(os.getcwd(), 'converted_files')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Build and publish configuration
    BUILD_DIR = os.path.join(os.getcwd(), 'build')
    STATIC_BUILD = os.path.join(BUILD_DIR, 'static')
    TEMPLATES_BUILD = os.path.join(BUILD_DIR, 'templates')
    
    # SambaNova API Keys
    SAMBANOVA_API_KEYS = [
        os.getenv(f"SAMBANOVA_API_KEY_{i}") 
        for i in range(1, 6) 
        if os.getenv(f"SAMBANOVA_API_KEY_{i}")
    ] 