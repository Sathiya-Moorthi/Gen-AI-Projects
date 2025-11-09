# Resume Comparison Tool

A full-stack application for comparing multiple resumes to detect duplicates and similarities.

## Features
- 🔍 Exact duplicate detection (byte-level comparison)
- 📊 Similarity analysis with adjustable threshold
- 📄 Support for PDF, DOCX, and TXT formats
- 🎨 Beautiful Streamlit UI
- ⚡ Fast FastAPI backend with automatic API docs
- 📈 Visual comparison results

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Run separately (Recommended for development)

1. Start FastAPI backend:
```bash
python app.py
```
Backend will run on http://localhost:8000
API docs available at http://localhost:8000/docs

2. In a new terminal, start Streamlit frontend:
```bash
streamlit run streamlit_app.py
```
Frontend will run on http://localhost:8501

### Option 2: Run both with one command

```bash
python run.py
```

## Project Structure
```
resume-comparison-tool/
├── scripts/app.py                        # FastAPI backend
├── scripts/streamlit_app.py              # Streamlit frontend
├── required files/requirements.txt       # Python dependencies
├── scripts/run.py                        # Script to run both servers
└── documentation/README.md               # This file
|__ required files/.env                   # Optional - for configuration

```

## API Endpoints

### POST /compare-resumes
Upload multiple resume files for comparison
- **Parameters**: 
  - `files`: List of resume files (PDF, DOCX, TXT)
  - `similarity_threshold`: Float (0.0 to 1.0, default: 0.95)
- **Returns**: Comparison results with duplicates and similar pairs

### GET /health
Health check endpoint

### GET /
Root endpoint

## Usage Tips

1. **Similarity Threshold**: 
   - 95-100%: Very similar/identical content
   - 80-94%: Moderately similar
   - 50-79%: Some similarities

2. **Supported Formats**: PDF, DOCX, TXT

3. **Best Practices**:
   - Upload at least 2 files
   - Use consistent file formats for better comparison
   - Adjust threshold based on your needs

## Troubleshooting

**API Connection Error**: 
- Ensure FastAPI backend is running on port 8000
- Check if port 8000 is already in use

**File Upload Issues**:
- Ensure files are in supported formats (PDF, DOCX, TXT)
- Check file size (large PDFs may take longer to process)

## License
MIT License