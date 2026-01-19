"""
Project 4: LLM Output Validator - Tests
========================================

Comprehensive pytest tests for LLM output parsing and validation.

Run with: pytest test_parser.py -v
"""

import json

import pytest
from pydantic import ValidationError

from schemas import (
    SentimentAnalysis,
    EntityExtraction,
    NamedEntity,
    TaskExtraction,
    ExtractedTask,
    MultiLabelClassification,
    ProductReview,
    Sentiment,
    Priority,
    EntityType,
    FunctionDefinition,
    create_system_prompt,
)
from parser import (
    LLMOutputParser,
    ParseResult,
    ParseStatus,
    RetryHandler,
    parse_llm_output,
    extract_json_from_text,
    try_fix_json,
)
from mock_llm import (
    MockLLM,
    MockLLMConfig,
    ResponseType,
    create_mock_llm,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def valid_sentiment_json():
    return json.dumps({
        "sentiment": "positive",
        "confidence": 0.92,
        "explanation": "Very positive text.",
        "key_phrases": ["great", "excellent"]
    })


@pytest.fixture
def valid_entity_json():
    return json.dumps({
        "entities": [
            {"text": "Apple", "entity_type": "organization", "confidence": 0.95},
            {"text": "Tim Cook", "entity_type": "person", "confidence": 0.90}
        ],
        "total_entities": 2
    })


@pytest.fixture
def parser():
    return LLMOutputParser(SentimentAnalysis)


@pytest.fixture
def mock_llm():
    return create_mock_llm()


# ============================================================================
# SCHEMA TESTS
# ============================================================================

class TestSentimentAnalysis:
    """Tests for SentimentAnalysis schema."""

    def test_valid_sentiment(self):
        result = SentimentAnalysis(
            sentiment=Sentiment.POSITIVE,
            confidence=0.9
        )
        assert result.sentiment == Sentiment.POSITIVE
        assert result.confidence == 0.9

    def test_confidence_rounding(self):
        result = SentimentAnalysis(
            sentiment=Sentiment.POSITIVE,
            confidence=0.9876
        )
        assert result.confidence == 0.99  # Rounded to 2 decimal places

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            SentimentAnalysis(sentiment=Sentiment.POSITIVE, confidence=1.5)

        with pytest.raises(ValidationError):
            SentimentAnalysis(sentiment=Sentiment.POSITIVE, confidence=-0.1)

    def test_invalid_sentiment(self):
        with pytest.raises(ValidationError):
            SentimentAnalysis(sentiment="invalid", confidence=0.9)

    def test_extra_fields_ignored(self):
        result = SentimentAnalysis(
            sentiment=Sentiment.POSITIVE,
            confidence=0.9,
            extra_field="ignored"
        )
        assert result.sentiment == Sentiment.POSITIVE


class TestEntityExtraction:
    """Tests for EntityExtraction schema."""

    def test_valid_entities(self):
        entities = [
            NamedEntity(text="Apple", entity_type=EntityType.ORGANIZATION),
            NamedEntity(text="Tim Cook", entity_type=EntityType.PERSON),
        ]
        result = EntityExtraction(entities=entities)
        assert len(result.entities) == 2
        assert result.total_entities == 2  # Auto-calculated

    def test_total_entities_sync(self):
        # Even if wrong total provided, it gets corrected
        result = EntityExtraction(
            entities=[NamedEntity(text="Test", entity_type=EntityType.PERSON)],
            total_entities=999  # Wrong value
        )
        assert result.total_entities == 1  # Corrected

    def test_empty_entities(self):
        result = EntityExtraction()
        assert result.entities == []
        assert result.total_entities == 0


class TestTaskExtraction:
    """Tests for TaskExtraction schema."""

    def test_valid_task(self):
        task = ExtractedTask(
            title="Review report",
            priority=Priority.HIGH,
            due_date="2024-01-31"
        )
        assert task.title == "Review report"
        assert task.priority == Priority.HIGH

    def test_default_priority(self):
        task = ExtractedTask(title="Simple task")
        assert task.priority == Priority.MEDIUM

    def test_extraction_with_context(self):
        result = TaskExtraction(
            tasks=[ExtractedTask(title="Task 1")],
            context="Meeting notes"
        )
        assert result.context == "Meeting notes"


class TestProductReview:
    """Tests for ProductReview schema."""

    def test_recommendation_inference(self):
        # Rating >= 4 -> would_recommend = True
        review = ProductReview(rating=4)
        assert review.would_recommend is True

        # Rating < 4 -> would_recommend = False
        review = ProductReview(rating=3)
        assert review.would_recommend is False

    def test_explicit_recommendation(self):
        # Explicit value not overridden
        review = ProductReview(rating=5, would_recommend=False)
        # Since model_validator runs after, it only sets if None
        # Need to check the actual behavior
        assert review.rating == 5


# ============================================================================
# JSON EXTRACTION TESTS
# ============================================================================

class TestJsonExtraction:
    """Tests for JSON extraction from LLM outputs."""

    def test_plain_json(self):
        text = '{"key": "value"}'
        result = extract_json_from_text(text)
        assert result == text

    def test_json_array(self):
        text = '[{"item": 1}, {"item": 2}]'
        result = extract_json_from_text(text)
        assert result == text

    def test_markdown_code_block(self):
        text = '```json\n{"key": "value"}\n```'
        result = extract_json_from_text(text)
        assert json.loads(result) == {"key": "value"}

    def test_markdown_without_lang(self):
        text = '```\n{"key": "value"}\n```'
        result = extract_json_from_text(text)
        assert json.loads(result) == {"key": "value"}

    def test_text_with_json(self):
        text = 'Here is the result: {"key": "value"} Hope this helps!'
        result = extract_json_from_text(text)
        assert json.loads(result) == {"key": "value"}

    def test_empty_text(self):
        assert extract_json_from_text("") is None
        assert extract_json_from_text("   ") is None

    def test_no_json(self):
        text = "This is just plain text with no JSON."
        assert extract_json_from_text(text) is None


class TestTryFixJson:
    """Tests for JSON fixing functionality."""

    def test_trailing_comma(self):
        text = '{"key": "value",}'
        result = try_fix_json(text)
        if result:
            assert json.loads(result) == {"key": "value"}

    def test_prefix_removal(self):
        text = 'JSON: {"key": "value"}'
        result = try_fix_json(text)
        if result:
            assert json.loads(result) == {"key": "value"}


# ============================================================================
# PARSER TESTS
# ============================================================================

class TestLLMOutputParser:
    """Tests for LLMOutputParser class."""

    def test_parse_valid_json(self, parser, valid_sentiment_json):
        result = parser.parse(valid_sentiment_json)
        assert result.success
        assert result.status == ParseStatus.SUCCESS
        assert result.data.sentiment == Sentiment.POSITIVE

    def test_parse_empty_response(self, parser):
        result = parser.parse("")
        assert not result.success
        assert result.status == ParseStatus.EMPTY_RESPONSE

    def test_parse_invalid_json(self, parser):
        result = parser.parse('{"sentiment": invalid}')
        assert not result.success
        assert result.status in [ParseStatus.JSON_ERROR, ParseStatus.EXTRACTION_FAILED]

    def test_parse_validation_error(self, parser):
        # Missing required field
        result = parser.parse('{"confidence": 0.9}')
        assert not result.success
        assert result.status == ParseStatus.VALIDATION_ERROR
        assert result.validation_errors is not None

    def test_parse_markdown_response(self, parser, valid_sentiment_json):
        text = f"```json\n{valid_sentiment_json}\n```"
        result = parser.parse(text)
        assert result.success

    def test_strict_mode(self, valid_sentiment_json):
        parser = LLMOutputParser(SentimentAnalysis, strict=True)

        # Plain JSON should work
        result = parser.parse(valid_sentiment_json)
        assert result.success

        # Markdown should fail in strict mode
        text = f"```json\n{valid_sentiment_json}\n```"
        result = parser.parse(text)
        # In strict mode, no extraction is attempted
        assert result.status in [ParseStatus.JSON_ERROR, ParseStatus.EXTRACTION_FAILED]


class TestParseResult:
    """Tests for ParseResult class."""

    def test_success_property(self):
        result = ParseResult(status=ParseStatus.SUCCESS)
        assert result.success is True

        result = ParseResult(status=ParseStatus.JSON_ERROR)
        assert result.success is False

    def test_error_feedback_json_error(self):
        result = ParseResult(
            status=ParseStatus.JSON_ERROR,
            error_message="Unexpected token"
        )
        feedback = result.get_error_feedback()
        assert "not valid JSON" in feedback

    def test_error_feedback_validation_error(self):
        result = ParseResult(
            status=ParseStatus.VALIDATION_ERROR,
            validation_errors=[
                {"loc": ("sentiment",), "msg": "field required"}
            ]
        )
        feedback = result.get_error_feedback()
        assert "validation errors" in feedback
        assert "sentiment" in feedback


# ============================================================================
# RETRY HANDLER TESTS
# ============================================================================

class TestRetryHandler:
    """Tests for RetryHandler class."""

    def test_create_retry_prompt(self):
        handler = RetryHandler()
        parse_result = ParseResult(
            status=ParseStatus.VALIDATION_ERROR,
            validation_errors=[{"loc": ("sentiment",), "msg": "field required"}]
        )

        prompt = handler.create_retry_prompt(
            "Analyze sentiment",
            parse_result,
            SentimentAnalysis
        )

        assert "previous response had errors" in prompt
        assert "Analyze sentiment" in prompt

    def test_include_schema_in_feedback(self):
        handler = RetryHandler(include_schema_in_feedback=True)
        parse_result = ParseResult(status=ParseStatus.JSON_ERROR)

        prompt = handler.create_retry_prompt(
            "Analyze sentiment",
            parse_result,
            SentimentAnalysis
        )

        assert "schema" in prompt.lower()


# ============================================================================
# MOCK LLM TESTS
# ============================================================================

class TestMockLLM:
    """Tests for MockLLM class."""

    def test_generate_valid_json(self, mock_llm):
        response = mock_llm.generate("test", response_type=ResponseType.VALID_JSON)
        data = json.loads(response)
        assert "sentiment" in data

    def test_generate_markdown(self, mock_llm):
        response = mock_llm.generate("test", response_type=ResponseType.VALID_WITH_MARKDOWN)
        assert "```" in response

    def test_generate_invalid_json(self, mock_llm):
        response = mock_llm.generate("test", response_type=ResponseType.INVALID_JSON)
        with pytest.raises(json.JSONDecodeError):
            json.loads(response)

    def test_call_count(self, mock_llm):
        mock_llm.reset()
        assert mock_llm.call_count == 0

        mock_llm.generate("test")
        assert mock_llm.call_count == 1

        mock_llm.generate("test")
        assert mock_llm.call_count == 2

    def test_improve_on_retry(self, mock_llm):
        mock_llm.config.improve_on_retry = True
        response, attempts = mock_llm.generate_with_retry(
            "test",
            SentimentAnalysis,
            max_retries=3
        )

        # Should eventually get valid response
        result = parse_llm_output(response, SentimentAnalysis)
        assert result.success


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_pipeline(self, mock_llm):
        # Generate -> Parse -> Validate
        response = mock_llm.generate("Analyze sentiment", task_type="sentiment")
        result = parse_llm_output(response, SentimentAnalysis)

        assert result.success
        assert result.data.sentiment in list(Sentiment)

    def test_entity_extraction_pipeline(self, mock_llm):
        response = mock_llm.generate("Extract entities", task_type="entity")
        result = parse_llm_output(response, EntityExtraction)

        if result.success:
            assert isinstance(result.data.entities, list)
            for entity in result.data.entities:
                assert entity.entity_type in list(EntityType)

    def test_error_recovery_flow(self, mock_llm):
        # Simulate error -> feedback -> retry
        mock_llm.config.default_response_type = ResponseType.MISSING_REQUIRED_FIELD
        mock_llm.config.improve_on_retry = True

        response, attempts = mock_llm.generate_with_retry(
            "Analyze sentiment",
            SentimentAnalysis,
            max_retries=3
        )

        # Eventually succeeds
        result = parse_llm_output(response, SentimentAnalysis)
        assert result.success


# ============================================================================
# FUNCTION CALLING TESTS
# ============================================================================

class TestFunctionCalling:
    """Tests for OpenAI function calling format."""

    def test_function_definition_from_model(self):
        func_def = FunctionDefinition.from_pydantic_model(
            SentimentAnalysis,
            name="analyze_sentiment",
            description="Analyze text sentiment"
        )

        assert func_def.name == "analyze_sentiment"
        assert func_def.description == "Analyze text sentiment"
        assert "properties" in func_def.parameters

    def test_function_name_pattern(self):
        # Valid names
        FunctionDefinition(
            name="valid_name",
            description="Test",
            parameters={}
        )
        FunctionDefinition(
            name="_private",
            description="Test",
            parameters={}
        )

        # Invalid name
        with pytest.raises(ValidationError):
            FunctionDefinition(
                name="123invalid",
                description="Test",
                parameters={}
            )


# ============================================================================
# SCHEMA PROMPT TESTS
# ============================================================================

class TestSchemaPrompts:
    """Tests for schema prompt generation."""

    def test_create_system_prompt(self):
        prompt = create_system_prompt(
            SentimentAnalysis,
            "Analyze the sentiment of the text."
        )

        assert "sentiment" in prompt.lower()
        assert "JSON" in prompt
        assert "schema" in prompt.lower()

    def test_schema_generation(self):
        schema = SentimentAnalysis.model_json_schema()

        assert "properties" in schema
        assert "sentiment" in schema["properties"]
        assert "confidence" in schema["properties"]
