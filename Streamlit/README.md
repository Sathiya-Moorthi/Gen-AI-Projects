# Streamlit Applications

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io/)

Interactive web applications built with [Streamlit](https://streamlit.io/) for data visualization and utility tools.

## Project Structure

```
Streamlit/
├── scripts/
│   ├── basic_calculator_dashboard.py   # Calculator with UI
│   ├── personal_expense_tracker.py     # Expense tracking app
│   └── test_streamlit.py               # Streamlit testing/demo
├── output files/                        # Generated files and exports
├── .gitignore
└── README.md
```

## App Catalog

| Application | Description | Features |
|-------------|-------------|----------|
| **Basic Calculator Dashboard** | Interactive calculator | Basic arithmetic, history |
| **Personal Expense Tracker** | Track personal expenses | Add/edit expenses, charts, export |
| **Test Streamlit** | Demo/testing app | Streamlit components showcase |

## Prerequisites

- Python 3.8 or higher
- Modern web browser

## Installation

1. Navigate to this directory:
   ```bash
   cd Streamlit
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Applications

### Basic Calculator
```bash
streamlit run scripts/basic_calculator_dashboard.py
```

### Personal Expense Tracker
```bash
streamlit run scripts/personal_expense_tracker.py
```

### Test App
```bash
streamlit run scripts/test_streamlit.py
```

The app will open in your default browser at `http://localhost:8501`

## App Screenshots

### Personal Expense Tracker
- Dashboard with expense overview
- Add new expenses with categories
- Visualize spending with charts
- Export data to CSV

### Calculator Dashboard
- Clean, responsive UI
- Real-time calculations
- Operation history

## Configuration

Create `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
port = 8501
headless = true
```

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect repository to [share.streamlit.io](https://share.streamlit.io)
3. Deploy

### Local Network
```bash
streamlit run scripts/your_app.py --server.address 0.0.0.0
```

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.
