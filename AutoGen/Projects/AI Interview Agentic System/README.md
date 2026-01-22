# Agentic AI Interview Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A portfolio-grade mock technical interview system powered by **AutoGen agents** and **GPT-4o**. This platform demonstrates advanced agentic AI patterns with a multi-agent architecture that conducts realistic technical interviews.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)

## Overview

This platform conducts AI-powered technical interviews that:

- **Analyze** your resume to detect seniority level (Junior/Mid/Senior)
- **Generate** personalized theory and system design questions
- **Adapt** follow-up questions based on your responses
- **Score** in real-time across three dimensions
- **Produce** comprehensive feedback reports with learning roadmaps

### Key Differentiators

| Feature | Description |
|---------|-------------|
| **Multi-Agent System** | 7 specialized AI agents coordinating through AutoGen |
| **Transparent Process** | Full visibility into AI reasoning and scoring |
| **No Coding Questions** | Focus on theory, system design, and real-world tradeoffs |
| **Learning-Focused** | Constructive feedback, not just pass/fail |

## Features

### Interview Capabilities

- **Resume Analysis**: Automatic seniority detection, strengths/gaps identification
- **Adaptive Questions**: Questions tailored to your profile and role
- **Follow-up Probing**: Deeper questions for vague or incomplete answers
- **Real-time Scoring**: Live visibility into your performance
- **Comprehensive Reports**: Detailed feedback with actionable learning paths

### Technical Features

- **WebSocket Communication**: Real-time interview interaction
- **Voice Mode Support**: Toggle between text and voice input
- **Session Persistence**: Optional memory for cross-session learning
- **RESTful API**: Complete API documentation with Swagger UI

## Architecture

```
+-------------------------------------------------------------+
|                    Frontend (React/Vite)                     |
|    Upload Resume -> JD -> Start Interview -> View Report     |
+---------------------------+---------------------------------+
                            | REST + WebSocket
+---------------------------v---------------------------------+
|                    Backend (FastAPI)                         |
|  +-------------------------------------------------------+  |
|  |               AutoGen Agent System                     |  |
|  |  +-------------+  +----------------+  +--------------+ |  |
|  |  | Orchestrator|->| Resume Analyzer|->| Question Gen | |  |
|  |  +-------------+  +----------------+  +--------------+ |  |
|  |        |                                     |         |  |
|  |        v                                     v         |  |
|  |  +-------------+  +----------------+  +--------------+ |  |
|  |  |  Feedback   |<-|   Evaluation   |<-| Follow-up    | |  |
|  |  +-------------+  +----------------+  +--------------+ |  |
|  +-------------------------------------------------------+  |
|                            |                                 |
|  +-------------------------------------------------------+  |
|  |                 Memory System                          |  |
|  |    FAISS (Embeddings)  <->  SQLite/PostgreSQL          |  |
|  +-------------------------------------------------------+  |
+-------------------------------------------------------------+
```

### Agent Responsibilities

| Agent | Role |
|-------|------|
| **Orchestrator** | Controls interview flow, timing, and state management |
| **Resume Analyzer** | Extracts skills, detects seniority, identifies focus areas |
| **Question Generator** | Creates theory and system design questions |
| **Follow-up Agent** | Probes for deeper understanding on vague answers |
| **Evaluation Agent** | Scores responses across three dimensions |
| **Memory Agent** | Manages FAISS embeddings and session persistence |
| **Feedback Agent** | Generates comprehensive reports and recommendations |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

### Option 1: Local Development (Recommended for Development)

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/ai-interview-platform.git
cd ai-interview-platform
```

**2. Set up the backend:**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

**3. Configure environment:**
```bash
# Create .env file in project root
cp .env.example .env

# Edit .env with your credentials
# Required: OPENAI_API_KEY
```

**4. Start the backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0
```

**5. Start the frontend (new terminal):**
```bash
cd frontend
npm install
npm run dev
```

**6. Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Docker Compose

```bash
# Start all services
docker-compose up --build

# Access
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

## Project Structure

```
ai-interview-platform/
├── .github/                    # GitHub workflows and templates
│   ├── workflows/
│   │   └── ci.yml             # CI/CD pipeline
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── agents/            # AutoGen agent implementations
│   │   ├── api/               # REST routes and WebSocket
│   │   │   ├── routes/        # API route handlers
│   │   │   └── websocket.py   # WebSocket handler
│   │   ├── core/              # Config and database
│   │   ├── memory/            # FAISS and session stores
│   │   ├── models/            # SQLAlchemy models
│   │   ├── orchestration/     # Interview flow management
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # LLM and document services
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom React hooks
│   │   └── services/          # API client
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── README.md
├── .env.example               # Environment template
├── .gitignore
├── docker-compose.yml
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Database (SQLite for local dev, PostgreSQL for production)
DATABASE_URL=sqlite:///./interview.db
# DATABASE_URL=postgresql://user:pass@localhost:5432/interview_db

# Optional
FAISS_INDEX_PATH=./faiss_index
```

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (secrets) |
| `backend/app/core/config.py` | Backend configuration |
| `frontend/vite.config.js` | Frontend build configuration |
| `docker-compose.yml` | Container orchestration |

## API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/session/start` | Create new interview session |
| `GET` | `/session/{id}` | Get session details |
| `POST` | `/upload/resume` | Upload and analyze resume |
| `POST` | `/upload/jd` | Submit job description |
| `POST` | `/interview/opt-in-memory` | Toggle memory persistence |
| `GET` | `/interview/report/{id}` | Get final interview report |

### WebSocket

Connect to `/ws/interview/{session_id}` for real-time interview communication.

**Client Messages:**
```json
{"type": "start"}
{"type": "answer", "data": {"text": "Your answer here"}}
{"type": "ready"}
{"type": "voice_toggle", "data": {"enabled": true}}
```

**Server Events:**
- `new_question` - Interview question
- `followup` - Follow-up probe
- `score_update` - Real-time scoring
- `phase_update` - Interview phase change
- `feedback` - Final report

For complete API documentation, see the [Backend README](backend/README.md) or visit `/docs` when running.

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | Web framework |
| AutoGen | Multi-agent orchestration |
| OpenAI GPT-4o | Language model |
| SQLAlchemy | ORM |
| FAISS | Vector similarity search |
| WebSockets | Real-time communication |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| Vite | Build tool |
| WebSocket API | Real-time updates |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |

## Scoring System

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **Technical** | 0-10 | Accuracy, depth, understanding of concepts |
| **Design** | 0-10 | Problem decomposition, tradeoffs, scalability |
| **Communication** | 0-10 | Clarity, structure, use of examples |

**Note:** Grammar and nervousness are NOT penalized.

### Recommendations

| Rating | Criteria |
|--------|----------|
| **Hire** | Consistent scores 7+, strong fundamentals |
| **Borderline** | Mixed scores (5-7), potential but has gaps |
| **No-Hire** | Scores below 5, significant knowledge gaps |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest` for backend, `npm test` for frontend)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with AutoGen and GPT-4o** | [Report Bug](../../issues) | [Request Feature](../../issues)
