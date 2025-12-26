# Quickstart Guide

## Prerequisites
- Python 3.8+
- pip

## Installation

1. Clone the repository (if applicable) or navigate to the project directory:
   ```bash
   cd ESMS
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
   *Note: If `flask db init` fails, ensure `FLASK_APP=run.py` is set.*

## Running the Application

1. Start the server:
   ```bash
   python run.py
   ```
   The server will start at `http://127.0.0.1:5000`.

## Testing

1. **Register a User**:
   ```bash
   curl -X POST http://127.0.0.1:5000/auth/register -H "Content-Type: application/json" -d "{\"email\": \"emp@test.com\", \"password\": \"pass\", \"role\": \"Employee\"}"
   ```

2. **Login**:
   ```bash
   curl -X POST http://127.0.0.1:5000/auth/login -H "Content-Type: application/json" -d "{\"email\": \"emp@test.com\", \"password\": \"pass\"}"
   ```
   Copy the `token` from the response.

3. **Initiate Separation**:
   ```bash
   curl -X POST http://127.0.0.1:5000/separation/initiate -H "Authorization: Bearer <TOKEN>"
   ```
