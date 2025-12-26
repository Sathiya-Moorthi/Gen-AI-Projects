# Context Engineering Demo Project Structure

```
Context Engineering/
│
├── README.md                          # Main project documentation
├── QUICKSTART.md                      # Quick setup guide (5 minutes)
├── CONCEPTS.md                        # Visual explanations with diagrams
├── PROJECT_STRUCTURE.md               # This file
│
├── requirements.txt                   # Python dependencies
├── config.example.json                # Configuration template
├── .gitignore                        # Git ignore rules (keeps API keys safe)
│
├── main_demo.py                      # Interactive menu to run all demos
│
├── demos/                            # Demo scripts
│   ├── 1_context_write.py           # Demo: Context growth & token tracking
│   ├── 2_context_select.py          # Demo: Selective message passing
│   ├── 3_context_compress.py        # Demo: Context compression/summarization
│   └── 4_context_isolate.py         # Demo: Context isolation & separation
│
└── utils/                            # Utility modules
    ├── __init__.py                   # Package initialization
    ├── token_counter.py              # Token counting functions
    └── visualizer.py                 # Pretty printing & visualization
```

## File Descriptions

### Core Files

**README.md** (3.4 KB)
- Complete project overview
- Concept explanations
- Setup instructions
- Key learnings and requirements

**QUICKSTART.md** (4.5 KB)
- 5-minute setup guide
- Step-by-step instructions
- Troubleshooting tips
- Quick command reference

**CONCEPTS.md** (14.6 KB)
- Visual explanations with ASCII diagrams
- Decision trees and flowcharts
- Real-world examples
- Best practices summary

**main_demo.py** (6.6 KB)
- Interactive menu system
- Configuration checker
- Demo launcher
- Colored terminal interface

### Configuration

**requirements.txt**
- pyautogen (AutoGen framework)
- openai (OpenAI API)
- tiktoken (token counting)
- colorama (colored output)
- termcolor (terminal colors)
- python-dotenv (environment variables)

**config.example.json**
- API key placeholder
- Model selection
- Token limits
- Context window sizes for different models

### Demo Scripts (demos/)

**1_context_write.py** (5.5 KB)
- Shows context accumulation over 6 turns
- Real-time token visualization
- Warning system for high usage
- Growth analysis table
- Interactive conversation simulation

**2_context_select.py** (9.4 KB)
- Three selection strategies:
  - Recent messages only
  - Keyword-based selection
  - Minimal context
- Token savings comparisons
- Best practices guide

**3_context_compress.py** (10.9 KB)
- Two compression strategies:
  - Partial compression (old messages)
  - Aggressive compression (most messages)
- LLM-based summarization
- Before/after comparisons
- When to use compression guide

**4_context_isolate.py** (11.1 KB)
- Context leakage demonstration
- Separate context solution
- Multi-domain agents
- Implementation patterns
- Trade-offs analysis

### Utility Modules (utils/)

**token_counter.py** (2.7 KB)
Functions:
- `count_tokens()` - Count tokens in text
- `estimate_tokens_for_messages()` - Estimate tokens for conversation
- `get_context_window_size()` - Get model's context limit
- `calculate_token_percentage()` - Calculate context usage %

**visualizer.py** (4.7 KB)
Functions:
- `print_header()` - Formatted headers
- `print_section()` - Section dividers
- `visualize_tokens()` - Progress bar visualization
- `print_comparison()` - Before/after comparisons
- `print_messages()` - Format message lists
- `print_success/error/warning()` - Status messages

## File Sizes Summary

```
Total Project Size: ~74 KB

Documentation:     22.5 KB (30%)
Demo Scripts:      36.9 KB (50%)
Utilities:          7.7 KB (10%)
Config/Setup:       7.0 KB (10%)
```

## Lines of Code

```
Demo Scripts:       ~400 lines (total)
Utilities:          ~200 lines
Main Runner:        ~160 lines
Total Python:       ~760 lines
Documentation:    ~1,200 lines
```

## Usage Flow

```
1. Install dependencies (requirements.txt)
   ↓
2. Configure API key (config.example.json → config.json)
   ↓
3. Run main_demo.py
   ↓
4. Select demo from menu
   ↓
5. Watch visual demonstrations
   ↓
6. Learn context engineering techniques!
```

## Customization Points

**Easy to modify:**
- Questions in demo scripts
- Selection strategies (keywords, max messages)
- Compression thresholds
- Visualization styles
- Model selection in config

**Advanced customization:**
- Add new demo scripts
- Extend utility functions
- Create custom visualizations
- Implement new context strategies
- Add logging/metrics

## Dependencies Graph

```
main_demo.py
    ↓
    ├─→ demos/1_context_write.py
    ├─→ demos/2_context_select.py
    ├─→ demos/3_context_compress.py
    └─→ demos/4_context_isolate.py
            ↓
            ├─→ utils/token_counter.py
            ├─→ utils/visualizer.py
            ├─→ autogen (external)
            └─→ openai (external)
```

## Key Features

✓ **Modular Design:** Each demo is independent
✓ **Visual Feedback:** Progress bars, colors, comparisons
✓ **Educational:** Comments and explanations throughout
✓ **Production-Ready:** Utilities can be used in real projects
✓ **Extensible:** Easy to add new demos or strategies
✓ **Safe:** .gitignore protects API keys

## Next Steps

1. **Run the demos** to see concepts in action
2. **Read the code** to understand implementation
3. **Modify demos** to test your scenarios
4. **Extract utilities** for your own projects
5. **Combine strategies** for optimal results

## Support Files Created

- `.gitignore` - Protects sensitive files
- `__init__.py` - Makes utils a proper Python package
- Config template - Easy API key setup

## Testing Checklist

- [ ] Install dependencies
- [ ] Configure API key
- [ ] Run main_demo.py
- [ ] Run each demo individually
- [ ] Verify visual output
- [ ] Check token counting accuracy
- [ ] Test different models
- [ ] Modify and experiment

Happy Context Engineering!
