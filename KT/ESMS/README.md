# Employee Separation Management System (ESMS)

A Flask-based backend for managing employee off-boarding, including separation initiation, manager approvals, checklist tracking, and handover scheduling.

## Features
- **Role-Based Access Control (RBAC)**: Secure endpoints for Employees, Managers, and Admins.
- **Separation Workflow**: Initiate separation, approve/reject requests.
- **Checklists**: Track department-wise clearance (IT, Finance, etc.).
- **Scheduling**: Mock integration with Google Calendar for handover events.
- **Notifications**: Mock email notifications for key events.

## Tech Stack
- Python 3.x
- Flask
- SQLAlchemy (SQLite for dev)
- JWT for Authentication

## Setup
See [QUICKSTART.md](QUICKSTART.md) for installation and running instructions.

## API Documentation
See [API_DOCS.md](API_DOCS.md) for detailed API endpoints and usage.
