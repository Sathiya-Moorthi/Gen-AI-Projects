"""
Project 3: Data Pipeline Input Validator - Schemas
===================================================

This module demonstrates advanced Pydantic features for data pipeline validation.

Key Concepts:
- TypeAdapter for validating lists/dicts
- Strict vs lax mode (ConfigDict(strict=True))
- ValidationError handling and error aggregation
- BeforeValidator and AfterValidator (Annotated validators)
- Discriminated unions for polymorphic records
- Performance considerations for large datasets

Real-World Problem:
Data pipelines ingest CSV/JSON from external sources.
Bad data (nulls, wrong types, outliers) corrupts downstream analytics.
Pydantic validates each record before processing.
"""

import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, Literal

import structlog
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
    BeforeValidator,
    AfterValidator,
    PlainSerializer,
    ValidationError,
)

logger = structlog.get_logger(__name__)


# ============================================================================
# CUSTOM VALIDATORS (Annotated pattern)
# ============================================================================

def parse_date_string(v: Any) -> Any:
    """
    BeforeValidator: Parse various date string formats.

    Handles:
    - ISO format: 2024-01-15
    - US format: 01/15/2024
    - European format: 15-01-2024
    - Already datetime/date objects
    """
    if isinstance(v, (datetime, date)):
        return v

    if isinstance(v, str):
        v = v.strip()

        # ISO format: 2024-01-15
        if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            return datetime.strptime(v, "%Y-%m-%d").date()

        # US format: 01/15/2024
        if re.match(r"^\d{2}/\d{2}/\d{4}$", v):
            return datetime.strptime(v, "%m/%d/%Y").date()

        # European format: 15-01-2024
        if re.match(r"^\d{2}-\d{2}-\d{4}$", v):
            return datetime.strptime(v, "%d-%m-%Y").date()

        # Try ISO datetime
        try:
            return datetime.fromisoformat(v).date()
        except ValueError:
            pass

    return v  # Let Pydantic handle validation error


def clean_string(v: str) -> str:
    """BeforeValidator: Clean and normalize string values."""
    if isinstance(v, str):
        # Strip whitespace
        v = v.strip()
        # Normalize multiple spaces
        v = re.sub(r"\s+", " ", v)
        # Convert empty string to trigger required validation
        if v == "":
            return None
    return v


def validate_positive(v: float | int) -> float | int:
    """AfterValidator: Ensure numeric value is positive."""
    if v <= 0:
        raise ValueError("Value must be positive")
    return v


def clamp_percentage(v: float) -> float:
    """AfterValidator: Clamp percentage to 0-100 range."""
    return max(0.0, min(100.0, v))


def normalize_currency(v: Any) -> Decimal:
    """BeforeValidator: Parse currency strings to Decimal."""
    if isinstance(v, Decimal):
        return v

    if isinstance(v, (int, float)):
        return Decimal(str(v))

    if isinstance(v, str):
        # Remove currency symbols and commas
        v = re.sub(r"[$€£¥,\s]", "", v.strip())
        try:
            return Decimal(v)
        except Exception:
            pass

    return v


def serialize_decimal(v: Decimal) -> float:
    """PlainSerializer: Serialize Decimal to float for JSON."""
    return float(v)


# ============================================================================
# ANNOTATED TYPES
# ============================================================================

# Date that accepts multiple formats
FlexibleDate = Annotated[date, BeforeValidator(parse_date_string)]

# Cleaned string (whitespace normalized)
CleanString = Annotated[str, BeforeValidator(clean_string)]

# Positive number
PositiveFloat = Annotated[float, AfterValidator(validate_positive)]
PositiveInt = Annotated[int, AfterValidator(validate_positive)]

# Percentage clamped to 0-100
Percentage = Annotated[float, AfterValidator(clamp_percentage)]

# Currency value
Currency = Annotated[
    Decimal,
    BeforeValidator(normalize_currency),
    PlainSerializer(serialize_decimal),
]


# ============================================================================
# ENUMS
# ============================================================================

class RecordType(str, Enum):
    """Type discriminator for polymorphic records."""
    TRANSACTION = "transaction"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class TransactionStatus(str, Enum):
    """Transaction status values."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CurrencyCode(str, Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class BaseRecord(BaseModel):
    """
    Base record with common fields.

    Demonstrates:
    - ConfigDict for model behavior
    - Common fields for all record types
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",  # Reject unknown fields
        populate_by_name=True,  # Allow field aliases
    )

    record_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique record identifier",
        alias="id"
    )

    created_at: FlexibleDate = Field(
        ...,
        description="Record creation date"
    )

    source_system: str = Field(
        default="unknown",
        max_length=50,
        description="Source system identifier"
    )


class StrictRecord(BaseModel):
    """
    Record with strict type checking.

    Demonstrates:
    - strict=True to disable type coercion
    - Use when data types must match exactly
    """

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    id: int  # Must be int, not "123"
    name: str  # Must be str, not 123
    value: float  # Must be float/int, not "1.5"
    active: bool  # Must be bool, not "true"


class LaxRecord(BaseModel):
    """
    Record with lax type coercion (default).

    Demonstrates:
    - Default Pydantic behavior
    - Automatic type coercion
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    id: int  # "123" -> 123
    name: str  # 123 -> "123"
    value: float  # "1.5" -> 1.5
    active: bool  # "true" -> True


# ============================================================================
# TRANSACTION SCHEMAS (Discriminated Union)
# ============================================================================

class BaseTransaction(BaseRecord):
    """Base for all transaction types."""

    type: RecordType = Field(
        ...,
        description="Transaction type discriminator"
    )

    customer_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Customer identifier"
    )

    amount: Currency = Field(
        ...,
        description="Transaction amount"
    )

    currency_code: str = Field(
        default="USD",
        pattern=r"^[A-Z]{3}$",
        description="ISO 4217 currency code"
    )


class Transaction(BaseTransaction):
    """
    Regular transaction record.

    Demonstrates:
    - Literal type for discriminator
    - Transaction-specific fields
    """

    type: Literal[RecordType.TRANSACTION] = RecordType.TRANSACTION

    status: TransactionStatus = Field(
        default=TransactionStatus.PENDING,
        description="Transaction status"
    )

    merchant_id: str = Field(
        ...,
        min_length=1,
        description="Merchant identifier"
    )

    description: CleanString | None = Field(
        default=None,
        max_length=500,
        description="Transaction description"
    )


class Refund(BaseTransaction):
    """
    Refund transaction record.

    Demonstrates:
    - Different fields for refund type
    - Reference to original transaction
    """

    type: Literal[RecordType.REFUND] = RecordType.REFUND

    original_transaction_id: str = Field(
        ...,
        min_length=1,
        description="ID of original transaction being refunded"
    )

    refund_reason: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Reason for refund"
    )

    partial: bool = Field(
        default=False,
        description="Is this a partial refund"
    )

    @model_validator(mode="after")
    def validate_refund(self) -> "Refund":
        """Ensure refund references different transaction."""
        if self.record_id == self.original_transaction_id:
            raise ValueError("Refund cannot reference itself")
        return self


class Adjustment(BaseTransaction):
    """
    Adjustment record.

    Demonstrates:
    - Adjustment-specific validation
    - Can be positive or negative
    """

    type: Literal[RecordType.ADJUSTMENT] = RecordType.ADJUSTMENT

    adjustment_type: Literal["credit", "debit"] = Field(
        ...,
        description="Type of adjustment"
    )

    reason_code: str = Field(
        ...,
        pattern=r"^ADJ-\d{3}$",
        description="Adjustment reason code (ADJ-XXX format)"
    )

    approved_by: str = Field(
        ...,
        min_length=1,
        description="Approver identifier"
    )


# Discriminated union for all transaction types
AnyTransaction = Annotated[
    Transaction | Refund | Adjustment,
    Field(discriminator="type")
]


# ============================================================================
# PRODUCT SCHEMAS (for batch validation demo)
# ============================================================================

class Product(BaseModel):
    """
    Product record for batch validation.

    Demonstrates:
    - Multiple validators
    - Real-world e-commerce data
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",  # Ignore unknown fields
    )

    sku: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Z0-9\-]+$",
        description="Stock Keeping Unit"
    )

    name: CleanString = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Product name"
    )

    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Product category"
    )

    price: Currency = Field(
        ...,
        ge=0,
        description="Product price"
    )

    quantity: int = Field(
        ...,
        ge=0,
        description="Available quantity"
    )

    weight_kg: float | None = Field(
        default=None,
        ge=0,
        le=1000,
        description="Product weight in kg"
    )

    is_active: bool = Field(
        default=True,
        description="Is product active"
    )

    tags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Product tags"
    )

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, v: str) -> str:
        """Ensure SKU is uppercase."""
        return v.upper()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Normalize and deduplicate tags."""
        normalized = [tag.lower().strip() for tag in v if tag.strip()]
        return list(set(normalized))

    @model_validator(mode="after")
    def validate_active_has_quantity(self) -> "Product":
        """Warn if active product has zero quantity."""
        if self.is_active and self.quantity == 0:
            logger.warning(
                "active_product_no_stock",
                sku=self.sku,
                name=self.name
            )
        return self


# ============================================================================
# SCHEMA VERSIONING
# ============================================================================

class ProductV1(BaseModel):
    """Version 1 of product schema (legacy)."""

    model_config = ConfigDict(extra="ignore")

    product_code: str = Field(..., alias="sku")  # Old name
    product_name: str = Field(..., alias="name")
    unit_price: float = Field(..., alias="price")
    stock: int = Field(..., alias="quantity")


class ProductV2(Product):
    """Version 2 of product schema (current)."""
    pass  # Same as Product


def migrate_v1_to_v2(v1_data: dict) -> dict:
    """Migrate V1 product data to V2 format."""
    return {
        "sku": v1_data.get("product_code", v1_data.get("sku")),
        "name": v1_data.get("product_name", v1_data.get("name")),
        "price": v1_data.get("unit_price", v1_data.get("price")),
        "quantity": v1_data.get("stock", v1_data.get("quantity")),
        "category": v1_data.get("category", "uncategorized"),
        "is_active": v1_data.get("is_active", True),
    }


# ============================================================================
# TYPE ADAPTERS
# ============================================================================

# TypeAdapter for validating lists of products
ProductListAdapter = TypeAdapter(list[Product])

# TypeAdapter for validating any transaction type
TransactionAdapter = TypeAdapter(AnyTransaction)

# TypeAdapter for list of transactions
TransactionListAdapter = TypeAdapter(list[AnyTransaction])

# TypeAdapter for strict records
StrictRecordAdapter = TypeAdapter(StrictRecord)

# TypeAdapter for lax records
LaxRecordAdapter = TypeAdapter(LaxRecord)
