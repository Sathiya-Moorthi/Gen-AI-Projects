# Project 3: Data Pipeline Input Validator - Exercises

Complete these exercises to master data pipeline validation with Pydantic.

---

## Exercise 1: Add a Customer Schema

**Objective**: Create a `Customer` schema for validating customer records.

**Requirements**:
- Fields:
  - `customer_id: str` (pattern: `CUST-\d{6}`)
  - `email: EmailStr`
  - `phone: str` (with BeforeValidator to normalize)
  - `country_code: str` (ISO 3166-1 alpha-2)
  - `created_date: FlexibleDate`
  - `lifetime_value: Currency`
  - `is_active: bool`
- Use Annotated validators where appropriate

**Test data**:
```python
customers = [
    {"customer_id": "CUST-000001", "email": "user@example.com", "phone": "+1-555-123-4567", "country_code": "US", "created_date": "2024-01-15", "lifetime_value": "$1,234.56", "is_active": True},
    {"customer_id": "CUST-000002", "email": "invalid", ...},  # Should fail
]
```

---

## Exercise 2: Implement Error Recovery

**Objective**: Add error recovery strategies to the batch validator.

**Requirements**:
- Add `on_error` parameter to `BatchValidator`:
  - `"skip"`: Skip invalid records (current behavior)
  - `"default"`: Use default values for invalid fields
  - `"transform"`: Apply transformation function
- Implement `default_factory` for creating default records
- Add `transform_fn` for error recovery

**Example usage**:
```python
validator = BatchValidator(
    model_class=Product,
    on_error="default",
    default_factory=lambda data: Product(
        sku=data.get("sku", "UNKNOWN"),
        name=data.get("name", "Unknown Product"),
        category="uncategorized",
        price=0,
        quantity=0
    )
)
```

---

## Exercise 3: Add Streaming Validation

**Objective**: Support streaming validation for large files.

**Requirements**:
- Create `StreamingValidator` class
- Validate records one at a time (generator-based)
- Support progress callbacks
- Limit memory usage

**Example**:
```python
def streaming_validate(file_path: Path, chunk_size: int = 1000):
    """Yield validated records in chunks."""
    for chunk in read_chunks(file_path, chunk_size):
        result = validate_chunk(chunk)
        yield result

# Usage
for batch_result in streaming_validate("large_file.csv"):
    process_valid_records(batch_result.valid_records)
    log_errors(batch_result.errors)
```

---

## Exercise 4: Create an Inventory Schema with Cross-Field Validation

**Objective**: Build an `InventoryRecord` schema with complex validation.

**Requirements**:
- Fields:
  - `sku: str`
  - `warehouse_id: str`
  - `quantity_available: int`
  - `quantity_reserved: int`
  - `quantity_incoming: int`
  - `reorder_point: int`
  - `max_capacity: int`
  - `last_updated: datetime`
- Validations:
  - `quantity_available + quantity_reserved <= max_capacity`
  - `quantity_available >= 0`
  - Alert if `quantity_available < reorder_point`
  - `last_updated` cannot be in the future

**Use `@model_validator` for cross-field checks.**

---

## Exercise 5: Implement Data Quality Scoring

**Objective**: Add data quality metrics to validation results.

**Requirements**:
- Calculate quality score (0-100) based on:
  - Completeness: % of non-null fields
  - Validity: % of valid records
  - Consistency: % matching expected patterns
  - Freshness: % of recent records (configurable threshold)
- Add `quality_score` property to `ValidationResult`
- Generate quality report

**Example output**:
```
DATA QUALITY REPORT
==================
Overall Score: 78/100

Completeness: 92%
  - 8% of records have null optional fields

Validity: 85%
  - 15% of records failed validation

Consistency: 75%
  - 25% have inconsistent category values

Freshness: 60%
  - 40% of records older than 30 days
```

---

## Exercise 6: Add Schema Inference

**Objective**: Automatically infer Pydantic schema from sample data.

**Requirements**:
- Analyze sample records to detect:
  - Field names
  - Data types (int, float, str, date, bool)
  - Nullable fields
  - Value patterns (email, URL, date formats)
- Generate Pydantic model code

**Example**:
```python
sample_data = [
    {"id": 1, "email": "a@b.com", "created": "2024-01-15", "score": 95.5},
    {"id": 2, "email": "c@d.com", "created": "2024-01-16", "score": None},
]

schema = infer_schema(sample_data)
print(schema.generate_code())

# Output:
# class InferredModel(BaseModel):
#     id: int
#     email: EmailStr
#     created: date
#     score: float | None
```

---

## Exercise 7: Implement Delta Validation

**Objective**: Validate only changed records (delta processing).

**Requirements**:
- Track previously validated records (by ID)
- Only validate new/changed records
- Support "full" vs "delta" mode
- Track validation history

**Example**:
```python
# First run - validate all
result1 = delta_validator.validate(records, mode="full")

# Second run - only validate changes
result2 = delta_validator.validate(new_records, mode="delta")
# Only validates records not seen before or with changes
```

---

## Exercise 8: Create Validation Rules DSL

**Objective**: Define validation rules in YAML/JSON config.

**Requirements**:
- Support external rule definitions
- Rules include:
  - Field-level constraints
  - Cross-field rules
  - Custom error messages
- Load rules at runtime

**Example config (YAML)**:
```yaml
model: Product
fields:
  sku:
    type: string
    pattern: "^[A-Z]{3}-\\d{3}$"
    required: true
    error_message: "SKU must be format ABC-123"

  price:
    type: decimal
    min: 0
    max: 10000

rules:
  - name: "high_value_requires_description"
    condition: "price > 100"
    require: "description is not null"
    error_message: "Products over $100 require a description"
```

---

## Exercise 9: Add Parallel Batch Validation

**Objective**: Parallelize validation for large datasets.

**Requirements**:
- Use `concurrent.futures` for parallel processing
- Split data into chunks
- Aggregate results from workers
- Handle errors across threads

**Example**:
```python
def parallel_validate(
    records: list[dict],
    workers: int = 4,
    chunk_size: int = 1000
) -> ValidationResult:
    """Validate records in parallel."""
    chunks = split_into_chunks(records, chunk_size)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(validate_chunk, chunk) for chunk in chunks]
        results = [f.result() for f in futures]

    return merge_results(results)
```

---

## Exercise 10: Challenge - Build a Validation Pipeline

**Objective**: Create a complete data validation pipeline.

**Requirements**:
- Multi-stage pipeline:
  1. Load (CSV/JSON/API)
  2. Transform (clean, normalize)
  3. Validate (Pydantic schemas)
  4. Enrich (add computed fields)
  5. Output (write to destination)
- Configurable via YAML
- Support for retries and dead-letter queue
- Metrics and monitoring

**Example pipeline config**:
```yaml
pipeline:
  name: "product_import"
  source:
    type: csv
    path: "data/products.csv"

  transform:
    - normalize_strings: true
    - uppercase: ["sku"]
    - parse_dates: ["created_at"]

  validate:
    schema: Product
    on_error: skip
    max_errors: 100

  enrich:
    - add_field:
        name: "import_timestamp"
        value: "{{ now }}"

  output:
    type: json
    path: "output/validated_products.json"
    include_errors: true
```

---

## Solutions

Create a `solutions/` directory with your implementations.

**Checklist before moving to Project 4**:
- [ ] Completed at least 5 exercises
- [ ] All tests pass (`pytest test_validator.py -v`)
- [ ] Understand `TypeAdapter` for non-model validation
- [ ] Can use `BeforeValidator` and `AfterValidator`
- [ ] Understand discriminated unions
- [ ] Can implement batch validation with error aggregation
- [ ] Understand strict vs lax validation modes

---

## Key Takeaways

1. **TypeAdapter** validates non-model data (lists, dicts)
2. **Annotated validators** (`BeforeValidator`, `AfterValidator`) transform data
3. **Strict mode** disables type coercion for exact type matching
4. **Discriminated unions** handle polymorphic data with type field
5. **Batch validation** collects all errors instead of failing fast
6. **Schema versioning** supports data format evolution
7. **Performance** matters for large datasets - profile and optimize

Ready for Project 4? Move on to the LLM Output Validator!
