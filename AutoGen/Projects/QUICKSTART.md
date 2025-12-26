# Quick Start Guide - Multi-Agent System

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (1 minute)

```bash
pip install autogen-core autogen-ext flask flask-cors streamlit requests pandas
```

### Step 2: Set API Keys (1 minute)

```bash
export OPENAI_API_KEY="your_openai_key_here"
export SERP_API_KEY="your_serp_key_here" # Optional but recommended for real-time research
```

### Step 3: Test Standalone Workflow (2 minutes)

```bash
python content_workflow_improved.py
```

**Expected Output**: Complete workflow execution with research, content, SEO analysis, and final score.

---

## 🌐 Full Stack Setup (10 minutes)

### Terminal 1: Start Flask Backend

```bash
python flask_backend_app.py
```

Wait for: `* Running on http://0.0.0.0:5000`

### Terminal 2: Start Streamlit Frontend

```bash
streamlit run streamlit_frontend_app.py
```

Wait for: Browser opens to `http://localhost:8501`

### Terminal 3: Test API (Optional)

```bash
curl -X POST http://localhost:5000/api/generate-content \
  -H "Content-Type: application/json" \
  -d '{"request": "Generate a blog post about AI automation"}'
```

---

## 🎯 First Request via UI

1. Open browser to `http://localhost:8501`
2. Enter request: "Generate a blog post about AI automation tools for small businesses"
3. Click "🚀 Generate Content"
4. Wait 30-60 seconds
5. View results in tabs:
   - **Research**: Keywords, audience analysis
   - **Content**: Full HTML article
   - **SEO**: Technical analysis
   - **Score**: Quality evaluation

---

## 🐛 Troubleshooting

### Issue: "OPENAI_API_KEY not set"
```bash
# Solution: Export the key
export OPENAI_API_KEY="your-key-here"
```

### Issue: "Cannot connect to backend"
```bash
# Solution: Check Flask is running and accessible
curl http://localhost:5000/
# Should return: {"status": "healthy", ...}
```

### Issue: "Workflow timeout"
```python
# Solution: Increase timeout in content_workflow_improved.py
class WorkflowConfig:
    WORKFLOW_TIMEOUT = 1200  # Increase from 600 to 1200
```

---

## 📊 Sample Request Templates

### Template 1: Blog Post
```
Generate a comprehensive 800-word blog post about [TOPIC] targeting [AUDIENCE]. 
Focus on [KEY_ANGLE] and include actionable tips.
```

Example:
```
Generate a comprehensive 800-word blog post about sustainable home gardening 
targeting urban millennials. Focus on space-saving techniques and include 
actionable tips for small apartments.
```

### Template 2: Technical Guide
```
Create a technical guide explaining [CONCEPT] for [SKILL_LEVEL]. 
Include examples and best practices.
```

Example:
```
Create a technical guide explaining Docker containers for beginners. 
Include practical examples and deployment best practices.
```

### Template 3: Marketing Copy
```
Write [COPY_TYPE] for [PRODUCT] highlighting [KEY_BENEFITS]. 
Use [TONE] tone and target [AUDIENCE].
```

Example:
```
Write landing page copy for a project management SaaS tool highlighting 
team collaboration features. Use professional yet friendly tone and 
target small business owners.
```

---

## 🎨 Customization Quick Tips

### Change Model
```python
# In content_workflow_improved.py
class WorkflowConfig:
    OPENAI_MODEL = "gpt-4"  # Change from gpt-4o-mini
```

### Adjust Scoring Thresholds
```python
class WorkflowConfig:
    SEO_PASS_THRESHOLD = 70      # Lower for more lenient
    OVERALL_PASS_THRESHOLD = 75  # Lower for more approvals
```

### Modify Agent Behavior
Edit the `_system_message` in each agent class in `content_workflow_improved.py` to change their behavior.

---

## 📈 Next Steps

1. ✅ Basic setup working? → Explore workflow history in UI
2. ✅ Understanding the flow? → Read ANALYSIS.md for architecture
3. ✅ Want to customize? → Modify agent prompts in workflow file
4. ✅ Ready for production? → Check README.md deployment section

---

## 🆘 Need Help?

- **Architecture**: Read ANALYSIS.md
- **Full Documentation**: Read README.md
- **API Reference**: Check Flask endpoints in flask_backend_app.py
- **UI Guide**: Explore Streamlit tabs in streamlit_frontend_app.py

---
