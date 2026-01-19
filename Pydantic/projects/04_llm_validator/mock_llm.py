"""
Project 4: LLM Output Validator - Mock LLM
===========================================

This module provides a mock LLM for testing validation logic.

Features:
- Configurable response types (valid, invalid, malformed)
- Simulates common LLM output patterns
- Supports retry testing
"""

import json
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


# ============================================================================
# RESPONSE TYPES
# ============================================================================

class ResponseType(str, Enum):
    """Type of mock response to generate."""
    VALID_JSON = "valid_json"
    VALID_WITH_MARKDOWN = "valid_with_markdown"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    WRONG_TYPE = "wrong_type"
    EXTRA_FIELDS = "extra_fields"
    INVALID_JSON = "invalid_json"
    EMPTY_RESPONSE = "empty_response"
    TEXT_WITH_JSON = "text_with_json"
    PARTIAL_JSON = "partial_json"


# ============================================================================
# MOCK RESPONSES
# ============================================================================

MOCK_SENTIMENT_RESPONSES = {
    ResponseType.VALID_JSON: {
        "sentiment": "positive",
        "confidence": 0.92,
        "explanation": "The text contains positive language and enthusiasm.",
        "key_phrases": ["excellent", "highly recommend", "love it"]
    },
    ResponseType.VALID_WITH_MARKDOWN: """```json
{
    "sentiment": "negative",
    "confidence": 0.85,
    "explanation": "The text expresses disappointment and frustration.",
    "key_phrases": ["disappointed", "not worth it", "poor quality"]
}
```""",
    ResponseType.MISSING_REQUIRED_FIELD: {
        "confidence": 0.75,
        "explanation": "Missing sentiment field"
    },
    ResponseType.WRONG_TYPE: {
        "sentiment": "positive",
        "confidence": "high",  # Should be float
        "explanation": "Type error in confidence"
    },
    ResponseType.EXTRA_FIELDS: {
        "sentiment": "neutral",
        "confidence": 0.60,
        "explanation": "Neutral sentiment detected.",
        "key_phrases": [],
        "extra_field": "This should be ignored",
        "another_extra": 123
    },
    ResponseType.INVALID_JSON: '{"sentiment": "positive", confidence: 0.9}',  # Missing quotes
    ResponseType.EMPTY_RESPONSE: "",
    ResponseType.TEXT_WITH_JSON: """Based on my analysis, here is the sentiment:

{
    "sentiment": "mixed",
    "confidence": 0.70,
    "explanation": "The text contains both positive and negative elements.",
    "key_phrases": ["good but", "however", "on the other hand"]
}

I hope this helps!""",
    ResponseType.PARTIAL_JSON: '{"sentiment": "positive", "confidence": 0.8',  # Incomplete
}

MOCK_ENTITY_RESPONSES = {
    ResponseType.VALID_JSON: {
        "entities": [
            {"text": "Apple Inc.", "entity_type": "organization", "confidence": 0.95},
            {"text": "Tim Cook", "entity_type": "person", "confidence": 0.92},
            {"text": "Cupertino", "entity_type": "location", "confidence": 0.88},
            {"text": "$100 billion", "entity_type": "money", "confidence": 0.90},
        ],
        "total_entities": 4
    },
    ResponseType.VALID_WITH_MARKDOWN: """Here are the extracted entities:

```json
{
    "entities": [
        {"text": "Google", "entity_type": "organization", "confidence": 0.98},
        {"text": "Sundar Pichai", "entity_type": "person", "confidence": 0.95}
    ],
    "total_entities": 2
}
```""",
    ResponseType.MISSING_REQUIRED_FIELD: {
        "entities": [
            {"entity_type": "person", "confidence": 0.9}  # Missing text
        ]
    },
}

MOCK_TASK_RESPONSES = {
    ResponseType.VALID_JSON: {
        "tasks": [
            {
                "title": "Review Q4 financial report",
                "description": "Complete review and provide feedback",
                "priority": "high",
                "due_date": "2024-01-31",
                "assignee": "John Smith",
                "tags": ["finance", "quarterly"]
            },
            {
                "title": "Schedule team meeting",
                "priority": "medium",
                "tags": ["admin"]
            }
        ],
        "context": "Q4 Planning Meeting Notes"
    },
}

MOCK_CLASSIFICATION_RESPONSES = {
    ResponseType.VALID_JSON: {
        "classifications": [
            {"category": "technical_support", "confidence": 0.85, "reasoning": "User mentions software issues"},
            {"category": "billing", "confidence": 0.15, "reasoning": "No billing-related keywords"}
        ],
        "primary_category": "technical_support"
    },
}

MOCK_REVIEW_RESPONSES = {
    ResponseType.VALID_JSON: {
        "product_name": "Wireless Headphones XYZ",
        "rating": 4,
        "pros": ["Great sound quality", "Comfortable fit", "Long battery life"],
        "cons": ["Price is a bit high", "No carrying case included"],
        "sentiment": "positive",
        "would_recommend": True
    },
}


# ============================================================================
# MOCK LLM CLASS
# ============================================================================

@dataclass
class MockLLMConfig:
    """Configuration for mock LLM behavior."""

    default_response_type: ResponseType = ResponseType.VALID_JSON
    failure_rate: float = 0.0  # Probability of returning invalid response
    delay_ms: int = 0  # Simulated delay
    improve_on_retry: bool = True  # Return valid response on retry
    retry_count: int = 0  # Track retries


class MockLLM:
    """
    Mock LLM for testing validation logic.

    Generates various types of responses to test parsing robustness.
    """

    def __init__(self, config: MockLLMConfig | None = None):
        """Initialize mock LLM with configuration."""
        self.config = config or MockLLMConfig()
        self._call_count = 0
        self._last_prompt = ""

    def reset(self) -> None:
        """Reset call count and state."""
        self._call_count = 0
        self._last_prompt = ""
        self.config.retry_count = 0

    @property
    def call_count(self) -> int:
        return self._call_count

    def generate(
        self,
        prompt: str,
        response_type: ResponseType | None = None,
        task_type: str = "sentiment",
    ) -> str:
        """
        Generate a mock LLM response.

        Args:
            prompt: The prompt (stored for debugging)
            response_type: Type of response to generate
            task_type: Type of task (sentiment, entity, task, classification, review)

        Returns:
            Mock response string
        """
        self._call_count += 1
        self._last_prompt = prompt

        # Determine response type
        if response_type is None:
            if self.config.failure_rate > 0 and random.random() < self.config.failure_rate:
                response_type = random.choice([
                    ResponseType.INVALID_JSON,
                    ResponseType.MISSING_REQUIRED_FIELD,
                    ResponseType.WRONG_TYPE,
                ])
            elif self.config.improve_on_retry and self.config.retry_count > 0:
                response_type = ResponseType.VALID_JSON
            else:
                response_type = self.config.default_response_type

        # Get mock responses for task type
        mock_responses = self._get_mock_responses(task_type)

        # Get response for type
        response = mock_responses.get(response_type, mock_responses[ResponseType.VALID_JSON])

        # Convert to string if needed
        if isinstance(response, dict):
            response = json.dumps(response, indent=2)

        logger.info(
            "mock_llm_generate",
            call_count=self._call_count,
            response_type=response_type.value,
            task_type=task_type
        )

        return response

    def _get_mock_responses(self, task_type: str) -> dict:
        """Get mock responses for a task type."""
        responses = {
            "sentiment": MOCK_SENTIMENT_RESPONSES,
            "entity": MOCK_ENTITY_RESPONSES,
            "task": MOCK_TASK_RESPONSES,
            "classification": MOCK_CLASSIFICATION_RESPONSES,
            "review": MOCK_REVIEW_RESPONSES,
        }
        return responses.get(task_type, MOCK_SENTIMENT_RESPONSES)

    def generate_with_retry(
        self,
        prompt: str,
        schema: type[BaseModel],
        task_type: str = "sentiment",
        max_retries: int = 3,
    ) -> tuple[str, int]:
        """
        Generate response with simulated retry behavior.

        Args:
            prompt: The prompt
            schema: Expected schema
            task_type: Type of task
            max_retries: Maximum retries

        Returns:
            Tuple of (response, attempt_count)
        """
        from parser import LLMOutputParser

        parser = LLMOutputParser(schema)

        for attempt in range(max_retries):
            self.config.retry_count = attempt

            response = self.generate(prompt, task_type=task_type)
            result = parser.parse(response)

            if result.success:
                return response, attempt + 1

            # Simulate LLM learning from feedback
            if self.config.improve_on_retry:
                logger.info(
                    "mock_llm_retry",
                    attempt=attempt + 1,
                    error=result.error_message
                )

        # Final attempt with valid response
        self.config.retry_count = max_retries
        return self.generate(prompt, response_type=ResponseType.VALID_JSON, task_type=task_type), max_retries


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_mock_llm(
    response_type: ResponseType = ResponseType.VALID_JSON,
    failure_rate: float = 0.0,
) -> MockLLM:
    """
    Create a configured mock LLM.

    Args:
        response_type: Default response type
        failure_rate: Probability of generating invalid responses

    Returns:
        Configured MockLLM instance
    """
    config = MockLLMConfig(
        default_response_type=response_type,
        failure_rate=failure_rate,
    )
    return MockLLM(config)


def get_all_response_types() -> list[ResponseType]:
    """Get all available response types."""
    return list(ResponseType)


def get_sample_prompts() -> dict[str, str]:
    """Get sample prompts for each task type."""
    return {
        "sentiment": "Analyze the sentiment of the following review: 'This product exceeded my expectations!'",
        "entity": "Extract named entities from: 'Apple CEO Tim Cook announced new products in Cupertino.'",
        "task": "Extract tasks from: 'We need to review the report by Friday and schedule a meeting.'",
        "classification": "Classify this support ticket: 'My app keeps crashing when I try to login.'",
        "review": "Extract structured data from: 'Great headphones! Sound is amazing but a bit pricey.'",
    }
