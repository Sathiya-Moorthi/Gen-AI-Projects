"""
Project 3: Data Pipeline Input Validator - Main Demonstration
=============================================================

This script demonstrates batch validation for data pipelines.

Run with: python main.py
"""

import json
import logging
from pathlib import Path
from decimal import Decimal

from pydantic import ValidationError

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
    Currency,
    migrate_v1_to_v2,
)
from validator import (
    BatchValidator,
    ValidationResult,
    load_csv,
    load_json,
    validate_products,
    validate_products_from_csv,
    validate_transactions,
)

logging.basicConfig(level=logging.INFO)

# Sample data directory
SAMPLE_DIR = Path(__file__).parent / "sample_data"


def demonstrate_basic_validation():
    """Show basic model validation."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Product Validation")
    print("=" * 60)

    # Valid product
    valid_data = {
        "sku": "TEST-001",
        "name": "Test Product",
        "category": "Testing",
        "price": "29.99",  # String will be coerced
        "quantity": 100,
    }

    print("\n1. Valid product data:")
    print(json.dumps(valid_data, indent=2))

    product = Product.model_validate(valid_data)
    print("\n   Validated product:")
    print(f"   SKU: {product.sku}")
    print(f"   Name: {product.name}")
    print(f"   Price: {product.price} (type: {type(product.price).__name__})")
    print(f"   Quantity: {product.quantity}")

    # Invalid product
    print("\n2. Invalid product data:")
    invalid_data = {
        "sku": "invalid sku!",  # Invalid pattern
        "name": "",  # Too short
        "category": "Testing",
        "price": -10,  # Negative
        "quantity": "not a number",  # Wrong type
    }
    print(json.dumps(invalid_data, indent=2))

    try:
        Product.model_validate(invalid_data)
    except ValidationError as e:
        print(f"\n   Caught {e.error_count()} validation errors:")
        for error in e.errors():
            loc = ".".join(str(l) for l in error["loc"])
            print(f"   - {loc}: {error['msg']}")


def demonstrate_annotated_validators():
    """Show Annotated validators (Before/After)."""
    print("\n" + "=" * 60)
    print("DEMO 2: Annotated Validators (BeforeValidator, AfterValidator)")
    print("=" * 60)

    print("\n1. FlexibleDate - accepts multiple formats:")
    from datetime import date
    from pydantic import TypeAdapter

    DateAdapter = TypeAdapter(FlexibleDate)

    date_formats = [
        "2024-01-15",      # ISO
        "01/15/2024",      # US
        "15-01-2024",      # European
        "2024-01-15T10:30:00",  # ISO datetime
    ]

    for date_str in date_formats:
        parsed = DateAdapter.validate_python(date_str)
        print(f"   '{date_str}' -> {parsed} (type: {type(parsed).__name__})")

    print("\n2. Currency - parses various formats:")
    CurrencyAdapter = TypeAdapter(Currency)

    currency_values = [
        "29.99",
        "$1,234.56",
        "€99.00",
        "£50",
        1000,
        Decimal("49.95"),
    ]

    for val in currency_values:
        parsed = CurrencyAdapter.validate_python(val)
        print(f"   {val!r} -> {parsed} (type: {type(parsed).__name__})")


def demonstrate_strict_vs_lax():
    """Show difference between strict and lax validation."""
    print("\n" + "=" * 60)
    print("DEMO 3: Strict vs Lax Validation Mode")
    print("=" * 60)

    # Data that can be coerced
    data = {
        "id": "123",      # String, should be int
        "name": 456,      # Int, should be string
        "value": "1.5",   # String, should be float
        "active": "true", # String, should be bool
    }

    print("\nInput data:")
    print(json.dumps(data, indent=2))

    print("\n1. LAX mode (default) - coerces types:")
    try:
        lax = LaxRecordAdapter.validate_python(data)
        print(f"   id: {lax.id} (type: {type(lax.id).__name__})")
        print(f"   name: {lax.name} (type: {type(lax.name).__name__})")
        print(f"   value: {lax.value} (type: {type(lax.value).__name__})")
        print(f"   active: {lax.active} (type: {type(lax.active).__name__})")
    except ValidationError as e:
        print(f"   Error: {e}")

    print("\n2. STRICT mode - requires exact types:")
    try:
        strict = StrictRecordAdapter.validate_python(data)
        print(f"   Result: {strict}")
    except ValidationError as e:
        print(f"   Caught {e.error_count()} errors:")
        for error in e.errors():
            loc = ".".join(str(l) for l in error["loc"])
            print(f"   - {loc}: {error['msg']}")


def demonstrate_discriminated_union():
    """Show discriminated union for polymorphic records."""
    print("\n" + "=" * 60)
    print("DEMO 4: Discriminated Unions (Polymorphic Records)")
    print("=" * 60)

    transactions = [
        {
            "record_id": "TXN-001",
            "type": "transaction",
            "created_at": "2024-01-15",
            "customer_id": "CUST-100",
            "amount": "150.00",
            "merchant_id": "MERCH-001",
            "status": "completed",
        },
        {
            "record_id": "REF-001",
            "type": "refund",
            "created_at": "2024-01-16",
            "customer_id": "CUST-100",
            "amount": "50.00",
            "original_transaction_id": "TXN-001",
            "refund_reason": "Item returned",
        },
        {
            "record_id": "ADJ-001",
            "type": "adjustment",
            "created_at": "2024-01-17",
            "customer_id": "CUST-101",
            "amount": "25.00",
            "adjustment_type": "credit",
            "reason_code": "ADJ-001",
            "approved_by": "admin",
        },
    ]

    print("\nValidating transactions with discriminator 'type':")
    for txn_data in transactions:
        txn = TransactionAdapter.validate_python(txn_data)
        print(f"\n   Record: {txn.record_id}")
        print(f"   Type: {type(txn).__name__}")
        print(f"   Amount: {txn.amount}")

        # Type-specific fields
        if isinstance(txn, Transaction):
            print(f"   Merchant: {txn.merchant_id}")
            print(f"   Status: {txn.status}")
        elif isinstance(txn, Refund):
            print(f"   Original: {txn.original_transaction_id}")
            print(f"   Reason: {txn.refund_reason}")
        elif isinstance(txn, Adjustment):
            print(f"   Adjustment Type: {txn.adjustment_type}")
            print(f"   Approved By: {txn.approved_by}")


def demonstrate_batch_validation():
    """Show batch validation with error aggregation."""
    print("\n" + "=" * 60)
    print("DEMO 5: Batch Validation with Error Aggregation")
    print("=" * 60)

    # Mix of valid and invalid products
    products = [
        {"sku": "PROD-001", "name": "Valid Product 1", "category": "A", "price": 10, "quantity": 100},
        {"sku": "PROD-002", "name": "Valid Product 2", "category": "B", "price": 20, "quantity": 50},
        {"sku": "invalid!", "name": "Invalid SKU", "category": "C", "price": 30, "quantity": 25},
        {"sku": "PROD-004", "name": "", "category": "D", "price": 40, "quantity": 10},  # Empty name
        {"sku": "PROD-005", "name": "Valid Product 5", "category": "E", "price": -5, "quantity": 5},  # Negative price
        {"sku": "PROD-006", "name": "Valid Product 6", "category": "F", "price": 60, "quantity": 200},
    ]

    print(f"\nValidating {len(products)} products...")
    result = validate_products(products)

    print("\n" + result.get_error_report())

    print("\nValidation Statistics:")
    stats = result.get_statistics()
    print(json.dumps(stats, indent=2))


def demonstrate_csv_validation():
    """Show CSV file validation."""
    print("\n" + "=" * 60)
    print("DEMO 6: CSV File Validation")
    print("=" * 60)

    # Valid CSV
    valid_csv = SAMPLE_DIR / "products.csv"
    if valid_csv.exists():
        print(f"\n1. Validating {valid_csv.name}:")
        result = validate_products_from_csv(valid_csv)
        print(f"   Valid: {result.valid_count}/{result.total_rows}")
        print(f"   Success Rate: {result.success_rate:.2f}%")

        if result.valid_records:
            print("\n   First valid product:")
            print(f"   SKU: {result.valid_records[0].sku}")
            print(f"   Name: {result.valid_records[0].name}")
            print(f"   Price: {result.valid_records[0].price}")

    # Invalid CSV
    invalid_csv = SAMPLE_DIR / "products_invalid.csv"
    if invalid_csv.exists():
        print(f"\n2. Validating {invalid_csv.name} (has errors):")
        result = validate_products_from_csv(invalid_csv)
        print(result.get_error_report())


def demonstrate_json_validation():
    """Show JSON file validation."""
    print("\n" + "=" * 60)
    print("DEMO 7: JSON Transaction Validation")
    print("=" * 60)

    json_file = SAMPLE_DIR / "transactions.json"
    if json_file.exists():
        print(f"\nValidating {json_file.name}:")
        records = load_json(json_file)
        result = validate_transactions(records)

        print(f"\nTotal: {result.total_rows}")
        print(f"Valid: {result.valid_count}")
        print(f"Errors: {result.error_count}")

        print("\nValidated transactions:")
        for txn in result.valid_records:
            print(f"  - {txn.record_id}: {type(txn).__name__} - {txn.amount}")


def demonstrate_type_adapter():
    """Show TypeAdapter for non-model validation."""
    print("\n" + "=" * 60)
    print("DEMO 8: TypeAdapter for List/Dict Validation")
    print("=" * 60)

    print("\n1. Validate list of products directly:")
    products_data = [
        {"sku": "TA-001", "name": "Product 1", "category": "Test", "price": 10, "quantity": 5},
        {"sku": "TA-002", "name": "Product 2", "category": "Test", "price": 20, "quantity": 10},
    ]

    validated_list = ProductListAdapter.validate_python(products_data)
    print(f"   Validated {len(validated_list)} products")
    for p in validated_list:
        print(f"   - {p.sku}: {p.name}")

    print("\n2. TypeAdapter with invalid data:")
    invalid_data = [
        {"sku": "TA-003", "name": "Valid", "category": "Test", "price": 10, "quantity": 5},
        {"sku": "invalid!", "name": "Invalid", "category": "Test", "price": 10, "quantity": 5},
    ]

    try:
        ProductListAdapter.validate_python(invalid_data)
    except ValidationError as e:
        print(f"   Caught error at index: {e.errors()[0]['loc']}")
        print(f"   Message: {e.errors()[0]['msg']}")


def demonstrate_schema_versioning():
    """Show schema versioning and migration."""
    print("\n" + "=" * 60)
    print("DEMO 9: Schema Versioning and Migration")
    print("=" * 60)

    # V1 format (legacy)
    v1_products = [
        {"product_code": "V1-001", "product_name": "Legacy Product", "unit_price": 29.99, "stock": 100},
        {"product_code": "V1-002", "product_name": "Old Format", "unit_price": 49.99, "stock": 50},
    ]

    print("\nV1 (Legacy) Format:")
    print(json.dumps(v1_products[0], indent=2))

    print("\nMigrated to V2 Format:")
    v2_data = migrate_v1_to_v2(v1_products[0])
    print(json.dumps(v2_data, indent=2))

    print("\nValidating migrated data:")
    product = Product.model_validate(v2_data)
    print(f"   SKU: {product.sku}")
    print(f"   Name: {product.name}")
    print(f"   Price: {product.price}")


def demonstrate_performance():
    """Show performance considerations."""
    print("\n" + "=" * 60)
    print("DEMO 10: Performance Considerations")
    print("=" * 60)

    import time

    # Generate large dataset
    num_records = 10000
    records = [
        {
            "sku": f"PERF-{i:05d}",
            "name": f"Performance Test Product {i}",
            "category": f"Category-{i % 10}",
            "price": round(10 + (i * 0.01), 2),
            "quantity": i % 1000,
        }
        for i in range(num_records)
    ]

    print(f"\nValidating {num_records:,} records...")

    # Batch validation with BatchValidator
    start = time.perf_counter()
    result = validate_products(records)
    batch_time = (time.perf_counter() - start) * 1000

    print(f"\n1. Batch Validation (BatchValidator):")
    print(f"   Time: {batch_time:.2f}ms")
    print(f"   Records/sec: {num_records / (batch_time / 1000):,.0f}")
    print(f"   Valid: {result.valid_count}")

    # TypeAdapter validation
    start = time.perf_counter()
    try:
        validated = ProductListAdapter.validate_python(records)
        ta_time = (time.perf_counter() - start) * 1000
        print(f"\n2. TypeAdapter (validates all at once):")
        print(f"   Time: {ta_time:.2f}ms")
        print(f"   Records/sec: {num_records / (ta_time / 1000):,.0f}")
    except ValidationError:
        print("\n2. TypeAdapter: Failed on first error (no error aggregation)")


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 60)
    print("# PYDANTIC MASTERY - PROJECT 3: DATA PIPELINE VALIDATOR")
    print("#" * 60)

    demonstrate_basic_validation()
    demonstrate_annotated_validators()
    demonstrate_strict_vs_lax()
    demonstrate_discriminated_union()
    demonstrate_batch_validation()
    demonstrate_csv_validation()
    demonstrate_json_validation()
    demonstrate_type_adapter()
    demonstrate_schema_versioning()
    demonstrate_performance()

    print("\n" + "=" * 60)
    print("All demonstrations complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review schemas.py and validator.py")
    print("2. Examine sample_data/ files")
    print("3. Run tests: pytest test_validator.py -v")
    print("4. Complete exercises in exercises.md")


if __name__ == "__main__":
    main()
