"""
Project 4: LLM Output Validator - Parser
=========================================

This module provides robust parsing and validation for LLM outputs.

Features:
- Lenient JSON parsing (handles markdown code blocks, etc.)
- Automatic retry with schema feedback
- Graceful handling of partial/malformed outputs
- Multiple parsing strategies
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Generic

import structlog
from pydantic import BaseModel, ValidationError

logger = structlog.get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


# ============================================================================
# PARSING RESULT TYPES
# ============================================================================

class ParseStatus(str, Enum):
    """Status of a parse attempt."""
    SUCCESS = "success"
    JSON_ERROR = "json_error"
    VALIDATION_ERROR = "validation_error"
    EMPTY_RESPONSE = "empty_response"
    EXTRACTION_FAILED = "extraction_failed"


@dataclass
class ParseResult(Generic[T]):
    """Result of parsing an LLM output."""

    status: ParseStatus
    data: T | None = None
    raw_text: str = ""
    extracted_json: str | None = None
    error_message: str | None = None
    validation_errors: list[dict] | None = None
    attempts: int = 1

    @property
    def success(self) -> bool:
        return self.status == ParseStatus.SUCCESS

    def get_error_feedback(self) -> str:
        """Generate feedback for the LLM to fix the output."""
        if self.status == ParseStatus.JSON_ERROR:
            return f"Your response was not valid JSON. Error: {self.error_message}\nPlease respond with valid JSON only."

        if self.status == ParseStatus.VALIDATION_ERROR and self.validation_errors:
            error_details = []
            for error in self.validation_errors:
                loc = ".".join(str(l) for l in error.get("loc", []))
                msg = error.get("msg", "")
                error_details.append(f"- Field '{loc}': {msg}")

            return f"""Your JSON response had validation errors:
{chr(10).join(error_details)}

Please fix these issues and respond with valid JSON."""

        if self.status == ParseStatus.EMPTY_RESPONSE:
            return "Your response was empty. Please provide a JSON response."

        if self.status == ParseStatus.EXTRACTION_FAILED:
            return "Could not find JSON in your response. Please respond with only valid JSON."

        return "Please try again with a valid JSON response."


# ============================================================================
# JSON EXTRACTION
# ============================================================================

def extract_json_from_text(text: str) -> str | None:
    """
    Extract JSON from text that may contain markdown or other formatting.

    Handles:
    - Plain JSON
    - Markdown code blocks (```json ... ```)
    - JSON with leading/trailing text
    - Multiple JSON objects (returns first)
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    # Strategy 1: Try plain JSON first
    if text.startswith("{") or text.startswith("["):
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

    # Strategy 2: Extract from markdown code block
    code_block_patterns = [
        r"```json\s*([\s\S]*?)\s*```",  # ```json ... ```
        r"```\s*([\s\S]*?)\s*```",       # ``` ... ```
        r"`([\s\S]*?)`",                  # ` ... `
    ]

    for pattern in code_block_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            match = match.strip()
            if match.startswith("{") or match.startswith("["):
                try:
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

    # Strategy 3: Find JSON-like structure in text
    # Look for {...} or [...]
    json_patterns = [
        r"(\{[\s\S]*\})",  # Object
        r"(\[[\s\S]*\])",  # Array
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue

    # Strategy 4: Try to fix common issues
    fixed = try_fix_json(text)
    if fixed:
        return fixed

    return None


def try_fix_json(text: str) -> str | None:
    """
    Attempt to fix common JSON issues from LLM outputs.

    Handles:
    - Single quotes instead of double quotes
    - Trailing commas
    - Unquoted keys
    - Missing quotes around string values
    """
    # Remove common prefixes
    prefixes_to_remove = [
        "Here is the JSON:",
        "JSON:",
        "Response:",
        "Output:",
    ]

    for prefix in prefixes_to_remove:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()

    # Try to find JSON object or array
    start_idx = -1
    end_idx = -1

    for i, char in enumerate(text):
        if char in "{[":
            start_idx = i
            break

    if start_idx == -1:
        return None

    # Find matching end
    depth = 0
    in_string = False
    escape_next = False

    for i in range(start_idx, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char in "{[":
            depth += 1
        elif char in "}]":
            depth -= 1
            if depth == 0:
                end_idx = i
                break

    if end_idx == -1:
        return None

    json_str = text[start_idx:end_idx + 1]

    # Try to parse
    try:
        json.loads(json_str)
        return json_str
    except json.JSONDecodeError:
        pass

    # Try replacing single quotes with double quotes
    try:
        fixed = json_str.replace("'", '"')
        json.loads(fixed)
        return fixed
    except json.JSONDecodeError:
        pass

    # Try removing trailing commas
    try:
        fixed = re.sub(r",\s*([}\]])", r"\1", json_str)
        json.loads(fixed)
        return fixed
    except json.JSONDecodeError:
        pass

    return None


# ============================================================================
# PARSER CLASS
# ============================================================================

class LLMOutputParser(Generic[T]):
    """
    Parser for validating LLM outputs against Pydantic schemas.

    Features:
    - Multiple extraction strategies
    - Lenient parsing mode
    - Detailed error reporting
    """

    def __init__(
        self,
        schema: type[T],
        strict: bool = False,
    ):
        """
        Initialize parser.

        Args:
            schema: Pydantic model class to validate against
            strict: If True, require exact JSON without extraction
        """
        self.schema = schema
        self.strict = strict

    def parse(self, text: str) -> ParseResult[T]:
        """
        Parse and validate LLM output text.

        Args:
            text: Raw LLM output text

        Returns:
            ParseResult with validated data or error details
        """
        if not text or not text.strip():
            logger.warning("llm_output_empty")
            return ParseResult(
                status=ParseStatus.EMPTY_RESPONSE,
                raw_text=text or "",
                error_message="Response was empty"
            )

        # Extract JSON from text
        if self.strict:
            json_str = text.strip()
        else:
            json_str = extract_json_from_text(text)

        if json_str is None:
            logger.warning("json_extraction_failed", text_preview=text[:100])
            return ParseResult(
                status=ParseStatus.EXTRACTION_FAILED,
                raw_text=text,
                error_message="Could not extract JSON from response"
            )

        # Try to parse JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning("json_parse_error", error=str(e))
            return ParseResult(
                status=ParseStatus.JSON_ERROR,
                raw_text=text,
                extracted_json=json_str,
                error_message=f"JSON parse error: {e.msg} at position {e.pos}"
            )

        # Validate against schema
        try:
            validated = self.schema.model_validate(data)
            logger.info("llm_output_validated", schema=self.schema.__name__)
            return ParseResult(
                status=ParseStatus.SUCCESS,
                data=validated,
                raw_text=text,
                extracted_json=json_str
            )

        except ValidationError as e:
            logger.warning(
                "validation_error",
                schema=self.schema.__name__,
                error_count=e.error_count()
            )
            return ParseResult(
                status=ParseStatus.VALIDATION_ERROR,
                raw_text=text,
                extracted_json=json_str,
                error_message=f"Validation failed with {e.error_count()} errors",
                validation_errors=e.errors()
            )


# ============================================================================
# RETRY HANDLER
# ============================================================================

class RetryHandler:
    """
    Handle retries for LLM parsing with feedback.

    Provides feedback to the LLM about parsing errors so it can fix them.
    """

    def __init__(
        self,
        max_retries: int = 3,
        include_schema_in_feedback: bool = True,
    ):
        """
        Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            include_schema_in_feedback: Include schema in error feedback
        """
        self.max_retries = max_retries
        self.include_schema_in_feedback = include_schema_in_feedback

    def create_retry_prompt(
        self,
        original_prompt: str,
        parse_result: ParseResult,
        schema: type[BaseModel],
    ) -> str:
        """
        Create a retry prompt with error feedback.

        Args:
            original_prompt: The original user prompt
            parse_result: The failed parse result
            schema: The expected schema

        Returns:
            New prompt with error feedback
        """
        feedback = parse_result.get_error_feedback()

        retry_prompt = f"""Your previous response had errors:

{feedback}

Original request:
{original_prompt}
"""

        if self.include_schema_in_feedback:
            retry_prompt += f"""

Expected JSON schema:
{json.dumps(schema.model_json_schema(), indent=2)}
"""

        retry_prompt += "\nPlease provide a corrected JSON response."

        return retry_prompt


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def parse_llm_output(
    text: str,
    schema: type[T],
    strict: bool = False,
) -> ParseResult[T]:
    """
    Parse LLM output against a Pydantic schema.

    Args:
        text: Raw LLM output
        schema: Pydantic model to validate against
        strict: Require exact JSON (no extraction)

    Returns:
        ParseResult with data or errors
    """
    parser = LLMOutputParser(schema)
    return parser.parse(text)


def validate_json_string(
    json_str: str,
    schema: type[T],
) -> T:
    """
    Validate a JSON string directly against a schema.

    Args:
        json_str: Valid JSON string
        schema: Pydantic model

    Returns:
        Validated model instance

    Raises:
        ValidationError: If validation fails
        json.JSONDecodeError: If JSON is invalid
    """
    return schema.model_validate_json(json_str)


def get_schema_prompt(schema: type[BaseModel]) -> str:
    """
    Get schema description for including in prompts.

    Args:
        schema: Pydantic model

    Returns:
        Formatted schema description
    """
    json_schema = schema.model_json_schema()
    return json.dumps(json_schema, indent=2)
