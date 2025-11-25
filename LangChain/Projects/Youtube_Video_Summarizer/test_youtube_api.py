from youtube_transcript_api import YouTubeTranscriptApi

video_id = "dQw4w9WgXcQ"

try:
    api = YouTubeTranscriptApi()
    result = api.fetch(video_id)
    
    print(f"Type: {type(result)}")
    print(f"Length: {len(result)}")
    print(f"\nFirst item type: {type(result[0])}")
    print(f"First item: {result[0]}")
    print(f"\nFirst item attributes: {dir(result[0])}")
    
    # Try different ways to access text
    print(f"\nTrying .text: {result[0].text}")
    print(f"Trying ['text']: {result[0]['text'] if hasattr(result[0], '__getitem__') else 'N/A'}")
    
    # Build transcript
    transcript = " ".join([item.text for item in result[:10]])
    print(f"\nTranscript preview: {transcript[:200]}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
