"""
Project 2: Configuration Manager
================================

This module demonstrates pydantic-settings for type-safe configuration management.

Key Concepts:
- pydantic-settings library
- BaseSettings class
- SettingsConfigDict for .env file loading
- SecretStr for sensitive values
- Nested settings models
- Environment variable naming conventions

Real-World Problem:
Applications need environment-specific configs (dev/staging/prod).
Hardcoded values cause security leaks and deployment failures.
Pydantic Settings provides type-safe config from env vars.
"""

import logging
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Literal

import structlog
from pydantic import (
    Field,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

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


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging level options."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseSettings(BaseSettings):
    """
    Database configuration settings.

    Demonstrates:
    - PostgresDsn for URL validation
    - SecretStr for passwords
    - Computed properties for connection strings
    - Pool configuration with sensible defaults
    """

    model_config = SettingsConfigDict(
        env_prefix="DB_",  # All vars start with DB_
        extra="ignore",
    )

    host: str = Field(
        default="localhost",
        description="Database host"
    )

    port: int = Field(
        default=5432,
        ge=1,
        le=65535,
        description="Database port"
    )

    name: str = Field(
        default="app_db",
        description="Database name"
    )

    user: str = Field(
        default="postgres",
        description="Database user"
    )

    password: SecretStr = Field(
        default=SecretStr(""),
        description="Database password (sensitive)"
    )

    # Connection pool settings
    pool_size: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Connection pool size"
    )

    pool_max_overflow: int = Field(
        default=10,
        ge=0,
        le=100,
        description="Max overflow connections"
    )

    pool_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Pool timeout in seconds"
    )

    ssl_mode: Literal["disable", "require", "verify-ca", "verify-full"] = Field(
        default="disable",
        description="SSL mode for database connection"
    )

    @property
    def connection_url(self) -> str:
        """Build PostgreSQL connection URL."""
        password = self.password.get_secret_value()
        return f"postgresql://{self.user}:{password}@{self.host}:{self.port}/{self.name}"

    @property
    def async_connection_url(self) -> str:
        """Build async PostgreSQL connection URL (for asyncpg)."""
        password = self.password.get_secret_value()
        return f"postgresql+asyncpg://{self.user}:{password}@{self.host}:{self.port}/{self.name}"

    @property
    def safe_connection_url(self) -> str:
        """Connection URL with password masked (for logging)."""
        return f"postgresql://{self.user}:***@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """
    Redis configuration settings.

    Demonstrates:
    - RedisDsn validation
    - Optional authentication
    - Database selection
    """

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        extra="ignore",
    )

    host: str = Field(
        default="localhost",
        description="Redis host"
    )

    port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis port"
    )

    password: SecretStr | None = Field(
        default=None,
        description="Redis password (optional)"
    )

    db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis database number"
    )

    ssl: bool = Field(
        default=False,
        description="Enable SSL for Redis"
    )

    # Connection settings
    socket_timeout: float = Field(
        default=5.0,
        gt=0,
        le=60,
        description="Socket timeout in seconds"
    )

    connection_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Connection pool size"
    )

    @property
    def connection_url(self) -> str:
        """Build Redis connection URL."""
        scheme = "rediss" if self.ssl else "redis"
        if self.password:
            return f"{scheme}://:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"
        return f"{scheme}://{self.host}:{self.port}/{self.db}"

    @property
    def safe_connection_url(self) -> str:
        """Connection URL with password masked."""
        scheme = "rediss" if self.ssl else "redis"
        if self.password:
            return f"{scheme}://:***@{self.host}:{self.port}/{self.db}"
        return f"{scheme}://{self.host}:{self.port}/{self.db}"


class LoggingSettings(BaseSettings):
    """
    Logging configuration settings.

    Demonstrates:
    - Enum field validation
    - Path validation
    - Format customization
    """

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        extra="ignore",
    )

    level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )

    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )

    json_format: bool = Field(
        default=False,
        description="Use JSON format for logs"
    )

    file_path: Path | None = Field(
        default=None,
        description="Log file path (None for stdout only)"
    )

    max_file_size_mb: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Max log file size in MB"
    )

    backup_count: int = Field(
        default=5,
        ge=0,
        le=100,
        description="Number of backup log files"
    )

    @field_validator("file_path")
    @classmethod
    def validate_log_path(cls, v: Path | None) -> Path | None:
        """Ensure log directory exists."""
        if v is not None:
            v.parent.mkdir(parents=True, exist_ok=True)
        return v


class APISettings(BaseSettings):
    """
    External API configuration settings.

    Demonstrates:
    - HttpUrl validation
    - SecretStr for API keys
    - Timeout configuration
    """

    model_config = SettingsConfigDict(
        env_prefix="API_",
        extra="ignore",
    )

    # OpenAI settings
    openai_api_key: SecretStr | None = Field(
        default=None,
        description="OpenAI API key"
    )

    openai_base_url: HttpUrl = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API base URL"
    )

    openai_model: str = Field(
        default="gpt-4",
        description="Default OpenAI model"
    )

    # Generic API settings
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API request timeout"
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Max retry attempts"
    )

    retry_delay_seconds: float = Field(
        default=1.0,
        ge=0.1,
        le=60,
        description="Delay between retries"
    )


class FeatureFlags(BaseSettings):
    """
    Feature flag configuration.

    Demonstrates:
    - Boolean flags with defaults
    - Environment-based feature toggling
    """

    model_config = SettingsConfigDict(
        env_prefix="FEATURE_",
        extra="ignore",
    )

    enable_caching: bool = Field(
        default=True,
        description="Enable response caching"
    )

    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable API rate limiting"
    )

    enable_metrics: bool = Field(
        default=True,
        description="Enable Prometheus metrics"
    )

    enable_debug_endpoints: bool = Field(
        default=False,
        description="Enable debug/admin endpoints"
    )

    maintenance_mode: bool = Field(
        default=False,
        description="Enable maintenance mode"
    )

    max_upload_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum file upload size in MB"
    )


class Settings(BaseSettings):
    """
    Main application settings.

    Demonstrates:
    - Nested settings models
    - Environment-based configuration
    - .env file loading
    - Cross-field validation
    - Singleton pattern with caching
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # Allows REDIS__HOST=xxx
        extra="ignore",
        case_sensitive=False,
    )

    # Application metadata
    app_name: str = Field(
        default="Pydantic Mastery App",
        description="Application name"
    )

    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )

    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )

    debug: bool = Field(
        default=False,
        description="Debug mode"
    )

    # Server settings
    host: str = Field(
        default="0.0.0.0",
        description="Server host"
    )

    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port"
    )

    workers: int = Field(
        default=1,
        ge=1,
        le=32,
        description="Number of worker processes"
    )

    # Nested configuration groups
    database: DatabaseSettings = Field(
        default_factory=DatabaseSettings,
        description="Database configuration"
    )

    redis: RedisSettings = Field(
        default_factory=RedisSettings,
        description="Redis configuration"
    )

    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Logging configuration"
    )

    api: APISettings = Field(
        default_factory=APISettings,
        description="External API configuration"
    )

    features: FeatureFlags = Field(
        default_factory=FeatureFlags,
        description="Feature flags"
    )

    # Security
    secret_key: SecretStr = Field(
        default=SecretStr("change-me-in-production"),
        min_length=16,
        description="Application secret key (min 16 chars)"
    )

    allowed_hosts: list[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed host headers"
    )

    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """
        Validate settings are appropriate for production.

        Demonstrates:
        - Environment-specific validation
        - Security checks
        """
        if self.environment == Environment.PRODUCTION:
            # Check debug is off
            if self.debug:
                raise ValueError("Debug mode must be disabled in production")

            # Check secret key is not default
            if self.secret_key.get_secret_value() == "change-me-in-production":
                raise ValueError("Secret key must be changed in production")

            # Check database password is set
            if not self.database.password.get_secret_value():
                raise ValueError("Database password must be set in production")

            # Warn about feature flags
            if self.features.enable_debug_endpoints:
                logger.warning(
                    "debug_endpoints_in_production",
                    message="Debug endpoints enabled in production - security risk!"
                )

        logger.info(
            "settings_loaded",
            environment=self.environment.value,
            debug=self.debug,
            database_host=self.database.host,
            redis_host=self.redis.host,
        )

        return self

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION

    def configure_logging(self) -> None:
        """Configure Python logging based on settings."""
        log_config = {
            "level": self.logging.level.value,
            "format": self.logging.format,
        }

        if self.logging.file_path:
            log_config["filename"] = str(self.logging.file_path)

        logging.basicConfig(**log_config)

        logger.info(
            "logging_configured",
            level=self.logging.level.value,
            json_format=self.logging.json_format,
            file_path=str(self.logging.file_path) if self.logging.file_path else None,
        )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    This is the recommended pattern for FastAPI dependency injection.

    Usage:
        settings = get_settings()
        # or in FastAPI:
        # def endpoint(settings: Settings = Depends(get_settings)):
    """
    return Settings()


def clear_settings_cache() -> None:
    """Clear the settings cache. Useful for testing."""
    get_settings.cache_clear()
