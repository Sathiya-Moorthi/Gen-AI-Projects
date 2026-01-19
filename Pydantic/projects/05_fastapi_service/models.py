"""
Project 5: FastAPI + Pydantic Microservice - Models
====================================================

This module defines Pydantic models for the FastAPI service.

Key Concepts:
- Separate models for Create/Read/Update operations
- Response models with field exclusion
- Query parameter validation
- Error response models
- Reusing patterns from previous projects

Real-World Problem:
Production APIs need request validation, response serialization, and
OpenAPI documentation. FastAPI + Pydantic provides all three with minimal boilerplate.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, Generic, TypeVar

import structlog
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

logger = structlog.get_logger(__name__)

T = TypeVar("T")


# ============================================================================
# ENUMS
# ============================================================================

class TaskStatus(str, Enum):
    """Task status values."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SortOrder(str, Enum):
    """Sort order for queries."""
    ASC = "asc"
    DESC = "desc"


# ============================================================================
# BASE MODELS
# ============================================================================

class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        str_strip_whitespace=True,
        validate_assignment=True,
    )


# ============================================================================
# TASK MODELS
# ============================================================================

class TaskBase(BaseSchema):
    """Base task fields shared between Create/Update/Read."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title",
        examples=["Complete project documentation"]
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Detailed task description"
    )

    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority level"
    )

    tags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Task tags for categorization"
    )

    due_date: datetime | None = Field(
        default=None,
        description="Task due date"
    )

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list[str]:
        """Normalize and deduplicate tags."""
        normalized = [tag.lower().strip() for tag in v if tag.strip()]
        return list(set(normalized))[:10]

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: datetime | None) -> datetime | None:
        """Ensure due date is not in the past."""
        if v and v < datetime.now():
            logger.warning("due_date_in_past", due_date=v)
            # Don't reject, just log warning
        return v


class TaskCreate(TaskBase):
    """
    Model for creating a new task.

    All fields from TaskBase, plus any create-specific fields.
    """

    assignee_email: EmailStr | None = Field(
        default=None,
        description="Email of person assigned to task"
    )


class TaskUpdate(BaseSchema):
    """
    Model for updating an existing task.

    All fields are optional for partial updates.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: str | None = None

    priority: TaskPriority | None = None

    status: TaskStatus | None = None

    tags: list[str] | None = None

    due_date: datetime | None = None

    assignee_email: EmailStr | None = None

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        normalized = [tag.lower().strip() for tag in v if tag.strip()]
        return list(set(normalized))[:10]


class TaskRead(TaskBase):
    """
    Model for reading/returning a task.

    Includes server-generated fields.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Complete project documentation",
                "description": "Write comprehensive docs",
                "priority": "high",
                "status": "in_progress",
                "tags": ["documentation", "priority"],
                "due_date": "2024-02-01T17:00:00",
                "assignee_email": "dev@example.com",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-16T14:00:00"
            }
        }
    )

    id: int = Field(..., description="Unique task identifier")

    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description="Current task status"
    )

    assignee_email: EmailStr | None = None

    created_at: datetime = Field(..., description="Creation timestamp")

    updated_at: datetime = Field(..., description="Last update timestamp")

    @computed_field
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status not in [TaskStatus.DONE, TaskStatus.CANCELLED]:
            return datetime.now() > self.due_date
        return False


class TaskSummary(BaseSchema):
    """Minimal task representation for lists."""

    id: int
    title: str
    status: TaskStatus
    priority: TaskPriority
    is_overdue: bool = False


# ============================================================================
# PAGINATION AND QUERY MODELS
# ============================================================================

class PaginationParams(BaseSchema):
    """Common pagination parameters."""

    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)"
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Items per page (max 100)"
    )

    @computed_field
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size


class TaskQueryParams(PaginationParams):
    """Query parameters for filtering tasks."""

    status: TaskStatus | None = Field(
        default=None,
        description="Filter by status"
    )

    priority: TaskPriority | None = Field(
        default=None,
        description="Filter by priority"
    )

    tag: str | None = Field(
        default=None,
        description="Filter by tag"
    )

    search: str | None = Field(
        default=None,
        max_length=100,
        description="Search in title and description"
    )

    sort_by: str = Field(
        default="created_at",
        description="Field to sort by"
    )

    sort_order: SortOrder = Field(
        default=SortOrder.DESC,
        description="Sort order"
    )

    overdue_only: bool = Field(
        default=False,
        description="Only show overdue tasks"
    )


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T] = Field(..., description="List of items")

    total: int = Field(..., ge=0, description="Total number of items")

    page: int = Field(..., ge=1, description="Current page")

    page_size: int = Field(..., ge=1, description="Items per page")

    @computed_field
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @computed_field
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @computed_field
    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


class TaskListResponse(PaginatedResponse[TaskSummary]):
    """Paginated task list response."""
    pass


class TaskStatistics(BaseSchema):
    """Task statistics response."""

    total_tasks: int = Field(..., ge=0)

    by_status: dict[str, int] = Field(
        default_factory=dict,
        description="Count by status"
    )

    by_priority: dict[str, int] = Field(
        default_factory=dict,
        description="Count by priority"
    )

    overdue_count: int = Field(default=0, ge=0)

    completed_this_week: int = Field(default=0, ge=0)


# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorDetail(BaseSchema):
    """Details of a single error."""

    field: str | None = Field(
        default=None,
        description="Field that caused the error"
    )

    message: str = Field(
        ...,
        description="Error message"
    )

    code: str | None = Field(
        default=None,
        description="Error code for programmatic handling"
    )


class ErrorResponse(BaseSchema):
    """Standard error response."""

    error: str = Field(
        ...,
        description="Error type"
    )

    message: str = Field(
        ...,
        description="Human-readable error message"
    )

    details: list[ErrorDetail] = Field(
        default_factory=list,
        description="Detailed error information"
    )

    request_id: str | None = Field(
        default=None,
        description="Request ID for tracking"
    )


class ValidationErrorResponse(ErrorResponse):
    """Response for validation errors."""

    error: str = "validation_error"


class NotFoundErrorResponse(ErrorResponse):
    """Response for not found errors."""

    error: str = "not_found"


# ============================================================================
# HEALTH CHECK MODELS
# ============================================================================

class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseSchema):
    """Health of a single component."""

    name: str
    status: HealthStatus
    message: str | None = None
    latency_ms: float | None = None


class HealthResponse(BaseSchema):
    """Health check response."""

    status: HealthStatus
    version: str
    uptime_seconds: float
    components: list[ComponentHealth] = Field(default_factory=list)


# ============================================================================
# BULK OPERATION MODELS
# ============================================================================

class BulkTaskCreate(BaseSchema):
    """Model for creating multiple tasks."""

    tasks: list[TaskCreate] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of tasks to create"
    )


class BulkOperationResult(BaseSchema):
    """Result of a bulk operation."""

    successful: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)
    errors: list[ErrorDetail] = Field(default_factory=list)
    created_ids: list[int] = Field(default_factory=list)


class BulkStatusUpdate(BaseSchema):
    """Update status of multiple tasks."""

    task_ids: list[int] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="IDs of tasks to update"
    )

    status: TaskStatus = Field(
        ...,
        description="New status for all tasks"
    )


# ============================================================================
# USER CONTEXT (from Project 1)
# ============================================================================

class UserContext(BaseSchema):
    """User context for authenticated requests."""

    user_id: str
    email: EmailStr
    roles: list[str] = Field(default_factory=list)
    is_admin: bool = False

    def can_modify_task(self, task_assignee: str | None) -> bool:
        """Check if user can modify a task."""
        if self.is_admin:
            return True
        return task_assignee == self.email
