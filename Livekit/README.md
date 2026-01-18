# 🤖 LiveKit Voice Agent - JARVIS

A real-time voice AI agent powered by **LiveKit** that emulates **JARVIS** from the Iron Man universe. Built with OpenAI's speech-to-text, GPT language model, and text-to-speech capabilities.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LiveKit](https://img.shields.io/badge/LiveKit-Agents-purple.svg)](https://livekit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## ✨ Features

- 🎤 **Real-time Voice Interaction**: Full-duplex voice conversation with instant responses
- 🧠 **JARVIS Personality**: Hyper-intelligent, calm, with dry wit (addresses you as "Sir")
- 🔊 **Voice Activity Detection**: Silero VAD for accurate speech detection
- 🎙️ **OpenAI Integration**: STT, LLM (GPT), and TTS all powered by OpenAI
- ⚡ **Low Latency**: Optimized for responsive voice interactions

## 🏗️ Architecture

```
Voice_Agent/
├── agent.py           # Main voice agent with JARVIS personality
├── generate_token.py  # Utility to generate LiveKit access tokens
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- [LiveKit Cloud Account](https://cloud.livekit.io/) or local LiveKit server
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sathiya-Moorthi/Voice_Agent.git
   cd Voice_Agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your credentials
   ```

## ⚙️ Configuration

Create a `.env` file with the following variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `LIVEKIT_API_KEY` | Your LiveKit API key | ✅ |
| `LIVEKIT_API_SECRET` | Your LiveKit API secret | ✅ |
| `LIVEKIT_URL` | LiveKit server URL (e.g., `wss://your-project.livekit.cloud`) | ✅ |
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ |

## 🎮 Usage

### Running the Agent

Start the voice agent server:
```bash
python agent.py dev
```

The agent will connect to your LiveKit server and wait for participants to join.

### Generating Test Tokens

To generate a test access token for joining the room:
```bash
python generate_token.py
```

### Testing with LiveKit Playground

1. Go to [LiveKit Playground](https://agents-playground.livekit.io/)
2. Enter your LiveKit URL and generated token
3. Start talking to JARVIS!

## 📦 Dependencies

- `livekit-agents` - LiveKit Agents framework
- `livekit-plugins-openai` - OpenAI integration (STT, LLM, TTS)
- `livekit-plugins-silero` - Silero VAD for voice activity detection
- `python-dotenv` - Environment variable management

## 🔧 Customization

### Changing the Personality

Edit the `instructions` in the `Assistant` class in `agent.py`:

```python
class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
                YOUR CUSTOM PERSONALITY HERE
            """,
        )
```

### Changing the Greeting

Modify the initial greeting in the `entrypoint` function:

```python
await session.say("Your custom greeting here", allow_interruptions=True)
```

## 🙏 Acknowledgments

- [LiveKit](https://livekit.io/) for the real-time communication framework
- [OpenAI](https://openai.com/) for STT, LLM, and TTS capabilities
- Inspired by JARVIS from Marvel's Iron Man

---

**"At your service, Sir." 🤵**
