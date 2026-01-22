# AutoGen Projects

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AutoGen](https://img.shields.io/badge/AutoGen-Latest-purple.svg)](https://microsoft.github.io/autogen/)

Multi-agent systems and workflows built with Microsoft AutoGen framework for conversational AI and task automation.

## Project Structure

```
AutoGen/
├── Projects/                    # Complex multi-agent applications
│   ├── AI Interview Agentic System/    # Mock interview platform (7 agents, FastAPI+React)
│   └── Multi Agents System/            # Content generation workflow (4 agents, Flask+Streamlit)
├── Workflows/                   # Standalone agent examples
│   ├── first_agent.py          # Basic AutoGen introduction
│   ├── weather_agent.py        # Weather tool integration
│   └── image_agent.py          # Image generation agent
├── .gitignore
└── README.md
```

## Featured Projects

### 🎯 AI Interview Agentic System
A portfolio-grade mock technical interview platform powered by **7 specialized AutoGen agents** and GPT-4o. Features resume analysis, adaptive questioning, real-time scoring, and comprehensive feedback reports.

**Tech Stack:** FastAPI, React, WebSockets, FAISS, SQLAlchemy
**Key Features:**
- Automatic seniority detection from resume
- Adaptive theory and system design questions
- Real-time scoring across 3 dimensions
- Learning-focused feedback with roadmaps

[View Project →](./Projects/AI%20Interview%20Agentic%20System/)

### ✍️ Multi Agents System
Publication-ready content generation with **4 sequential agents** (Research → Writer → SEO → Scorer). Integrates SERP API for real-time research and enforces strict quality thresholds.

**Tech Stack:** Flask, Streamlit, AutoGen, SERP API
**Key Features:**
- Real-time research integration
- SEO optimization (score ≥ 80)
- Quality control (overall ≥ 85)
- Interactive UI with progress tracking

[View Project →](./Projects/Multi%20Agents%20System/)

## Standalone Workflows

The `Workflows/` directory contains beginner-friendly examples for learning AutoGen:
- **first_agent.py** - Your first AutoGen agent
- **weather_agent.py** - External API integration with tools
- **image_agent.py** - Image generation capabilities

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

### Running Standalone Workflows
```bash
cd Workflows
python first_agent.py        # Basic agent example
python weather_agent.py      # Weather tool integration
python image_agent.py        # Image generation
```

### Running Projects

**AI Interview Agentic System:**
```bash
cd "Projects/AI Interview Agentic System"
# See project README for full setup
```

**Multi Agents System:**
```bash
cd "Projects/Multi Agents System"
# Backend
python flask_backend_app.py
# Frontend (new terminal)
streamlit run streamlit_frontend_app.py
```

For detailed project setup, see individual project READMEs.

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