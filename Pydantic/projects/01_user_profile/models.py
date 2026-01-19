"""
Project 1: User Profile Validator
=================================

This module demonstrates Pydantic v2 fundamentals for validating user data.

Key Concepts:
- BaseModel fundamentals
- Field types and constraints (Field, EmailStr, constr, conint)
- @field_validator decorator for custom validation
- @model_validator for cross-field validation
- Nested models (Address within UserProfile)
- Model serialization (model_dump, model_dump_json)

Real-World Problem:
APIs and applications constantly receive user data (registration, profile updates).
Invalid data causes database errors, security vulnerabilities, and poor UX.
Pydantic provides declarative validation at the boundary.
"""

import re
import logging
from datetime import datetime
from typing import Annotated

import structlog
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class Address(BaseModel):
    """
    Nested model for user address information.

    Demonstrates:
    - Basic field types with constraints
    - Optional fields with defaults
    - Field descriptions for documentation
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Automatically strip whitespace from strings
    )

    street: str = Field(
        ...,  # ... means required
        min_length=5,
        max_length=200,
        description="Street address including number",
        examples=["123 Main Street"]
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City name"
    )

    state: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="State or province"
    )

    postal_code: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Postal/ZIP code"
    )

    country: str = Field(
        default="USA",
        min_length=2,
        max_length=100,
        description="Country name"
    )

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        """
        Validate postal code format.

        Supports:
        - US ZIP codes: 12345 or 12345-6789
        - Canadian postal codes: A1A 1A1
        - UK postal codes: SW1A 1AA
        """
        # Remove extra spaces
        v = " ".join(v.split())

        # US ZIP code pattern
        us_pattern = r"^\d{5}(-\d{4})?$"
        # Canadian postal code pattern
        ca_pattern = r"^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$"
        # UK postal code pattern (simplified)
        uk_pattern = r"^[A-Za-z]{1,2}\d[A-Za-z\d]? ?\d[A-Za-z]{2}$"

        if not (re.match(us_pattern, v) or re.match(ca_pattern, v) or re.match(uk_pattern, v)):
            # Allow generic alphanumeric postal codes for other countries
            if not re.match(r"^[\w\s-]{3,20}$", v):
                raise ValueError(
                    "Invalid postal code format. "
                    "Expected formats: US (12345), Canada (A1A 1A1), UK (SW1A 1AA)"
                )

        return v.upper()


class UserProfile(BaseModel):
    """
    Main user profile model with comprehensive validation.

    Demonstrates:
    - EmailStr for email validation
    - Field constraints (ge, le, min_length, max_length)
    - Custom field validators
    - Model validators for cross-field validation
    - Nested models (Address)
    - Computed fields
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,  # Re-validate when attributes are changed
        extra="forbid",  # Raise error if extra fields provided
    )

    # Basic identification
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$",
        description="Username must start with a letter and contain only alphanumeric characters and underscores"
    )

    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )

    # Password - stored as string, validated for strength
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be 8-128 characters with specific complexity requirements"
    )

    # Personal information
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's first name"
    )

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's last name"
    )

    # Age with range constraints
    age: int = Field(
        ...,
        ge=13,  # Greater than or equal to 13
        le=120,  # Less than or equal to 120
        description="User age (must be between 13 and 120)"
    )

    # Optional phone number
    phone: str | None = Field(
        default=None,
        description="Phone number in international format"
    )

    # Nested address model
    address: Address = Field(
        ...,
        description="User's primary address"
    )

    # Terms acceptance
    terms_accepted: bool = Field(
        ...,
        description="User must accept terms of service"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Profile creation timestamp"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements.

        Requirements:
        - At least 8 characters (enforced by Field)
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        errors = []

        if not re.search(r"[A-Z]", v):
            errors.append("at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            errors.append("at least one lowercase letter")

        if not re.search(r"\d", v):
            errors.append("at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            errors.append("at least one special character (!@#$%^&*(),.?\":{}|<>)")

        if errors:
            raise ValueError(f"Password must contain {', '.join(errors)}")

        # Check for common weak patterns
        common_patterns = ["password", "123456", "qwerty", "admin"]
        if any(pattern in v.lower() for pattern in common_patterns):
            raise ValueError("Password contains common weak patterns")

        logger.debug("password_validation_passed", password_length=len(v))
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """
        Validate phone number format.

        Accepts various formats and normalizes to E.164-like format.
        """
        if v is None:
            return v

        # Remove all non-digit characters except leading +
        cleaned = re.sub(r"[^\d+]", "", v)

        # Ensure it starts with + or add default country code
        if not cleaned.startswith("+"):
            # Assume US number if no country code
            if len(cleaned) == 10:
                cleaned = "+1" + cleaned
            elif len(cleaned) == 11 and cleaned.startswith("1"):
                cleaned = "+" + cleaned

        # Validate length (E.164 max is 15 digits plus +)
        digits_only = cleaned.replace("+", "")
        if not (7 <= len(digits_only) <= 15):
            raise ValueError(
                "Phone number must have between 7 and 15 digits"
            )

        logger.debug("phone_validation_passed", normalized_phone=cleaned)
        return cleaned

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate name contains only valid characters.

        Allows letters, spaces, hyphens, and apostrophes for names like:
        - Mary-Jane
        - O'Connor
        - José María
        """
        # Allow letters (including unicode), spaces, hyphens, apostrophes
        if not re.match(r"^[\w\s\-']+$", v, re.UNICODE):
            raise ValueError(
                "Name can only contain letters, spaces, hyphens, and apostrophes"
            )

        # Capitalize properly
        return v.title()

    @model_validator(mode="after")
    def validate_terms_and_age(self) -> "UserProfile":
        """
        Cross-field validation after all fields are validated.

        Demonstrates:
        - Accessing multiple fields for validation
        - Business logic that spans fields
        """
        # Terms must be accepted
        if not self.terms_accepted:
            raise ValueError("Terms of service must be accepted")

        # Additional validation for minors (under 18)
        if self.age < 18:
            logger.info(
                "minor_registration",
                username=self.username,
                age=self.age,
                message="Minor user registered - may require parental consent"
            )

        logger.info(
            "user_profile_validated",
            username=self.username,
            email=self.email,
            age=self.age
        )

        return self

    @property
    def full_name(self) -> str:
        """Computed property for full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_adult(self) -> bool:
        """Check if user is 18 or older."""
        return self.age >= 18

    def to_public_dict(self) -> dict:
        """
        Export user data without sensitive fields.

        Use this for API responses where password should not be included.
        """
        return self.model_dump(
            exclude={"password", "terms_accepted"},
            mode="json"
        )

    def to_database_dict(self) -> dict:
        """
        Export user data for database storage.

        Note: In production, password should be hashed before storage.
        """
        data = self.model_dump(mode="json")
        # In production, you would hash the password here
        # data["password"] = hash_password(data["password"])
        return data


class UserProfileUpdate(BaseModel):
    """
    Model for partial user profile updates.

    All fields are optional - only provided fields will be updated.
    Demonstrates:
    - Optional fields for partial updates
    - Reusing validation logic
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    phone: str | None = None

    address: Address | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Reuse name validation from UserProfile."""
        if v is None:
            return v
        if not re.match(r"^[\w\s\-']+$", v, re.UNICODE):
            raise ValueError(
                "Name can only contain letters, spaces, hyphens, and apostrophes"
            )
        return v.title()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Reuse phone validation from UserProfile."""
        if v is None:
            return v
        cleaned = re.sub(r"[^\d+]", "", v)
        if not cleaned.startswith("+"):
            if len(cleaned) == 10:
                cleaned = "+1" + cleaned
            elif len(cleaned) == 11 and cleaned.startswith("1"):
                cleaned = "+" + cleaned
        digits_only = cleaned.replace("+", "")
        if not (7 <= len(digits_only) <= 15):
            raise ValueError("Phone number must have between 7 and 15 digits")
        return cleaned


# Type alias for documentation
PasswordStr = Annotated[str, Field(min_length=8, max_length=128)]
