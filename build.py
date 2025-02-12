import os
import shutil
from pathlib import Path
from config import Config

def clean_build():
    """Clean the build directory"""
    if os.path.exists(Config.BUILD_DIR):
        shutil.rmtree(Config.BUILD_DIR)

def create_build_dirs():
    """Create necessary build directories"""
    os.makedirs(Config.BUILD_DIR, exist_ok=True)
    os.makedirs(Config.STATIC_BUILD, exist_ok=True)
    os.makedirs(Config.TEMPLATES_BUILD, exist_ok=True)
    os.makedirs(os.path.join(Config.BUILD_DIR, 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(Config.BUILD_DIR, 'converted_files'), exist_ok=True)

def copy_static_files():
    """Copy static files to build directory"""
    static_source = os.path.join(os.getcwd(), 'static')
    if os.path.exists(static_source):
        shutil.copytree(static_source, Config.STATIC_BUILD, dirs_exist_ok=True)

def copy_templates():
    """Copy template files to build directory"""
    templates_source = os.path.join(os.getcwd(), 'templates')
    if os.path.exists(templates_source):
        shutil.copytree(templates_source, Config.TEMPLATES_BUILD, dirs_exist_ok=True)

def copy_python_files():
    """Copy necessary Python files to build directory"""
    python_files = [
        'app.py',
        'config.py',
        'dataset_generator_web.py',
        'run.py',
        'requirements.txt'
    ]
    for file in python_files:
        if os.path.exists(file):
            shutil.copy2(file, Config.BUILD_DIR)

def create_env_file():
    """Create a new .env file in build directory"""
    env_template = """# SambaNova API Keys (add as many as needed)
SAMBANOVA_API_KEY_1=your_first_api_key_here
# Add more API keys if needed"""
    
    with open(os.path.join(Config.BUILD_DIR, '.env'), 'w') as f:
        f.write(env_template)

def build():
    """Run the complete build process"""
    print("Starting build process...")
    
    # Clean and create directories
    clean_build()
    create_build_dirs()
    
    # Copy files
    copy_static_files()
    copy_templates()
    copy_python_files()
    create_env_file()
    
    print(f"Build completed successfully. Build directory: {Config.BUILD_DIR}")
    print("Don't forget to set up your API keys in the .env file!")

if __name__ == "__main__":
    build() 