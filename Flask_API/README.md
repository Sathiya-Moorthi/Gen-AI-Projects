# Flask API Projects

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

Simple Flask applications and API examples demonstrating RESTful API development patterns.

## Project Structure

```
Flask_API/
├── scripts/
│   ├── basic_calculator_app.py      # Calculator API with basic operations
│   ├── flask_math_operation_app.py  # Extended math operations API
│   └── flask_structure.py           # Flask project structure example
├── output files/                    # API response examples and logs
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation

1. Navigate to this directory:
   ```bash
   cd Flask_API
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## API Documentation

### Basic Calculator App

**Endpoint:** `POST /calculate`

Performs basic arithmetic operations.

| Parameter | Type | Description |
|-----------|------|-------------|
| `num1` | float | First operand |
| `num2` | float | Second operand |
| `operation` | string | One of: `add`, `subtract`, `multiply`, `divide` |

**Example Request:**
```bash
curl -X POST http://localhost:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1": 10, "num2": 5, "operation": "add"}'
```

**Example Response:**
```json
{
  "result": 15,
  "operation": "add",
  "status": "success"
}
```

### Math Operations App

**Endpoint:** `POST /math`

Extended mathematical operations including power, modulo, and more.

| Operation | Description |
|-----------|-------------|
| `add` | Addition |
| `subtract` | Subtraction |
| `multiply` | Multiplication |
| `divide` | Division |
| `power` | Exponentiation |
| `modulo` | Remainder |

## Running the Applications

1. **Start the Calculator API:**
   ```bash
   python scripts/basic_calculator_app.py
   ```
   Server runs at: `http://localhost:5000`

2. **Start the Math Operations API:**
   ```bash
   python scripts/flask_math_operation_app.py
   ```

## Configuration

Default configuration runs in development mode. For production:

```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.
