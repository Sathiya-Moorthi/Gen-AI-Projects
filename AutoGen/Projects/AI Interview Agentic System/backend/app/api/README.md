# API Layer

This directory contains the REST API routes and WebSocket handlers for the interview platform.

## Structure

```
api/
├── routes/
│   ├── session.py      # Session management endpoints
│   ├── upload.py       # Resume and JD upload endpoints
│   ├── interview.py    # Interview configuration endpoints
│   └── report.py       # Report retrieval endpoints
├── websocket.py        # WebSocket handler for live interviews
└── __init__.py
```

## REST API Endpoints

### Session Management (`routes/session.py`)

#### `POST /session/start`
Creates a new interview session.

**Response:**
```json
{
  "session_id": "uuid-here",
  "status": "created",
  "message": "Session created successfully"
}
```

#### `GET /session/{session_id}`
Retrieves session details.

**Response:**
```json
{
  "session_id": "uuid-here",
  "status": "created",
  "current_phase": "setup",
  "has_resume": false,
  "has_jd": false,
  "memory_opt_in": false
}
```

---

### Upload Endpoints (`routes/upload.py`)

#### `POST /upload/resume`
Uploads and parses resume file (PDF, DOCX, TXT).

**Form Data:**
- `session_id`: UUID
- `file`: Resume file

**Response:**
```json
{
  "session_id": "uuid-here",
  "resume_received": true,
  "detected_seniority": "mid",
  "strengths": ["Python", "FastAPI"],
  "gaps": ["Kubernetes"],
  "focus_areas": ["System Design"]
}
```

#### `POST /upload/jd`
Submits job description and role.

**Form Data:**
- `session_id`: UUID
- `job_description`: string
- `role`: string

**Response:**
```json
{
  "session_id": "uuid-here",
  "jd_received": true,
  "role": "Senior Software Engineer"
}
```

---

### Interview Configuration (`routes/interview.py`)

#### `POST /interview/opt-in-memory`
Toggles memory storage for the session.

**Request:**
```json
{
  "opt_in": true
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "memory_opt_in": true,
  "message": "Memory storage enabled"
}
```

---

### Report Retrieval (`routes/report.py`)

#### `GET /interview/report/{session_id}`
Retrieves final interview report.

**Response:**
```json
{
  "session_id": "uuid-here",
  "status": "completed",
  "detected_seniority": "mid",
  "strengths": ["System thinking", "Clear communication"],
  "gaps": ["Kubernetes concepts"],
  "scores": {
    "technical": 7.5,
    "design": 8.0,
    "communication": 9.0
  },
  "qa_history": [...],
  "final_report": "...",
  "recommendation": "Hire",
  "skill_roadmap": [...],
  "duration_minutes": 35,
  "started_at": "2024-01-01T10:00:00",
  "ended_at": "2024-01-01T10:35:00"
}
```

---

## WebSocket Connection (`websocket.py`)

### Endpoint: `/ws/interview/{session_id}`

Real-time bidirectional communication during interviews.

### Client → Server Messages

#### Start Interview
```json
{"type": "start"}
```

#### Submit Answer
```json
{
  "type": "answer",
  "data": {
    "text": "Your answer here..."
  }
}
```

#### Ready for Next Question
```json
{"type": "ready"}
```

#### Toggle Voice Mode
```json
{
  "type": "voice_toggle",
  "data": {
    "enabled": true
  }
}
```

---

### Server → Client Events

#### Connected
Sent immediately after connection.
```json
{
  "type": "connected",
  "data": {
    "session_id": "uuid-here",
    "status": "created",
    "phase": "setup",
    "seniority": "mid"
  }
}
```

#### Interview Introduction
```json
{
  "type": "intro",
  "data": {
    "message": "Welcome to your interview...",
    "phase": "intro",
    "focus_areas": [...]
  }
}
```

#### New Question
```json
{
  "type": "new_question",
  "data": {
    "question": "Explain CAP theorem...",
    "difficulty": "medium",
    "topic": "Distributed Systems",
    "explanation": "This tests your understanding of...",
    "question_number": 1,
    "time_remaining": 2100
  }
}
```

#### Follow-up Question
```json
{
  "type": "followup",
  "data": {
    "question": "Can you elaborate on...",
    "reason": "Answer was vague on consistency guarantees",
    "time_remaining": 1980
  }
}
```

#### Score Update
```json
{
  "type": "score_update",
  "data": {
    "current_scores": {
      "technical": 8,
      "design": 7,
      "communication": 9
    },
    "running_average": {
      "technical": 7.5,
      "design": 7.2,
      "communication": 8.8
    },
    "feedback": "Good explanation with clear examples",
    "strengths": ["Clear communication"],
    "improvements": ["Could explain CAP in more depth"]
  }
}
```

#### Phase Update
```json
{
  "type": "phase_update",
  "data": {
    "phase": "evaluation",
    "message": "Evaluating your overall performance..."
  }
}
```

#### Time Remaining
Sent every 30 seconds.
```json
{
  "type": "time_remaining",
  "data": {
    "seconds": 1800,
    "formatted": "30:00"
  }
}
```

#### Final Feedback
```json
{
  "type": "feedback",
  "data": {
    "report": "Overall, you demonstrated...",
    "recommendation": "Hire",
    "skill_roadmap": [...],
    "final_scores": {
      "technical": 7.5,
      "design": 8.0,
      "communication": 9.0
    },
    "phase": "completed"
  }
}
```

#### Error
```json
{
  "type": "error",
  "data": {
    "message": "Session not found",
    "code": 4004
  }
}
```

---

## Error Handling

### HTTP Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | Invalid file format |
| 404 | Not Found | Session doesn't exist |
| 500 | Server Error | Database connection failed |

### WebSocket Close Codes

| Code | Reason |
|------|--------|
| 1000 | Normal closure |
| 4000 | Upload resume and JD first |
| 4001 | Invalid session ID format |
| 4003 | Origin not allowed (CORS) |
| 4004 | Session not found |

---

## CORS Configuration

Allowed origins are defined in `app/main.py`:
- `http://localhost:5173`
- `http://localhost:5174`
- `http://localhost:3000`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:5174`
- `http://127.0.0.1:3000`

---

## Testing

### Manual Testing with cURL

```bash
# Start session
curl -X POST http://localhost:8000/session/start

# Upload resume
curl -X POST http://localhost:8000/upload/resume \
  -F "session_id=your-uuid" \
  -F "file=@resume.pdf"

# Get session
curl http://localhost:8000/session/your-uuid
```

### WebSocket Testing

Use `wscat` for WebSocket testing:
```bash
npm install -g wscat
wscat -c ws://localhost:8000/ws/interview/your-uuid
```

---

## Implementation Notes

1. **Session Validation:** All endpoints validate that the session exists before processing
2. **File Upload:** Resume parser supports PDF, DOCX, and TXT formats
3. **WebSocket State:** Connection manager maintains active connections and interview flows
4. **Database Sessions:** Each request creates a new DB session via dependency injection
5. **Error Logging:** All errors are logged with context for debugging

---

## Dependencies

- `FastAPI` - Web framework
- `SQLAlchemy` - Database ORM
- `Pydantic` - Request/response validation
- `python-multipart` - File upload support

For more details on agent coordination, see `/backend/app/orchestration/`.
