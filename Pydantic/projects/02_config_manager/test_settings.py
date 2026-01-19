"""
Project 2: Configuration Manager - Tests
=========================================

Comprehensive pytest tests for pydantic-settings.

Run with: pytest test_settings.py -v
"""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from settings import (
    Settings,
    DatabaseSettings,
    RedisSettings,
    LoggingSettings,
    APISettings,
    FeatureFlags,
    Environment,
    LogLevel,
    get_settings,
    clear_settings_cache,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before and after each test."""
    # Store original environment
    original_env = dict(os.environ)

    # Clear relevant env vars
    env_prefixes = ["APP_", "DB_", "REDIS_", "LOG_", "API_", "FEATURE_",
                    "ENVIRONMENT", "DEBUG", "HOST", "PORT", "SECRET_KEY",
                    "DATABASE__", "REDIS__", "LOGGING__"]

    for key in list(os.environ.keys()):
        if any(key.startswith(prefix) for prefix in env_prefixes):
            os.environ.pop(key, None)

    clear_settings_cache()

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
    clear_settings_cache()


@pytest.fixture
def env_file(tmp_path):
    """Create a temporary .env file."""
    env_path = tmp_path / ".env"

    def _create_env(content: str):
        env_path.write_text(content)
        return env_path

    return _create_env


# ============================================================================
# DATABASE SETTINGS TESTS
# ============================================================================

class TestDatabaseSettings:
    """Tests for DatabaseSettings."""

    def test_defaults(self):
        """Test default database settings."""
        db = DatabaseSettings()
        assert db.host == "localhost"
        assert db.port == 5432
        assert db.name == "app_db"
        assert db.user == "postgres"
        assert db.pool_size == 5

    def test_env_override(self):
        """Test environment variable overrides."""
        os.environ["DB_HOST"] = "prod-db.example.com"
        os.environ["DB_PORT"] = "5433"
        os.environ["DB_NAME"] = "production_db"

        db = DatabaseSettings()
        assert db.host == "prod-db.example.com"
        assert db.port == 5433
        assert db.name == "production_db"

    def test_connection_url(self):
        """Test connection URL generation."""
        os.environ["DB_PASSWORD"] = "secret123"

        db = DatabaseSettings()
        url = db.connection_url
        assert "postgresql://" in url
        assert "secret123" in url
        assert "localhost:5432" in url

    def test_safe_connection_url(self):
        """Test safe connection URL masks password."""
        os.environ["DB_PASSWORD"] = "secret123"

        db = DatabaseSettings()
        safe_url = db.safe_connection_url
        assert "***" in safe_url
        assert "secret123" not in safe_url

    def test_async_connection_url(self):
        """Test async connection URL."""
        os.environ["DB_PASSWORD"] = "secret123"

        db = DatabaseSettings()
        async_url = db.async_connection_url
        assert "postgresql+asyncpg://" in async_url

    def test_port_validation(self):
        """Test port range validation."""
        os.environ["DB_PORT"] = "0"
        with pytest.raises(ValidationError):
            DatabaseSettings()

        os.environ["DB_PORT"] = "70000"
        with pytest.raises(ValidationError):
            DatabaseSettings()

    def test_pool_size_validation(self):
        """Test pool size validation."""
        os.environ["DB_POOL_SIZE"] = "0"
        with pytest.raises(ValidationError):
            DatabaseSettings()

        os.environ["DB_POOL_SIZE"] = "101"
        with pytest.raises(ValidationError):
            DatabaseSettings()

    @pytest.mark.parametrize("ssl_mode", ["disable", "require", "verify-ca", "verify-full"])
    def test_ssl_modes(self, ssl_mode):
        """Test valid SSL modes."""
        os.environ["DB_SSL_MODE"] = ssl_mode
        db = DatabaseSettings()
        assert db.ssl_mode == ssl_mode

    def test_invalid_ssl_mode(self):
        """Test invalid SSL mode."""
        os.environ["DB_SSL_MODE"] = "invalid"
        with pytest.raises(ValidationError):
            DatabaseSettings()


# ============================================================================
# REDIS SETTINGS TESTS
# ============================================================================

class TestRedisSettings:
    """Tests for RedisSettings."""

    def test_defaults(self):
        """Test default Redis settings."""
        redis = RedisSettings()
        assert redis.host == "localhost"
        assert redis.port == 6379
        assert redis.db == 0
        assert redis.ssl is False
        assert redis.password is None

    def test_connection_url_no_auth(self):
        """Test connection URL without authentication."""
        redis = RedisSettings()
        url = redis.connection_url
        assert url == "redis://localhost:6379/0"

    def test_connection_url_with_auth(self):
        """Test connection URL with authentication."""
        os.environ["REDIS_PASSWORD"] = "redis-secret"

        redis = RedisSettings()
        url = redis.connection_url
        assert "redis://:redis-secret@" in url

    def test_ssl_connection_url(self):
        """Test SSL connection URL."""
        os.environ["REDIS_SSL"] = "true"

        redis = RedisSettings()
        url = redis.connection_url
        assert url.startswith("rediss://")

    def test_safe_connection_url(self):
        """Test safe connection URL masks password."""
        os.environ["REDIS_PASSWORD"] = "redis-secret"

        redis = RedisSettings()
        safe_url = redis.safe_connection_url
        assert "***" in safe_url
        assert "redis-secret" not in safe_url

    def test_db_range(self):
        """Test Redis DB number range."""
        os.environ["REDIS_DB"] = "15"
        redis = RedisSettings()
        assert redis.db == 15

        os.environ["REDIS_DB"] = "16"
        with pytest.raises(ValidationError):
            RedisSettings()


# ============================================================================
# LOGGING SETTINGS TESTS
# ============================================================================

class TestLoggingSettings:
    """Tests for LoggingSettings."""

    def test_defaults(self):
        """Test default logging settings."""
        logging = LoggingSettings()
        assert logging.level == LogLevel.INFO
        assert logging.json_format is False
        assert logging.file_path is None

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_log_levels(self, level):
        """Test valid log levels."""
        os.environ["LOG_LEVEL"] = level
        logging = LoggingSettings()
        assert logging.level.value == level

    def test_invalid_log_level(self):
        """Test invalid log level."""
        os.environ["LOG_LEVEL"] = "TRACE"
        with pytest.raises(ValidationError):
            LoggingSettings()

    def test_file_path(self, tmp_path):
        """Test log file path."""
        log_path = tmp_path / "logs" / "app.log"
        os.environ["LOG_FILE_PATH"] = str(log_path)

        logging = LoggingSettings()
        assert logging.file_path == log_path
        # Directory should be created
        assert log_path.parent.exists()


# ============================================================================
# API SETTINGS TESTS
# ============================================================================

class TestAPISettings:
    """Tests for APISettings."""

    def test_defaults(self):
        """Test default API settings."""
        api = APISettings()
        assert str(api.openai_base_url) == "https://api.openai.com/v1"
        assert api.openai_model == "gpt-4"
        assert api.timeout_seconds == 30
        assert api.max_retries == 3

    def test_openai_api_key(self):
        """Test OpenAI API key as SecretStr."""
        os.environ["API_OPENAI_API_KEY"] = "sk-test-key-12345"

        api = APISettings()
        assert api.openai_api_key is not None
        assert api.openai_api_key.get_secret_value() == "sk-test-key-12345"
        # Should be hidden in repr
        assert "sk-test-key" not in str(api.openai_api_key)

    def test_timeout_validation(self):
        """Test timeout range validation."""
        os.environ["API_TIMEOUT_SECONDS"] = "0"
        with pytest.raises(ValidationError):
            APISettings()

        os.environ["API_TIMEOUT_SECONDS"] = "301"
        with pytest.raises(ValidationError):
            APISettings()


# ============================================================================
# FEATURE FLAGS TESTS
# ============================================================================

class TestFeatureFlags:
    """Tests for FeatureFlags."""

    def test_defaults(self):
        """Test default feature flags."""
        features = FeatureFlags()
        assert features.enable_caching is True
        assert features.enable_rate_limiting is True
        assert features.enable_metrics is True
        assert features.enable_debug_endpoints is False
        assert features.maintenance_mode is False

    def test_boolean_parsing(self):
        """Test boolean environment variable parsing."""
        os.environ["FEATURE_ENABLE_CACHING"] = "false"
        os.environ["FEATURE_MAINTENANCE_MODE"] = "true"

        features = FeatureFlags()
        assert features.enable_caching is False
        assert features.maintenance_mode is True

    @pytest.mark.parametrize("value,expected", [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
    ])
    def test_boolean_variations(self, value, expected):
        """Test various boolean string representations."""
        os.environ["FEATURE_ENABLE_CACHING"] = value
        features = FeatureFlags()
        assert features.enable_caching is expected


# ============================================================================
# MAIN SETTINGS TESTS
# ============================================================================

class TestSettings:
    """Tests for main Settings class."""

    def test_defaults(self):
        """Test default settings."""
        settings = Settings()
        assert settings.app_name == "Pydantic Mastery App"
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.debug is False
        assert settings.port == 8000

    def test_environment_enum(self):
        """Test environment enum values."""
        for env in ["development", "staging", "production", "testing"]:
            os.environ["ENVIRONMENT"] = env
            clear_settings_cache()
            settings = Settings()
            assert settings.environment.value == env

    def test_nested_settings_loaded(self):
        """Test nested settings are properly loaded."""
        os.environ["DB_HOST"] = "test-db.example.com"
        os.environ["REDIS_HOST"] = "test-redis.example.com"

        settings = Settings()
        assert settings.database.host == "test-db.example.com"
        assert settings.redis.host == "test-redis.example.com"

    def test_is_development_property(self):
        """Test is_development property."""
        os.environ["ENVIRONMENT"] = "development"
        settings = Settings()
        assert settings.is_development is True
        assert settings.is_production is False

    def test_is_production_property(self):
        """Test is_production property."""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["DEBUG"] = "false"
        os.environ["SECRET_KEY"] = "production-secret-key-long-enough"
        os.environ["DB_PASSWORD"] = "prod-password"

        settings = Settings()
        assert settings.is_production is True
        assert settings.is_development is False

    def test_secret_key_minimum_length(self):
        """Test secret key minimum length."""
        os.environ["SECRET_KEY"] = "short"
        with pytest.raises(ValidationError):
            Settings()


# ============================================================================
# PRODUCTION VALIDATION TESTS
# ============================================================================

class TestProductionValidation:
    """Tests for production-specific validation."""

    def test_production_debug_must_be_false(self):
        """Test debug must be false in production."""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["DEBUG"] = "true"
        os.environ["SECRET_KEY"] = "production-secret-key-long-enough"
        os.environ["DB_PASSWORD"] = "prod-password"

        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "Debug mode must be disabled" in str(exc_info.value)

    def test_production_secret_key_required(self):
        """Test custom secret key required in production."""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["DEBUG"] = "false"
        os.environ["SECRET_KEY"] = "change-me-in-production"
        os.environ["DB_PASSWORD"] = "prod-password"

        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "Secret key must be changed" in str(exc_info.value)

    def test_production_db_password_required(self):
        """Test database password required in production."""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["DEBUG"] = "false"
        os.environ["SECRET_KEY"] = "production-secret-key-long-enough"
        os.environ["DB_PASSWORD"] = ""

        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "Database password must be set" in str(exc_info.value)

    def test_valid_production_settings(self):
        """Test valid production configuration passes."""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["DEBUG"] = "false"
        os.environ["SECRET_KEY"] = "production-secret-key-long-enough"
        os.environ["DB_PASSWORD"] = "secure-prod-password"

        settings = Settings()
        assert settings.is_production is True


# ============================================================================
# CACHED SETTINGS TESTS
# ============================================================================

class TestCachedSettings:
    """Tests for settings caching."""

    def test_get_settings_caches(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_clear_cache(self):
        """Test cache clearing."""
        settings1 = get_settings()
        clear_settings_cache()
        settings2 = get_settings()
        assert settings1 is not settings2


# ============================================================================
# ENV FILE TESTS
# ============================================================================

class TestEnvFileLoading:
    """Tests for .env file loading."""

    def test_env_file_loaded(self, tmp_path, monkeypatch):
        """Test settings loaded from .env file."""
        # Create .env file
        env_content = """
APP_NAME="Test App from File"
PORT=9999
"""
        env_file = tmp_path / ".env"
        env_file.write_text(env_content)

        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        clear_settings_cache()

        settings = Settings()
        assert settings.app_name == "Test App from File"
        assert settings.port == 9999

    def test_env_var_overrides_file(self, tmp_path, monkeypatch):
        """Test environment variables override .env file."""
        # Create .env file
        env_content = """
APP_NAME="From File"
PORT=8080
"""
        env_file = tmp_path / ".env"
        env_file.write_text(env_content)

        monkeypatch.chdir(tmp_path)
        os.environ["APP_NAME"] = "From Environment"
        clear_settings_cache()

        settings = Settings()
        assert settings.app_name == "From Environment"
        assert settings.port == 8080  # Still from file


# ============================================================================
# SERIALIZATION TESTS
# ============================================================================

class TestSerialization:
    """Tests for settings serialization."""

    def test_model_dump(self):
        """Test model_dump serialization."""
        settings = Settings()
        data = settings.model_dump()

        assert "app_name" in data
        assert "database" in data
        assert isinstance(data["database"], dict)

    def test_exclude_secrets(self):
        """Test excluding secrets from dump."""
        os.environ["DB_PASSWORD"] = "secret"
        settings = Settings()

        data = settings.model_dump(
            exclude={"secret_key", "database": {"password"}}
        )

        assert "secret_key" not in data
        assert "password" not in data.get("database", {})

    def test_nested_model_dump(self):
        """Test nested model serialization."""
        settings = Settings()
        db_data = settings.database.model_dump()

        assert "host" in db_data
        assert "port" in db_data
        assert "pool_size" in db_data
