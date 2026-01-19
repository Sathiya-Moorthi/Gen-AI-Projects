"""
Project 1: User Profile Validator - Tests
==========================================

Comprehensive pytest tests demonstrating Pydantic validation.

Run with: pytest test_models.py -v
"""

import json
import pytest
from pydantic import ValidationError

from models import Address, UserProfile, UserProfileUpdate


# ============================================================================
# FIXTURES - Reusable test data
# ============================================================================

@pytest.fixture
def valid_address_data():
    """Return valid address data."""
    return {
        "street": "123 Main Street",
        "city": "San Francisco",
        "state": "California",
        "postal_code": "94102",
        "country": "USA"
    }


@pytest.fixture
def valid_user_data(valid_address_data):
    """Return valid user profile data."""
    return {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password": "SecureP@ss123!",
        "first_name": "John",
        "last_name": "Doe",
        "age": 28,
        "phone": "555-123-4567",
        "address": valid_address_data,
        "terms_accepted": True
    }


# ============================================================================
# ADDRESS MODEL TESTS
# ============================================================================

class TestAddress:
    """Tests for the Address model."""

    def test_valid_address(self, valid_address_data):
        """Test creating a valid address."""
        address = Address(**valid_address_data)
        assert address.street == "123 Main Street"
        assert address.city == "San Francisco"
        assert address.state == "California"
        assert address.postal_code == "94102"
        assert address.country == "USA"

    def test_default_country(self):
        """Test that country defaults to USA."""
        address = Address(
            street="123 Main St",
            city="Boston",
            state="MA",
            postal_code="02101"
        )
        assert address.country == "USA"

    @pytest.mark.parametrize("postal_code,expected", [
        ("12345", "12345"),  # US 5-digit
        ("12345-6789", "12345-6789"),  # US 9-digit
        ("M5V 3A8", "M5V 3A8"),  # Canadian
        ("m5v3a8", "M5V3A8"),  # Canadian lowercase
        ("SW1A 1AA", "SW1A 1AA"),  # UK
        ("sw1a1aa", "SW1A1AA"),  # UK lowercase
    ])
    def test_valid_postal_codes(self, postal_code, expected):
        """Test various valid postal code formats."""
        address = Address(
            street="123 Test Street",
            city="Test City",
            state="TS",
            postal_code=postal_code
        )
        assert address.postal_code == expected

    def test_whitespace_stripping(self):
        """Test that whitespace is stripped from string fields."""
        address = Address(
            street="  123 Main St  ",
            city="  Boston  ",
            state="  MA  ",
            postal_code="02101"
        )
        assert address.street == "123 Main St"
        assert address.city == "Boston"
        assert address.state == "MA"

    def test_street_too_short(self):
        """Test validation fails for short street."""
        with pytest.raises(ValidationError) as exc_info:
            Address(
                street="St",  # Too short
                city="Boston",
                state="MA",
                postal_code="02101"
            )
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("street",)
        assert "at least 5" in errors[0]["msg"]


# ============================================================================
# USER PROFILE TESTS
# ============================================================================

class TestUserProfile:
    """Tests for the UserProfile model."""

    def test_valid_user_profile(self, valid_user_data):
        """Test creating a valid user profile."""
        user = UserProfile(**valid_user_data)
        assert user.username == "johndoe"
        assert user.email == "john.doe@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.age == 28
        assert user.terms_accepted is True

    def test_full_name_property(self, valid_user_data):
        """Test the full_name computed property."""
        user = UserProfile(**valid_user_data)
        assert user.full_name == "John Doe"

    def test_is_adult_property(self, valid_user_data):
        """Test the is_adult computed property."""
        # Adult user
        user = UserProfile(**valid_user_data)
        assert user.is_adult is True

        # Minor user
        valid_user_data["age"] = 15
        minor = UserProfile(**valid_user_data)
        assert minor.is_adult is False

    # ---------- Email Validation ----------

    def test_invalid_email(self, valid_user_data):
        """Test that invalid email is rejected."""
        valid_user_data["email"] = "not-an-email"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "user.name@example.com",
        "user+tag@example.com",
        "user@subdomain.example.com",
    ])
    def test_valid_emails(self, valid_user_data, email):
        """Test various valid email formats."""
        valid_user_data["email"] = email
        user = UserProfile(**valid_user_data)
        assert user.email == email

    # ---------- Password Validation ----------

    def test_password_too_short(self, valid_user_data):
        """Test that short password is rejected."""
        valid_user_data["password"] = "Short1!"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any("at least 8" in str(e["msg"]) for e in errors)

    def test_password_no_uppercase(self, valid_user_data):
        """Test password requires uppercase letter."""
        valid_user_data["password"] = "lowercase123!"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any("uppercase" in str(e["msg"]) for e in errors)

    def test_password_no_lowercase(self, valid_user_data):
        """Test password requires lowercase letter."""
        valid_user_data["password"] = "UPPERCASE123!"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any("lowercase" in str(e["msg"]) for e in errors)

    def test_password_no_digit(self, valid_user_data):
        """Test password requires digit."""
        valid_user_data["password"] = "NoDigitsHere!"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any("digit" in str(e["msg"]) for e in errors)

    def test_password_no_special_char(self, valid_user_data):
        """Test password requires special character."""
        valid_user_data["password"] = "NoSpecial123"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any("special" in str(e["msg"]) for e in errors)

    def test_password_common_pattern(self, valid_user_data):
        """Test password rejects common patterns."""
        valid_user_data["password"] = "Password123!"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any("common" in str(e["msg"]).lower() for e in errors)

    # ---------- Age Validation ----------

    def test_age_minimum(self, valid_user_data):
        """Test age minimum constraint."""
        valid_user_data["age"] = 12
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("age",) for e in errors)

    def test_age_maximum(self, valid_user_data):
        """Test age maximum constraint."""
        valid_user_data["age"] = 121
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("age",) for e in errors)

    @pytest.mark.parametrize("age", [13, 18, 65, 120])
    def test_valid_ages(self, valid_user_data, age):
        """Test valid age values."""
        valid_user_data["age"] = age
        user = UserProfile(**valid_user_data)
        assert user.age == age

    # ---------- Username Validation ----------

    def test_username_pattern_starts_with_letter(self, valid_user_data):
        """Test username must start with letter."""
        valid_user_data["username"] = "123user"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("username",) for e in errors)

    def test_username_pattern_valid_chars(self, valid_user_data):
        """Test username allows only valid characters."""
        valid_user_data["username"] = "user@name"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("username",) for e in errors)

    @pytest.mark.parametrize("username", [
        "user",
        "User123",
        "user_name",
        "UserName_123",
    ])
    def test_valid_usernames(self, valid_user_data, username):
        """Test valid username patterns."""
        valid_user_data["username"] = username
        user = UserProfile(**valid_user_data)
        assert user.username == username

    # ---------- Phone Validation ----------

    def test_phone_normalization_us(self, valid_user_data):
        """Test US phone number normalization."""
        valid_user_data["phone"] = "555-123-4567"
        user = UserProfile(**valid_user_data)
        assert user.phone == "+15551234567"

    def test_phone_normalization_with_country_code(self, valid_user_data):
        """Test phone with country code."""
        valid_user_data["phone"] = "+44 20 7946 0958"
        user = UserProfile(**valid_user_data)
        assert user.phone == "+442079460958"

    def test_phone_optional(self, valid_user_data):
        """Test phone is optional."""
        valid_user_data["phone"] = None
        user = UserProfile(**valid_user_data)
        assert user.phone is None

    def test_phone_invalid_length(self, valid_user_data):
        """Test phone with invalid length."""
        valid_user_data["phone"] = "123"  # Too short
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any("7 and 15" in str(e["msg"]) for e in errors)

    # ---------- Name Validation ----------

    def test_name_capitalization(self, valid_user_data):
        """Test names are capitalized."""
        valid_user_data["first_name"] = "john"
        valid_user_data["last_name"] = "DOE"
        user = UserProfile(**valid_user_data)
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    @pytest.mark.parametrize("name", [
        "Mary-Jane",
        "O'Connor",
        "José",
        "María",
    ])
    def test_special_name_characters(self, valid_user_data, name):
        """Test names with special characters."""
        valid_user_data["first_name"] = name
        user = UserProfile(**valid_user_data)
        assert user.first_name == name.title()

    # ---------- Terms Acceptance ----------

    def test_terms_must_be_accepted(self, valid_user_data):
        """Test terms must be accepted."""
        valid_user_data["terms_accepted"] = False
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any("must be accepted" in str(e["msg"]) for e in errors)

    # ---------- Serialization ----------

    def test_model_dump(self, valid_user_data):
        """Test model_dump serialization."""
        user = UserProfile(**valid_user_data)
        data = user.model_dump()

        assert data["username"] == "johndoe"
        assert data["email"] == "john.doe@example.com"
        assert "password" in data  # Full dump includes password
        assert isinstance(data["address"], dict)

    def test_to_public_dict(self, valid_user_data):
        """Test public dict excludes sensitive fields."""
        user = UserProfile(**valid_user_data)
        public = user.to_public_dict()

        assert "password" not in public
        assert "terms_accepted" not in public
        assert public["email"] == "john.doe@example.com"

    def test_model_dump_json(self, valid_user_data):
        """Test JSON serialization."""
        user = UserProfile(**valid_user_data)
        json_str = user.model_dump_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["username"] == "johndoe"

    # ---------- Extra Fields ----------

    def test_extra_fields_forbidden(self, valid_user_data):
        """Test extra fields are rejected."""
        valid_user_data["unknown_field"] = "value"
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)
        errors = exc_info.value.errors()
        assert any("extra" in str(e["type"]) for e in errors)

    # ---------- Validation on Assignment ----------

    def test_validate_assignment(self, valid_user_data):
        """Test validation occurs on attribute assignment."""
        user = UserProfile(**valid_user_data)

        # Valid assignment
        user.age = 30
        assert user.age == 30

        # Invalid assignment should raise
        with pytest.raises(ValidationError):
            user.age = 5


# ============================================================================
# USER PROFILE UPDATE TESTS
# ============================================================================

class TestUserProfileUpdate:
    """Tests for the UserProfileUpdate model."""

    def test_partial_update_phone_only(self):
        """Test updating only phone."""
        update = UserProfileUpdate(phone="555-999-1234")
        assert update.phone == "+15559991234"
        assert update.first_name is None
        assert update.address is None

    def test_partial_update_address_only(self):
        """Test updating only address."""
        update = UserProfileUpdate(
            address={
                "street": "456 New Street",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001"
            }
        )
        assert update.address is not None
        assert update.address.city == "New York"
        assert update.first_name is None

    def test_exclude_unset(self):
        """Test exclude_unset for partial updates."""
        update = UserProfileUpdate(phone="555-999-1234")
        data = update.model_dump(exclude_unset=True)

        # Only phone should be in the dict
        assert "phone" in data
        assert "first_name" not in data
        assert "last_name" not in data
        assert "address" not in data


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple features."""

    def test_create_update_flow(self, valid_user_data):
        """Test creating a user then applying partial update."""
        # Create user
        user = UserProfile(**valid_user_data)
        original_name = user.first_name

        # Create update
        update = UserProfileUpdate(
            first_name="Johnny",
            phone="888-555-1234"
        )

        # Apply update
        update_data = update.model_dump(exclude_unset=True)

        # In a real app, you'd merge and create new model
        updated_user_data = {**user.model_dump(), **update_data}
        updated_user = UserProfile(**updated_user_data)

        assert updated_user.first_name == "Johnny"
        assert updated_user.phone == "+18885551234"
        # Original unchanged
        assert user.first_name == original_name

    def test_multiple_validation_errors(self, valid_user_data):
        """Test that all errors are collected."""
        valid_user_data["email"] = "invalid"
        valid_user_data["password"] = "weak"
        valid_user_data["age"] = 5
        valid_user_data["terms_accepted"] = False

        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**valid_user_data)

        errors = exc_info.value.errors()
        # Should have multiple errors
        assert len(errors) >= 3

        # Check specific fields have errors
        error_locs = {e["loc"][0] for e in errors}
        assert "email" in error_locs
        assert "password" in error_locs
        assert "age" in error_locs
