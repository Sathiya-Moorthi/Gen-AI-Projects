# Pydantic Mastery Learning Path

A hands-on, project-based approach to mastering Pydantic v2 for Data Engineering, DevOps, and GenAI use cases.

## Prerequisites

- Python 3.10+
- Basic understanding of Python type hints
- Familiarity with JSON and APIs

## Projects Overview

| Project | Focus Area | Key Concepts |
|---------|------------|--------------|
| 01 | User Profile Validator | BaseModel, Field validators, Nested models |
| 02 | Configuration Manager | pydantic-settings, Environment variables, SecretStr |
| 03 | Data Pipeline Validator | TypeAdapter, Batch validation, Discriminated unions |
| 04 | LLM Output Validator | JSON schema generation, Lenient parsing |
| 05 | FastAPI Microservice | Request/Response models, OpenAPI integration |

## Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd pydantic-mastery

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run a project
cd projects/01_user_profile
python main.py
```

## Project Structure

```
pydantic-mastery/
├── README.md
├── requirements.txt
├── pyproject.toml
├── projects/
│   ├── 01_user_profile/      # Basic validation fundamentals
│   ├── 02_config_manager/    # Environment configuration
│   ├── 03_data_pipeline/     # Batch data validation
│   ├── 04_llm_validator/     # LLM output parsing
│   └── 05_fastapi_service/   # Full API integration
└── docs/
    └── career_mapping.md     # Career opportunities guide
```

## Learning Path

### Project 1: User Profile Validator
Learn Pydantic fundamentals by building a user registration validator with email validation, password strength checking, and nested address models.

### Project 2: Configuration Manager
Master `pydantic-settings` for type-safe configuration management from environment variables and `.env` files.

### Project 3: Data Pipeline Input Validator
Handle real-world data ingestion with batch validation, error aggregation, and schema versioning.

### Project 4: LLM Output Validator
Parse and validate structured outputs from Large Language Models with graceful error handling.

### Project 5: FastAPI + Pydantic Microservice
Build a production-ready REST API combining all previous concepts.

## Running Tests

```bash
# Run all tests
pytest

# Run tests for a specific project
pytest projects/01_user_profile/

# Run with coverage
pytest --cov=projects
```

## Key Pydantic v2 Features Covered

- `BaseModel` and `Field` configuration
- `@field_validator` and `@model_validator` decorators
- `TypeAdapter` for non-model validation
- `Annotated` validators (`BeforeValidator`, `AfterValidator`)
- Discriminated unions
- `pydantic-settings` for configuration
- JSON schema generation
- Strict vs lax validation modes

## Resources

- [Pydantic v2 Documentation](https://docs.pydantic.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## License

MIT License - Feel free to use this for learning and portfolio purposes.
