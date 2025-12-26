"""Token counting utilities for context management."""

import tiktoken
from typing import List, Dict, Any


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count the number of tokens in a text string.

    Args:
        text: The text to count tokens for
        model: The model name to use for encoding

    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def estimate_tokens_for_messages(messages: List[Dict[str, Any]], model: str = "gpt-3.5-turbo") -> int:
    """
    Estimate the number of tokens used by a list of messages.

    Based on OpenAI's token counting guide:
    https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: The model name to use for encoding

    Returns:
        Estimated total number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens_per_message = 3  # every message follows <|start|>{role/name}\n{content}<|end|>\n
    tokens_per_name = 1

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            if isinstance(value, str):
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name

    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def get_context_window_size(model: str) -> int:
    """
    Get the context window size for a given model.

    Args:
        model: The model name

    Returns:
        Context window size in tokens
    """
    context_windows = {
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-turbo": 128000,
        "gpt-4-turbo-preview": 128000,
    }

    return context_windows.get(model, 4096)


def calculate_token_percentage(used_tokens: int, model: str = "gpt-3.5-turbo") -> float:
    """
    Calculate the percentage of context window used.

    Args:
        used_tokens: Number of tokens used
        model: The model name

    Returns:
        Percentage of context window used (0-100)
    """
    window_size = get_context_window_size(model)
    return (used_tokens / window_size) * 100
