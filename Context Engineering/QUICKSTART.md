# Quick Start Guide

Get up and running with the Context Engineering demos in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- pip (Python package installer)

## Setup Steps

### 1. Install Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- pyautogen (AutoGen framework)
- openai (OpenAI API client)
- tiktoken (Token counting)
- colorama (Colored terminal output)
- termcolor (Terminal colors)

### 2. Configure OpenAI API Key

Create your configuration file:

```bash
# On Windows
copy config.example.json config.json

# On Mac/Linux
cp config.example.json config.json
```

Edit `config.json` and replace the API key:

```json
{
  "api_key": "sk-your-actual-api-key-here",
  "model": "gpt-3.5-turbo",
  "max_tokens": 4096
}
```

### 3. Run the Demos

#### Option A: Interactive Menu (Recommended)

```bash
python main_demo.py
```

This launches an interactive menu where you can:
- Run individual demos
- Run all demos sequentially
- See visual comparisons

#### Option B: Run Individual Demos

```bash
# Demo 1: Context Write - Token Tracking
python demos/1_context_write.py

# Demo 2: Context Select - Message Filtering
python demos/2_context_select.py

# Demo 3: Context Compress - Summarization
python demos/3_context_compress.py

# Demo 4: Context Isolate - Separate Contexts
python demos/4_context_isolate.py
```

## What Each Demo Shows

### Demo 1: Context WRITE
- **Duration:** ~2 minutes
- **API Calls:** 6
- **Shows:** How context grows with each message, token visualization, context window usage

### Demo 2: Context SELECT
- **Duration:** ~1 minute
- **API Calls:** 0 (uses pre-built examples)
- **Shows:** Three selection strategies, token savings comparison

### Demo 3: Context COMPRESS
- **Duration:** ~3 minutes
- **API Calls:** 2-4
- **Shows:** Two compression strategies, before/after comparisons, token savings

### Demo 4: Context ISOLATE
- **Duration:** ~2 minutes
- **API Calls:** 6-8
- **Shows:** Context leakage problem and solution, separate context management

## Expected Costs

Using `gpt-3.5-turbo` (default):
- Per demo: $0.01 - $0.05
- All demos: $0.05 - $0.20

Using `gpt-4`:
- Per demo: $0.10 - $0.50
- All demos: $0.50 - $2.00

## Troubleshooting

### Error: "config.json not found"
**Solution:** Create config.json from config.example.json and add your API key.

### Error: "No module named 'autogen'"
**Solution:** Run `pip install -r requirements.txt`

### Error: "OpenAI API error"
**Solution:**
1. Check your API key is valid
2. Ensure you have credits in your OpenAI account
3. Check your internet connection

### Output looks weird / no colors
**Solution:**
- Windows: Colorama should handle this automatically
- If issues persist, try running in Windows Terminal instead of CMD

### Token counts seem wrong
**Solution:** Token counting is approximate. Actual API usage may vary slightly.

## Tips for Best Experience

1. **Run in sequence:** Start with Demo 1 and progress through Demo 4
2. **Read the output:** Each demo includes explanations and insights
3. **Check token visualizations:** The progress bars show context usage
4. **Compare strategies:** Note the token savings in each approach
5. **Experiment:** Modify the demos to test your own scenarios

## Next Steps

After completing the demos:

1. **Modify the demos** to test with your own use cases
2. **Combine strategies** for optimal context management
3. **Read the code** in each demo to understand implementation
4. **Apply to your projects** using the patterns demonstrated

## Model Selection

Edit `config.json` to try different models:

```json
{
  "model": "gpt-3.5-turbo",      // Fast, cheap, 4K context
  "model": "gpt-3.5-turbo-16k",  // Same but 16K context
  "model": "gpt-4",              // Better quality, 8K context
  "model": "gpt-4-turbo",        // Best quality, 128K context
}
```

## Support

- **Issues:** Check the main README.md
- **Questions:** Review the demo output messages
- **Errors:** Check the troubleshooting section above

## Quick Command Reference

```bash
# Setup
pip install -r requirements.txt
cp config.example.json config.json
# (edit config.json with your API key)

# Run
python main_demo.py              # Interactive menu
python demos/1_context_write.py  # Individual demo

# Check
python -c "import autogen; print('AutoGen OK')"  # Verify install
```

Happy learning!
