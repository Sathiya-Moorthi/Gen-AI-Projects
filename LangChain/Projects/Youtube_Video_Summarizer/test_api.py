import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR: OPENAI_API_KEY not found in environment")
    print("Please create a .env file with your API key")
else:
    print(f"API Key found: {api_key[:10]}...")
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say hello"}
            ]
        )
        print("SUCCESS! API is working")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"ERROR: {e}")
