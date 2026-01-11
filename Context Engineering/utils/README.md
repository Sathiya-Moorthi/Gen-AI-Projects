# Context Engineering Utilities

Helper utilities for context engineering demonstrations.

## 📂 Modules

| Module | Description |
|--------|-------------|
| `__init__.py` | Package initialization and exports |
| `token_counter.py` | Token counting utilities using tiktoken |
| `visualizer.py` | Visual output helpers for demos |

## 💡 Usage

```python
from utils import count_tokens, visualize_context

# Count tokens in a message
tokens = count_tokens("Your message here")

# Visualize context usage
visualize_context(messages, max_tokens=4096)
```

## 📦 Dependencies

- `tiktoken` - OpenAI's tokenizer
- `rich` - Terminal formatting (optional)
