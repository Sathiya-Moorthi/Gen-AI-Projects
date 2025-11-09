import os
import hashlib
from pathlib import Path
from difflib import SequenceMatcher
import PyPDF2
import docx

class ResumeComparator:
    def __init__(self, resume_folder):
        self.resume_folder = resume_folder
        self.resumes = {}
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
        return text.strip()
    
    def extract_text_from_docx(self, docx_path):
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = docx.Document(docx_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {docx_path}: {e}")
        return text.strip()
    
    def extract_text_from_txt(self, txt_path):
        """Extract text from TXT file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading TXT {txt_path}: {e}")
            return ""
    
    def get_file_hash(self, file_path):
        """Calculate MD5 hash of file for exact comparison"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        except Exception as e:
            print(f"Error hashing file {file_path}: {e}")
            return None
        return hash_md5.hexdigest()
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity ratio between two texts"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def load_resumes(self):
        """Load all resumes from the folder"""
        supported_formats = {'.pdf', '.docx', '.txt'}
        
        for file_path in Path(self.resume_folder).rglob('*'):
            if file_path.suffix.lower() in supported_formats:
                file_name = file_path.name
                
                # Extract text based on file type
                if file_path.suffix.lower() == '.pdf':
                    text = self.extract_text_from_pdf(file_path)
                elif file_path.suffix.lower() == '.docx':
                    text = self.extract_text_from_docx(file_path)
                elif file_path.suffix.lower() == '.txt':
                    text = self.extract_text_from_txt(file_path)
                else:
                    continue
                
                # Store resume info
                self.resumes[file_name] = {
                    'path': str(file_path),
                    'text': text,
                    'hash': self.get_file_hash(file_path)
                }
        
        print(f"Loaded {len(self.resumes)} resumes\n")
    
    def compare_resumes(self, similarity_threshold=0.95):
        """Compare all resumes and find duplicates or similar ones"""
        resume_names = list(self.resumes.keys())
        duplicates = []
        similar_pairs = []
        
        # Check for exact duplicates by hash
        hash_groups = {}
        for name, data in self.resumes.items():
            file_hash = data['hash']
            if file_hash in hash_groups:
                hash_groups[file_hash].append(name)
            else:
                hash_groups[file_hash] = [name]
        
        # Report exact duplicates
        print("=" * 60)
        print("EXACT DUPLICATES (Identical files):")
        print("=" * 60)
        exact_duplicates_found = False
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                exact_duplicates_found = True
                print(f"\nThe following files are IDENTICAL:")
                for f in files:
                    print(f"  - {f}")
        
        if not exact_duplicates_found:
            print("No exact duplicates found.\n")
        
        # Compare text content for similarity
        print("\n" + "=" * 60)
        print(f"SIMILAR RESUMES (Similarity >= {similarity_threshold*100}%):")
        print("=" * 60)
        similar_found = False
        
        for i in range(len(resume_names)):
            for j in range(i + 1, len(resume_names)):
                name1, name2 = resume_names[i], resume_names[j]
                text1 = self.resumes[name1]['text']
                text2 = self.resumes[name2]['text']
                
                # Skip if both texts are empty
                if not text1 or not text2:
                    continue
                
                similarity = self.calculate_similarity(text1, text2)
                
                if similarity >= similarity_threshold:
                    similar_found = True
                    print(f"\n{name1}")
                    print(f"  vs")
                    print(f"{name2}")
                    print(f"  Similarity: {similarity*100:.2f}%")
        
        if not similar_found:
            print(f"No similar resumes found (threshold: {similarity_threshold*100}%).\n")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print("=" * 60)
        print(f"Total resumes analyzed: {len(self.resumes)}")
        print(f"Unique resumes: {len(hash_groups)}")
        print(f"Similarity threshold: {similarity_threshold*100}%")


# Example usage
if __name__ == "__main__":
    # Specify the folder containing your resumes
    resume_folder = r"E:\resume"  # Change this to your folder path
    
    # Create comparator instance
    comparator = ResumeComparator(resume_folder)
    
    # Load all resumes
    comparator.load_resumes()
    
    # Compare resumes (0.95 = 95% similarity threshold)
    # Adjust threshold as needed: 1.0 = identical, 0.8 = 80% similar
    comparator.compare_resumes(similarity_threshold=0.95)