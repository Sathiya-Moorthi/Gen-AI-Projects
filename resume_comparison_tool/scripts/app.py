from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import hashlib
from difflib import SequenceMatcher
import PyPDF2
import docx
import io
from pydantic import BaseModel

app = FastAPI(title="Resume Comparison API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ComparisonResult(BaseModel):
    exact_duplicates: List[List[str]]
    similar_pairs: List[dict]
    summary: dict

class ResumeProcessor:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX bytes"""
        try:
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """Extract text from TXT bytes"""
        try:
            return file_content.decode('utf-8').strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading TXT: {str(e)}")
    
    @staticmethod
    def get_file_hash(file_content: bytes) -> str:
        """Calculate MD5 hash"""
        return hashlib.md5(file_content).hexdigest()
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity ratio"""
        return SequenceMatcher(None, text1, text2).ratio()

@app.get("/")
async def root():
    return {"message": "Resume Comparison API is running"}

@app.post("/compare-resumes", response_model=ComparisonResult)
async def compare_resumes(
    files: List[UploadFile] = File(...),
    similarity_threshold: float = 0.95
):
    """
    Compare multiple resumes
    - Detects exact duplicates
    - Finds similar resumes based on threshold
    """
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least 2 files")
    
    processor = ResumeProcessor()
    resumes = {}
    
    # Process all uploaded files
    for file in files:
        file_content = await file.read()
        filename = file.filename
        
        # Determine file type and extract text
        if filename.lower().endswith('.pdf'):
            text = processor.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            text = processor.extract_text_from_docx(file_content)
        elif filename.lower().endswith('.txt'):
            text = processor.extract_text_from_txt(file_content)
        else:
            continue
        
        resumes[filename] = {
            'text': text,
            'hash': processor.get_file_hash(file_content),
            'size': len(file_content)
        }
    
    if len(resumes) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Need at least 2 valid files (PDF, DOCX, or TXT)"
        )
    
    # Find exact duplicates by hash
    hash_groups = {}
    for name, data in resumes.items():
        file_hash = data['hash']
        if file_hash in hash_groups:
            hash_groups[file_hash].append(name)
        else:
            hash_groups[file_hash] = [name]
    
    exact_duplicates = [files for files in hash_groups.values() if len(files) > 1]
    
    # Find similar resumes
    similar_pairs = []
    resume_names = list(resumes.keys())
    
    for i in range(len(resume_names)):
        for j in range(i + 1, len(resume_names)):
            name1, name2 = resume_names[i], resume_names[j]
            text1 = resumes[name1]['text']
            text2 = resumes[name2]['text']
            
            if not text1 or not text2:
                continue
            
            similarity = processor.calculate_similarity(text1, text2)
            
            if similarity >= similarity_threshold:
                similar_pairs.append({
                    'file1': name1,
                    'file2': name2,
                    'similarity': round(similarity * 100, 2)
                })
    
    # Create summary
    summary = {
        'total_files': len(resumes),
        'unique_files': len(hash_groups),
        'exact_duplicate_groups': len(exact_duplicates),
        'similar_pairs_found': len(similar_pairs),
        'similarity_threshold': similarity_threshold * 100
    }
    
    return ComparisonResult(
        exact_duplicates=exact_duplicates,
        similar_pairs=similar_pairs,
        summary=summary
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)