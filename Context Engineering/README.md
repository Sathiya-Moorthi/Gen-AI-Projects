# Context Engineering Demo with AutoGen

A comprehensive demonstration of context engineering techniques using Microsoft's AutoGen framework and OpenAI LLMs.

## What is Context Engineering?

Context engineering is the practice of managing and optimizing the context (conversation history and information) sent to Large Language Models (LLMs) to improve performance, reduce costs, and work within token limits.

## Demo Concepts

This project demonstrates four key context engineering techniques:

### 1. **WRITE** - Context Creation and Token Tracking
- Shows how context grows with each message
- Visualizes token consumption
- Demonstrates context window limitations

### 2. **SELECT** - Selective Context Passing
- Filters relevant messages from conversation history
- Reduces unnecessary context
- Improves response quality and reduces costs

### 3. **COMPRESS** - Context Compression
- Summarizes long conversations
- Maintains key information while reducing tokens
- Extends effective conversation length

### 4. **ISOLATE** - Context Isolation
- Separates different conversation contexts
- Prevents context leakage between tasks
- Manages multiple independent conversations

## Project Structure

```
Context Engineering/
├── README.md
├── requirements.txt
├── config.json (create from config.example.json)
├── demos/
│   ├── 1_context_write.py      # Basic context and token tracking
│   ├── 2_context_select.py     # Selective message passing
│   ├── 3_context_compress.py   # Context summarization
│   └── 4_context_isolate.py    # Context isolation
├── utils/
│   ├── __init__.py
│   ├── token_counter.py        # Token counting utilities
│   └── visualizer.py           # Visual output helpers
└── main_demo.py                # Run all demos with visual comparison

```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Create a `config.json` file from the template:

```bash
cp config.example.json config.json
```

Edit `config.json` and add your OpenAI API key:

```json
{
  "api_key": "your-openai-api-key-here",
  "model": "gpt-3.5-turbo",
  "max_tokens": 4096
}
```

### 3. Run Individual Demos

```bash
# Demo 1: Context Write
python demos/1_context_write.py

# Demo 2: Context Select
python demos/2_context_select.py

# Demo 3: Context Compress
python demos/3_context_compress.py

# Demo 4: Context Isolate
python demos/4_context_isolate.py
```

### 4. Run Complete Demo Suite

```bash
python main_demo.py
```

## Key Learnings

- **Token Management**: Understanding how context grows and impacts costs
- **Strategic Selection**: Choosing what context to include
- **Compression Techniques**: Maintaining information density
- **Context Boundaries**: Preventing information leakage

## Requirements

- Python 3.8+
- OpenAI API key
- AutoGen framework
- tiktoken for token counting

## Visual Output

Each demo provides:
- Token usage visualization with bars
- Context size comparisons
- Before/After examples
- Real-time metrics

## Cost Considerations

The demos use GPT-3.5-turbo by default to minimize costs. You can change to GPT-4 in `config.json` for better results (higher cost).

Estimated cost per full demo run: $0.05 - $0.20 depending on model choice.

## License

MIT License - Feel free to use for learning and demonstrations.
