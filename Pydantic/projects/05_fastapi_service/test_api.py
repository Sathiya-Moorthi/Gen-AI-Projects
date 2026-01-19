"""
Project 5: FastAPI + Pydantic Microservice - Tests
==================================================

Comprehensive pytest tests for the FastAPI service.

Run with: pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from models import TaskStatus, TaskPriority
from dependencies import reset_database


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test."""
    reset_database()
    yield
    reset_database()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Authentication headers for requests."""
    return {"X-API-Key": "dev-key-123"}


@pytest.fixture
def valid_task_data():
    """Valid task creation data."""
    return {
        "title": "Test Task",
        "description": "A test task description",
        "priority": "high",
        "tags": ["test", "example"]
    }


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data

    def test_health_components(self, client):
        """Test health check returns components."""
        response = client.get("/health")
        data = response.json()

        assert "components" in data
        assert len(data["components"]) > 0

        for component in data["components"]:
            assert "name" in component
            assert "status" in component


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Tests for authentication."""

    def test_no_api_key(self, client):
        """Test request without API key is rejected."""
        response = client.post("/tasks", json={"title": "Test"})
        assert response.status_code == 401

    def test_invalid_api_key(self, client):
        """Test invalid API key is rejected."""
        response = client.post(
            "/tasks",
            json={"title": "Test"},
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 401

    def test_valid_api_key(self, client, auth_headers, valid_task_data):
        """Test valid API key is accepted."""
        response = client.post("/tasks", json=valid_task_data, headers=auth_headers)
        assert response.status_code == 201

    def test_list_without_auth(self, client):
        """Test list endpoint works without auth (read-only)."""
        response = client.get("/tasks")
        assert response.status_code == 200


# ============================================================================
# TASK CRUD TESTS
# ============================================================================

class TestTaskCreate:
    """Tests for task creation."""

    def test_create_task(self, client, auth_headers, valid_task_data):
        """Test creating a valid task."""
        response = client.post("/tasks", json=valid_task_data, headers=auth_headers)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == valid_task_data["title"]
        assert data["status"] == "todo"
        assert "id" in data
        assert "created_at" in data

    def test_create_task_minimal(self, client, auth_headers):
        """Test creating task with minimal data."""
        response = client.post(
            "/tasks",
            json={"title": "Minimal task"},
            headers=auth_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Minimal task"
        assert data["priority"] == "medium"  # Default

    def test_create_task_invalid_title(self, client, auth_headers):
        """Test validation rejects empty title."""
        response = client.post(
            "/tasks",
            json={"title": ""},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_task_invalid_priority(self, client, auth_headers):
        """Test validation rejects invalid priority."""
        response = client.post(
            "/tasks",
            json={"title": "Test", "priority": "invalid"},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_task_with_email(self, client, auth_headers):
        """Test creating task with assignee email."""
        response = client.post(
            "/tasks",
            json={
                "title": "Assigned task",
                "assignee_email": "user@example.com"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        assert response.json()["assignee_email"] == "user@example.com"

    def test_create_task_invalid_email(self, client, auth_headers):
        """Test validation rejects invalid email."""
        response = client.post(
            "/tasks",
            json={
                "title": "Test",
                "assignee_email": "not-an-email"
            },
            headers=auth_headers
        )
        assert response.status_code == 422


class TestTaskList:
    """Tests for task listing."""

    def test_list_tasks(self, client):
        """Test listing tasks."""
        response = client.get("/tasks")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_list_tasks_pagination(self, client):
        """Test pagination parameters."""
        response = client.get("/tasks?page=1&page_size=2")
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) <= 2

    def test_list_tasks_filter_status(self, client):
        """Test filtering by status."""
        response = client.get("/tasks?status=todo")
        assert response.status_code == 200

        data = response.json()
        for item in data["items"]:
            assert item["status"] == "todo"

    def test_list_tasks_filter_priority(self, client):
        """Test filtering by priority."""
        response = client.get("/tasks?priority=high")
        assert response.status_code == 200

        data = response.json()
        for item in data["items"]:
            assert item["priority"] == "high"

    def test_list_tasks_search(self, client):
        """Test search functionality."""
        response = client.get("/tasks?search=authentication")
        assert response.status_code == 200

        data = response.json()
        # Should find the seeded task about authentication
        assert data["total"] >= 1

    def test_list_tasks_computed_fields(self, client):
        """Test response includes computed fields."""
        response = client.get("/tasks")
        data = response.json()

        assert "total_pages" in data
        assert "has_next" in data
        assert "has_prev" in data


class TestTaskGet:
    """Tests for getting a single task."""

    def test_get_task(self, client):
        """Test getting a task by ID."""
        response = client.get("/tasks/1")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == 1
        assert "title" in data
        assert "is_overdue" in data  # Computed field

    def test_get_task_not_found(self, client):
        """Test 404 for non-existent task."""
        response = client.get("/tasks/9999")
        assert response.status_code == 404


class TestTaskUpdate:
    """Tests for updating tasks."""

    def test_update_task(self, client, auth_headers):
        """Test updating a task."""
        response = client.patch(
            "/tasks/1",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_update_task_status(self, client, auth_headers):
        """Test updating task status."""
        response = client.patch(
            "/tasks/1",
            json={"status": "done"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "done"

    def test_update_task_partial(self, client, auth_headers):
        """Test partial update preserves other fields."""
        # Get original
        original = client.get("/tasks/1").json()

        # Update only title
        response = client.patch(
            "/tasks/1",
            json={"title": "New Title"},
            headers=auth_headers
        )

        data = response.json()
        assert data["title"] == "New Title"
        assert data["priority"] == original["priority"]  # Unchanged

    def test_update_task_not_found(self, client, auth_headers):
        """Test updating non-existent task."""
        response = client.patch(
            "/tasks/9999",
            json={"title": "Test"},
            headers=auth_headers
        )
        assert response.status_code == 404


class TestTaskDelete:
    """Tests for deleting tasks."""

    def test_delete_task(self, client, auth_headers):
        """Test deleting a task."""
        response = client.delete("/tasks/1", headers=auth_headers)
        assert response.status_code == 204

        # Verify deleted
        response = client.get("/tasks/1")
        assert response.status_code == 404

    def test_delete_task_not_found(self, client, auth_headers):
        """Test deleting non-existent task."""
        response = client.delete("/tasks/9999", headers=auth_headers)
        assert response.status_code == 404


# ============================================================================
# BULK OPERATION TESTS
# ============================================================================

class TestBulkOperations:
    """Tests for bulk operations."""

    def test_bulk_create(self, client, auth_headers):
        """Test bulk task creation."""
        tasks = [
            {"title": f"Bulk Task {i}"} for i in range(5)
        ]
        response = client.post(
            "/tasks/bulk",
            json={"tasks": tasks},
            headers=auth_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["successful"] == 5
        assert data["failed"] == 0
        assert len(data["created_ids"]) == 5

    def test_bulk_status_update(self, client, auth_headers):
        """Test bulk status update."""
        response = client.patch(
            "/tasks/bulk/status",
            json={
                "task_ids": [1, 2, 3],
                "status": "done"
            },
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["successful"] >= 1

    def test_bulk_status_update_partial_failure(self, client, auth_headers):
        """Test bulk update with some invalid IDs."""
        response = client.patch(
            "/tasks/bulk/status",
            json={
                "task_ids": [1, 9999],  # One valid, one invalid
                "status": "done"
            },
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["successful"] >= 1
        assert data["failed"] >= 1


# ============================================================================
# STATISTICS TESTS
# ============================================================================

class TestStatistics:
    """Tests for statistics endpoint."""

    def test_get_statistics(self, client):
        """Test getting statistics."""
        response = client.get("/tasks/statistics")
        assert response.status_code == 200

        data = response.json()
        assert "total_tasks" in data
        assert "by_status" in data
        assert "by_priority" in data
        assert "overdue_count" in data

    def test_statistics_by_status(self, client):
        """Test status counts are correct."""
        response = client.get("/tasks/statistics")
        data = response.json()

        # Sum of all statuses should equal total
        status_sum = sum(data["by_status"].values())
        assert status_sum == data["total_tasks"]


# ============================================================================
# VALIDATION ERROR TESTS
# ============================================================================

class TestValidationErrors:
    """Tests for validation error responses."""

    def test_validation_error_format(self, client, auth_headers):
        """Test validation errors are properly formatted."""
        response = client.post(
            "/tasks",
            json={"title": ""},  # Empty title
            headers=auth_headers
        )
        assert response.status_code == 422

        data = response.json()
        assert data["error"] == "validation_error"
        assert "details" in data
        assert len(data["details"]) > 0

        error_detail = data["details"][0]
        assert "field" in error_detail
        assert "message" in error_detail

    def test_multiple_validation_errors(self, client, auth_headers):
        """Test multiple validation errors are collected."""
        response = client.post(
            "/tasks",
            json={
                "title": "",
                "priority": "invalid",
                "assignee_email": "not-email"
            },
            headers=auth_headers
        )
        assert response.status_code == 422

        data = response.json()
        # Should have multiple errors
        assert len(data["details"]) >= 2


# ============================================================================
# OPENAPI TESTS
# ============================================================================

class TestOpenAPI:
    """Tests for OpenAPI documentation."""

    def test_openapi_schema(self, client):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
        assert "components" in schema

    def test_swagger_ui(self, client):
        """Test Swagger UI is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc(self, client):
        """Test ReDoc is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
