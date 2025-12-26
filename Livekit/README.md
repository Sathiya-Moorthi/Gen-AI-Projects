# Livekit Voice Agent

This project contains experiments with Livekit for building voice and video agents.

## 📂 Files
- `agent.py`: Main agent logic (Python).
- `generate_token.py`: Script to generate access tokens.
- `token.txt`: (Excluded) Stores the generated token.

## 🚀 Setup

1.  **Install Dependencies**:
    Ensure you have the required Livekit Python SDK installed.
    ```bash
    pip install livekit-agents livekit-server-sdk-python python-dotenv
    ```

2.  **Environment Variables**:
    Create a `.env` file with your Livekit credentials:
    ```ini
    LIVEKIT_API_KEY=your_key
    LIVEKIT_API_SECRET=your_secret
    LIVEKIT_URL=your_url
    ```

3.  **Run the Agent**:
    ```bash
    python agent.py
    ```
