# AutoGen Projects

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AutoGen](https://img.shields.io/badge/AutoGen-Latest-purple.svg)](https://microsoft.github.io/autogen/)

Multi-agent systems and workflows built with Microsoft AutoGen framework for conversational AI and task automation.

## Project Structure

```
AutoGen/
├── Projects/           # Complex multi-file applications
│   └── Content Workflow (Flask/Streamlit integration)
├── Workflows/          # Standalone agent scripts
│   ├── Weather Agent
│   └── Image Agent
├── .gitignore
└── README.md
```

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           AutoGen Framework             │
├─────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌───────┐ │
│  │ Assistant│◄─►│  User    │◄─►│ Tools │ │
│  │  Agent   │  │  Proxy   │  │       │ │
│  └──────────┘  └──────────┘  └───────┘ │
├─────────────────────────────────────────┤
│            LLM Backend (GPT-4)          │
└─────────────────────────────────────────┘
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (or compatible LLM)

## Installation

1. Navigate to this directory:
   ```bash
   cd AutoGen
   ```

2. Install dependencies:
   ```bash
   pip install pyautogen
   ```

3. Configure API key:
   ```bash
   export OPENAI_API_KEY=your_api_key
   ```

## Usage

### Running Workflows
```bash
cd Workflows
python weather_agent.py
```

### Running Projects
```bash
cd Projects
# Follow instructions in Projects/README.md
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **AssistantAgent** | AI agent that can use tools and generate responses |
| **UserProxyAgent** | Represents user, can execute code and provide feedback |
| **GroupChat** | Multi-agent conversation management |
| **Tool Use** | Function calling for external actions |

## Configuration

Create `OAI_CONFIG_LIST` file:
```json
[
    {
        "model": "gpt-4",
        "api_key": "your-api-key"
    }
]
```

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.
