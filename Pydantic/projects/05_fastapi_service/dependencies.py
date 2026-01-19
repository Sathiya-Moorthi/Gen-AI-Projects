"""
Project 5: FastAPI + Pydantic Microservice - Dependencies
=========================================================

This module provides dependency injection for the FastAPI service.

Key Concepts:
- Settings injection from pydantic-settings
- Database session management (mock)
- Request context and logging
- Authentication stubs
"""

import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from typing import Annotated, AsyncGenerator

import structlog
from fastapi import Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from models import UserContext, TaskRead, TaskStatus, TaskPriority

logger = structlog.get_logger(__name__)


# ============================================================================
# SETTINGS (from Project 2)
# ============================================================================

class AppSettings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",
    )

    # Application
    app_name: str = "Task Manager API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (mock)
    database_url: str = "sqlite:///./tasks.db"

    # Auth (mock)
    api_key_header: str = "X-API-Key"
    valid_api_keys: list[str] = ["dev-key-123", "test-key-456"]

    # Rate limiting
    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> AppSettings:
    """Get cached settings instance."""
    return AppSettings()


# Dependency annotation
Settings = Annotated[AppSettings, Depends(get_settings)]


# ============================================================================
# REQUEST CONTEXT
# ============================================================================

@dataclass
class RequestContext:
    """Context for the current request."""

    request_id: str
    start_time: float
    user: UserContext | None = None

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return (time.time() - self.start_time) * 1000


async def get_request_context(request: Request) -> RequestContext:
    """Create request context with unique ID."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    context = RequestContext(
        request_id=request_id,
        start_time=time.time()
    )

    # Add to request state for access in other dependencies
    request.state.context = context

    logger.info(
        "request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path
    )

    return context


RequestCtx = Annotated[RequestContext, Depends(get_request_context)]


# ============================================================================
# AUTHENTICATION (Mock)
# ============================================================================

async def get_api_key(
    settings: Settings,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> str:
    """Validate API key from header."""
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )

    if x_api_key not in settings.valid_api_keys:
        logger.warning("invalid_api_key", key_prefix=x_api_key[:8])
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return x_api_key


async def get_current_user(
    api_key: Annotated[str, Depends(get_api_key)],
) -> UserContext:
    """Get current user from API key (mock implementation)."""
    # In production, this would look up the user from a database
    # based on the API key

    # Mock user based on API key
    if api_key == "dev-key-123":
        return UserContext(
            user_id="user-1",
            email="dev@example.com",
            roles=["developer"],
            is_admin=True
        )

    return UserContext(
        user_id="user-2",
        email="test@example.com",
        roles=["user"],
        is_admin=False
    )


CurrentUser = Annotated[UserContext, Depends(get_current_user)]


async def get_optional_user(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = None,
) -> UserContext | None:
    """Get user if authenticated, None otherwise."""
    if x_api_key is None:
        return None

    if settings is None:
        settings = get_settings()

    if x_api_key not in settings.valid_api_keys:
        return None

    return await get_current_user(x_api_key)


OptionalUser = Annotated[UserContext | None, Depends(get_optional_user)]


# ============================================================================
# DATABASE (Mock In-Memory)
# ============================================================================

@dataclass
class TaskEntity:
    """Mock database entity for tasks."""

    id: int
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    tags: list[str]
    due_date: datetime | None
    assignee_email: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class MockDatabase:
    """Mock in-memory database for demonstration."""

    tasks: dict[int, TaskEntity] = field(default_factory=dict)
    _next_id: int = 1

    def get_next_id(self) -> int:
        """Get next available ID."""
        id = self._next_id
        self._next_id += 1
        return id

    def seed_data(self) -> None:
        """Seed with sample data."""
        sample_tasks = [
            {
                "title": "Set up project structure",
                "description": "Initialize the repository with proper folder structure",
                "priority": TaskPriority.HIGH,
                "status": TaskStatus.DONE,
                "tags": ["setup", "infrastructure"],
            },
            {
                "title": "Implement user authentication",
                "description": "Add JWT-based authentication with refresh tokens",
                "priority": TaskPriority.CRITICAL,
                "status": TaskStatus.IN_PROGRESS,
                "tags": ["auth", "security"],
                "assignee_email": "dev@example.com",
            },
            {
                "title": "Write API documentation",
                "description": "Document all endpoints with OpenAPI examples",
                "priority": TaskPriority.MEDIUM,
                "status": TaskStatus.TODO,
                "tags": ["documentation"],
            },
            {
                "title": "Add unit tests",
                "description": "Achieve 80% code coverage",
                "priority": TaskPriority.HIGH,
                "status": TaskStatus.TODO,
                "tags": ["testing", "quality"],
            },
            {
                "title": "Performance optimization",
                "description": "Profile and optimize slow endpoints",
                "priority": TaskPriority.LOW,
                "status": TaskStatus.TODO,
                "tags": ["performance"],
            },
        ]

        now = datetime.now()
        for data in sample_tasks:
            task = TaskEntity(
                id=self.get_next_id(),
                title=data["title"],
                description=data.get("description"),
                priority=data["priority"],
                status=data["status"],
                tags=data.get("tags", []),
                due_date=data.get("due_date"),
                assignee_email=data.get("assignee_email"),
                created_at=now,
                updated_at=now,
            )
            self.tasks[task.id] = task

        logger.info("database_seeded", task_count=len(self.tasks))


# Global mock database instance
_db = MockDatabase()
_db.seed_data()


async def get_database() -> MockDatabase:
    """Get database instance."""
    return _db


Database = Annotated[MockDatabase, Depends(get_database)]


def reset_database() -> None:
    """Reset database for testing."""
    global _db
    _db = MockDatabase()
    _db.seed_data()


# ============================================================================
# RATE LIMITING (Simple implementation)
# ============================================================================

@dataclass
class RateLimitState:
    """Track rate limit state per client."""

    requests: list[float] = field(default_factory=list)

    def is_allowed(self, limit: int, window_seconds: int = 60) -> bool:
        """Check if request is allowed."""
        now = time.time()
        cutoff = now - window_seconds

        # Remove old requests
        self.requests = [t for t in self.requests if t > cutoff]

        if len(self.requests) >= limit:
            return False

        self.requests.append(now)
        return True


_rate_limits: dict[str, RateLimitState] = {}


async def check_rate_limit(
    request: Request,
    settings: Settings,
) -> None:
    """Check rate limit for the request."""
    # Use IP or API key as client identifier
    client_id = request.headers.get("X-API-Key", request.client.host if request.client else "unknown")

    if client_id not in _rate_limits:
        _rate_limits[client_id] = RateLimitState()

    if not _rate_limits[client_id].is_allowed(settings.rate_limit_per_minute):
        logger.warning("rate_limit_exceeded", client_id=client_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )


RateLimited = Annotated[None, Depends(check_rate_limit)]


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan_manager(app):
    """Manage application lifespan."""
    # Startup
    logger.info("application_starting", version=get_settings().app_version)
    _startup_time = time.time()

    yield {"startup_time": _startup_time}

    # Shutdown
    logger.info("application_shutting_down")


# ============================================================================
# COMMON DEPENDENCIES BUNDLE
# ============================================================================

class CommonDeps:
    """Bundle of common dependencies."""

    def __init__(
        self,
        settings: Settings,
        context: RequestCtx,
        db: Database,
        user: CurrentUser,
    ):
        self.settings = settings
        self.context = context
        self.db = db
        self.user = user


async def get_common_deps(
    settings: Settings,
    context: RequestCtx,
    db: Database,
    user: CurrentUser,
) -> CommonDeps:
    """Get common dependencies bundle."""
    return CommonDeps(
        settings=settings,
        context=context,
        db=db,
        user=user
    )


CommonDependencies = Annotated[CommonDeps, Depends(get_common_deps)]
