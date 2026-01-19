"""
Project 4: LLM Output Validator - Schemas
==========================================

This module defines Pydantic schemas for validating LLM outputs.

Key Concepts:
- JSON schema generation (model_json_schema())
- Lenient parsing strategies
- model_validate_json() for direct JSON parsing
- Optional fields for uncertain LLM outputs
- Integration patterns with LLM APIs
- OpenAI function calling format

Real-World Problem:
LLMs return unstructured text. Applications need structured JSON for
downstream processing. Pydantic validates and normalizes LLM outputs,
handling hallucinations and format errors.
"""

from datetime import date, datetime
from enum import Enum
from typing import Literal

import structlog
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

logger = structlog.get_logger(__name__)


# ============================================================================
# COMMON ENUMS
# ============================================================================

class Sentiment(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class Priority(str, Enum):
    """Priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EntityType(str, Enum):
    """Named entity types."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PRODUCT = "product"
    OTHER = "other"


# ============================================================================
# BASE SCHEMA FOR LLM OUTPUTS
# ============================================================================

class LLMOutputBase(BaseModel):
    """
    Base class for LLM output schemas.

    Features:
    - Lenient parsing (extra fields ignored)
    - Coercion enabled
    - Common metadata fields
    """

    model_config = ConfigDict(
        extra="ignore",  # Ignore unexpected fields from LLM
        str_strip_whitespace=True,
        populate_by_name=True,
    )


# ============================================================================
# TEXT ANALYSIS SCHEMAS
# ============================================================================

class SentimentAnalysis(LLMOutputBase):
    """
    Schema for sentiment analysis output.

    Example prompt:
    "Analyze the sentiment of the following text and return JSON..."
    """

    sentiment: Sentiment = Field(
        ...,
        description="Overall sentiment of the text"
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1)"
    )

    explanation: str | None = Field(
        default=None,
        max_length=500,
        description="Brief explanation of the sentiment"
    )

    key_phrases: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Key phrases that influenced the sentiment"
    )

    @field_validator("confidence")
    @classmethod
    def round_confidence(cls, v: float) -> float:
        """Round confidence to 2 decimal places."""
        return round(v, 2)


class NamedEntity(LLMOutputBase):
    """Schema for a single named entity."""

    text: str = Field(
        ...,
        min_length=1,
        description="The entity text"
    )

    entity_type: EntityType = Field(
        ...,
        description="Type of entity"
    )

    start_pos: int | None = Field(
        default=None,
        ge=0,
        description="Start position in original text"
    )

    end_pos: int | None = Field(
        default=None,
        ge=0,
        description="End position in original text"
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Extraction confidence"
    )


class EntityExtraction(LLMOutputBase):
    """
    Schema for named entity extraction output.

    Example prompt:
    "Extract all named entities from the following text..."
    """

    entities: list[NamedEntity] = Field(
        default_factory=list,
        description="List of extracted entities"
    )

    total_entities: int = Field(
        default=0,
        ge=0,
        description="Total number of entities found"
    )

    @model_validator(mode="after")
    def sync_total(self) -> "EntityExtraction":
        """Ensure total_entities matches actual count."""
        self.total_entities = len(self.entities)
        return self


class TextSummary(LLMOutputBase):
    """
    Schema for text summarization output.

    Example prompt:
    "Summarize the following text in 2-3 sentences..."
    """

    summary: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="The summarized text"
    )

    key_points: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Main points from the text"
    )

    word_count: int = Field(
        default=0,
        ge=0,
        description="Word count of summary"
    )

    @model_validator(mode="after")
    def calculate_word_count(self) -> "TextSummary":
        """Calculate word count from summary."""
        self.word_count = len(self.summary.split())
        return self


# ============================================================================
# TASK EXTRACTION SCHEMAS
# ============================================================================

class ExtractedTask(LLMOutputBase):
    """Schema for a single extracted task."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title"
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Detailed task description"
    )

    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Task priority"
    )

    due_date: date | None = Field(
        default=None,
        description="Due date if mentioned"
    )

    assignee: str | None = Field(
        default=None,
        description="Person assigned to task"
    )

    tags: list[str] = Field(
        default_factory=list,
        max_length=5,
        description="Relevant tags"
    )


class TaskExtraction(LLMOutputBase):
    """
    Schema for extracting tasks from text.

    Example prompt:
    "Extract actionable tasks from the following meeting notes..."
    """

    tasks: list[ExtractedTask] = Field(
        default_factory=list,
        description="List of extracted tasks"
    )

    context: str | None = Field(
        default=None,
        max_length=500,
        description="Overall context/project"
    )


# ============================================================================
# CLASSIFICATION SCHEMAS
# ============================================================================

class ClassificationResult(LLMOutputBase):
    """Schema for a single classification."""

    category: str = Field(
        ...,
        min_length=1,
        description="Classification category"
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Classification confidence"
    )

    reasoning: str | None = Field(
        default=None,
        description="Reasoning for classification"
    )


class MultiLabelClassification(LLMOutputBase):
    """
    Schema for multi-label classification output.

    Example prompt:
    "Classify the following support ticket into categories..."
    """

    classifications: list[ClassificationResult] = Field(
        ...,
        min_length=1,
        description="List of classifications"
    )

    primary_category: str = Field(
        ...,
        description="Most likely category"
    )

    @model_validator(mode="after")
    def set_primary(self) -> "MultiLabelClassification":
        """Ensure primary_category matches highest confidence."""
        if self.classifications:
            highest = max(self.classifications, key=lambda x: x.confidence)
            self.primary_category = highest.category
        return self


# ============================================================================
# QUESTION ANSWERING SCHEMAS
# ============================================================================

class Answer(LLMOutputBase):
    """Schema for question answering output."""

    answer: str = Field(
        ...,
        min_length=1,
        description="The answer to the question"
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Answer confidence"
    )

    sources: list[str] = Field(
        default_factory=list,
        description="Source references"
    )

    is_uncertain: bool = Field(
        default=False,
        description="Whether the answer is uncertain"
    )


class QuestionAnswer(LLMOutputBase):
    """
    Schema for Q&A with context.

    Example prompt:
    "Answer the following question based on the provided context..."
    """

    question: str = Field(
        ...,
        description="The original question"
    )

    answer: Answer = Field(
        ...,
        description="The answer details"
    )

    relevant_context: str | None = Field(
        default=None,
        description="Relevant context used for answering"
    )


# ============================================================================
# OPENAI FUNCTION CALLING SCHEMAS
# ============================================================================

class FunctionParameter(BaseModel):
    """Schema for a function parameter (OpenAI format)."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=True, description="Is parameter required")
    enum: list[str] | None = Field(default=None, description="Allowed values")


class FunctionDefinition(BaseModel):
    """
    Schema for OpenAI function calling format.

    This generates the schema that tells the LLM how to call functions.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        description="Function name"
    )

    description: str = Field(
        ...,
        max_length=1000,
        description="What the function does"
    )

    parameters: dict = Field(
        ...,
        description="JSON schema for parameters"
    )

    @classmethod
    def from_pydantic_model(cls, model: type[BaseModel], name: str, description: str) -> "FunctionDefinition":
        """Create FunctionDefinition from a Pydantic model."""
        return cls(
            name=name,
            description=description,
            parameters=model.model_json_schema()
        )


class FunctionCall(LLMOutputBase):
    """
    Schema for an LLM function call response.

    This is what the LLM returns when using function calling.
    """

    name: str = Field(
        ...,
        description="Function name to call"
    )

    arguments: dict = Field(
        default_factory=dict,
        description="Function arguments"
    )


# ============================================================================
# STRUCTURED OUTPUT SCHEMAS
# ============================================================================

class ProductReview(LLMOutputBase):
    """
    Schema for structured product review extraction.

    Example prompt:
    "Extract structured data from this product review..."
    """

    product_name: str | None = Field(
        default=None,
        description="Product being reviewed"
    )

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Star rating (1-5)"
    )

    pros: list[str] = Field(
        default_factory=list,
        description="Positive aspects mentioned"
    )

    cons: list[str] = Field(
        default_factory=list,
        description="Negative aspects mentioned"
    )

    sentiment: Sentiment = Field(
        default=Sentiment.NEUTRAL,
        description="Overall sentiment"
    )

    would_recommend: bool | None = Field(
        default=None,
        description="Would reviewer recommend product"
    )

    @model_validator(mode="after")
    def infer_recommendation(self) -> "ProductReview":
        """Infer recommendation from rating if not provided."""
        if self.would_recommend is None and self.rating is not None:
            self.would_recommend = self.rating >= 4
        return self


class ConversationTurn(LLMOutputBase):
    """Schema for a conversation turn."""

    role: Literal["user", "assistant", "system"] = Field(
        ...,
        description="Speaker role"
    )

    content: str = Field(
        ...,
        description="Message content"
    )

    intent: str | None = Field(
        default=None,
        description="Detected intent"
    )


class ConversationAnalysis(LLMOutputBase):
    """
    Schema for analyzing conversations.

    Example prompt:
    "Analyze this customer support conversation..."
    """

    turns: list[ConversationTurn] = Field(
        default_factory=list,
        description="Conversation turns"
    )

    topic: str | None = Field(
        default=None,
        description="Main conversation topic"
    )

    resolution_status: Literal["resolved", "unresolved", "escalated", "unknown"] = Field(
        default="unknown",
        description="How the conversation ended"
    )

    customer_sentiment: Sentiment = Field(
        default=Sentiment.NEUTRAL,
        description="Overall customer sentiment"
    )

    action_items: list[str] = Field(
        default_factory=list,
        description="Follow-up actions needed"
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_schema_for_prompt(model: type[BaseModel]) -> str:
    """
    Get a formatted JSON schema for including in prompts.

    This helps guide the LLM to output properly structured data.
    """
    schema = model.model_json_schema()

    # Clean up for prompt
    if "title" in schema:
        del schema["title"]

    return schema


def create_system_prompt(model: type[BaseModel], task_description: str) -> str:
    """
    Create a system prompt that instructs the LLM to output structured JSON.

    Args:
        model: The Pydantic model defining the expected output
        task_description: What the LLM should do

    Returns:
        System prompt string
    """
    schema = get_schema_for_prompt(model)

    return f"""You are a helpful assistant that outputs structured JSON data.

{task_description}

You MUST respond with valid JSON that matches this schema:
{schema}

Important:
- Output ONLY valid JSON, no additional text
- Ensure all required fields are present
- Use null for optional fields if information is not available
- Do not include fields not in the schema
"""
