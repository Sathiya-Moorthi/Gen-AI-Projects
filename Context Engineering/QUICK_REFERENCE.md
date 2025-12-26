# Context Engineering - Quick Reference Card

## 🚀 To Run the Demo

```bash
cd "D:\Context Engineering"
python run_demo.py
```

**Duration:** ~2-3 minutes
**Cost:** ~$0.01-0.03 (GPT-3.5-turbo)

---

## 📊 What Gets Demonstrated

| Demo | Technique | Key Metric | What It Shows |
|------|-----------|------------|---------------|
| 1 | **WRITE** | Context growth | Tokens: 0 → 218 (3 turns) |
| 2 | **SELECT** | Filtering | 37% savings (109 → 69 tokens) |
| 3 | **COMPRESS** | Summarization | 68% savings (108 → 35 tokens) |
| 4 | **ISOLATE** | Separation | Problem → Solution |

---

## 💡 Explanation in 30 Seconds

> "Context Engineering manages what we send to LLMs to avoid limits and reduce costs. Four techniques:
>
> 1. **WRITE** - Track token growth
> 2. **SELECT** - Keep only relevant messages (40-80% savings)
> 3. **COMPRESS** - Summarize old conversations (60-80% savings)
> 4. **ISOLATE** - Separate user/topic contexts
>
> Combined: 70% cost reduction in production!"

---

## 🎯 Key Talking Points

### Demo 1: WRITE
- "Context grows linearly - see the progress bar"
- "10 turns can use 25-50% of your context window"
- "Monitoring prevents hitting limits unexpectedly"

### Demo 2: SELECT
- "We don't always need ALL history"
- "Three strategies: Recent / Keywords / Minimal"
- "37% savings while maintaining relevance"

### Demo 3: COMPRESS
- "Summarize old, keep recent detailed"
- "LLM creates its own summaries"
- "68% savings preserving key information"

### Demo 4: ISOLATE
- "Mixed contexts = confusion"
- "Separate users/sessions/topics"
- "Clarity + Security + Better responses"

---

## 📈 Real-World Impact Example

```
1,000 users × 20 messages each:

WITHOUT Context Engineering:
  2,000,000 tokens
  Cost: $4.00/batch

WITH Context Engineering:
  600,000 tokens
  Cost: $1.20/batch

SAVINGS: 70% ($2.80/batch)
```

---

## 📁 Project Files at a Glance

```
run_demo.py              ← Run this!
PRESENTATION_GUIDE.md    ← How to explain
CONCEPTS.md              ← Visual explanations
QUICKSTART.md            ← Setup guide
config.json              ← Your API key
```

---

## ⚡ Quick Commands

```bash
# Run demo
python run_demo.py

# Check if setup works
python -c "from utils import *; print('OK')"

# Verify API key loaded
python -c "import json; c=json.load(open('config.json')); print('Model:', c['model'])"
```

---

## 🎤 Presentation Flow (15 min)

1. **Intro** (2 min) - The problem: context limits
2. **Run Demo** (8 min) - Let it run, explain each part
3. **Real Impact** (3 min) - Show cost savings
4. **Q&A** (2 min) - Questions

---

## ❓ Common Questions

**Q: Which technique is most important?**
A: Monitoring (WRITE) first, then ISOLATE for multi-user, SELECT+COMPRESS as needed

**Q: Does it work with other LLMs?**
A: Yes! Techniques are universal. Token counting needs adjustment per model.

**Q: Production-ready?**
A: Yes! The utility functions can be used as-is. Combine all 4 techniques.

---

## 🔧 Troubleshooting

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"Config not found"**
```bash
copy config.example.json config.json
# Edit config.json with your API key
```

**Unicode errors**
Already fixed! Uses ASCII-safe characters.

---

## 📊 Cheat Sheet - When to Use What

| Scenario | Use These Techniques |
|----------|---------------------|
| Multi-user chatbot | ISOLATE + WRITE + SELECT |
| Long conversations | COMPRESS + WRITE |
| Cost-sensitive app | SELECT + COMPRESS |
| Real-time chat | WRITE + SELECT |
| Single-user assistant | WRITE + COMPRESS |
| Production system | **ALL FOUR** |

---

## 💾 Share After Presentation

1. Code (GitHub/ZIP)
2. PRESENTATION_GUIDE.md
3. QUICKSTART.md
4. Your slides (optional)

---

## 🎯 Success Metrics

Your audience should leave understanding:
- ✅ Why context management matters
- ✅ What each technique does
- ✅ Real cost savings possible
- ✅ How to implement basics

---

## 📱 One-Liner for Each Technique

| Technique | One-Liner |
|-----------|-----------|
| WRITE | "Watch your tokens like you watch your budget" |
| SELECT | "Send less, get more" |
| COMPRESS | "Summarize the past, detail the present" |
| ISOLATE | "Good fences make good contexts" |

---

**Remember:** The demo is visual and self-explanatory. Your job is to highlight key points and explain the "why"!

Good luck! 🚀
