from openai import OpenAI
from typing import List, Dict, Any, Optional
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    tools: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Make a chat completion request to OpenAI GPT-4o.

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (default: gpt-4o)
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        tools: Optional list of function/tool definitions

    Returns:
        Dict containing the response content and any tool calls
    """
    try:
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**kwargs)

        result = {
            "content": response.choices[0].message.content,
            "role": response.choices[0].message.role,
            "tool_calls": None
        }

        if response.choices[0].message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in response.choices[0].message.tool_calls
            ]

        return result

    except Exception as e:
        raise RuntimeError(f"LLM request failed: {str(e)}")


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Get embedding vector for text.

    Args:
        text: Text to embed
        model: Embedding model to use

    Returns:
        List of floats representing the embedding vector
    """
    try:
        response = client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"Embedding request failed: {str(e)}")
