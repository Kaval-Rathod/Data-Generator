import os
import shutil
import PyPDF2
import json
import csv
import uuid
import fitz
import pandas as pd
import time
import requests
from pathlib import Path
from flask import current_app

class DatasetConverter:
    def __init__(self):
        self.api_keys = []
        self.current_key_index = 0
        
    def init_app(self, app):
        """Initialize with app context"""
        self.api_keys = app.config['SAMBANOVA_API_KEYS']
    
    def process_files(self, files, output_format):
        results = []
        for file_path in files:
            try:
                content = self.read_file_content(file_path)
                converted_data = self.ai_conversion(content, output_format)
                
                output_path = Path(current_app.config['CONVERTED_FOLDER']) / f"{Path(file_path).stem}_{uuid.uuid4().hex[:6]}{self.get_extension(output_format)}"
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

    def read_file_content(self, file_path):
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            doc = fitz.open(file_path)
            content = ""
            for page in doc:
                content += page.get_text()
            doc.close()
            return content
        elif ext == '.csv':
            df = pd.read_csv(file_path)
            return df.to_string()
        elif ext == '.json':
            with open(file_path) as f:
                return json.dumps(json.load(f), indent=2)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

    def ai_conversion(self, content, output_format):
        """Convert content using AI API"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Prepare system message based on format
                system_message = self.get_system_message(output_format)
                
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Convert this content into {output_format}. Content: {content}"}
                ]

                headers = {
                    "Authorization": f"Bearer {self.api_keys[self.current_key_index]}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                data = {
                    "model": "Meta-Llama-3.1-8B-Instruct",
                    "messages": messages,
                    "temperature": 0.1,
                    "top_p": 0.1,
                    "max_tokens": 1500,
                    "presence_penalty": 0,
                    "frequency_penalty": 0
                }
                
                response = requests.post(
                    "https://api.sambanova.ai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 429:  # Rate limit exceeded
                    self.rotate_api_key()
                    time.sleep(5)
                    retry_count += 1
                    continue
                
                response.raise_for_status()
                response_data = response.json()
                
                if not response_data.get("choices") or not response_data["choices"][0].get("message", {}).get("content"):
                    raise Exception("Empty response from API")
                    
                return response_data["choices"][0]["message"]["content"]
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"Failed to convert after {max_retries} attempts. Error: {str(e)}")
                self.rotate_api_key()
                time.sleep(3)

    def get_system_message(self, output_format):
        """Get appropriate system message based on format"""
        base_message = "You are a data formatting expert. Your task is to convert the given content into the specified format while preserving the important information."
        
        format_specific = {
            "Alpaca Format": """Format the content into clear instruction-input-output JSON format. Each section should be concise and meaningful.
                Structure: {"instruction": "...", "input": "...", "output": "..."}""",
            "Prompt-Completion Format": """Create natural prompt-completion pairs from the content.
                Structure: {"prompt": "...", "completion": "..."}""",
            "Chat Format": """Convert content into a flowing conversation format.
                Structure: {"messages": [{"role": "system"/"user"/"assistant", "content": "..."}]}""",
            "Q/A Format": """Extract key questions and answers from the content.
                Structure: {"question": "...", "answer": "..."}""",
            "JSONL": """Create JSONL format with text and summary for each logical section.
                Structure: {"text": "...", "summary": "..."}""",
            "CSV": """Convert content into CSV format with relevant columns.""",
            "Table Format": """Create a structured table with appropriate headers and data rows."""
        }
        
        return f"{base_message}\n\n{format_specific.get(output_format, '')}"

    def get_extension(self, format_name):
        """Get appropriate file extension based on format"""
        format_extensions = {
            "JSONL": ".jsonl",
            "CSV": ".csv",
            "Table Format": ".csv",
        }
        return format_extensions.get(format_name, ".txt")

    def save_converted(self, data, output_path, format_name):
        """Save converted data in appropriate format"""
        try:
            if format_name in ["CSV", "Table Format"]:
                # Convert string data to CSV
                lines = [line.strip().split(',') for line in data.split('\n') if line.strip()]
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(lines)
            elif format_name == "JSONL":
                # Ensure each line is valid JSON
                with open(output_path, 'w', encoding='utf-8') as f:
                    for line in data.split('\n'):
                        if line.strip():
                            try:
                                json_obj = json.loads(line)
                                f.write(json.dumps(json_obj) + '\n')
                            except:
                                f.write(json.dumps({"text": line}) + '\n')
            else:
                # Save as plain text for other formats
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(data)
                    
        except Exception as e:
            raise Exception(f"Error saving file: {str(e)}")

    def rotate_api_key(self):
        """Rotate to next available API key"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys) 