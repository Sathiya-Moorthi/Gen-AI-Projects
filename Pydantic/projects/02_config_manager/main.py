"""
Project 2: Configuration Manager - Main Demonstration
=====================================================

This script demonstrates all the key concepts from pydantic-settings.

Run with: python main.py
"""

import json
import os
import logging
from pathlib import Path

import structlog

from settings import (
    Settings,
    DatabaseSettings,
    RedisSettings,
    LoggingSettings,
    APISettings,
    FeatureFlags,
    Environment,
    get_settings,
    clear_settings_cache,
)

# Configure logging
logging.basicConfig(level=logging.INFO)


def demonstrate_default_settings():
    """Show default settings without any environment variables."""
    print("\n" + "=" * 60)
    print("DEMO 1: Default Settings (No Environment Variables)")
    print("=" * 60)

    # Clear any cached settings
    clear_settings_cache()

    # Create settings with defaults
    settings = Settings()

    print("\n1. Application Metadata:")
    print(f"   App Name: {settings.app_name}")
    print(f"   Version: {settings.app_version}")
    print(f"   Environment: {settings.environment.value}")
    print(f"   Debug: {settings.debug}")

    print("\n2. Server Configuration:")
    print(f"   Host: {settings.host}")
    print(f"   Port: {settings.port}")
    print(f"   Workers: {settings.workers}")

    print("\n3. Database (Nested Settings):")
    print(f"   Host: {settings.database.host}")
    print(f"   Port: {settings.database.port}")
    print(f"   Database: {settings.database.name}")
    print(f"   User: {settings.database.user}")
    print(f"   Pool Size: {settings.database.pool_size}")
    print(f"   Safe URL: {settings.database.safe_connection_url}")

    print("\n4. Redis (Nested Settings):")
    print(f"   Host: {settings.redis.host}")
    print(f"   Port: {settings.redis.port}")
    print(f"   Database: {settings.redis.db}")
    print(f"   Safe URL: {settings.redis.safe_connection_url}")

    print("\n5. Feature Flags:")
    print(f"   Caching: {settings.features.enable_caching}")
    print(f"   Rate Limiting: {settings.features.enable_rate_limiting}")
    print(f"   Metrics: {settings.features.enable_metrics}")
    print(f"   Debug Endpoints: {settings.features.enable_debug_endpoints}")


def demonstrate_environment_variables():
    """Show how environment variables override defaults."""
    print("\n" + "=" * 60)
    print("DEMO 2: Environment Variable Overrides")
    print("=" * 60)

    # Clear cache
    clear_settings_cache()

    # Set environment variables
    env_vars = {
        "APP_NAME": "My Custom App",
        "ENVIRONMENT": "staging",
        "DEBUG": "true",
        "PORT": "9000",
        "DB_HOST": "staging-db.example.com",
        "DB_PORT": "5433",
        "DB_NAME": "staging_db",
        "DB_PASSWORD": "staging-secret-password",
        "REDIS_HOST": "staging-redis.example.com",
        "FEATURE_ENABLE_DEBUG_ENDPOINTS": "true",
    }

    # Set them
    for key, value in env_vars.items():
        os.environ[key] = value

    print("\nEnvironment variables set:")
    for key, value in env_vars.items():
        display_value = "***" if "PASSWORD" in key else value
        print(f"   {key}={display_value}")

    # Load settings
    settings = Settings()

    print("\n--- Settings Loaded ---")
    print(f"\nApp Name: {settings.app_name}")
    print(f"Environment: {settings.environment.value}")
    print(f"Debug: {settings.debug}")
    print(f"Port: {settings.port}")

    print(f"\nDatabase Host: {settings.database.host}")
    print(f"Database Port: {settings.database.port}")
    print(f"Database Name: {settings.database.name}")
    print(f"Database Password Set: {bool(settings.database.password.get_secret_value())}")

    print(f"\nRedis Host: {settings.redis.host}")
    print(f"Debug Endpoints: {settings.features.enable_debug_endpoints}")

    # Clean up
    for key in env_vars:
        os.environ.pop(key, None)


def demonstrate_nested_delimiter():
    """Show nested settings with delimiter."""
    print("\n" + "=" * 60)
    print("DEMO 3: Nested Settings with Delimiter")
    print("=" * 60)

    clear_settings_cache()

    # pydantic-settings supports nested delimiter (__)
    env_vars = {
        "DATABASE__HOST": "nested-db.example.com",
        "DATABASE__PORT": "5434",
        "REDIS__HOST": "nested-redis.example.com",
        "LOGGING__LEVEL": "DEBUG",
    }

    for key, value in env_vars.items():
        os.environ[key] = value

    print("\nUsing nested delimiter (__) for env vars:")
    for key, value in env_vars.items():
        print(f"   {key}={value}")

    settings = Settings()

    print("\n--- Loaded Values ---")
    print(f"Database Host: {settings.database.host}")
    print(f"Database Port: {settings.database.port}")
    print(f"Redis Host: {settings.redis.host}")
    print(f"Log Level: {settings.logging.level.value}")

    # Clean up
    for key in env_vars:
        os.environ.pop(key, None)


def demonstrate_secret_str():
    """Show SecretStr behavior."""
    print("\n" + "=" * 60)
    print("DEMO 4: SecretStr for Sensitive Values")
    print("=" * 60)

    clear_settings_cache()

    os.environ["DB_PASSWORD"] = "super-secret-password"
    os.environ["SECRET_KEY"] = "my-application-secret-key"

    settings = Settings()

    print("\n1. SecretStr in repr/str (hidden):")
    print(f"   settings.database.password = {settings.database.password}")
    print(f"   settings.secret_key = {settings.secret_key}")

    print("\n2. Getting actual value with get_secret_value():")
    print(f"   Password: {settings.database.password.get_secret_value()}")
    print(f"   Secret Key: {settings.secret_key.get_secret_value()}")

    print("\n3. In model_dump() (still hidden by default):")
    dump = settings.database.model_dump()
    print(f"   password field: {dump['password']}")

    print("\n4. Safe connection URL (password masked):")
    print(f"   {settings.database.safe_connection_url}")

    print("\n5. Actual connection URL (password exposed):")
    print(f"   {settings.database.connection_url}")

    # Clean up
    os.environ.pop("DB_PASSWORD", None)
    os.environ.pop("SECRET_KEY", None)


def demonstrate_production_validation():
    """Show production-specific validation."""
    print("\n" + "=" * 60)
    print("DEMO 5: Production Environment Validation")
    print("=" * 60)

    clear_settings_cache()

    print("\n1. Attempting production with debug=true (should fail):")
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DEBUG"] = "true"
    os.environ["SECRET_KEY"] = "production-secret-key-very-long"
    os.environ["DB_PASSWORD"] = "prod-password"

    try:
        Settings()
        print("   ERROR: Should have raised!")
    except ValueError as e:
        print(f"   Caught error: {e}")

    print("\n2. Attempting production with default secret_key (should fail):")
    os.environ["DEBUG"] = "false"
    os.environ["SECRET_KEY"] = "change-me-in-production"

    try:
        Settings()
        print("   ERROR: Should have raised!")
    except ValueError as e:
        print(f"   Caught error: {e}")

    print("\n3. Attempting production without DB password (should fail):")
    os.environ["SECRET_KEY"] = "production-secret-key-very-long"
    os.environ["DB_PASSWORD"] = ""

    try:
        Settings()
        print("   ERROR: Should have raised!")
    except ValueError as e:
        print(f"   Caught error: {e}")

    print("\n4. Valid production configuration:")
    os.environ["DB_PASSWORD"] = "secure-production-password"

    settings = Settings()
    print(f"   Environment: {settings.environment.value}")
    print(f"   Debug: {settings.debug}")
    print(f"   Is Production: {settings.is_production}")

    # Clean up
    for key in ["ENVIRONMENT", "DEBUG", "SECRET_KEY", "DB_PASSWORD"]:
        os.environ.pop(key, None)


def demonstrate_cached_settings():
    """Show the singleton pattern with lru_cache."""
    print("\n" + "=" * 60)
    print("DEMO 6: Cached Settings (Singleton Pattern)")
    print("=" * 60)

    clear_settings_cache()

    print("\n1. First call to get_settings():")
    settings1 = get_settings()
    print(f"   Settings ID: {id(settings1)}")
    print(f"   App Name: {settings1.app_name}")

    print("\n2. Second call to get_settings():")
    settings2 = get_settings()
    print(f"   Settings ID: {id(settings2)}")
    print(f"   Same object: {settings1 is settings2}")

    print("\n3. After clearing cache:")
    clear_settings_cache()
    settings3 = get_settings()
    print(f"   Settings ID: {id(settings3)}")
    print(f"   Same as original: {settings1 is settings3}")


def demonstrate_individual_settings():
    """Show using individual settings classes."""
    print("\n" + "=" * 60)
    print("DEMO 7: Individual Settings Classes")
    print("=" * 60)

    # You can use individual settings classes standalone
    print("\n1. DatabaseSettings standalone:")
    os.environ["DB_HOST"] = "standalone-db.example.com"
    os.environ["DB_PORT"] = "5435"

    db = DatabaseSettings()
    print(f"   Host: {db.host}")
    print(f"   Port: {db.port}")

    print("\n2. FeatureFlags standalone:")
    os.environ["FEATURE_ENABLE_CACHING"] = "false"
    os.environ["FEATURE_MAINTENANCE_MODE"] = "true"

    features = FeatureFlags()
    print(f"   Caching: {features.enable_caching}")
    print(f"   Maintenance: {features.maintenance_mode}")

    # Clean up
    for key in ["DB_HOST", "DB_PORT", "FEATURE_ENABLE_CACHING", "FEATURE_MAINTENANCE_MODE"]:
        os.environ.pop(key, None)


def demonstrate_serialization():
    """Show settings serialization."""
    print("\n" + "=" * 60)
    print("DEMO 8: Settings Serialization")
    print("=" * 60)

    clear_settings_cache()
    settings = Settings()

    print("\n1. model_dump() with exclude:")
    safe_dump = settings.model_dump(
        exclude={"secret_key": True, "database": {"password"}, "redis": {"password"}}
    )
    print(json.dumps(safe_dump, indent=2, default=str)[:500] + "...")

    print("\n2. Exporting specific sections:")
    db_config = settings.database.model_dump(exclude={"password"})
    print(f"\nDatabase config (no password):")
    print(json.dumps(db_config, indent=2))

    print("\n3. Feature flags as dict:")
    print(json.dumps(settings.features.model_dump(), indent=2))


def demonstrate_env_file_loading():
    """Show .env file loading."""
    print("\n" + "=" * 60)
    print("DEMO 9: .env File Loading")
    print("=" * 60)

    # Create a temporary .env file
    env_content = """
# Test .env file
APP_NAME="App From .env File"
ENVIRONMENT=staging
DEBUG=false
PORT=8080
DB_HOST=env-file-db.example.com
"""

    env_path = Path(".env")
    env_path.write_text(env_content)

    print(f"\nCreated .env file with content:")
    print(env_content)

    clear_settings_cache()
    settings = Settings()

    print("--- Loaded from .env ---")
    print(f"App Name: {settings.app_name}")
    print(f"Environment: {settings.environment.value}")
    print(f"Port: {settings.port}")
    print(f"Database Host: {settings.database.host}")

    # Clean up
    env_path.unlink()
    print("\n(.env file deleted)")


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 60)
    print("# PYDANTIC MASTERY - PROJECT 2: CONFIGURATION MANAGER")
    print("#" * 60)

    demonstrate_default_settings()
    demonstrate_environment_variables()
    demonstrate_nested_delimiter()
    demonstrate_secret_str()
    demonstrate_production_validation()
    demonstrate_cached_settings()
    demonstrate_individual_settings()
    demonstrate_serialization()
    demonstrate_env_file_loading()

    print("\n" + "=" * 60)
    print("All demonstrations complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review settings.py to understand the code")
    print("2. Copy .env.example to .env and customize")
    print("3. Run tests: pytest test_settings.py -v")
    print("4. Complete the exercises in exercises.md")


if __name__ == "__main__":
    main()
