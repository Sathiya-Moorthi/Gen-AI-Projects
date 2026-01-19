# Project 2: Configuration Manager - Exercises

Complete these exercises to master pydantic-settings for configuration management.

---

## Exercise 1: Add AWS Settings

**Objective**: Create a new `AWSSettings` nested model for AWS credentials.

**Requirements**:
- Add fields for:
  - `aws_access_key_id: SecretStr`
  - `aws_secret_access_key: SecretStr`
  - `aws_region: str` (default: "us-east-1")
  - `aws_endpoint_url: HttpUrl | None` (for LocalStack/testing)
  - `s3_bucket: str`
- Use `AWS_` prefix for environment variables
- Integrate into main `Settings` class

**Hints**:
```python
class AWSSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AWS_")

    access_key_id: SecretStr = Field(...)
    secret_access_key: SecretStr = Field(...)
    region: str = Field(default="us-east-1")
    # ...
```

**Test with**:
```bash
AWS_ACCESS_KEY_ID=AKIAXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_REGION=us-west-2
AWS_S3_BUCKET=my-app-bucket
```

---

## Exercise 2: Add Email/SMTP Settings

**Objective**: Create `EmailSettings` for sending emails.

**Requirements**:
- Fields:
  - `smtp_host: str`
  - `smtp_port: int` (default: 587)
  - `smtp_user: str`
  - `smtp_password: SecretStr`
  - `smtp_use_tls: bool` (default: True)
  - `from_email: EmailStr`
  - `from_name: str`
- Add `@model_validator` to ensure TLS is enabled in production

**Test cases to write**:
```python
def test_email_settings_defaults():
    ...

def test_production_requires_tls():
    # Should fail if smtp_use_tls=False in production
    ...
```

---

## Exercise 3: Environment-Specific Config Files

**Objective**: Load different `.env` files based on environment.

**Requirements**:
- Support loading:
  - `.env.development`
  - `.env.staging`
  - `.env.production`
- Override base `.env` with environment-specific file
- Implement a `get_env_file()` function

**Hints**:
```python
def get_env_files() -> list[str]:
    """Return list of .env files to load based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    files = [".env"]  # Base config

    env_specific = f".env.{env}"
    if Path(env_specific).exists():
        files.append(env_specific)

    return files

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_files(),
        # ...
    )
```

---

## Exercise 4: Add Rate Limiting Settings

**Objective**: Create `RateLimitSettings` with different limits per tier.

**Requirements**:
- Fields:
  - `enabled: bool`
  - `requests_per_minute: int`
  - `requests_per_hour: int`
  - `burst_limit: int`
- Add a method `get_limits_for_tier(tier: str)` returning limits
- Tiers: "free", "basic", "premium", "enterprise"

**Example usage**:
```python
rate_limits = RateLimitSettings()

# Default limits
print(rate_limits.requests_per_minute)  # 60

# Tier-specific
limits = rate_limits.get_limits_for_tier("premium")
print(limits)  # {"requests_per_minute": 300, ...}
```

---

## Exercise 5: Secrets from Files

**Objective**: Support loading secrets from files (Docker secrets pattern).

**Requirements**:
- Support `DB_PASSWORD_FILE=/run/secrets/db_password` pattern
- If `*_FILE` env var exists, read secret from that file
- Implement using `@field_validator` or settings customization

**Hints**:
```python
from pydantic import field_validator

@field_validator("password", mode="before")
@classmethod
def load_secret_from_file(cls, v: str) -> str:
    """Load secret from file if *_FILE pattern used."""
    file_key = "DB_PASSWORD_FILE"
    if file_key in os.environ:
        secret_file = Path(os.environ[file_key])
        if secret_file.exists():
            return secret_file.read_text().strip()
    return v
```

---

## Exercise 6: Configuration Validation Report

**Objective**: Create a method that validates and reports configuration status.

**Requirements**:
- Add `validate_all()` method to `Settings`
- Check:
  - Database connectivity (mock)
  - Redis connectivity (mock)
  - Required API keys present
  - All URLs are reachable (mock)
- Return a report dict with status for each check

**Example output**:
```python
settings = Settings()
report = settings.validate_all()
print(report)
# {
#     "database": {"status": "ok", "host": "localhost"},
#     "redis": {"status": "ok", "host": "localhost"},
#     "openai_api": {"status": "warning", "message": "API key not set"},
#     "overall": "warning"
# }
```

---

## Exercise 7: Dynamic Feature Flags

**Objective**: Support runtime feature flag updates.

**Requirements**:
- Create `DynamicFeatureFlags` class
- Allow updating flags without restart
- Add `reload()` method
- Implement thread-safe access

**Hints**:
```python
from threading import Lock

class DynamicFeatureFlags:
    _lock = Lock()
    _flags: dict[str, bool] = {}

    def reload(self):
        """Reload flags from environment/file."""
        with self._lock:
            # Re-read from environment
            ...

    def is_enabled(self, flag_name: str) -> bool:
        with self._lock:
            return self._flags.get(flag_name, False)
```

---

## Exercise 8: Export Configuration

**Objective**: Add methods to export settings in different formats.

**Requirements**:
- `to_env_file()` - Export as .env format
- `to_yaml()` - Export as YAML (use pyyaml)
- `to_json()` - Export as JSON (with secrets masked)
- Handle nested settings properly

**Example**:
```python
settings = Settings()

# Export to .env format
print(settings.to_env_file())
# APP_NAME="Pydantic Mastery App"
# ENVIRONMENT="development"
# DB_HOST="localhost"
# ...

# Export to YAML
print(settings.to_yaml())
# app_name: Pydantic Mastery App
# database:
#   host: localhost
#   port: 5432
# ...
```

---

## Exercise 9: Settings Schema Documentation

**Objective**: Auto-generate documentation for all settings.

**Requirements**:
- Create `generate_docs()` method
- Include:
  - Field name
  - Environment variable name
  - Type
  - Default value
  - Description
- Output as Markdown table

**Example output**:
```markdown
## Application Settings

| Env Variable | Type | Default | Description |
|-------------|------|---------|-------------|
| APP_NAME | str | "Pydantic Mastery App" | Application name |
| ENVIRONMENT | Environment | development | Application environment |
| DEBUG | bool | false | Debug mode |

## Database Settings (prefix: DB_)

| Env Variable | Type | Default | Description |
|-------------|------|---------|-------------|
| DB_HOST | str | "localhost" | Database host |
...
```

---

## Exercise 10: Challenge - Multi-Tenant Configuration

**Objective**: Support different configurations per tenant.

**Requirements**:
- Create `TenantSettings` that can override base `Settings`
- Load tenant-specific overrides from:
  - Environment: `TENANT_<id>_<setting>`
  - Files: `config/tenants/<tenant_id>.env`
- Implement `get_settings_for_tenant(tenant_id: str)`

**Example**:
```python
# Base settings
settings = Settings()  # DB_HOST=main-db.example.com

# Tenant-specific
tenant_settings = get_settings_for_tenant("acme")
# Loads TENANT_ACME_DB_HOST or config/tenants/acme.env
# Merges with base settings
```

---

## Solutions

After attempting, create a `solutions/` directory with your implementations.

**Checklist before moving to Project 3**:
- [ ] Completed at least 5 exercises
- [ ] All tests pass (`pytest test_settings.py -v`)
- [ ] Understand `BaseSettings` vs `BaseModel`
- [ ] Can use `SecretStr` for sensitive data
- [ ] Understand `.env` file loading
- [ ] Can validate environment-specific requirements
- [ ] Comfortable with nested settings

---

## Key Takeaways

1. **BaseSettings** loads from environment variables automatically
2. **SettingsConfigDict** configures `.env` loading and prefixes
3. **SecretStr** protects sensitive values from accidental exposure
4. **Nested settings** organize complex configurations
5. **model_validator** enables cross-field and environment validation
6. **@lru_cache** implements singleton pattern for settings
7. **Prefixes** namespace environment variables (DB_, REDIS_, etc.)

Ready for Project 3? Move on to the Data Pipeline Input Validator!
