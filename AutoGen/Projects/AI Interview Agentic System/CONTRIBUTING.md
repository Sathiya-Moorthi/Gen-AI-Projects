# Contributing to Agentic AI Interview Platform

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Docker (optional, for containerized development)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/ai-interview-platform.git
   cd ai-interview-platform
   ```

2. **Set up Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

**Branch Naming Conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation as needed

### 3. Test Your Changes

**Backend:**
```bash
cd backend
pytest
# or with coverage
pytest --cov=app --cov-report=html
```

**Frontend:**
```bash
cd frontend
npm test
npm run build  # Ensure build succeeds
```

### 4. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add resume parsing for DOCX files"
git commit -m "fix: resolve WebSocket connection timeout"
git commit -m "docs: update API documentation"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `isort` for import sorting

**Formatting:**
```bash
cd backend
black app/
isort app/
flake8 app/
```

### JavaScript/React (Frontend)

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks
- Use meaningful variable and function names
- Add PropTypes or TypeScript types

**Formatting:**
```bash
cd frontend
npm run lint
npm run format  # if configured
```

## Project Structure

### Backend (`backend/app/`)

```
app/
├── agents/          # AutoGen agent implementations
├── api/             # FastAPI routes and WebSocket
├── core/            # Configuration and database
├── memory/          # FAISS and session stores
├── models/          # SQLAlchemy models
├── orchestration/   # Interview flow management
├── schemas/         # Pydantic schemas
└── services/        # LLM and document services
```

### Frontend (`frontend/src/`)

```
src/
├── components/      # Reusable UI components
├── pages/           # Page components
├── hooks/           # Custom React hooks
└── services/        # API client
```

## Testing Guidelines

### Backend Tests

- Write unit tests for all new functions
- Use `pytest` and `pytest-asyncio` for async tests
- Aim for >80% code coverage
- Test both success and error cases

**Example:**
```python
import pytest
from app.services.llm_service import LLMService

def test_llm_service_initialization():
    service = LLMService()
    assert service is not None
```

### Frontend Tests

- Test component rendering
- Test user interactions
- Test API integration (use mocks)
- Test error handling

## Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Use Google-style docstrings for Python
- Use JSDoc comments for JavaScript

**Python Example:**
```python
def analyze_resume(resume_text: str) -> dict:
    """
    Analyzes a resume to extract skills and detect seniority level.
    
    Args:
        resume_text: The text content of the resume
        
    Returns:
        Dictionary containing skills, seniority, and focus areas
    """
    pass
```

### API Documentation

- Update API route docstrings
- FastAPI automatically generates docs at `/docs`
- Keep examples up to date

## Pull Request Process

1. **Update Documentation**
   - Update README if needed
   - Add/update docstrings
   - Update API documentation

2. **Add Tests**
   - Unit tests for new functionality
   - Integration tests if applicable
   - Update existing tests if needed

3. **Ensure CI Passes**
   - All tests pass
   - Linting passes
   - Build succeeds

4. **Write Clear PR Description**
   - Describe what changes were made
   - Explain why the changes were needed
   - Link related issues
   - Add screenshots if UI changes

5. **Request Review**
   - Tag relevant maintainers
   - Address review comments promptly
   - Keep PR focused (one feature/fix per PR)

## Review Process

- Maintainers will review within 48 hours
- Address feedback promptly
- Be open to suggestions
- Ask questions if something is unclear

## Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error logs/screenshots

## Suggesting Features

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- Clear description
- Problem statement
- Proposed solution
- Use cases

## Questions?

- Open an issue for discussion
- Check existing issues and PRs
- Review the documentation

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md (if created)
- Credited in release notes
- Acknowledged in the project README

Thank you for contributing! 🎉

