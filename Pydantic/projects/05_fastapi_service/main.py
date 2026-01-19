"""
Project 5: FastAPI + Pydantic Microservice - Main Application
=============================================================

This module implements a complete FastAPI service with Pydantic models.

Run with: uvicorn main:app --reload

Key Features:
- CRUD operations for tasks
- Request/response validation
- Auto-generated OpenAPI docs
- Error handling
- Dependency injection
"""

import time
from datetime import datetime
from typing import Annotated

import structlog
from fastapi import FastAPI, HTTPException, Path, Query, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from models import (
    TaskCreate,
    TaskUpdate,
    TaskRead,
    TaskSummary,
    TaskStatus,
    TaskPriority,
    TaskQueryParams,
    TaskListResponse,
    TaskStatistics,
    BulkTaskCreate,
    BulkOperationResult,
    BulkStatusUpdate,
    ErrorResponse,
    ValidationErrorResponse,
    NotFoundErrorResponse,
    HealthResponse,
    HealthStatus,
    ComponentHealth,
    ErrorDetail,
)
from dependencies import (
    get_settings,
    lifespan_manager,
    Settings,
    RequestCtx,
    Database,
    CurrentUser,
    OptionalUser,
    RateLimited,
    CommonDependencies,
    TaskEntity,
    reset_database,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Track startup time for health checks
_startup_time: float = time.time()


# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="Task Manager API",
    description="""
A demonstration of FastAPI + Pydantic integration.

## Features

* **CRUD Operations** - Create, Read, Update, Delete tasks
* **Validation** - Automatic request/response validation
* **Filtering** - Filter tasks by status, priority, tags
* **Pagination** - Paginated list endpoints
* **Authentication** - API key authentication
* **Error Handling** - Structured error responses

## Authentication

Include your API key in the `X-API-Key` header:

```
X-API-Key: dev-key-123
```
""",
    version="1.0.0",
    lifespan=lifespan_manager,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ValidationErrorResponse, "description": "Validation Error"},
        429: {"model": ErrorResponse, "description": "Rate Limited"},
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        errors.append(ErrorDetail(
            field=field_path,
            message=error["msg"],
            code=error["type"]
        ))

    logger.warning(
        "validation_error",
        error_count=len(errors),
        path=request.url.path
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationErrorResponse(
            message="Request validation failed",
            details=errors
        ).model_dump()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with structured response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"http_{exc.status_code}",
            message=exc.detail
        ).model_dump()
    )


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
)
async def health_check(settings: Settings) -> HealthResponse:
    """
    Check application health.

    Returns status of all components.
    """
    uptime = time.time() - _startup_time

    components = [
        ComponentHealth(
            name="api",
            status=HealthStatus.HEALTHY,
            message="API is responding"
        ),
        ComponentHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database connected (mock)"
        ),
    ]

    return HealthResponse(
        status=HealthStatus.HEALTHY,
        version=settings.app_version,
        uptime_seconds=uptime,
        components=components
    )


# ============================================================================
# TASK CRUD ENDPOINTS
# ============================================================================

@app.post(
    "/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
    summary="Create a new task",
    responses={
        201: {"description": "Task created successfully"},
    }
)
async def create_task(
    task_data: TaskCreate,
    deps: CommonDependencies,
    _: RateLimited,
) -> TaskRead:
    """
    Create a new task.

    - **title**: Task title (required)
    - **description**: Detailed description (optional)
    - **priority**: low, medium, high, or critical
    - **tags**: List of tags for categorization
    - **due_date**: Optional due date
    - **assignee_email**: Email of assigned person
    """
    now = datetime.now()

    task = TaskEntity(
        id=deps.db.get_next_id(),
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        status=TaskStatus.TODO,
        tags=task_data.tags,
        due_date=task_data.due_date,
        assignee_email=task_data.assignee_email,
        created_at=now,
        updated_at=now,
    )

    deps.db.tasks[task.id] = task

    logger.info(
        "task_created",
        task_id=task.id,
        title=task.title,
        user=deps.user.email,
        request_id=deps.context.request_id
    )

    return TaskRead.model_validate(task)


@app.get(
    "/tasks",
    response_model=TaskListResponse,
    tags=["Tasks"],
    summary="List all tasks",
)
async def list_tasks(
    db: Database,
    context: RequestCtx,
    user: OptionalUser,
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = Query(default=None),
    tag: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> TaskListResponse:
    """
    List tasks with filtering and pagination.

    Supports filtering by:
    - **status**: Filter by task status
    - **priority**: Filter by priority level
    - **tag**: Filter by tag
    - **search**: Search in title and description
    """
    # Filter tasks
    tasks = list(db.tasks.values())

    if status_filter:
        tasks = [t for t in tasks if t.status == status_filter]

    if priority:
        tasks = [t for t in tasks if t.priority == priority]

    if tag:
        tasks = [t for t in tasks if tag.lower() in [tg.lower() for tg in t.tags]]

    if search:
        search_lower = search.lower()
        tasks = [
            t for t in tasks
            if search_lower in t.title.lower()
            or (t.description and search_lower in t.description.lower())
        ]

    # Sort by created_at descending
    tasks.sort(key=lambda t: t.created_at, reverse=True)

    # Paginate
    total = len(tasks)
    start = (page - 1) * page_size
    end = start + page_size
    page_tasks = tasks[start:end]

    # Convert to summaries
    summaries = [
        TaskSummary(
            id=t.id,
            title=t.title,
            status=t.status,
            priority=t.priority,
            is_overdue=(
                t.due_date is not None
                and datetime.now() > t.due_date
                and t.status not in [TaskStatus.DONE, TaskStatus.CANCELLED]
            )
        )
        for t in page_tasks
    ]

    logger.info(
        "tasks_listed",
        total=total,
        returned=len(summaries),
        request_id=context.request_id
    )

    return TaskListResponse(
        items=summaries,
        total=total,
        page=page,
        page_size=page_size
    )


@app.get(
    "/tasks/{task_id}",
    response_model=TaskRead,
    tags=["Tasks"],
    summary="Get a task by ID",
    responses={
        404: {"model": NotFoundErrorResponse, "description": "Task not found"},
    }
)
async def get_task(
    task_id: Annotated[int, Path(ge=1, description="Task ID")],
    db: Database,
    context: RequestCtx,
) -> TaskRead:
    """
    Get a specific task by ID.

    Returns full task details including computed fields.
    """
    if task_id not in db.tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    task = db.tasks[task_id]

    logger.info(
        "task_retrieved",
        task_id=task_id,
        request_id=context.request_id
    )

    return TaskRead.model_validate(task)


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskRead,
    tags=["Tasks"],
    summary="Update a task",
    responses={
        404: {"model": NotFoundErrorResponse, "description": "Task not found"},
    }
)
async def update_task(
    task_id: Annotated[int, Path(ge=1)],
    task_update: TaskUpdate,
    deps: CommonDependencies,
) -> TaskRead:
    """
    Update an existing task.

    Only provided fields will be updated (partial update).
    """
    if task_id not in deps.db.tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    task = deps.db.tasks[task_id]

    # Check authorization
    if not deps.user.can_modify_task(task.assignee_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this task"
        )

    # Apply updates
    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.now()

    logger.info(
        "task_updated",
        task_id=task_id,
        updated_fields=list(update_data.keys()),
        user=deps.user.email,
        request_id=deps.context.request_id
    )

    return TaskRead.model_validate(task)


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
    summary="Delete a task",
    responses={
        404: {"model": NotFoundErrorResponse, "description": "Task not found"},
    }
)
async def delete_task(
    task_id: Annotated[int, Path(ge=1)],
    deps: CommonDependencies,
) -> None:
    """
    Delete a task by ID.

    This action is irreversible.
    """
    if task_id not in deps.db.tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    task = deps.db.tasks[task_id]

    # Check authorization
    if not deps.user.can_modify_task(task.assignee_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this task"
        )

    del deps.db.tasks[task_id]

    logger.info(
        "task_deleted",
        task_id=task_id,
        user=deps.user.email,
        request_id=deps.context.request_id
    )


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@app.post(
    "/tasks/bulk",
    response_model=BulkOperationResult,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
    summary="Create multiple tasks",
)
async def bulk_create_tasks(
    bulk_data: BulkTaskCreate,
    deps: CommonDependencies,
) -> BulkOperationResult:
    """
    Create multiple tasks in a single request.

    Maximum 100 tasks per request.
    """
    created_ids = []
    errors = []
    now = datetime.now()

    for idx, task_data in enumerate(bulk_data.tasks):
        try:
            task = TaskEntity(
                id=deps.db.get_next_id(),
                title=task_data.title,
                description=task_data.description,
                priority=task_data.priority,
                status=TaskStatus.TODO,
                tags=task_data.tags,
                due_date=task_data.due_date,
                assignee_email=task_data.assignee_email,
                created_at=now,
                updated_at=now,
            )
            deps.db.tasks[task.id] = task
            created_ids.append(task.id)

        except Exception as e:
            errors.append(ErrorDetail(
                field=f"tasks[{idx}]",
                message=str(e)
            ))

    logger.info(
        "bulk_create_completed",
        successful=len(created_ids),
        failed=len(errors),
        user=deps.user.email
    )

    return BulkOperationResult(
        successful=len(created_ids),
        failed=len(errors),
        errors=errors,
        created_ids=created_ids
    )


@app.patch(
    "/tasks/bulk/status",
    response_model=BulkOperationResult,
    tags=["Tasks"],
    summary="Update status of multiple tasks",
)
async def bulk_update_status(
    update_data: BulkStatusUpdate,
    deps: CommonDependencies,
) -> BulkOperationResult:
    """
    Update the status of multiple tasks at once.
    """
    updated = 0
    errors = []

    for task_id in update_data.task_ids:
        if task_id not in deps.db.tasks:
            errors.append(ErrorDetail(
                field=str(task_id),
                message=f"Task {task_id} not found"
            ))
            continue

        task = deps.db.tasks[task_id]

        if not deps.user.can_modify_task(task.assignee_email):
            errors.append(ErrorDetail(
                field=str(task_id),
                message=f"No permission to modify task {task_id}"
            ))
            continue

        task.status = update_data.status
        task.updated_at = datetime.now()
        updated += 1

    logger.info(
        "bulk_status_update",
        updated=updated,
        failed=len(errors),
        new_status=update_data.status.value
    )

    return BulkOperationResult(
        successful=updated,
        failed=len(errors),
        errors=errors,
        created_ids=[]
    )


# ============================================================================
# STATISTICS ENDPOINT
# ============================================================================

@app.get(
    "/tasks/statistics",
    response_model=TaskStatistics,
    tags=["Tasks"],
    summary="Get task statistics",
)
async def get_statistics(
    db: Database,
    context: RequestCtx,
) -> TaskStatistics:
    """
    Get aggregated task statistics.

    Returns counts by status and priority.
    """
    tasks = list(db.tasks.values())
    now = datetime.now()

    # Count by status
    by_status = {}
    for status_val in TaskStatus:
        count = sum(1 for t in tasks if t.status == status_val)
        by_status[status_val.value] = count

    # Count by priority
    by_priority = {}
    for priority in TaskPriority:
        count = sum(1 for t in tasks if t.priority == priority)
        by_priority[priority.value] = count

    # Overdue count
    overdue = sum(
        1 for t in tasks
        if t.due_date
        and now > t.due_date
        and t.status not in [TaskStatus.DONE, TaskStatus.CANCELLED]
    )

    return TaskStatistics(
        total_tasks=len(tasks),
        by_status=by_status,
        by_priority=by_priority,
        overdue_count=overdue,
        completed_this_week=by_status.get("done", 0)  # Simplified
    )


# ============================================================================
# DEVELOPMENT ENDPOINTS
# ============================================================================

@app.post(
    "/dev/reset",
    tags=["Development"],
    summary="Reset database (dev only)",
    include_in_schema=True,  # Set to False in production
)
async def reset_db(
    deps: CommonDependencies,
) -> dict:
    """
    Reset the database to initial state.

    Only available in development mode.
    """
    if not deps.settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in debug mode"
        )

    reset_database()

    logger.info("database_reset", user=deps.user.email)

    return {"message": "Database reset successfully"}


# ============================================================================
# STARTUP MESSAGE
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    print(f"""
    {'=' * 50}
    {settings.app_name} v{settings.app_version}
    {'=' * 50}

    API Documentation:
    - Swagger UI: http://localhost:{settings.port}/docs
    - ReDoc: http://localhost:{settings.port}/redoc

    Health Check:
    - http://localhost:{settings.port}/health

    Sample API Calls:
    - List tasks: GET /tasks
    - Create task: POST /tasks
    - Get task: GET /tasks/1

    API Key (for testing):
    - X-API-Key: dev-key-123

    {'=' * 50}
    """)

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
