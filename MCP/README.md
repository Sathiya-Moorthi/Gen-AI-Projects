# Calculator MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple calculator MCP (Model Context Protocol) server that exposes arithmetic operations as tools for AI assistants like Claude.

## What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open protocol that enables AI assistants to interact with external tools and data sources. This server demonstrates how to build MCP tools using Python.

## Features

| Tool | Description | Example |
|------|-------------|---------|
| `add` | Add two numbers | `add(5, 3)` → `8` |
| `subtract` | Subtract numbers | `subtract(10, 4)` → `6` |
| `multiply` | Multiply numbers | `multiply(6, 7)` → `42` |
| `divide` | Divide with zero-check | `divide(15, 3)` → `5.0` |
| `power` | Exponentiation | `power(2, 3)` → `8.0` |
| `modulo` | Remainder operation | `modulo(17, 5)` → `2` |
| `square_root` | Square root | `square_root(16)` → `4.0` |
| `absolute` | Absolute value | `absolute(-5)` → `5` |
| `percentage` | Calculate percentage | `percentage(200, 15)` → `30.0` |

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Install from source

```bash
git clone https://github.com/Sathiya-Moorthi/MCP.git
cd calculator-mcp
pip install -e .
```

### Install dependencies only

```bash
pip install mcp
```

## Usage

### With Claude Desktop

Add to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["/path/to/calculator-mcp/calculator_server.py"]
    }
  }
}
```

Restart Claude Desktop, then ask Claude to perform calculations!

### With Cursor IDE

Add to your Cursor MCP configuration (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["/path/to/calculator-mcp/calculator_server.py"]
    }
  }
}
```

### Standalone Testing

```bash
python calculator_server.py
```

The server communicates via stdio (standard input/output) using the MCP protocol.

## Development

### Setup development environment

```bash
# Clone the repository
git clone https://github.com/Sathiya-Moorthi/MCP.git
cd calculator-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Project Structure

```
calculator-mcp/
├── calculator_server.py    # Main MCP server implementation
├── pyproject.toml          # Project configuration
├── tests/
│   └── test_calculator.py  # Unit tests
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI
├── README.md
├── LICENSE
└── .gitignore
```

## How It Works

This server uses **FastMCP**, a high-level API from the official MCP Python SDK:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

Key concepts:
- **`@mcp.tool()` decorator** - Registers functions as MCP tools
- **Type hints** - Define parameter types for validation
- **Docstrings** - Become tool descriptions visible to AI
- **`mcp.run()`** - Starts the server with stdio transport

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- [Anthropic](https://www.anthropic.com/) for the MCP protocol
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
