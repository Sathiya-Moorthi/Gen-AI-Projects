"""
Test the YouTube summarizer functionality
"""
from langchain_community.document_loaders import YoutubeLoader
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Test URL - a short video
video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

print("Testing YouTube Transcript Loader...")
try:
    loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
    docs = loader.load()
    
    if docs:
        print(f"✅ Successfully loaded transcript")
        print(f"Title: {docs[0].metadata.get('title', 'N/A')}")
        print(f"Author: {docs[0].metadata.get('author', 'N/A')}")
        print(f"Transcript length: {len(docs[0].page_content)} characters")
        print(f"\nFirst 200 characters:\n{docs[0].page_content[:200]}")
        
        # Test OpenAI
        print("\n\nTesting OpenAI API...")
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
            
            transcript = docs[0].page_content[:5000]  # First 5000 chars
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": f"Summarize in 3 bullet points: {transcript}"}
                ],
                max_tokens=200
            )
            
            print("✅ OpenAI API working!")
            print(f"\nSummary:\n{response.choices[0].message.content}")
        else:
            print("❌ No API key found")
    else:
        print("❌ No transcript found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
