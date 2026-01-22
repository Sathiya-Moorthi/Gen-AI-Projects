# Multi-Agent Content Generation System

A powerful multi-agent system for generating publication-ready content with real-time research, SEO optimization, and strict quality control.

## 🚀 Key Features

*   **Sequential Agent Execution**: Research → Writer → SEO → Scorer workflow.
*   **Publication-Ready Quality**: 
    *   Strict SEO thresholds (Score ≥ 80).
    *   Overall Quality Score ≥ 85.
    *   Flesch Reading Ease ≥ 65.
*   **Real-Time Research**: Integrated **SERP API** for up-to-date facts and statistics.
*   **Full-Stack UI**: 
    *   **Backend**: Flask API with async workflow management.
    *   **Frontend**: Streamlit UI with real-time agent monitoring and progress bars.
    *   **Theme**: Fully compatible with Light/Dark modes.

## 📂 Project Structure

*   `content_workflow_improved.py`: Core logic for the multi-agent workflow (Research, Writer, SEO, Scorer).
*   `flask_backend_app.py`: REST API backend to manage workflows.
*   `streamlit_frontend_app.py`: Interactive web interface for users.
*   `publication_ready_workflow.py`: Specialized module for high-quality content generation standards.
*   `agent_monitor.py`: Utilities for tracking agent progress.

## 🛠️ Quick Start

### 1. Prerequisites
*   Python 3.8+
*   OpenAI API Key
*   SERP API Key (Recommended for real-time research)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Running the System (Full Stack)

**Terminal 1: Start Backend**
```bash
python flask_backend_app.py
```

**Terminal 2: Start Frontend**
```bash
streamlit run streamlit_frontend_app.py
```

Access the UI at `http://localhost:8501`.

### 4. Running Standalone Workflow (CLI)
To test the workflow directly in your terminal:
```bash
python content_workflow_improved.py
```

## 📚 Documentation
*   **[QUICKSTART.md](QUICKSTART.md)**: Detailed step-by-step setup and usage guide.
*   **[PUBLICATION_READY_SETUP.md](PUBLICATION_READY_SETUP.md)**: Deep dive into the publication standards and SERP API configuration.
*   **[ANALYSIS.md](ANALYSIS.md)**: Architecture and workflow analysis.

## 🔧 Configuration
You can adjust strictness and model settings in `content_workflow_improved.py` > `WorkflowConfig` class.

*   `SEO_PASS_THRESHOLD`: Default 80
*   `OVERALL_PASS_THRESHOLD`: Default 85
*   `OPENAI_MODEL`: Default "gpt-4o-mini"
