# Agentic AI Interview Platform - Backend

A FastAPI backend for conducting AI-powered mock technical interviews using AutoGen agents.

## Features

- **Multi-Agent System**: 7 specialized AI agents coordinating through AutoGen
- **Real-time Communication**: WebSocket support for live interviews
- **Memory System**: FAISS for embeddings, PostgreSQL for metadata
- **Document Parsing**: Support for PDF, DOCX, and TXT resumes

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- OpenAI API key

### Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and database URL
```

4. Start PostgreSQL (or use Docker):
```bash
docker run -d --name interview_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=interview_db \
  -p 5432:5432 postgres:15-alpine
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. API docs at `/docs`.

## API Endpoints

### REST

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/session/start` | Create new interview session |
| GET | `/session/{id}` | Get session details |
| POST | `/upload/resume` | Upload and parse resume |
| POST | `/upload/jd` | Upload job description |
| POST | `/interview/opt-in-memory` | Toggle memory storage |
| GET | `/interview/report/{id}` | Get final report |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws/interview/{session_id}` | Live interview connection |

#### WebSocket Messages

**Client → Server:**
- `{"type": "start"}` - Start interview
- `{"type": "answer", "data": {"text": "..."}}` - Submit answer
- `{"type": "ready"}` - Ready for next question
- `{"type": "voice_toggle", "data": {"enabled": true}}` - Toggle voice mode

**Server → Client:**
- `new_question` - New interview question
- `followup` - Follow-up question
- `score_update` - Real-time score update
- `phase_update` - Interview phase change
- `time_remaining` - Timer update
- `feedback` - Final feedback report

## Architecture

```
app/
├── agents/          # AutoGen agent implementations
├── api/             # FastAPI routes and WebSocket
├── core/            # Config and database setup
├── memory/          # FAISS and PostgreSQL stores
├── models/          # SQLAlchemy models
├── orchestration/   # Interview flow management
├── schemas/         # Pydantic schemas
└── services/        # LLM and document services
```

## Agents

1. **Orchestrator**: Controls interview flow and timing
2. **Resume Analyzer**: Analyzes resume, detects seniority
3. **Question Generator**: Creates theory/system design questions
4. **Follow-up Agent**: Probes for deeper understanding
5. **Evaluation Agent**: Scores answers (0-10)
6. **Memory Agent**: Manages data persistence
7. **Feedback Agent**: Generates final report

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `FAISS_INDEX_PATH` | Path for FAISS index | No (default: ./faiss_index) |
