# AutoGen Agents

This directory contains the specialized AI agents that power the interview system. Each agent has a specific responsibility in the interview workflow.

## Agent Overview

### 1. **Orchestrator Agent** (`orchestrator.py`)
**Role:** Interview Flow Controller

**Responsibilities:**
- Controls interview timing (30-45 minutes)
- Maintains interview state and phase transitions
- Coordinates other agents
- Ensures transparency with candidates
- Manages question count and pacing

**Key Methods:**
- `start_interview()` - Initializes the interview
- `transition_phase()` - Moves between interview phases
- `should_end_interview()` - Determines if interview should conclude
- `get_time_remaining()` - Returns remaining time

---

### 2. **Resume Analyzer Agent** (`resume_analyzer.py`)
**Role:** Profile Analysis

**Responsibilities:**
- Parses resume text
- Detects seniority level (Junior/Mid/Senior)
- Identifies candidate strengths
- Finds skill gaps relative to job description
- Determines interview focus areas

**Output:**
```python
{
    "seniority": "mid",
    "strengths": ["Python", "FastAPI", "System Design"],
    "gaps": ["Kubernetes", "CI/CD"],
    "focus_areas": ["Microservices", "Scalability"]
}
```

---

### 3. **Question Generator Agent** (`question_generator.py`)
**Role:** Question Creation

**Responsibilities:**
- Generates theory and system design questions
- Adjusts difficulty based on seniority
- Avoids coding questions (per design principles)
- Ensures questions match focus areas
- Prevents duplicate questions

**Question Types:**
- Theory (e.g., "Explain CAP theorem")
- System Design (e.g., "Design a rate limiter")
- Real-world Tradeoffs (e.g., "SQL vs NoSQL for this use case")

---

### 4. **Follow-up Agent** (`followup.py`)
**Role:** Depth Probing

**Responsibilities:**
- Detects vague or incomplete answers
- Asks clarifying questions
- Probes for deeper understanding
- Limits follow-ups to 2 per question
- Helps candidates elaborate their reasoning

**Triggers:**
- Vague terminology ("it depends", "usually")
- Missing details in system design
- Unclear reasoning

---

### 5. **Evaluation Agent** (`evaluation.py`)
**Role:** Answer Scoring

**Responsibilities:**
- Scores answers across three dimensions
- Provides constructive feedback
- Tracks running averages
- Does NOT penalize grammar or accent

**Scoring Dimensions (0-10):**
| Dimension | Measures |
|-----------|----------|
| **Technical** | Accuracy, depth, concept understanding |
| **Design** | Problem decomposition, tradeoffs, scalability |
| **Communication** | Clarity, structure, use of examples |

---

### 6. **Memory Agent** (`memory_agent.py`)
**Role:** Data Persistence

**Responsibilities:**
- Stores interview data to FAISS (embeddings)
- Manages PostgreSQL metadata
- Handles opt-in memory storage
- Retrieves past performance data
- Enables learning from previous sessions

**Storage:**
- FAISS: Question/answer embeddings for similarity search
- PostgreSQL: Session metadata, scores, reports

---

### 7. **Feedback Agent** (`feedback.py`)
**Role:** Report Generation

**Responsibilities:**
- Generates comprehensive feedback reports
- Produces hiring recommendations
- Creates skill-gap learning roadmaps
- Maintains honest, constructive tone

**Recommendations:**
| Rating | Criteria |
|--------|----------|
| **Hire** | Consistent scores 7+, strong fundamentals |
| **Borderline** | Mixed scores (5-7), potential but has gaps |
| **No-Hire** | Scores below 5, significant knowledge gaps |

**Report Sections:**
1. Performance summary
2. Strengths demonstrated
3. Areas for improvement
4. Skill roadmap with resources

---

## Agent Communication Flow

```
Start Interview
       ↓
Orchestrator → Resume Analyzer → Profile Analysis
       ↓
Orchestrator → Question Generator → New Question
       ↓
[Candidate Answers]
       ↓
Evaluation Agent → Score Answer
       ↓
Follow-up Agent → Check if follow-up needed
       ↓         (if yes, ask follow-up)
       ↓         (if no, next question)
Orchestrator → Check if should end
       ↓         (if yes, generate feedback)
       ↓         (if no, generate next question)
Feedback Agent → Final Report
       ↓
Memory Agent → Store (if opted in)
```

---

## Design Principles

1. **Transparency:** Candidates see all scores and reasoning in real-time
2. **Learning Focus:** Constructive feedback, not just pass/fail
3. **No Coding:** Focus on theory, design, and problem-solving
4. **Adaptive:** Questions match candidate's profile and level
5. **Respect:** No penalties for nervousness, grammar, or accent

---

## Configuration

Agents are configured via environment variables and `app/core/config.py`:

```python
# Interview settings
DEFAULT_DURATION = 35  # minutes
MAX_QUESTIONS = 8
MAX_FOLLOWUPS_PER_QUESTION = 2

# Scoring
MIN_SCORE = 0
MAX_SCORE = 10
```

---

## Testing

Each agent should be testable independently:

```bash
# Run agent tests
pytest tests/agents/test_orchestrator.py
pytest tests/agents/test_evaluation.py
```

---

## Future Enhancements

- [ ] Multi-language support
- [ ] Voice analysis integration
- [ ] Adaptive difficulty within interviews
- [ ] Team interview mode (multiple agents as interviewers)
- [ ] Custom agent templates for specific roles

---

For implementation details, see the individual agent files and `app/orchestration/interview_flow.py` for the coordination logic.
