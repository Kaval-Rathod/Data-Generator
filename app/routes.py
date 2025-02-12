from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import os
from app.utils import DatasetConverter
from pathlib import Path

main = Blueprint('main', __name__)
converter = DatasetConverter()

def init_converter(app):
    """Initialize converter with app context"""
    converter.init_app(app)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')
    filenames = []
    
    for file in files:
        if file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            filenames.append(filename)
    
    return jsonify({'files': filenames})

@main.route('/process', methods=['POST'])
def process_files():
    data = request.get_json()
    files = data.get('files', [])
    output_format = data.get('format')
    
    try:
        results = converter.process_files(
            [os.path.join(current_app.config['UPLOAD_FOLDER'], f) for f in files],
            output_format
        )
        return jsonify({'status': 'success', 'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(current_app.config['CONVERTED_FOLDER'], filename),
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404 