# ==================== FILE: app.py ====================
"""
Streamlit Frontend Application
Modern UI with custom CSS styling
"""

import streamlit as st
from pdf_processor import PDFProcessor
from rag_engine import RAGEngine
import config
from utils import format_confidence_badge, format_sources, validate_pdf_file
import time

with open('styles.css', 'r') as f:
    CSS_STYLES = f'<style>{f.read()}</style>'

# Inject custom CSS
st.markdown(CSS_STYLES, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor()
    if 'uploaded_files_names' not in st.session_state:
        st.session_state.uploaded_files_names = []
    if 'processing_stats' not in st.session_state:
        st.session_state.processing_stats = None


def display_message(message: dict):
    """Display a single chat message with styling"""
    role = message['role']
    content = message['content']
    
    if role == 'user':
        st.markdown(
            f'<div class="message-container"><div class="user-message">{content}</div></div>',
            unsafe_allow_html=True
        )
    
    elif role == 'assistant':
        # AI message bubble
        st.markdown(
            f'<div class="message-container"><div class="ai-message">{content}</div></div>',
            unsafe_allow_html=True
        )
        
        # Metadata display
        metadata = message.get('metadata', {})
        if metadata:
            source = metadata.get('source')
            confidence = metadata.get('confidence', 0)
            reasoning = metadata.get('reasoning', '')
            grade = metadata.get('grade', 'LOW')
            retrieved_docs = metadata.get('retrieved_docs', [])
            scores = metadata.get('scores', [])
            web_results = metadata.get('web_results')
            
            # Source card
            badge_text, badge_class = format_confidence_badge(confidence)
            
            if source == 'pdf':
                source_icon = "📄"
                card_class = "source-card"
                source_label = "PDF Document"
                
                # Get source file info
                if retrieved_docs:
                    source_file = retrieved_docs[0].metadata.get('source', 'Unknown')
                    source_page = retrieved_docs[0].metadata.get('page', 'N/A')
                    doc_info = f"📖 Document: {source_file} (Page {source_page})"
                else:
                    doc_info = ""
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="font-size: 1.1em; font-weight: 600; margin-bottom: 8px;">
                        {source_icon} Source: {source_label}
                    </div>
                    <div style="margin: 8px 0;">
                        📊 Confidence: <span class="confidence-badge badge-{badge_class.lower()}">{badge_text}</span>
                        <strong>{confidence:.3f}</strong>
                    </div>
                    {f'<div style="margin: 8px 0;">{doc_info}</div>' if doc_info else ''}
                    <div style="margin-top: 12px; padding: 10px; background: rgba(0,0,0,0.05); border-radius: 6px;">
                        💡 <strong>Reasoning:</strong><br/>{reasoning}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            elif source == 'web':
                source_icon = "🌐"
                card_class = "source-card web"
                source_label = "Web Search"
                
                refined_query = web_results.get('refined_query', '') if web_results else ''
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="font-size: 1.1em; font-weight: 600; margin-bottom: 8px;">
                        {source_icon} Source: {source_label}
                    </div>
                    <div style="margin: 8px 0;">
                        📊 PDF Confidence: <span class="confidence-badge badge-{badge_class.lower()}">{badge_text}</span>
                        <strong>{confidence:.3f}</strong> (Below threshold: {config.SIMILARITY_THRESHOLD:.2f})
                    </div>
                    {f'<div style="margin: 8px 0;">🔍 Search Query: <em>{refined_query}</em></div>' if refined_query else ''}
                    <div style="margin-top: 12px; padding: 10px; background: rgba(0,0,0,0.05); border-radius: 6px;">
                        💡 <strong>Reasoning:</strong><br/>{reasoning}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Retrieved context expander
            if retrieved_docs and scores:
                with st.expander("📚 View Retrieved PDF Chunks"):
                    st.markdown(format_sources(retrieved_docs, scores), unsafe_allow_html=True)
            
            # Web results expander
            if web_results and web_results.get('results'):
                with st.expander("🌐 View Web Search Results"):
                    st.text_area(
                        "Search Results",
                        web_results['results'],
                        height=200,
                        disabled=True
                    )


def main():
    """Main application function"""
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # HuggingFace API Token
        st.markdown("### 🔑 API Keys")
        hf_token = st.text_input(
            "HuggingFace API Token",
            type="password",
            help="Required for LLM inference. Get yours at https://huggingface.co/settings/tokens"
        )
        
        if hf_token and st.session_state.rag_engine is None:
            st.session_state.rag_engine = RAGEngine(
                vectorstore=st.session_state.vectorstore,
                hf_token=hf_token
            )
        
        st.divider()
        
        # System info
        st.markdown("### 📊 System Configuration")
        st.markdown(f"""
        - **Model:** {config.LLM_MODEL.split('/')[-1]}
        - **Embeddings:** {config.EMBEDDING_MODEL.split('/')[-1]}
        - **Threshold:** {config.SIMILARITY_THRESHOLD}
        - **Chunk Size:** {config.CHUNK_SIZE}
        - **Top-K:** {config.TOP_K_RETRIEVAL}
        """)
        
        st.divider()
        
        # PDF Upload Section
        st.markdown("### 📄 Upload PDFs")
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Drag and drop PDF files here",
            type=['pdf'],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process uploaded files
        if uploaded_files:
            current_names = [f.name for f in uploaded_files]
            
            if current_names != st.session_state.uploaded_files_names:
                if not hf_token:
                    st.error("⚠️ Please enter HuggingFace API token first!")
                else:
                    with st.spinner("🔄 Processing PDFs..."):
                        try:
                            vectorstore, num_chunks, stats = st.session_state.pdf_processor.process_documents(
                                uploaded_files
                            )
                            
                            st.session_state.vectorstore = vectorstore
                            st.session_state.uploaded_files_names = current_names
                            st.session_state.processing_stats = stats
                            
                            # Update RAG engine
                            if st.session_state.rag_engine:
                                st.session_state.rag_engine.update_vectorstore(vectorstore)
                            else:
                                st.session_state.rag_engine = RAGEngine(
                                    vectorstore=vectorstore,
                                    hf_token=hf_token
                                )
                            
                            st.success("✅ PDFs processed successfully!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error processing PDFs: {str(e)}")
        
        # Display processing stats
        if st.session_state.processing_stats:
            stats = st.session_state.processing_stats
            st.markdown("### 📈 Document Statistics")
            st.markdown(f"""
            - **Files:** {stats['total_files']}
            - **Pages:** {stats['total_pages']}
            - **Chunks:** {stats['total_chunks']}
            """)
            
            with st.expander("📑 File Details"):
                for file_info in stats['files_processed']:
                    st.write(f"• {file_info['name']} ({file_info['pages']} pages)")
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Reset system button
        if st.button("♻️ Reset System", use_container_width=True):
            st.session_state.messages = []
            st.session_state.vectorstore = None
            st.session_state.rag_engine = None
            st.session_state.uploaded_files_names = []
            st.session_state.processing_stats = None
            st.rerun()
    
    # Main content area
    st.markdown(f"# {config.APP_TITLE}")
    st.markdown(f"*{config.APP_DESCRIPTION}*")
    st.markdown("---")
    
    # Welcome message
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.95); border-radius: 12px; padding: 30px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h2 style="color: #2D3748; margin-bottom: 16px;">👋 Welcome to Fallback RAG!</h2>
            <p style="color: #4A5568; font-size: 1.1em; line-height: 1.6;">
                This intelligent chatbot combines the power of your uploaded documents with real-time web search. 
                The system automatically decides the best source based on confidence scores.
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 24px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white;">
                    <div style="font-size: 2em; margin-bottom: 8px;">📄</div>
                    <h3 style="margin: 8px 0;">PDF Analysis</h3>
                    <p style="font-size: 0.9em; opacity: 0.9;">High confidence matches from your uploaded documents</p>
                </div>
                <div style="background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); padding: 20px; border-radius: 10px; color: white;">
                    <div style="font-size: 2em; margin-bottom: 8px;">🌐</div>
                    <h3 style="margin: 8px 0;">Web Fallback</h3>
                    <p style="font-size: 0.9em; opacity: 0.9;">Automatic search when PDF relevance is low</p>
                </div>
            </div>
            <div style="margin-top: 24px; padding: 16px; background: #F7FAFC; border-radius: 8px; border-left: 4px solid #4299E1;">
                <strong style="color: #2D3748;">Getting Started:</strong>
                <ol style="color: #4A5568; margin: 8px 0 0 0; padding-left: 20px;">
                    <li>Enter your HuggingFace API token in the sidebar</li>
                    <li>Upload one or more PDF documents</li>
                    <li>Start asking questions!</li>
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        display_message(message)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Ask a question about your documents...")
    
    if user_input:
        if not hf_token:
            st.error("⚠️ Please enter your HuggingFace API token in the sidebar!")
            st.stop()
        
        if not st.session_state.rag_engine:
            st.error("⚠️ Please upload PDF documents first or check your API token!")
            st.stop()
        
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input
        })
        
        # Display user message immediately
        st.markdown(
            f'<div class="message-container"><div class="user-message">{user_input}</div></div>',
            unsafe_allow_html=True
        )
        
        # Generate response
        with st.spinner("🤔 Thinking..."):
            try:
                result = st.session_state.rag_engine.query(user_input)
                
                # Add assistant message
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': result['answer'],
                    'metadata': {
                        'source': result['source'],
                        'confidence': result['confidence'],
                        'reasoning': result['reasoning'],
                        'grade': result['grade'],
                        'retrieved_docs': result['retrieved_docs'],
                        'scores': result['scores'],
                        'web_results': result['web_results']
                    }
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                st.stop()


if __name__ == "__main__":
    main()

