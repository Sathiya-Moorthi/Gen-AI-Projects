# Project 4: LLM Output Validator - Exercises

Complete these exercises to master LLM output validation with Pydantic.

---

## Exercise 1: Add Code Review Schema

**Objective**: Create a schema for validating code review outputs from LLMs.

**Requirements**:
- Fields:
  - `file_path: str`
  - `issues: list[CodeIssue]` where `CodeIssue` has:
    - `line_number: int`
    - `severity: Literal["error", "warning", "info"]`
    - `category: str` (e.g., "security", "performance", "style")
    - `message: str`
    - `suggestion: str | None`
  - `overall_quality: int` (1-10)
  - `summary: str`
- Add validation to ensure line numbers are positive
- Ensure overall_quality correlates with issue count

**Test with**:
```python
review = CodeReview.model_validate({
    "file_path": "src/main.py",
    "issues": [
        {"line_number": 42, "severity": "warning", "category": "style", "message": "Line too long"}
    ],
    "overall_quality": 7,
    "summary": "Generally good code with minor style issues."
})
```

---

## Exercise 2: Implement Streaming Parser

**Objective**: Parse LLM outputs as they stream in (token by token).

**Requirements**:
- Create `StreamingParser` class
- Buffer tokens until valid JSON is detected
- Return partial results when possible
- Handle incomplete JSON gracefully

**Example**:
```python
parser = StreamingParser(SentimentAnalysis)

for token in llm.stream("Analyze sentiment"):
    result = parser.add_token(token)
    if result.is_complete:
        print(result.data)
        break
    elif result.partial_data:
        print(f"Partial: {result.partial_data}")
```

---

## Exercise 3: Add Confidence Thresholds

**Objective**: Implement automatic rejection of low-confidence outputs.

**Requirements**:
- Add `min_confidence` parameter to parser
- If output confidence below threshold, treat as invalid
- Return special status `LOW_CONFIDENCE`
- Support field-level confidence checks

**Example**:
```python
parser = LLMOutputParser(
    SentimentAnalysis,
    min_confidence=0.8,
    confidence_field="confidence"
)

result = parser.parse(response)
if result.status == ParseStatus.LOW_CONFIDENCE:
    # Retry or escalate
    pass
```

---

## Exercise 4: Create Schema Registry

**Objective**: Build a registry for managing multiple LLM output schemas.

**Requirements**:
- Register schemas by name
- Generate prompts for any registered schema
- Support schema versioning
- Validate against schema by name

**Example**:
```python
registry = SchemaRegistry()
registry.register("sentiment_v1", SentimentAnalysis)
registry.register("sentiment_v2", SentimentAnalysisV2)

# Get schema by name
schema = registry.get("sentiment_v1")
prompt = registry.get_prompt("sentiment_v1")

# Validate
result = registry.validate("sentiment_v1", llm_response)
```

---

## Exercise 5: Implement Output Normalization

**Objective**: Normalize LLM outputs to consistent formats.

**Requirements**:
- Create `OutputNormalizer` class
- Handle common variations:
  - Different date formats
  - Case variations in enums
  - Synonymous values (yes/true, no/false)
  - Number formats (1,000 vs 1000)
- Chain normalizers with parser

**Example**:
```python
normalizer = OutputNormalizer()
normalizer.add_rule("sentiment", lambda x: x.lower())
normalizer.add_rule("confidence", lambda x: float(x.strip("%")) / 100 if "%" in str(x) else x)

parser = LLMOutputParser(SentimentAnalysis, normalizer=normalizer)
```

---

## Exercise 6: Add Chain-of-Thought Schema

**Objective**: Create schema for structured chain-of-thought outputs.

**Requirements**:
- `ThinkingStep` model:
  - `step_number: int`
  - `thought: str`
  - `action: str | None`
  - `observation: str | None`
- `ChainOfThought` model:
  - `question: str`
  - `thinking_steps: list[ThinkingStep]`
  - `final_answer: str`
  - `confidence: float`
- Validate step numbers are sequential

**Example output**:
```json
{
    "question": "What is 25 * 4?",
    "thinking_steps": [
        {"step_number": 1, "thought": "I need to multiply 25 by 4"},
        {"step_number": 2, "thought": "25 * 4 = 100"}
    ],
    "final_answer": "100",
    "confidence": 0.99
}
```

---

## Exercise 7: Implement Error Categorization

**Objective**: Categorize and track LLM output errors.

**Requirements**:
- Create `ErrorAnalyzer` class
- Categorize errors:
  - Format errors (invalid JSON)
  - Schema errors (missing/wrong fields)
  - Semantic errors (invalid values)
  - Hallucination indicators
- Track error patterns over time
- Generate reports

**Example**:
```python
analyzer = ErrorAnalyzer()

for response in llm_responses:
    result = parser.parse(response)
    if not result.success:
        analyzer.record_error(result)

report = analyzer.get_report()
print(f"Most common error: {report.most_common_error}")
print(f"Error rate: {report.error_rate:.2%}")
```

---

## Exercise 8: Add Multi-Model Validation

**Objective**: Validate outputs from different LLM providers.

**Requirements**:
- Support different response formats:
  - OpenAI (function_call, tool_calls)
  - Anthropic (content blocks)
  - Google (structured outputs)
- Create provider-specific extractors
- Unified validation interface

**Example**:
```python
validator = MultiModelValidator(SentimentAnalysis)

# Works with any provider
result = validator.validate(openai_response, provider="openai")
result = validator.validate(anthropic_response, provider="anthropic")
result = validator.validate(google_response, provider="google")
```

---

## Exercise 9: Implement Schema Evolution

**Objective**: Handle schema changes gracefully.

**Requirements**:
- Support backward-compatible changes
- Migrate old outputs to new schema
- Track schema versions
- Generate migration code

**Example**:
```python
# V1 schema
class SentimentV1(BaseModel):
    sentiment: str
    score: float

# V2 schema (renamed field)
class SentimentV2(BaseModel):
    sentiment: Sentiment  # Now enum
    confidence: float  # Renamed from score

# Migration
migrator = SchemaMigrator()
migrator.add_migration(
    from_version="v1",
    to_version="v2",
    transform=lambda d: {"sentiment": d["sentiment"], "confidence": d["score"]}
)

# Auto-migrate old outputs
result = migrator.validate_and_migrate(old_output, target_version="v2")
```

---

## Exercise 10: Challenge - Build an LLM Output Quality System

**Objective**: Create a comprehensive quality system for LLM outputs.

**Requirements**:
- Quality dimensions:
  - Structural validity (valid JSON, matches schema)
  - Completeness (all fields populated meaningfully)
  - Consistency (no contradictory information)
  - Confidence (self-reported and computed)
- Quality score calculation
- Automatic retry decision
- Quality reporting dashboard data

**Example**:
```python
quality_system = LLMOutputQuality(
    schema=SentimentAnalysis,
    min_quality_score=0.7,
    auto_retry=True,
    max_retries=3
)

# Validate with quality assessment
result = quality_system.validate(llm_response)

print(f"Quality Score: {result.quality_score}")
print(f"Dimensions:")
print(f"  Structural: {result.structural_score}")
print(f"  Completeness: {result.completeness_score}")
print(f"  Consistency: {result.consistency_score}")
print(f"  Confidence: {result.confidence_score}")

if result.should_retry:
    print(f"Recommendation: Retry with feedback")
    print(f"Feedback: {result.retry_feedback}")
```

---

## Solutions

Create a `solutions/` directory with your implementations.

**Checklist before moving to Project 5**:
- [ ] Completed at least 5 exercises
- [ ] All tests pass (`pytest test_parser.py -v`)
- [ ] Understand `model_json_schema()` for prompt engineering
- [ ] Can extract JSON from various LLM output formats
- [ ] Understand retry patterns with schema feedback
- [ ] Comfortable with optional fields for uncertain outputs
- [ ] Can create function calling definitions from Pydantic models

---

## Key Takeaways

1. **JSON Schema Generation** (`model_json_schema()`) guides LLM output structure
2. **Lenient Parsing** handles markdown blocks and text wrapping
3. **Validation Errors** provide feedback for LLM retries
4. **Optional Fields** handle uncertain or missing LLM outputs
5. **Type Coercion** (lax mode) helps normalize LLM variations
6. **Mock LLMs** enable comprehensive testing without API calls
7. **Function Calling Format** integrates with OpenAI-style tool use

Ready for Project 5? Move on to the FastAPI + Pydantic Microservice!
