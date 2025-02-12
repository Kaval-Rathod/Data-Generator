from flask import Flask
from config import Config
from pathlib import Path

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure required directories exist
    Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
    Path(app.config['CONVERTED_FOLDER']).mkdir(exist_ok=True)
    
    # Register blueprints
    from app.routes import main, init_converter
    app.register_blueprint(main)
    
    # Initialize converter with app context
    init_converter(app)
    
    return app 