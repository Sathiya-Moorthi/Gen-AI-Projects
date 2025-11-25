from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

video_id = "dQw4w9WgXcQ"
api_key = os.getenv("OPENAI_API_KEY")

print("Step 1: Fetching transcript...")
try:
    api = YouTubeTranscriptApi()
    transcript_list = api.fetch(video_id)
    transcript_text = " ".join([item.text for item in transcript_list])
    print(f"✅ Success! Got {len(transcript_text)} characters")
    print(f"Preview: {transcript_text[:200]}...")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("\nStep 2: Generating summary with OpenAI...")
try:
    client = OpenAI(api_key=api_key)
    
    # Truncate
    transcript_text = transcript_text[:8000]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
            {"role": "user", "content": f"Summarize this in 3-5 bullet points:\n\n{transcript_text}"}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    summary = response.choices[0].message.content
    print(f"✅ Success!\n\nSummary:\n{summary}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
