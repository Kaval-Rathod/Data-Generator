from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from dataset_generator_web import DatasetGeneratorWeb
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and output directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path('converted_files').mkdir(exist_ok=True)

generator = DatasetGeneratorWeb()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')
    filenames = []
    
    for file in files:
        if file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            filenames.append(filename)
    
    return jsonify({'files': filenames})

@app.route('/process', methods=['POST'])
def process_files():
    data = request.get_json()
    files = data.get('files', [])
    output_format = data.get('format')
    
    try:
        results = generator.process_files(
            [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in files],
            output_format
        )
        return jsonify({'status': 'success', 'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            f'converted_files/{filename}',
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True) 