import os
import shutil
import PyPDF2
import json
import csv
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from dotenv import load_dotenv
import openai
import uuid
import threading
from pathlib import Path
import fitz  # PyMuPDF for better PDF handling
import pandas as pd
import time
import subprocess
import requests

# Load environment variables
load_dotenv()

class DatasetGenerator:
    def __init__(self):
        self.api_keys = [
            os.getenv(f"SAMBANOVA_API_KEY_{i}") 
            for i in range(1, 6) 
            if os.getenv(f"SAMBANOVA_API_KEY_{i}")
        ]
        self.current_key_index = 0
        self.root = Tk()
        self.root.title("Dataset Generator Pro")
        self.root.geometry("1200x700")  # Wider window
        
        # Apply modern styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors and styles
        self.style.configure('Accent.TButton', padding=5)
        self.style.configure('TLabelframe', padding=10)
        self.style.configure('TLabelframe.Label', font=('Helvetica', 10, 'bold'))
        
        # Setup folders first
        self.setup_folders()
        
        # Then create UI Components
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Top frame for upload and format selection
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=X, pady=(0, 10))
        
        # File Upload Section
        upload_frame = ttk.LabelFrame(top_frame, text="Upload & Process", padding=10)
        upload_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        button_frame = ttk.Frame(upload_frame)
        button_frame.pack(fill=X, pady=5)
        
        self.upload_btn = ttk.Button(
            button_frame, 
            text="📂 Upload Files",
            command=self.upload_files,
            style='Accent.TButton'
        )
        self.upload_btn.pack(side=LEFT, padx=5)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="▶️ Start Processing",
            command=self.start_processing,
            style='Accent.TButton',
            state='disabled'
        )
        self.start_btn.pack(side=LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear Files",
            command=self.clear_files,
            style='Accent.TButton',
            state='disabled'
        )
        self.clear_btn.pack(side=LEFT, padx=5)
        
        # Format Selection
        format_frame = ttk.LabelFrame(top_frame, text="Output Format", padding=10)
        format_frame.pack(side=LEFT, fill=BOTH, padx=(5, 0))
        
        self.format_var = StringVar()
        formats = [
            "Alpaca Format",
            "Prompt-Completion Format",
            "Chat Format",
            "Q/A Format",
            "Instruction-Context-Response Format",
            "JSONL",
            "CSV",
            "Table Format"
        ]
        self.format_dropdown = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=formats,
            state="readonly",
            width=30
        )
        self.format_dropdown.set(formats[0])
        self.format_dropdown.pack(pady=5)
        
        # Middle section with files and converted files
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Files List Section
        files_frame = ttk.LabelFrame(middle_frame, text="Input Files", padding=10)
        files_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        self.files_list = ttk.Treeview(
            files_frame,
            columns=("File", "Status"),
            show="headings",
            height=10
        )
        self.files_list.heading("File", text="File")
        self.files_list.heading("Status", text="Status")
        self.files_list.column("File", width=300)
        self.files_list.column("Status", width=100)
        self.files_list.pack(fill=BOTH, expand=True)
        
        files_scroll = ttk.Scrollbar(files_frame, orient=VERTICAL, command=self.files_list.yview)
        files_scroll.pack(side=RIGHT, fill=Y)
        self.files_list.configure(yscrollcommand=files_scroll.set)
        
        # Converted Files Section
        converted_frame = ttk.LabelFrame(middle_frame, text="Converted Files", padding=10)
        converted_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))
        
        converted_buttons = ttk.Frame(converted_frame)
        converted_buttons.pack(fill=X, pady=(0, 5))
        
        self.refresh_btn = ttk.Button(
            converted_buttons,
            text="↻ Refresh",
            command=self.refresh_converted_files,
            style='Accent.TButton'
        )
        self.refresh_btn.pack(side=LEFT, padx=5)
        
        self.open_folder_btn = ttk.Button(
            converted_buttons,
            text="📁 Open Folder",
            command=self.open_converted_folder,
            style='Accent.TButton'
        )
        self.open_folder_btn.pack(side=LEFT, padx=5)
        
        self.download_btn = ttk.Button(
            converted_buttons,
            text="⬇️ Download",
            command=self.download_selected,
            style='Accent.TButton'
        )
        self.download_btn.pack(side=LEFT, padx=5)
        
        self.converted_list = ttk.Treeview(
            converted_frame,
            columns=("File", "Format", "Size"),
            show="headings",
            height=10
        )
        self.converted_list.heading("File", text="File")
        self.converted_list.heading("Format", text="Format")
        self.converted_list.heading("Size", text="Size")
        self.converted_list.column("File", width=300)
        self.converted_list.column("Format", width=100)
        self.converted_list.column("Size", width=100)
        self.converted_list.pack(fill=BOTH, expand=True)
        
        converted_scroll = ttk.Scrollbar(converted_frame, orient=VERTICAL, command=self.converted_list.yview)
        converted_scroll.pack(side=RIGHT, fill=Y)
        self.converted_list.configure(yscrollcommand=converted_scroll.set)
        
        # Bottom section with progress and status
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=X, pady=(10, 0))
        
        # Progress bar and status
        progress_frame = ttk.LabelFrame(bottom_frame, text="Progress", padding=10)
        progress_frame.pack(fill=X)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            orient=HORIZONTAL,
            mode='determinate'
        )
        self.progress.pack(fill=X, pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack()
        
        # Console Log Section
        console_frame = ttk.LabelFrame(main_frame, text="Process Log", padding=10)
        console_frame.pack(fill=BOTH, expand=True, pady=(10, 0))
        
        # Console with custom styling
        self.console = Text(
            console_frame,
            height=5,
            wrap=WORD,
            font=('Consolas', 9),
            bg='#f5f5f5',
            relief=FLAT
        )
        self.console.pack(fill=BOTH, expand=True, pady=(0, 5))
        
        # Scrollbar for console
        console_scroll = ttk.Scrollbar(console_frame, orient=VERTICAL, command=self.console.yview)
        console_scroll.pack(side=RIGHT, fill=Y)
        self.console.configure(yscrollcommand=console_scroll.set)
        
        # Make console read-only
        self.console.configure(state='disabled')
        
        # Initial refresh of converted files
        self.refresh_converted_files()
        
    def setup_folders(self):
        self.remaining_dir = Path("remaining_files")
        self.converted_dir = Path("converted_files")
        self.remaining_dir.mkdir(exist_ok=True)
        self.converted_dir.mkdir(exist_ok=True)
        
    def upload_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[
                ("All Files", "*.*"),
                ("PDF Files", "*.pdf"),
                ("Text Files", "*.txt"),
                ("CSV Files", "*.csv"),
                ("JSON Files", "*.json")
            ]
        )
        if files:
            for file in files:
                # Check if file is already in the list
                existing = False
                for item in self.files_list.get_children():
                    if self.files_list.item(item)["values"][0] == file:
                        existing = True
                        break
                
                if not existing:
                    self.files_list.insert("", END, values=(file, "Pending"))
            
            # Enable start and clear buttons if files are added
            self.start_btn.config(state='normal')
            self.clear_btn.config(state='normal')
            
    def clear_files(self):
        self.files_list.delete(*self.files_list.get_children())
        self.start_btn.config(state='disabled')
        self.clear_btn.config(state='disabled')
        self.progress['value'] = 0
        self.status_label.config(text="Ready")
    
    def start_processing(self):
        # Disable buttons during processing
        self.upload_btn.config(state='disabled')
        self.start_btn.config(state='disabled')
        self.clear_btn.config(state='disabled')
        
        # Get all pending files
        files = []
        for item in self.files_list.get_children():
            values = self.files_list.item(item)["values"]
            if values[1] == "Pending":
                files.append(values[0])
        
        if files:
            # Start processing in a separate thread
            threading.Thread(target=self.process_files, args=(files,), daemon=True).start()
    
    def process_files(self, files):
        try:
            total_files = len(files)
            for index, file_path in enumerate(files, 1):
                try:
                    self.log(f"Starting to process file: {Path(file_path).name}")
                    self.status_label.config(text=f"Processing {Path(file_path).name} ({index}/{total_files})")
                    
                    # Update progress bar for file start
                    progress = (index - 1) / total_files * 100
                    self.progress['value'] = progress
                    self.root.update_idletasks()  # Force UI update
                    
                    # Save original file
                    dest_path = self.remaining_dir / Path(file_path).name
                    shutil.copy2(file_path, dest_path)
                    self.log(f"Saved original file to: {dest_path}")
                    
                    # Handle PDF splitting if needed
                    if file_path.lower().endswith('.pdf'):
                        self.log(f"PDF file detected, starting split and process")
                        self.split_and_process_pdf(file_path)
                    else:
                        self.log(f"Starting conversion for file: {Path(file_path).name}")
                        self.convert_file(file_path)
                    
                    self.update_file_status(file_path, "Completed")
                    self.refresh_converted_files()  # Refresh the converted files list
                    
                except Exception as e:
                    error_msg = f"Error processing {Path(file_path).name}: {str(e)}"
                    self.log(error_msg)
                    messagebox.showerror("Processing Error", error_msg)
                    self.update_file_status(file_path, "Failed")
                
                # Update progress bar for file completion
                progress = index / total_files * 100
                self.progress['value'] = progress
                self.root.update_idletasks()  # Force UI update
            
            self.status_label.config(text="Processing Complete")
            self.log("All files processed")
            messagebox.showinfo("Success", "All files have been processed")
            
        except Exception as e:
            error_msg = f"Critical error during processing: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("Critical Error", error_msg)
            
        finally:
            # Re-enable buttons after processing
            self.root.after(0, lambda: self.upload_btn.config(state='normal'))
            self.root.after(0, lambda: self.start_btn.config(state='normal'))
            self.root.after(0, lambda: self.clear_btn.config(state='normal'))
            self.refresh_converted_files()  # Final refresh of converted files list
        
    def split_and_process_pdf(self, file_path, max_size_mb=10):
        doc = fitz.open(file_path)
        total_pages = doc.page_count
        
        # Calculate pages per chunk based on file size
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        pages_per_chunk = max(1, int(total_pages * (max_size_mb / file_size_mb)))
        
        for start in range(0, total_pages, pages_per_chunk):
            end = min(start + pages_per_chunk, total_pages)
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start, to_page=end-1)
            
            chunk_path = self.remaining_dir / f"{Path(file_path).stem}_part_{start+1}.pdf"
            new_doc.save(chunk_path)
            new_doc.close()
            
            self.convert_file(str(chunk_path))
            
        doc.close()
        
    def convert_file(self, file_path):
        try:
            self.log(f"Reading content from: {Path(file_path).name}")
            content = self.read_file_content(file_path)
            
            target_format = self.format_var.get()
            self.log(f"Converting to format: {target_format}")
            
            # Generate conversion using AI
            converted_data = self.ai_conversion(content, target_format)
            
            # Save converted file
            output_path = self.converted_dir / f"{Path(file_path).stem}_{uuid.uuid4().hex[:6]}{self.get_extension(target_format)}"
            self.log(f"Saving converted file to: {output_path}")
            
            self.save_converted(converted_data, output_path, target_format)
            self.log(f"Successfully converted: {output_path.name}")
            
            # Refresh the converted files list
            self.refresh_converted_files()
            
        except Exception as e:
            error_msg = f"Conversion Error for {Path(file_path).name}: {str(e)}"
            self.log(error_msg)
            self.rotate_api_key()
            raise Exception(error_msg)
        
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
                
    def ai_conversion(self, content, target_format):
        max_retries = 3
        retry_count = 0
        converted_chunks = []
        
        # Prepare content chunks with smaller size
        max_chunk_size = 2000  # Reduced chunk size for better reliability
        content_chunks = [content[i:i + max_chunk_size] 
                        for i in range(0, len(content), max_chunk_size)]
        
        self.log(f"Content split into {len(content_chunks)} chunks")
        chunk_index = 0
        
        while chunk_index < len(content_chunks):
            try:
                self.log(f"Attempt {retry_count + 1}/{max_retries} - Using API Key #{self.current_key_index + 1}")
                
                while chunk_index < len(content_chunks):
                    chunk = content_chunks[chunk_index]
                    self.log(f"Processing chunk {chunk_index + 1}/{len(content_chunks)}")
                    
                    # Prepare system message based on format
                    system_message = self.get_system_message(target_format)
                    
                    messages = [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": f"Convert this content into {target_format}. Content: {chunk}"}
                    ]

                    try:
                        self.log(f"Sending chunk {chunk_index + 1} to API")
                        
                        # Make API request using requests library
                        headers = {
                            "Authorization": f"Bearer {self.current_api_key}",
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
                            self.log("Rate limit reached, switching API key and waiting...")
                            self.rotate_api_key()
                            time.sleep(5)  # Wait longer when rate limited
                            raise Exception("Rate limit exceeded")
                        
                        if response.status_code != 200:
                            error_data = response.json()
                            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                            raise Exception(f"API request failed with status {response.status_code}: {error_msg}")
                            
                        response_data = response.json()
                        if not response_data.get("choices") or not response_data["choices"][0].get("message", {}).get("content"):
                            raise Exception("Empty response from API")
                            
                        converted_chunks.append(response_data["choices"][0]["message"]["content"])
                        self.log(f"Successfully processed chunk {chunk_index + 1}")
                        chunk_index += 1  # Move to next chunk only on success
                        time.sleep(1)  # Add small delay between successful requests
                        
                    except Exception as chunk_error:
                        if "Rate limit exceeded" in str(chunk_error):
                            raise chunk_error  # Re-raise rate limit error to handle it in outer loop
                        error_msg = f"Error processing chunk {chunk_index + 1}: {str(chunk_error)}"
                        self.log(error_msg)
                        raise Exception(error_msg)
                
                # If we get here, all chunks were processed successfully
                self.log("All chunks processed successfully")
                break
                
            except Exception as e:
                if "Rate limit exceeded" in str(e):
                    continue  # Continue with new API key without incrementing retry count
                    
                retry_count += 1
                error_msg = f"API Error (Attempt {retry_count}/{max_retries}): {str(e)}"
                self.log(error_msg)
                
                if retry_count < max_retries:
                    self.rotate_api_key()
                    self.log(f"Retrying with API Key #{self.current_key_index + 1}")
                    time.sleep(3)  # Delay between retries
                else:
                    raise Exception(f"Failed to convert after {max_retries} attempts. Last error: {str(e)}")
        
        # Combine chunks based on format
        self.log("Combining processed chunks")
        if target_format in ["JSONL", "CSV", "Table Format"]:
            return self.combine_structured_chunks(converted_chunks, target_format)
        else:
            return "\n\n".join(converted_chunks)
        
    def get_system_message(self, target_format):
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
        
        return f"{base_message}\n\n{format_specific.get(target_format, '')}"
        
    def combine_structured_chunks(self, chunks, format_name):
        if format_name == "JSONL":
            # Combine JSONL by keeping all valid JSON lines
            combined = []
            for chunk in chunks:
                for line in chunk.split('\n'):
                    try:
                        json.loads(line.strip())
                        combined.append(line.strip())
                    except:
                        continue
            return '\n'.join(combined)
            
        elif format_name in ["CSV", "Table Format"]:
            # Keep headers from first chunk, combine data rows from all chunks
            chunks_lines = [chunk.split('\n') for chunk in chunks]
            headers = chunks_lines[0][0]
            data_rows = []
            for chunk_lines in chunks_lines:
                data_rows.extend(chunk_lines[1:])
            return headers + '\n' + '\n'.join(data_rows)
            
        return '\n\n'.join(chunks)  # Default combination for other formats
        
    def get_extension(self, format_name):
        format_extensions = {
            "JSONL": ".jsonl",
            "CSV": ".csv",
            "Table Format": ".csv",
        }
        return format_extensions.get(format_name, ".txt")
        
    def save_converted(self, data, path, format_name):
        try:
            if format_name in ["CSV", "Table Format"]:
                # Convert string data to CSV
                lines = [line.strip().split(',') for line in data.split('\n') if line.strip()]
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(lines)
            elif format_name == "JSONL":
                # Ensure each line is valid JSON
                with open(path, 'w', encoding='utf-8') as f:
                    for line in data.split('\n'):
                        if line.strip():
                            try:
                                json_obj = json.loads(line)
                                f.write(json.dumps(json_obj) + '\n')
                            except:
                                f.write(json.dumps({"text": line}) + '\n')
            else:
                # Save as plain text for other formats
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(data)
                    
        except Exception as e:
            self.log(f"Error saving file: {str(e)}")
            
    def rotate_api_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.log(f"Switched to API Key #{self.current_key_index + 1}")
        
    def update_file_status(self, file_path, status):
        for item in self.files_list.get_children():
            if self.files_list.item(item)["values"][0] == file_path:
                self.files_list.item(item, values=(file_path, status))
                break
                
    def log(self, message):
        """Log a message to the console with timestamp"""
        self.console.configure(state='normal')  # Temporarily enable writing
        self.console.insert(END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.console.see(END)  # Auto-scroll to bottom
        self.console.configure(state='disabled')  # Make read-only again
        
    @property
    def current_api_key(self):
        return self.api_keys[self.current_key_index]
        
    def refresh_converted_files(self):
        """Refresh the list of converted files"""
        # Clear existing items
        self.converted_list.delete(*self.converted_list.get_children())
        
        # Get all files in converted directory
        if self.converted_dir.exists():
            for file_path in self.converted_dir.glob('*'):
                if file_path.is_file():
                    # Get file format from extension
                    file_format = file_path.suffix.lstrip('.')
                    # Get file size
                    size_bytes = file_path.stat().st_size
                    size_str = self.format_file_size(size_bytes)
                    
                    self.converted_list.insert("", END, values=(file_path.name, file_format.upper(), size_str))
    
    def format_file_size(self, size_bytes):
        """Format file size in bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def open_converted_folder(self):
        """Open the converted files folder in file explorer"""
        try:
            os.startfile(self.converted_dir) if os.name == 'nt' else subprocess.run(['xdg-open', self.converted_dir])
        except Exception as e:
            self.log(f"Error opening folder: {str(e)}")
    
    def download_selected(self):
        """Download the selected converted file"""
        selection = self.converted_list.selection()
        if not selection:
            messagebox.showinfo("Select File", "Please select a file to download first")
            return
            
        item = self.converted_list.item(selection[0])
        file_name = item['values'][0]
        source_path = self.converted_dir / file_name
        
        if source_path.exists():
            try:
                # Ask user for download location
                download_path = filedialog.asksaveasfilename(
                    initialfile=file_name,
                    defaultextension=source_path.suffix,
                    filetypes=[("All Files", "*.*")]
                )
                
                if download_path:
                    shutil.copy2(source_path, download_path)
                    self.log(f"Downloaded: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Error downloading file: {str(e)}")
        else:
            messagebox.showerror("Error", f"File not found: {file_name}")
        
    def download_selected_file(self, event):
        """Download the selected converted file"""
        selection = self.converted_list.selection()
        if not selection:
            return
            
        item = self.converted_list.item(selection[0])
        file_name = item['values'][0]
        source_path = self.converted_dir / file_name
        
        if source_path.exists():
            try:
                # Ask user for download location
                download_path = filedialog.asksaveasfilename(
                    initialfile=file_name,
                    defaultextension=source_path.suffix,
                    filetypes=[("All Files", "*.*")]
                )
                
                if download_path:
                    shutil.copy2(source_path, download_path)
                    self.log(f"Downloaded: {file_name}")
            except Exception as e:
                self.log(f"Error downloading file: {str(e)}")
        else:
            self.log(f"File not found: {file_name}")
        
if __name__ == "__main__":
    app = DatasetGenerator()
    app.root.mainloop() 