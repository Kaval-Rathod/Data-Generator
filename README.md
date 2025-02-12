# Dataset Generator Pro

A powerful GUI application for converting various document formats into structured training datasets for machine learning models.

## Features

- **Multiple Input Formats Support**
  - PDF files
  - Text files
  - CSV files
  - JSON files

- **Various Output Formats**
  - Alpaca Format
  - Prompt-Completion Format
  - Chat Format
  - Q/A Format
  - Instruction-Context-Response Format
  - JSONL
  - CSV
  - Table Format

- **Advanced Features**
  - Automatic PDF splitting for large files
  - Multi-threaded processing
  - Real-time progress tracking
  - Process logging
  - Rate limit handling with API key rotation
  - File management system

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd dataset-generator
```

2. Create and activate a virtual environment (recommended):
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up your API keys:
   - Rename `.env.template` to `.env`
   - Add your SambaNova API keys to the `.env` file

## Required Dependencies

- python-dotenv==1.0.0
- openai==1.3.0
- PyMuPDF==1.23.8
- PyPDF2==3.0.1
- pandas==2.1.4
- python-tk==0.1.0
- uuid==1.30

## Usage

1. Start the application:
```bash
python dataset_generator.py
```

2. Using the Interface:
   - Click "Upload Files" to select input files
   - Choose desired output format from the dropdown
   - Click "Start Processing" to begin conversion
   - Monitor progress in the Process Log
   - Access converted files in the "Converted Files" section

3. Managing Files:
   - Use "Clear Files" to remove uploaded files
   - "Refresh" to update the converted files list
   - "Open Folder" to access the converted files directory
   - "Download" to save converted files to a desired location

## File Organization

- `dataset_generator.py`: Main application file
- `requirements.txt`: Python dependencies
- `.env`: Configuration file for API keys
- `remaining_files/`: Directory for original uploaded files
- `converted_files/`: Directory for processed output files

## Error Handling

The application includes robust error handling:
- API rate limit management
- Automatic API key rotation
- File processing error recovery
- Invalid file format detection
- Progress tracking and status updates

## Notes

- Large PDF files are automatically split into smaller chunks for processing
- The application supports multiple API keys for better rate limit handling
- Progress and status are displayed in real-time
- All operations are logged in the Process Log window

## Troubleshooting

1. **API Key Issues**:
   - Ensure your API keys are correctly set in the `.env` file
   - Check if the API keys are valid and active
   - Monitor the Process Log for API-related errors

2. **Processing Errors**:
   - Check input file format and encoding
   - Ensure sufficient disk space for output files
   - Monitor Process Log for specific error messages

3. **Performance Issues**:
   - Large files are automatically split into manageable chunks
   - Multiple API keys help handle rate limits
   - Progress bar shows real-time processing status

## Building for Production

To build the application for production:

1. Run the build script:
```bash
python build.py
```

This will create a `build` directory with the following structure:
```
build/
├── static/          # Static assets (CSS, JS)
├── templates/       # HTML templates
├── uploads/         # Upload directory
├── converted_files/ # Output directory
├── app.py          # Application code
├── config.py       # Configuration
├── run.py          # Entry point
├── requirements.txt # Dependencies
└── .env            # Environment configuration
```

2. Configure the production environment:
   - Navigate to the `build` directory
   - Set up your `.env` file with production API keys
   - Install dependencies: `pip install -r requirements.txt`

3. Run the production server:
```bash
cd build
python run.py
```

