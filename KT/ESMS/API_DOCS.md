# API Documentation

## Authentication

### Register
- **Endpoint**: `POST /auth/register`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "role": "Employee", // Employee, Direct_Manager, Separation_Manager, IT, Finance
    "department": "IT", // Optional
    "manager_id": 1 // Optional
  }
  ```

### Login
- **Endpoint**: `POST /auth/login`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**: `{ "token": "jwt_token", "role": "Employee" }`

## Separation Workflow

### Initiate Separation
- **Endpoint**: `POST /separation/initiate`
- **Role**: `Employee`
- **Response**: `{ "message": "Separation initiated", "case_id": 1 }`

### My Status
- **Endpoint**: `GET /separation/my-status`
- **Role**: `Employee`
- **Response**: Separation case details.

### Approve Separation
- **Endpoint**: `POST /separation/approve`
- **Role**: `Direct_Manager`, `Separation_Manager`
- **Body**:
  ```json
  {
    "case_id": 1,
    "action": "Approved" // or "Rejected"
  }
  ```

## Checklists

### Get Checklist
- **Endpoint**: `GET /checklist/<case_id>`
- **Role**: Authenticated User (involved in case)

### Update Checklist Item
- **Endpoint**: `PUT /checklist/<item_id>`
- **Role**: Department Owner (e.g., IT for IT items)
- **Body**:
  ```json
  {
    "completed": true
  }
  ```

## Scheduling

### Create Handover Event
- **Endpoint**: `POST /scheduling/event`
- **Role**: Authenticated User
- **Body**:
  ```json
  {
    "case_id": 1,
    "title": "Handover Meeting",
    "start_time": "2023-10-27T10:00:00",
    "end_time": "2023-10-27T11:00:00"
  }
  ```

## Hierarchy

### Get Team
- **Endpoint**: `GET /hierarchy/team`
- **Role**: `Direct_Manager`
- **Response**: Recursive list of subordinates.
