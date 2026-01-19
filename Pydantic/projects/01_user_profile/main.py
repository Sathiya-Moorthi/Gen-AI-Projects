"""
Project 1: User Profile Validator - Main Demonstration
======================================================

This script demonstrates all the key concepts from the User Profile models.

Run with: python main.py
"""

import json
import logging
from pydantic import ValidationError
import structlog

from models import Address, UserProfile, UserProfileUpdate

# Configure logging level
logging.basicConfig(level=logging.INFO)


def demonstrate_valid_user():
    """Create a valid user profile and show serialization options."""
    print("\n" + "=" * 60)
    print("DEMO 1: Creating a Valid User Profile")
    print("=" * 60)

    # Valid user data
    user_data = {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password": "SecureP@ss123!",
        "first_name": "john",  # Will be auto-capitalized
        "last_name": "doe",    # Will be auto-capitalized
        "age": 28,
        "phone": "555-123-4567",  # Will be normalized
        "address": {
            "street": "123 Main Street",
            "city": "San Francisco",
            "state": "California",
            "postal_code": "94102",
            "country": "USA"
        },
        "terms_accepted": True
    }

    # Create and validate
    user = UserProfile(**user_data)

    print("\n1. Created User Profile:")
    print(f"   Full Name: {user.full_name}")
    print(f"   Email: {user.email}")
    print(f"   Age: {user.age}")
    print(f"   Is Adult: {user.is_adult}")
    print(f"   Phone (normalized): {user.phone}")

    print("\n2. Address (Nested Model):")
    print(f"   {user.address.street}")
    print(f"   {user.address.city}, {user.address.state} {user.address.postal_code}")
    print(f"   {user.address.country}")

    print("\n3. Serialization - model_dump():")
    print(json.dumps(user.model_dump(mode="json"), indent=2, default=str))

    print("\n4. Public Export (excludes password):")
    print(json.dumps(user.to_public_dict(), indent=2, default=str))

    print("\n5. JSON String - model_dump_json():")
    print(user.model_dump_json(indent=2, exclude={"password"}))

    return user


def demonstrate_validation_errors():
    """Show how Pydantic handles invalid data."""
    print("\n" + "=" * 60)
    print("DEMO 2: Validation Error Handling")
    print("=" * 60)

    invalid_cases = [
        {
            "name": "Invalid Email",
            "data": {
                "username": "testuser",
                "email": "not-an-email",  # Invalid
                "password": "SecureP@ss123!",
                "first_name": "Test",
                "last_name": "User",
                "age": 25,
                "address": {
                    "street": "123 Test St",
                    "city": "Boston",
                    "state": "MA",
                    "postal_code": "02101"
                },
                "terms_accepted": True
            }
        },
        {
            "name": "Weak Password",
            "data": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "weak",  # Too short, no complexity
                "first_name": "Test",
                "last_name": "User",
                "age": 25,
                "address": {
                    "street": "123 Test St",
                    "city": "Boston",
                    "state": "MA",
                    "postal_code": "02101"
                },
                "terms_accepted": True
            }
        },
        {
            "name": "Age Out of Range",
            "data": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecureP@ss123!",
                "first_name": "Test",
                "last_name": "User",
                "age": 10,  # Below minimum (13)
                "address": {
                    "street": "123 Test St",
                    "city": "Boston",
                    "state": "MA",
                    "postal_code": "02101"
                },
                "terms_accepted": True
            }
        },
        {
            "name": "Terms Not Accepted",
            "data": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecureP@ss123!",
                "first_name": "Test",
                "last_name": "User",
                "age": 25,
                "address": {
                    "street": "123 Test St",
                    "city": "Boston",
                    "state": "MA",
                    "postal_code": "02101"
                },
                "terms_accepted": False  # Must be True
            }
        },
        {
            "name": "Invalid Username Pattern",
            "data": {
                "username": "123user",  # Can't start with number
                "email": "test@example.com",
                "password": "SecureP@ss123!",
                "first_name": "Test",
                "last_name": "User",
                "age": 25,
                "address": {
                    "street": "123 Test St",
                    "city": "Boston",
                    "state": "MA",
                    "postal_code": "02101"
                },
                "terms_accepted": True
            }
        },
    ]

    for case in invalid_cases:
        print(f"\n--- Testing: {case['name']} ---")
        try:
            UserProfile(**case["data"])
            print("ERROR: Should have raised ValidationError!")
        except ValidationError as e:
            print(f"Caught {e.error_count()} validation error(s):")
            for error in e.errors():
                loc = " -> ".join(str(l) for l in error["loc"])
                print(f"  - Field '{loc}': {error['msg']}")


def demonstrate_multiple_errors():
    """Show how Pydantic collects all errors at once."""
    print("\n" + "=" * 60)
    print("DEMO 3: Multiple Validation Errors")
    print("=" * 60)

    # Data with multiple problems
    bad_data = {
        "username": "ab",  # Too short
        "email": "invalid",  # Not an email
        "password": "short",  # Too weak
        "first_name": "",  # Too short
        "last_name": "User",
        "age": 5,  # Too young
        "address": {
            "street": "St",  # Too short
            "city": "X",  # Too short
            "state": "Y",  # OK (2 char minimum)
            "postal_code": "invalid!!!"  # Invalid format
        },
        "terms_accepted": False
    }

    print("\nAttempting to create user with multiple invalid fields...")
    try:
        UserProfile(**bad_data)
    except ValidationError as e:
        print(f"\nCaught {e.error_count()} validation errors:")
        print("-" * 40)

        # Group errors by location
        for error in e.errors():
            loc = " -> ".join(str(l) for l in error["loc"])
            error_type = error["type"]
            msg = error["msg"]
            print(f"\nField: {loc}")
            print(f"  Type: {error_type}")
            print(f"  Message: {msg}")

        # Show JSON representation
        print("\n" + "-" * 40)
        print("Errors as JSON (for API responses):")
        print(e.json(indent=2))


def demonstrate_nested_model():
    """Show nested model validation in detail."""
    print("\n" + "=" * 60)
    print("DEMO 4: Nested Model (Address) Validation")
    print("=" * 60)

    # Valid addresses with different postal codes
    addresses = [
        {"street": "123 Main St", "city": "NYC", "state": "NY", "postal_code": "10001"},
        {"street": "456 Oak Ave", "city": "LA", "state": "CA", "postal_code": "90210-1234"},
        {"street": "789 Queen St", "city": "Toronto", "state": "ON", "postal_code": "M5V 3A8", "country": "Canada"},
        {"street": "10 Downing", "city": "London", "state": "England", "postal_code": "SW1A 2AA", "country": "UK"},
    ]

    print("\nValidating addresses with different postal code formats:")
    for addr_data in addresses:
        try:
            addr = Address(**addr_data)
            print(f"\n  {addr.postal_code} ({addr.country})")
            print(f"    {addr.street}, {addr.city}, {addr.state}")
        except ValidationError as e:
            print(f"\n  INVALID: {addr_data['postal_code']}")
            for error in e.errors():
                print(f"    Error: {error['msg']}")


def demonstrate_partial_update():
    """Show partial update pattern with UserProfileUpdate."""
    print("\n" + "=" * 60)
    print("DEMO 5: Partial Updates")
    print("=" * 60)

    # Create initial user
    user = UserProfile(
        username="jsmith",
        email="jsmith@example.com",
        password="OldP@ssword123!",
        first_name="John",
        last_name="Smith",
        age=30,
        address={
            "street": "100 Old Street",
            "city": "Boston",
            "state": "MA",
            "postal_code": "02101"
        },
        terms_accepted=True
    )

    print("\nOriginal User:")
    print(f"  Name: {user.full_name}")
    print(f"  Phone: {user.phone}")
    print(f"  Address: {user.address.street}, {user.address.city}")

    # Partial update - only changing some fields
    update_data = {
        "phone": "617-555-0123",
        "address": {
            "street": "200 New Avenue",
            "city": "Cambridge",
            "state": "MA",
            "postal_code": "02139"
        }
    }

    update = UserProfileUpdate(**update_data)

    print("\nUpdate Request:")
    print(f"  Phone: {update.phone}")
    print(f"  Address: {update.address.street}, {update.address.city}")

    # Apply update to user (simulating database update)
    update_dict = update.model_dump(exclude_unset=True)
    print(f"\nFields to update: {list(update_dict.keys())}")

    # In a real application, you would merge this with the existing user
    # For demonstration, show what exclude_unset does
    print("\nUpdate dict (exclude_unset=True):")
    print(json.dumps(update_dict, indent=2, default=str))


def demonstrate_model_config():
    """Show ConfigDict effects."""
    print("\n" + "=" * 60)
    print("DEMO 6: Model Configuration Effects")
    print("=" * 60)

    # Demonstrate str_strip_whitespace
    print("\n1. Automatic whitespace stripping:")
    user = UserProfile(
        username="testuser",
        email="  test@example.com  ",  # Leading/trailing spaces
        password="SecureP@ss123!",
        first_name="  Alice  ",  # Spaces
        last_name="  Smith  ",
        age=25,
        address={
            "street": "  123 Main St  ",
            "city": "  Boston  ",
            "state": "  MA  ",
            "postal_code": "02101"
        },
        terms_accepted=True
    )
    print(f"   Email: '{user.email}' (whitespace stripped)")
    print(f"   Name: '{user.first_name} {user.last_name}' (whitespace stripped)")

    # Demonstrate extra="forbid"
    print("\n2. Extra fields forbidden:")
    try:
        UserProfile(
            username="testuser",
            email="test@example.com",
            password="SecureP@ss123!",
            first_name="Test",
            last_name="User",
            age=25,
            address={
                "street": "123 Main St",
                "city": "Boston",
                "state": "MA",
                "postal_code": "02101"
            },
            terms_accepted=True,
            extra_field="not allowed"  # This will fail
        )
    except ValidationError as e:
        print(f"   Error: {e.errors()[0]['msg']}")

    # Demonstrate validate_assignment
    print("\n3. Validation on assignment:")
    try:
        user.age = 5  # Invalid age
    except ValidationError as e:
        print(f"   Error when setting age=5: {e.errors()[0]['msg']}")


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 60)
    print("# PYDANTIC MASTERY - PROJECT 1: USER PROFILE VALIDATOR")
    print("#" * 60)

    demonstrate_valid_user()
    demonstrate_validation_errors()
    demonstrate_multiple_errors()
    demonstrate_nested_model()
    demonstrate_partial_update()
    demonstrate_model_config()

    print("\n" + "=" * 60)
    print("All demonstrations complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the models.py file to understand the code")
    print("2. Run the tests: pytest test_models.py -v")
    print("3. Complete the exercises in exercises.md")


if __name__ == "__main__":
    main()
