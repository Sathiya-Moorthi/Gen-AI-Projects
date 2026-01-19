# Project 1: User Profile Validator - Exercises

Complete these exercises to reinforce your understanding of Pydantic fundamentals.

---

## Exercise 1: Add a Bio Field

**Objective**: Add an optional `bio` field to `UserProfile` with length constraints.

**Requirements**:
- Field should be optional (can be `None`)
- Maximum 500 characters
- Should strip whitespace
- Should reject strings that are only whitespace

**Hints**:
```python
bio: str | None = Field(
    default=None,
    max_length=500,
    # Add more constraints...
)
```

**Validation to add**:
- Create a `@field_validator` that returns `None` if the bio is only whitespace

**Test your solution**:
```python
# Should work:
user = UserProfile(..., bio="I love Python!")
user = UserProfile(..., bio=None)
user = UserProfile(...)  # bio defaults to None

# Should fail:
user = UserProfile(..., bio="x" * 501)  # Too long
user = UserProfile(..., bio="   ")  # Only whitespace -> should become None
```

---

## Exercise 2: Add Social Media Links

**Objective**: Create a nested `SocialLinks` model with URL validation.

**Requirements**:
- Create a new `SocialLinks` model with optional fields:
  - `twitter`: Optional URL
  - `linkedin`: Optional URL
  - `github`: Optional URL
- Add `social_links: SocialLinks | None` to `UserProfile`
- Validate that URLs start with `https://`

**Hints**:
```python
from pydantic import HttpUrl

class SocialLinks(BaseModel):
    twitter: HttpUrl | None = None
    linkedin: HttpUrl | None = None
    github: HttpUrl | None = None
```

**Test your solution**:
```python
# Should work:
links = SocialLinks(github="https://github.com/username")

# Should fail:
links = SocialLinks(github="http://github.com/username")  # Not https
links = SocialLinks(github="not-a-url")
```

---

## Exercise 3: Custom Error Messages

**Objective**: Provide user-friendly error messages for password validation.

**Requirements**:
- Modify the `validate_password_strength` validator
- Instead of listing missing requirements, provide a user-friendly message
- Include a "password strength score" (0-4 based on criteria met)

**Example output**:
```python
# Instead of:
"Password must contain at least one uppercase letter, at least one digit"

# Provide:
"Password strength: 2/4. Missing: uppercase letter, digit"
```

**Hints**:
```python
@field_validator("password")
@classmethod
def validate_password_strength(cls, v: str) -> str:
    score = 0
    missing = []

    if re.search(r"[A-Z]", v):
        score += 1
    else:
        missing.append("uppercase letter")

    # Continue for other criteria...

    if score < 4:
        raise ValueError(f"Password strength: {score}/4. Missing: {', '.join(missing)}")

    return v
```

---

## Exercise 4: Date of Birth Instead of Age

**Objective**: Replace `age` with `date_of_birth` and compute age dynamically.

**Requirements**:
- Replace `age: int` with `date_of_birth: date`
- Add a `@property` that computes current age
- Validate that date is not in the future
- Validate that computed age is between 13 and 120

**Hints**:
```python
from datetime import date

date_of_birth: date = Field(..., description="User's date of birth")

@field_validator("date_of_birth")
@classmethod
def validate_dob(cls, v: date) -> date:
    if v > date.today():
        raise ValueError("Date of birth cannot be in the future")
    # Check age range...
    return v

@property
def age(self) -> int:
    today = date.today()
    return today.year - self.date_of_birth.year - (
        (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
    )
```

---

## Exercise 5: Username Uniqueness Check

**Objective**: Add a validator that checks username against a "database" of existing users.

**Requirements**:
- Create a mock database (set or list) of existing usernames
- Add a `@field_validator` that checks if username is already taken
- Make the validator configurable (can be disabled for testing)

**Hints**:
```python
# Mock database
EXISTING_USERNAMES = {"admin", "root", "system", "test"}

@field_validator("username")
@classmethod
def check_username_unique(cls, v: str) -> str:
    if v.lower() in EXISTING_USERNAMES:
        raise ValueError(f"Username '{v}' is already taken")
    return v
```

**Challenge**: How would you make this work with an actual async database call?

---

## Exercise 6: Computed Field for Profile Completeness

**Objective**: Add a computed field showing profile completeness percentage.

**Requirements**:
- Use Pydantic's `@computed_field` decorator
- Calculate percentage based on filled optional fields
- Optional fields: `phone`, `bio` (from Exercise 1), `social_links` (from Exercise 2)

**Hints**:
```python
from pydantic import computed_field

@computed_field
@property
def profile_completeness(self) -> int:
    """Return profile completeness as percentage (0-100)."""
    optional_fields = ["phone", "bio", "social_links"]
    filled = sum(1 for f in optional_fields if getattr(self, f, None) is not None)
    return int((filled / len(optional_fields)) * 100)
```

---

## Exercise 7: Write Additional Tests

**Objective**: Improve test coverage for edge cases.

**Write tests for**:

1. **Boundary values**:
   - Age exactly 13 (minimum)
   - Age exactly 120 (maximum)
   - Username exactly 3 characters (minimum)
   - Username exactly 30 characters (maximum)

2. **Unicode handling**:
   - Names with accents (José, François)
   - Non-Latin scripts (if supported)

3. **Serialization edge cases**:
   - Datetime serialization format
   - Nested model serialization
   - `exclude_unset` vs `exclude_none`

4. **Error message quality**:
   - Verify error messages are user-friendly
   - Test that multiple errors are all reported

---

## Exercise 8: Create a UserLogin Model

**Objective**: Create a separate model for login credentials.

**Requirements**:
- Only requires `email` or `username` (not both)
- Requires `password`
- Use `@model_validator(mode="before")` to allow either identifier

**Hints**:
```python
class UserLogin(BaseModel):
    identifier: str  # Could be email or username
    password: str

    @model_validator(mode="before")
    @classmethod
    def extract_identifier(cls, data: dict) -> dict:
        if "email" in data:
            data["identifier"] = data.pop("email")
        elif "username" in data:
            data["identifier"] = data.pop("username")
        return data
```

---

## Exercise 9: Add Logging Throughout

**Objective**: Add structured logging to track validation events.

**Requirements**:
- Log when validation succeeds (info level)
- Log when validation fails (warning level)
- Include relevant context (field names, error types)
- Use structlog for structured output

**Example**:
```python
logger.info(
    "user_validation_success",
    username=self.username,
    email=self.email,
    fields_validated=["username", "email", "password", "age"]
)

logger.warning(
    "user_validation_failed",
    error_count=len(errors),
    failed_fields=["email", "password"]
)
```

---

## Exercise 10: Challenge - Create a PasswordReset Flow

**Objective**: Design models for a password reset flow.

**Create these models**:

1. `PasswordResetRequest`:
   - `email: EmailStr`
   - Validates email exists (mock check)

2. `PasswordResetToken`:
   - `token: str` (UUID format)
   - `email: EmailStr`
   - `expires_at: datetime`
   - `used: bool = False`

3. `PasswordResetConfirm`:
   - `token: str`
   - `new_password: str` (with strength validation)
   - `confirm_password: str`
   - Validate passwords match using `@model_validator`

**Test the full flow**:
```python
# 1. Request reset
request = PasswordResetRequest(email="user@example.com")

# 2. Generate token (in real app, this would be stored)
token = PasswordResetToken(
    token=str(uuid.uuid4()),
    email=request.email,
    expires_at=datetime.now() + timedelta(hours=24)
)

# 3. Confirm reset
confirm = PasswordResetConfirm(
    token=token.token,
    new_password="NewSecureP@ss123!",
    confirm_password="NewSecureP@ss123!"
)
```

---

## Solutions

Solutions are available in the `solutions/` directory (create this yourself after attempting!).

**Checklist before moving to Project 2**:
- [ ] Completed at least 5 exercises
- [ ] All tests pass (`pytest test_models.py -v`)
- [ ] Understand `@field_validator` vs `@model_validator`
- [ ] Can serialize models to dict and JSON
- [ ] Understand `exclude_unset` and `exclude_none`
- [ ] Comfortable with nested models

---

## Key Takeaways

1. **BaseModel** provides automatic validation on instantiation
2. **Field()** allows constraints and metadata
3. **@field_validator** validates individual fields
4. **@model_validator** validates across multiple fields
5. **Nested models** compose complex structures
6. **Serialization** with `model_dump()` and `model_dump_json()`
7. **ConfigDict** customizes model behavior

Ready for Project 2? Move on to the Configuration Manager!
