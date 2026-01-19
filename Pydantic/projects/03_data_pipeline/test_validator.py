"""
Project 3: Data Pipeline Input Validator - Tests
================================================

Comprehensive pytest tests for data pipeline validation.

Run with: pytest test_validator.py -v
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError, TypeAdapter

from schemas import (
    Product,
    ProductListAdapter,
    Transaction,
    Refund,
    Adjustment,
    TransactionAdapter,
    StrictRecord,
    LaxRecord,
    StrictRecordAdapter,
    LaxRecordAdapter,
    FlexibleDate,
    AnyTransaction,
    migrate_v1_to_v2,
)
from validator import (
    BatchValidator,
    ValidationResult,
    ValidationErrorDetail,
    load_csv,
    load_json,
    validate_products,
    validate_transactions,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def valid_product_data():
    """Return valid product data."""
    return {
        "sku": "TEST-001",
        "name": "Test Product",
        "category": "Testing",
        "price": 29.99,
        "quantity": 100,
    }


@pytest.fixture
def valid_transaction_data():
    """Return valid transaction data."""
    return {
        "record_id": "TXN-001",
        "type": "transaction",
        "created_at": "2024-01-15",
        "customer_id": "CUST-100",
        "amount": "150.00",
        "merchant_id": "MERCH-001",
        "status": "completed",
    }


@pytest.fixture
def sample_products():
    """Return list of product data with mix of valid/invalid."""
    return [
        {"sku": "PROD-001", "name": "Valid 1", "category": "A", "price": 10, "quantity": 100},
        {"sku": "PROD-002", "name": "Valid 2", "category": "B", "price": 20, "quantity": 50},
        {"sku": "invalid!", "name": "Invalid SKU", "category": "C", "price": 30, "quantity": 25},
        {"sku": "PROD-004", "name": "", "category": "D", "price": 40, "quantity": 10},
    ]


@pytest.fixture
def sample_data_dir():
    """Return path to sample data directory."""
    return Path(__file__).parent / "sample_data"


# ============================================================================
# PRODUCT SCHEMA TESTS
# ============================================================================

class TestProductSchema:
    """Tests for Product schema."""

    def test_valid_product(self, valid_product_data):
        """Test valid product creation."""
        product = Product.model_validate(valid_product_data)
        assert product.sku == "TEST-001"
        assert product.name == "Test Product"
        assert product.price == Decimal("29.99")
        assert product.quantity == 100

    def test_sku_uppercase(self):
        """Test SKU is converted to uppercase."""
        product = Product(
            sku="test-lowercase",
            name="Test",
            category="Test",
            price=10,
            quantity=1
        )
        assert product.sku == "TEST-LOWERCASE"

    def test_sku_invalid_pattern(self):
        """Test invalid SKU pattern rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Product(
                sku="invalid sku!",
                name="Test",
                category="Test",
                price=10,
                quantity=1
            )
        assert "sku" in str(exc_info.value)

    def test_price_coercion(self):
        """Test price string coercion."""
        product = Product(
            sku="TEST-001",
            name="Test",
            category="Test",
            price="$29.99",
            quantity=1
        )
        assert product.price == Decimal("29.99")

    def test_negative_price_rejected(self):
        """Test negative price is rejected."""
        with pytest.raises(ValidationError):
            Product(
                sku="TEST-001",
                name="Test",
                category="Test",
                price=-10,
                quantity=1
            )

    def test_tags_normalized(self):
        """Test tags are normalized and deduplicated."""
        product = Product(
            sku="TEST-001",
            name="Test",
            category="Test",
            price=10,
            quantity=1,
            tags=["  TAG1  ", "tag2", "TAG1", "  "]
        )
        # Deduplicated and lowercase
        assert "tag1" in product.tags
        assert "tag2" in product.tags
        assert len(product.tags) == 2

    def test_extra_fields_ignored(self):
        """Test extra fields are ignored (not forbidden)."""
        product = Product(
            sku="TEST-001",
            name="Test",
            category="Test",
            price=10,
            quantity=1,
            unknown_field="ignored"
        )
        assert product.sku == "TEST-001"


# ============================================================================
# FLEXIBLE DATE TESTS
# ============================================================================

class TestFlexibleDate:
    """Tests for FlexibleDate Annotated type."""

    DateAdapter = TypeAdapter(FlexibleDate)

    @pytest.mark.parametrize("date_str,expected", [
        ("2024-01-15", date(2024, 1, 15)),  # ISO
        ("01/15/2024", date(2024, 1, 15)),  # US
        ("15-01-2024", date(2024, 1, 15)),  # European
    ])
    def test_date_formats(self, date_str, expected):
        """Test various date format parsing."""
        result = self.DateAdapter.validate_python(date_str)
        assert result == expected

    def test_datetime_to_date(self):
        """Test datetime string extracts date."""
        result = self.DateAdapter.validate_python("2024-01-15T10:30:00")
        assert result == date(2024, 1, 15)

    def test_date_object_passthrough(self):
        """Test date object passes through."""
        d = date(2024, 1, 15)
        result = self.DateAdapter.validate_python(d)
        assert result == d


# ============================================================================
# STRICT VS LAX MODE TESTS
# ============================================================================

class TestStrictVsLax:
    """Tests for strict vs lax validation modes."""

    def test_lax_coerces_types(self):
        """Test lax mode coerces types."""
        data = {
            "id": "123",
            "name": 456,
            "value": "1.5",
            "active": "true"
        }
        record = LaxRecordAdapter.validate_python(data)
        assert record.id == 123  # str -> int
        assert record.name == "456"  # int -> str
        assert record.value == 1.5  # str -> float
        assert record.active is True  # str -> bool

    def test_strict_rejects_wrong_types(self):
        """Test strict mode rejects wrong types."""
        data = {
            "id": "123",  # Should be int
            "name": "test",
            "value": 1.5,
            "active": True
        }
        with pytest.raises(ValidationError):
            StrictRecordAdapter.validate_python(data)

    def test_strict_accepts_correct_types(self):
        """Test strict mode accepts correct types."""
        data = {
            "id": 123,
            "name": "test",
            "value": 1.5,
            "active": True
        }
        record = StrictRecordAdapter.validate_python(data)
        assert record.id == 123


# ============================================================================
# DISCRIMINATED UNION TESTS
# ============================================================================

class TestDiscriminatedUnion:
    """Tests for discriminated union (polymorphic records)."""

    def test_transaction_type(self, valid_transaction_data):
        """Test transaction type discrimination."""
        txn = TransactionAdapter.validate_python(valid_transaction_data)
        assert isinstance(txn, Transaction)
        assert txn.type.value == "transaction"

    def test_refund_type(self):
        """Test refund type discrimination."""
        data = {
            "record_id": "REF-001",
            "type": "refund",
            "created_at": "2024-01-15",
            "customer_id": "CUST-100",
            "amount": "50.00",
            "original_transaction_id": "TXN-001",
            "refund_reason": "Item returned"
        }
        txn = TransactionAdapter.validate_python(data)
        assert isinstance(txn, Refund)
        assert txn.original_transaction_id == "TXN-001"

    def test_adjustment_type(self):
        """Test adjustment type discrimination."""
        data = {
            "record_id": "ADJ-001",
            "type": "adjustment",
            "created_at": "2024-01-15",
            "customer_id": "CUST-100",
            "amount": "25.00",
            "adjustment_type": "credit",
            "reason_code": "ADJ-001",
            "approved_by": "admin"
        }
        txn = TransactionAdapter.validate_python(data)
        assert isinstance(txn, Adjustment)
        assert txn.adjustment_type == "credit"

    def test_invalid_type(self):
        """Test invalid type value rejected."""
        data = {
            "record_id": "XXX-001",
            "type": "invalid_type",
            "created_at": "2024-01-15",
            "customer_id": "CUST-100",
            "amount": "50.00"
        }
        with pytest.raises(ValidationError):
            TransactionAdapter.validate_python(data)


# ============================================================================
# BATCH VALIDATOR TESTS
# ============================================================================

class TestBatchValidator:
    """Tests for BatchValidator class."""

    def test_all_valid(self):
        """Test batch with all valid records."""
        records = [
            {"sku": "PROD-001", "name": "Product 1", "category": "A", "price": 10, "quantity": 100},
            {"sku": "PROD-002", "name": "Product 2", "category": "B", "price": 20, "quantity": 50},
        ]
        result = validate_products(records)

        assert result.valid_count == 2
        assert result.error_count == 0
        assert result.success_rate == 100.0

    def test_all_invalid(self):
        """Test batch with all invalid records."""
        records = [
            {"sku": "invalid!", "name": "", "category": "", "price": -10, "quantity": -5},
            {"sku": "", "name": "", "category": "", "price": "bad", "quantity": "bad"},
        ]
        result = validate_products(records)

        assert result.valid_count == 0
        assert result.error_count > 0
        assert result.success_rate == 0.0

    def test_mixed_valid_invalid(self, sample_products):
        """Test batch with mixed valid/invalid records."""
        result = validate_products(sample_products)

        assert result.valid_count == 2
        assert result.error_count > 0
        assert 0 < result.success_rate < 100

    def test_stop_on_first_error(self, sample_products):
        """Test stop_on_first_error option."""
        validator = BatchValidator(
            model_class=Product,
            stop_on_first_error=True
        )
        result = validator.validate_batch(sample_products)

        # Should stop after first invalid record (index 2)
        assert result.valid_count == 2
        assert len(result.errors) > 0

    def test_max_errors(self):
        """Test max_errors option."""
        records = [
            {"sku": f"invalid-{i}!", "name": "", "category": "", "price": -1, "quantity": -1}
            for i in range(10)
        ]
        validator = BatchValidator(
            model_class=Product,
            max_errors=5
        )
        result = validator.validate_batch(records)

        assert len(result.errors) <= 5

    def test_error_details(self):
        """Test error details are captured."""
        records = [
            {"sku": "invalid!", "name": "Test", "category": "Test", "price": 10, "quantity": 1}
        ]
        result = validate_products(records)

        assert len(result.errors) > 0
        error = result.errors[0]
        assert error.row_index == 0
        assert error.field == "sku"

    def test_statistics(self, sample_products):
        """Test validation statistics."""
        result = validate_products(sample_products)
        stats = result.get_statistics()

        assert "total_rows" in stats
        assert "valid_count" in stats
        assert "error_count" in stats
        assert "success_rate" in stats
        assert "errors_by_field" in stats

    def test_error_report(self, sample_products):
        """Test error report generation."""
        result = validate_products(sample_products)
        report = result.get_error_report()

        assert "VALIDATION REPORT" in report
        assert "Total Rows" in report
        assert "ERRORS BY FIELD" in report


# ============================================================================
# FILE LOADING TESTS
# ============================================================================

class TestFileLoading:
    """Tests for file loading functions."""

    def test_load_csv(self, sample_data_dir):
        """Test CSV loading."""
        csv_file = sample_data_dir / "products.csv"
        if csv_file.exists():
            records = load_csv(csv_file)
            assert len(records) > 0
            assert "sku" in records[0]

    def test_load_json(self, sample_data_dir):
        """Test JSON loading."""
        json_file = sample_data_dir / "transactions.json"
        if json_file.exists():
            records = load_json(json_file)
            assert len(records) > 0
            assert "record_id" in records[0]

    def test_csv_empty_values_to_none(self, tmp_path):
        """Test CSV empty values become None."""
        csv_content = "sku,name,category\nTEST-001,Test,\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        records = load_csv(csv_file)
        assert records[0]["category"] is None


# ============================================================================
# SCHEMA VERSIONING TESTS
# ============================================================================

class TestSchemaVersioning:
    """Tests for schema versioning and migration."""

    def test_migrate_v1_to_v2(self):
        """Test V1 to V2 migration."""
        v1_data = {
            "product_code": "V1-001",
            "product_name": "Legacy Product",
            "unit_price": 29.99,
            "stock": 100
        }

        v2_data = migrate_v1_to_v2(v1_data)

        assert v2_data["sku"] == "V1-001"
        assert v2_data["name"] == "Legacy Product"
        assert v2_data["price"] == 29.99
        assert v2_data["quantity"] == 100

    def test_migrated_data_validates(self):
        """Test migrated data passes validation."""
        v1_data = {
            "product_code": "V1-001",
            "product_name": "Legacy Product",
            "unit_price": 29.99,
            "stock": 100
        }

        v2_data = migrate_v1_to_v2(v1_data)
        product = Product.model_validate(v2_data)

        assert product.sku == "V1-001"


# ============================================================================
# TYPE ADAPTER TESTS
# ============================================================================

class TestTypeAdapter:
    """Tests for TypeAdapter usage."""

    def test_validate_list(self):
        """Test validating list of products."""
        products = [
            {"sku": "TA-001", "name": "Product 1", "category": "Test", "price": 10, "quantity": 5},
            {"sku": "TA-002", "name": "Product 2", "category": "Test", "price": 20, "quantity": 10},
        ]

        validated = ProductListAdapter.validate_python(products)
        assert len(validated) == 2
        assert all(isinstance(p, Product) for p in validated)

    def test_validate_list_fails_on_invalid(self):
        """Test list validation fails if any item invalid."""
        products = [
            {"sku": "TA-001", "name": "Valid", "category": "Test", "price": 10, "quantity": 5},
            {"sku": "invalid!", "name": "Invalid", "category": "Test", "price": 10, "quantity": 5},
        ]

        with pytest.raises(ValidationError):
            ProductListAdapter.validate_python(products)


# ============================================================================
# VALIDATION RESULT TESTS
# ============================================================================

class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_properties(self):
        """Test ValidationResult properties."""
        result = ValidationResult()
        result.total_rows = 10
        result.valid_records = [Product(sku="A", name="A", category="A", price=1, quantity=1)] * 7
        result.errors = [
            ValidationErrorDetail(0, "field", "type", "msg"),
            ValidationErrorDetail(1, "field", "type", "msg"),
            ValidationErrorDetail(2, "field", "type", "msg"),
        ]

        assert result.valid_count == 7
        assert result.error_count == 3
        assert result.success_rate == 70.0
        assert result.has_errors is True

    def test_empty_result(self):
        """Test empty ValidationResult."""
        result = ValidationResult()

        assert result.valid_count == 0
        assert result.error_count == 0
        assert result.success_rate == 0.0
        assert result.has_errors is False
