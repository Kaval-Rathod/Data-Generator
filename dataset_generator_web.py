import os
import shutil
import PyPDF2
import json
import csv
from dotenv import load_dotenv
import uuid
import fitz
import pandas as pd
import time
import requests
from pathlib import Path

load_dotenv()

class DatasetGeneratorWeb:
    def __init__(self):
        self.api_keys = [
            os.getenv(f"SAMBANOVA_API_KEY_{i}") 
            for i in range(1, 6) 
            if os.getenv(f"SAMBANOVA_API_KEY_{i}")
        ]
        self.current_key_index = 0
        self.converted_dir = Path("converted_files")
        self.converted_dir.mkdir(exist_ok=True)
        
    # Keep all the processing methods from original DatasetGenerator class
    # Remove GUI-specific code and modify for web usage
    # Add methods for progress tracking and status updates via web
    
    def process_files(self, files, output_format):
        results = []
        for file_path in files:
            try:
                content = self.read_file_content(file_path)
                converted_data = self.ai_conversion(content, output_format)
                
                output_path = self.converted_dir / f"{Path(file_path).stem}_{uuid.uuid4().hex[:6]}{self.get_extension(output_format)}"
                self.save_converted(converted_data, output_path, output_format)
                
                results.append({
                    'original': Path(file_path).name,
                    'converted': output_path.name,
                    'status': 'success'
                })
                
            except Exception as e:
                results.append({
                    'original': Path(file_path).name,
                    'error': str(e),
                    'status': 'error'
                })
                
        return results

    # Include other necessary methods from original class
    # Modified for web usage 