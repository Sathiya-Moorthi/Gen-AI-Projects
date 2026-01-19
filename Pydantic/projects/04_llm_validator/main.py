"""
Project 4: LLM Output Validator - Main Demonstration
====================================================

This script demonstrates LLM output validation patterns.

Run with: python main.py
"""

import json
import logging

from pydantic import ValidationError

from schemas import (
    SentimentAnalysis,
    EntityExtraction,
    TaskExtraction,
    MultiLabelClassification,
    ProductReview,
    ConversationAnalysis,
    FunctionDefinition,
    create_system_prompt,
    get_schema_for_prompt,
)
from parser import (
    LLMOutputParser,
    ParseResult,
    ParseStatus,
    RetryHandler,
    parse_llm_output,
    extract_json_from_text,
)
from mock_llm import (
    MockLLM,
    MockLLMConfig,
    ResponseType,
    create_mock_llm,
    get_sample_prompts,
)

logging.basicConfig(level=logging.INFO)


def demonstrate_schema_generation():
    """Show JSON schema generation for LLM prompts."""
    print("\n" + "=" * 60)
    print("DEMO 1: JSON Schema Generation for LLM Prompts")
    print("=" * 60)

    print("\n1. SentimentAnalysis schema:")
    schema = SentimentAnalysis.model_json_schema()
    print(json.dumps(schema, indent=2))

    print("\n2. System prompt with schema:")
    system_prompt = create_system_prompt(
        SentimentAnalysis,
        "Analyze the sentiment of the provided text."
    )
    print(system_prompt[:500] + "...")

    print("\n3. Schema for prompt (simplified):")
    prompt_schema = get_schema_for_prompt(EntityExtraction)
    print(json.dumps(prompt_schema, indent=2)[:400] + "...")


def demonstrate_basic_parsing():
    """Show basic LLM output parsing."""
    print("\n" + "=" * 60)
    print("DEMO 2: Basic LLM Output Parsing")
    print("=" * 60)

    # Valid JSON response
    valid_response = """
    {
        "sentiment": "positive",
        "confidence": 0.92,
        "explanation": "The text expresses satisfaction and enthusiasm.",
        "key_phrases": ["love it", "excellent", "highly recommend"]
    }
    """

    print("\n1. Parsing valid JSON:")
    result = parse_llm_output(valid_response, SentimentAnalysis)
    print(f"   Status: {result.status.value}")
    print(f"   Success: {result.success}")
    if result.data:
        print(f"   Sentiment: {result.data.sentiment}")
        print(f"   Confidence: {result.data.confidence}")

    # Markdown code block
    markdown_response = """Here is the analysis:

```json
{
    "sentiment": "negative",
    "confidence": 0.85,
    "explanation": "The reviewer expressed disappointment."
}
```

Let me know if you need more details."""

    print("\n2. Parsing markdown code block:")
    result = parse_llm_output(markdown_response, SentimentAnalysis)
    print(f"   Status: {result.status.value}")
    if result.data:
        print(f"   Sentiment: {result.data.sentiment}")


def demonstrate_json_extraction():
    """Show JSON extraction from various formats."""
    print("\n" + "=" * 60)
    print("DEMO 3: JSON Extraction from LLM Outputs")
    print("=" * 60)

    test_cases = [
        ("Plain JSON", '{"key": "value"}'),
        ("Markdown block", '```json\n{"key": "value"}\n```'),
        ("Text with JSON", 'Here is the result: {"key": "value"} Hope this helps!'),
        ("Single quotes", "{'key': 'value'}"),
        ("Trailing comma", '{"key": "value",}'),
    ]

    for name, text in test_cases:
        extracted = extract_json_from_text(text)
        print(f"\n   {name}:")
        print(f"   Input: {text[:50]}...")
        print(f"   Extracted: {extracted}")


def demonstrate_error_handling():
    """Show error handling for various failure modes."""
    print("\n" + "=" * 60)
    print("DEMO 4: Error Handling")
    print("=" * 60)

    error_cases = [
        ("Empty response", ""),
        ("Invalid JSON", '{"sentiment": positive}'),  # Unquoted value
        ("Missing required field", '{"confidence": 0.9}'),
        ("Wrong type", '{"sentiment": "positive", "confidence": "high"}'),
        ("Invalid enum", '{"sentiment": "very_happy", "confidence": 0.9}'),
    ]

    for name, response in error_cases:
        print(f"\n   --- {name} ---")
        result = parse_llm_output(response, SentimentAnalysis)
        print(f"   Status: {result.status.value}")
        print(f"   Error: {result.error_message}")
        if result.validation_errors:
            print(f"   Validation errors: {len(result.validation_errors)}")
            for err in result.validation_errors[:2]:
                print(f"     - {err.get('loc')}: {err.get('msg')}")


def demonstrate_retry_mechanism():
    """Show retry with feedback mechanism."""
    print("\n" + "=" * 60)
    print("DEMO 5: Retry with Feedback")
    print("=" * 60)

    # Simulated failed response
    bad_response = '{"confidence": 0.9}'  # Missing sentiment

    parser = LLMOutputParser(SentimentAnalysis)
    retry_handler = RetryHandler(max_retries=3)

    result = parser.parse(bad_response)
    print("\n1. First attempt (failed):")
    print(f"   Status: {result.status.value}")

    print("\n2. Feedback for retry:")
    feedback = result.get_error_feedback()
    print(feedback)

    print("\n3. Retry prompt:")
    retry_prompt = retry_handler.create_retry_prompt(
        "Analyze the sentiment of this text.",
        result,
        SentimentAnalysis
    )
    print(retry_prompt[:500] + "...")


def demonstrate_mock_llm():
    """Show mock LLM for testing."""
    print("\n" + "=" * 60)
    print("DEMO 6: Mock LLM for Testing")
    print("=" * 60)

    llm = create_mock_llm()

    print("\n1. Valid response:")
    response = llm.generate("Analyze sentiment", response_type=ResponseType.VALID_JSON)
    print(response[:200] + "...")

    print("\n2. Markdown response:")
    response = llm.generate("Analyze sentiment", response_type=ResponseType.VALID_WITH_MARKDOWN)
    print(response[:200] + "...")

    print("\n3. Invalid response:")
    response = llm.generate("Analyze sentiment", response_type=ResponseType.INVALID_JSON)
    print(response[:200] + "...")

    print("\n4. Response with retry simulation:")
    llm.reset()
    llm.config.improve_on_retry = True
    response, attempts = llm.generate_with_retry(
        "Analyze sentiment",
        SentimentAnalysis,
        max_retries=3
    )
    print(f"   Attempts: {attempts}")
    print(f"   Final response valid: {'sentiment' in response}")


def demonstrate_entity_extraction():
    """Show entity extraction validation."""
    print("\n" + "=" * 60)
    print("DEMO 7: Entity Extraction")
    print("=" * 60)

    llm = create_mock_llm()
    response = llm.generate("Extract entities", task_type="entity")

    print("\nMock LLM response:")
    print(response)

    result = parse_llm_output(response, EntityExtraction)
    print(f"\nParsing status: {result.status.value}")

    if result.data:
        print(f"\nExtracted entities ({result.data.total_entities}):")
        for entity in result.data.entities:
            print(f"  - {entity.text} ({entity.entity_type.value}): {entity.confidence:.2f}")


def demonstrate_task_extraction():
    """Show task extraction validation."""
    print("\n" + "=" * 60)
    print("DEMO 8: Task Extraction")
    print("=" * 60)

    llm = create_mock_llm()
    response = llm.generate("Extract tasks from meeting notes", task_type="task")

    print("\nMock LLM response:")
    print(response)

    result = parse_llm_output(response, TaskExtraction)

    if result.data:
        print(f"\nContext: {result.data.context}")
        print(f"\nExtracted tasks ({len(result.data.tasks)}):")
        for task in result.data.tasks:
            print(f"\n  Title: {task.title}")
            print(f"  Priority: {task.priority.value}")
            if task.due_date:
                print(f"  Due: {task.due_date}")
            if task.assignee:
                print(f"  Assignee: {task.assignee}")


def demonstrate_classification():
    """Show multi-label classification."""
    print("\n" + "=" * 60)
    print("DEMO 9: Multi-Label Classification")
    print("=" * 60)

    llm = create_mock_llm()
    response = llm.generate("Classify support ticket", task_type="classification")

    print("\nMock LLM response:")
    print(response)

    result = parse_llm_output(response, MultiLabelClassification)

    if result.data:
        print(f"\nPrimary category: {result.data.primary_category}")
        print("\nAll classifications:")
        for cls in result.data.classifications:
            print(f"  - {cls.category}: {cls.confidence:.2f}")
            if cls.reasoning:
                print(f"    Reasoning: {cls.reasoning}")


def demonstrate_product_review():
    """Show product review extraction."""
    print("\n" + "=" * 60)
    print("DEMO 10: Product Review Extraction")
    print("=" * 60)

    llm = create_mock_llm()
    response = llm.generate("Extract review data", task_type="review")

    print("\nMock LLM response:")
    print(response)

    result = parse_llm_output(response, ProductReview)

    if result.data:
        print(f"\nProduct: {result.data.product_name}")
        print(f"Rating: {'*' * (result.data.rating or 0)}")
        print(f"Sentiment: {result.data.sentiment.value}")
        print(f"Would recommend: {result.data.would_recommend}")
        print(f"\nPros: {', '.join(result.data.pros)}")
        print(f"Cons: {', '.join(result.data.cons)}")


def demonstrate_function_calling():
    """Show OpenAI function calling format."""
    print("\n" + "=" * 60)
    print("DEMO 11: OpenAI Function Calling Format")
    print("=" * 60)

    # Create function definition from Pydantic model
    func_def = FunctionDefinition.from_pydantic_model(
        SentimentAnalysis,
        name="analyze_sentiment",
        description="Analyze the sentiment of the provided text"
    )

    print("\nFunction definition:")
    print(json.dumps(func_def.model_dump(), indent=2)[:500] + "...")

    print("\n\nThis can be passed to OpenAI's API as a tool definition.")


def demonstrate_direct_json_validation():
    """Show direct JSON validation without extraction."""
    print("\n" + "=" * 60)
    print("DEMO 12: Direct JSON Validation (model_validate_json)")
    print("=" * 60)

    json_str = '{"sentiment": "positive", "confidence": 0.95}'

    print(f"\nJSON string: {json_str}")

    # Direct validation (faster than parse -> validate)
    try:
        result = SentimentAnalysis.model_validate_json(json_str)
        print(f"\nValidated:")
        print(f"  Sentiment: {result.sentiment}")
        print(f"  Confidence: {result.confidence}")
    except ValidationError as e:
        print(f"Validation failed: {e}")


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 60)
    print("# PYDANTIC MASTERY - PROJECT 4: LLM OUTPUT VALIDATOR")
    print("#" * 60)

    demonstrate_schema_generation()
    demonstrate_basic_parsing()
    demonstrate_json_extraction()
    demonstrate_error_handling()
    demonstrate_retry_mechanism()
    demonstrate_mock_llm()
    demonstrate_entity_extraction()
    demonstrate_task_extraction()
    demonstrate_classification()
    demonstrate_product_review()
    demonstrate_function_calling()
    demonstrate_direct_json_validation()

    print("\n" + "=" * 60)
    print("All demonstrations complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review schemas.py for output schemas")
    print("2. Study parser.py for parsing strategies")
    print("3. Run tests: pytest test_parser.py -v")
    print("4. Complete exercises in exercises.md")


if __name__ == "__main__":
    main()
