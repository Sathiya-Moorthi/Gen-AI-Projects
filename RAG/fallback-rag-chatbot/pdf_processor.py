# ==================== FILE: pdf_processor.py ====================
"""
PDF Processing Module
Handles PDF upload, text extraction, chunking, and embedding generation
"""

import tempfile
import os
from typing import List, Tuple
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import config
from utils import logger


class PDFProcessor:
    """Handles all PDF processing operations"""
    
    def __init__(self):
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    @st.cache_resource
    def load_embeddings(_self):
        """Load and cache embedding model"""
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        return HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def extract_text_from_pdf(self, uploaded_file) -> List[Document]:
        """Extract text from uploaded PDF file"""
        documents = []
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        
        try:
            # Load PDF
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
            
            # Add filename to metadata
            for doc in docs:
                doc.metadata['source'] = uploaded_file.name
            
            documents.extend(docs)
            logger.info(f"Extracted {len(docs)} pages from {uploaded_file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {uploaded_file.name}: {str(e)}")
            raise
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
        
        return documents
    
    def process_documents(self, uploaded_files: List) -> Tuple[Chroma, int, dict]:
        """
        Process all uploaded PDFs and create vector store
        Returns: (vectorstore, total_chunks, processing_stats)
        """
        if self.embeddings is None:
            self.embeddings = self.load_embeddings()
        
        all_documents = []
        stats = {
            'total_files': len(uploaded_files),
            'total_pages': 0,
            'total_chunks': 0,
            'files_processed': []
        }
        
        # Extract text from all PDFs
        for uploaded_file in uploaded_files:
            try:
                docs = self.extract_text_from_pdf(uploaded_file)
                all_documents.extend(docs)
                stats['total_pages'] += len(docs)
                stats['files_processed'].append({
                    'name': uploaded_file.name,
                    'pages': len(docs)
                })
            except Exception as e:
                logger.error(f"Failed to process {uploaded_file.name}: {str(e)}")
                continue
        
        if not all_documents:
            raise ValueError("No documents were successfully processed")
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(all_documents)
        stats['total_chunks'] = len(chunks)
        
        logger.info(f"Created {len(chunks)} chunks from {len(all_documents)} pages")
        
        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name=config.COLLECTION_NAME,
            persist_directory=config.VECTOR_DB_PATH
        )
        
        return vectorstore, len(chunks), stats
    
    def load_existing_vectorstore(self) -> Chroma:
        """Load existing vector store from disk"""
        if self.embeddings is None:
            self.embeddings = self.load_embeddings()
        
        try:
            vectorstore = Chroma(
                collection_name=config.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=config.VECTOR_DB_PATH
            )
            logger.info("Loaded existing vector store")
            return vectorstore
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {str(e)}")
            return None