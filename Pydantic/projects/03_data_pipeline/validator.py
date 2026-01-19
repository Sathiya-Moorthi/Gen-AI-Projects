"""
Project 3: Data Pipeline Input Validator - Validation Logic
============================================================

This module provides batch validation utilities for data pipeline processing.

Key Features:
- Batch validation with error aggregation
- CSV/JSON file processing
- Validation statistics and reporting
- Performance optimization for large datasets
"""

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar, Generic

import structlog
from pydantic import BaseModel, ValidationError, TypeAdapter

from schemas import (
    Product,
    ProductListAdapter,
    TransactionAdapter,
    TransactionListAdapter,
    AnyTransaction,
    migrate_v1_to_v2,
)

logger = structlog.get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


# ============================================================================
# VALIDATION RESULT TYPES
# ============================================================================

@dataclass
class ValidationErrorDetail:
    """Details of a single validation error."""
    row_index: int
    field: str
    error_type: str
    message: str
    input_value: Any = None

    def to_dict(self) -> dict:
        return {
            "row": self.row_index,
            "field": self.field,
            "type": self.error_type,
            "message": self.message,
            "input": str(self.input_value)[:100] if self.input_value else None,
        }


@dataclass
class ValidationResult(Generic[T]):
    """
    Result of batch validation.

    Contains:
    - valid_records: Successfully validated records
    - errors: List of validation errors with details
    - statistics: Summary statistics
    """
    valid_records: list[T] = field(default_factory=list)
    errors: list[ValidationErrorDetail] = field(default_factory=list)
    total_rows: int = 0
    processing_time_ms: float = 0.0

    @property
    def valid_count(self) -> int:
        return len(self.valid_records)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def success_rate(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return (self.valid_count / self.total_rows) * 100

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def get_statistics(self) -> dict:
        """Return validation statistics."""
        return {
            "total_rows": self.total_rows,
            "valid_count": self.valid_count,
            "error_count": self.error_count,
            "success_rate": f"{self.success_rate:.2f}%",
            "processing_time_ms": f"{self.processing_time_ms:.2f}",
            "errors_by_field": self._errors_by_field(),
            "errors_by_type": self._errors_by_type(),
        }

    def _errors_by_field(self) -> dict[str, int]:
        """Count errors by field name."""
        counts: dict[str, int] = {}
        for error in self.errors:
            counts[error.field] = counts.get(error.field, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _errors_by_type(self) -> dict[str, int]:
        """Count errors by error type."""
        counts: dict[str, int] = {}
        for error in self.errors:
            counts[error.error_type] = counts.get(error.error_type, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def get_error_report(self, max_errors: int = 10) -> str:
        """Generate human-readable error report."""
        lines = [
            "=" * 60,
            "VALIDATION REPORT",
            "=" * 60,
            f"Total Rows: {self.total_rows}",
            f"Valid: {self.valid_count}",
            f"Invalid: {self.error_count}",
            f"Success Rate: {self.success_rate:.2f}%",
            f"Processing Time: {self.processing_time_ms:.2f}ms",
            "",
        ]

        if self.errors:
            lines.append("ERRORS BY FIELD:")
            for field_name, count in self._errors_by_field().items():
                lines.append(f"  {field_name}: {count} errors")

            lines.append("")
            lines.append(f"FIRST {min(max_errors, len(self.errors))} ERRORS:")
            for error in self.errors[:max_errors]:
                lines.append(f"  Row {error.row_index}: [{error.field}] {error.message}")

            if len(self.errors) > max_errors:
                lines.append(f"  ... and {len(self.errors) - max_errors} more errors")

        lines.append("=" * 60)
        return "\n".join(lines)


# ============================================================================
# BATCH VALIDATOR
# ============================================================================

class BatchValidator(Generic[T]):
    """
    Generic batch validator for Pydantic models.

    Validates lists of records with error aggregation.
    Supports both model classes and TypeAdapters.
    """

    def __init__(
        self,
        model_class: type[T] | None = None,
        type_adapter: TypeAdapter[T] | None = None,
        stop_on_first_error: bool = False,
        max_errors: int | None = None,
    ):
        """
        Initialize batch validator.

        Args:
            model_class: Pydantic model class to validate against
            type_adapter: TypeAdapter for validation (alternative to model_class)
            stop_on_first_error: Stop validation after first error
            max_errors: Maximum errors to collect before stopping
        """
        if model_class is None and type_adapter is None:
            raise ValueError("Either model_class or type_adapter must be provided")

        self.model_class = model_class
        self.type_adapter = type_adapter
        self.stop_on_first_error = stop_on_first_error
        self.max_errors = max_errors

    def validate_one(self, data: dict, row_index: int = 0) -> tuple[T | None, list[ValidationErrorDetail]]:
        """
        Validate a single record.

        Returns:
            Tuple of (validated_model or None, list of errors)
        """
        errors: list[ValidationErrorDetail] = []

        try:
            if self.type_adapter:
                validated = self.type_adapter.validate_python(data)
            else:
                validated = self.model_class.model_validate(data)
            return validated, []

        except ValidationError as e:
            for error in e.errors():
                field_path = ".".join(str(loc) for loc in error["loc"])
                errors.append(ValidationErrorDetail(
                    row_index=row_index,
                    field=field_path,
                    error_type=error["type"],
                    message=error["msg"],
                    input_value=error.get("input"),
                ))
            return None, errors

    def validate_batch(self, records: list[dict]) -> ValidationResult[T]:
        """
        Validate a batch of records.

        Args:
            records: List of dictionaries to validate

        Returns:
            ValidationResult containing valid records and errors
        """
        import time
        start_time = time.perf_counter()

        result: ValidationResult[T] = ValidationResult()
        result.total_rows = len(records)

        for idx, record in enumerate(records):
            if self.max_errors and len(result.errors) >= self.max_errors:
                logger.warning(
                    "max_errors_reached",
                    max_errors=self.max_errors,
                    rows_processed=idx
                )
                break

            validated, errors = self.validate_one(record, row_index=idx)

            if validated:
                result.valid_records.append(validated)
            else:
                result.errors.extend(errors)

                if self.stop_on_first_error:
                    logger.info(
                        "validation_stopped_on_first_error",
                        row_index=idx
                    )
                    break

        result.processing_time_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "batch_validation_complete",
            total_rows=result.total_rows,
            valid_count=result.valid_count,
            error_count=result.error_count,
            success_rate=f"{result.success_rate:.2f}%",
            processing_time_ms=f"{result.processing_time_ms:.2f}"
        )

        return result


# ============================================================================
# FILE PROCESSORS
# ============================================================================

def load_csv(file_path: Path | str) -> list[dict]:
    """
    Load records from CSV file.

    Args:
        file_path: Path to CSV file

    Returns:
        List of dictionaries
    """
    records = []
    file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert empty strings to None
            cleaned = {k: v if v != "" else None for k, v in row.items()}
            records.append(cleaned)

    logger.info("csv_loaded", file=str(file_path), record_count=len(records))
    return records


def load_json(file_path: Path | str) -> list[dict]:
    """
    Load records from JSON file.

    Args:
        file_path: Path to JSON file (array of objects)

    Returns:
        List of dictionaries
    """
    file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        # Single record
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError(f"Expected dict or list, got {type(data)}")

    logger.info("json_loaded", file=str(file_path), record_count=len(records))
    return records


def load_jsonl(file_path: Path | str) -> list[dict]:
    """
    Load records from JSON Lines file.

    Args:
        file_path: Path to JSONL file (one JSON object per line)

    Returns:
        List of dictionaries
    """
    records = []
    file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(
                        "jsonl_parse_error",
                        line_number=line_num,
                        error=str(e)
                    )

    logger.info("jsonl_loaded", file=str(file_path), record_count=len(records))
    return records


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def validate_products(records: list[dict]) -> ValidationResult[Product]:
    """Validate a list of product records."""
    validator = BatchValidator(model_class=Product)
    return validator.validate_batch(records)


def validate_products_from_csv(file_path: Path | str) -> ValidationResult[Product]:
    """Load and validate products from CSV file."""
    records = load_csv(file_path)
    return validate_products(records)


def validate_products_from_json(file_path: Path | str) -> ValidationResult[Product]:
    """Load and validate products from JSON file."""
    records = load_json(file_path)
    return validate_products(records)


def validate_transactions(records: list[dict]) -> ValidationResult[AnyTransaction]:
    """Validate a list of transaction records (discriminated union)."""
    validator: BatchValidator[AnyTransaction] = BatchValidator(
        type_adapter=TransactionAdapter
    )
    return validator.validate_batch(records)


# ============================================================================
# MIGRATION UTILITIES
# ============================================================================

def validate_with_migration(
    records: list[dict],
    detect_version: callable = None,
) -> ValidationResult[Product]:
    """
    Validate records with automatic version migration.

    Args:
        records: List of records (potentially mixed versions)
        detect_version: Optional function to detect record version

    Returns:
        ValidationResult with all records migrated to latest version
    """
    migrated_records = []

    for record in records:
        # Simple version detection: check for old field names
        if "product_code" in record or "unit_price" in record:
            # V1 record - migrate
            record = migrate_v1_to_v2(record)

        migrated_records.append(record)

    return validate_products(migrated_records)
