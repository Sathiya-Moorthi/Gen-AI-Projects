import streamlit as st
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import re

load_dotenv()

# Set page configuration
st.set_page_config(page_title="YouTube Video Summarizer", page_icon="📺", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #FF0000;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #CC0000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("📺 YouTube Video Summarizer")
st.markdown("### Summarize any YouTube video in seconds using AI")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    st.markdown("[Get your API Key here](https://platform.openai.com/account/api-keys)")
    st.markdown("---")
    st.markdown("Built with 🦜️🔗 LangChain & Streamlit")

# Main input area
video_url = st.text_input("Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

if st.button("Summarize Video"):
    if not api_key:
        st.error("❌ Please provide an OpenAI API Key in the sidebar.")
    elif not video_url:
        st.error("❌ Please enter a YouTube Video URL.")
    else:
        try:
            with st.spinner("Loading transcript and generating summary..."):
                # Extract video ID
                video_id = extract_video_id(video_url)
                
                if not video_id:
                    st.error("❌ Invalid YouTube URL. Please check the URL and try again.")
                else:
                    st.info(f"📹 Video ID: {video_id}")
                    
                    # Get transcript using youtube_transcript_api directly
                    try:
                        api = YouTubeTranscriptApi()
                        transcript_list = api.fetch(video_id)
                        
                        # Combine all transcript text
                        transcript_text = " ".join([item.text for item in transcript_list])
                        
                        st.success(f"✅ Transcript loaded! ({len(transcript_text)} characters)")
                        
                        # Show preview
                        with st.expander("Preview transcript"):
                            st.text(transcript_text[:300] + "...")
                        
                        # Truncate if too long
                        max_chars = 10000
                        if len(transcript_text) > max_chars:
                            transcript_text = transcript_text[:max_chars]
                            st.warning(f"⚠️ Transcript truncated to {max_chars} characters")
                        
                        # Generate summary using OpenAI
                        st.info("🤖 Generating summary...")
                        
                        client = OpenAI(api_key=api_key)
                        
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant that creates concise, informative summaries of YouTube video transcripts."},
                                {"role": "user", "content": f"""Please provide a comprehensive summary of this YouTube video transcript in bullet points:

{transcript_text}

Include:
- Main topic/theme
- Key points discussed
- Important conclusions or takeaways"""}
                            ],
                            temperature=0.3,
                            max_tokens=800
                        )
                        
                        summary = response.choices[0].message.content
                        
                        if summary:
                            st.success("✅ Summary Generated Successfully!")
                            st.markdown("### 📝 Video Summary")
                            st.markdown(summary)
                            
                            # Add download button
                            st.download_button(
                                label="📥 Download Summary",
                                data=summary,
                                file_name=f"summary_{video_id}.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error("❌ Received empty response from OpenAI")
                            
                    except Exception as transcript_error:
                        st.error(f"❌ Could not retrieve transcript: {str(transcript_error)}")
                        st.info("💡 This video might not have captions/subtitles available, or they might be disabled.")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            import traceback
            with st.expander("Show detailed error"):
                st.code(traceback.format_exc())


