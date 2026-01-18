"""
Calculator MCP Server
=====================

This is a simple MCP (Model Context Protocol) server that exposes calculator
operations as tools that AI assistants like Claude can use.

WHAT IS MCP?
------------
MCP (Model Context Protocol) is an open protocol developed by Anthropic that
allows AI assistants to interact with external tools, data sources, and services.
Think of it as a standardized way for AI to "plug in" to your applications.

An MCP server can expose three types of capabilities:
1. TOOLS   - Functions the AI can call (like our calculator operations)
2. RESOURCES - Data/content the AI can read (files, database records, etc.)
3. PROMPTS   - Pre-defined prompt templates for common tasks

HOW THIS SERVER WORKS:
---------------------
1. We use FastMCP - a simplified API from the official MCP Python SDK
2. Each calculator operation is decorated with @mcp.tool()
3. Type hints (float, int) tell MCP what parameters to expect
4. Docstrings become the tool descriptions that AI sees
5. The server communicates via stdio (standard input/output)

USAGE:
------
1. Install: pip install mcp
2. Run: python calculator_server.py
3. Or configure in Claude Desktop (see README)
"""

import math
from mcp.server.fastmcp import FastMCP

# =============================================================================
# CREATING THE MCP SERVER
# =============================================================================
# FastMCP is a high-level API that simplifies MCP server creation.
# The 'name' parameter identifies your server to clients.

mcp = FastMCP(name="calculator")

# =============================================================================
# DEFINING TOOLS
# =============================================================================
# Tools are functions that AI can call. We use the @mcp.tool() decorator
# to register each function as an MCP tool.
#
# KEY CONCEPTS:
# - The function name becomes the tool name
# - Type hints define parameter types (crucial for validation)
# - The docstring becomes the tool description (AI reads this!)
# - Return value is sent back to the AI

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Add two numbers together.

    Args:
        a: The first number
        b: The second number

    Returns:
        The sum of a and b

    Example: add(5, 3) returns 8
    """
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """
    Subtract the second number from the first.

    Args:
        a: The number to subtract from
        b: The number to subtract

    Returns:
        The difference (a - b)

    Example: subtract(10, 4) returns 6
    """
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a: The first number
        b: The second number

    Returns:
        The product of a and b

    Example: multiply(6, 7) returns 42
    """
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Divide the first number by the second.

    Args:
        a: The dividend (number to be divided)
        b: The divisor (number to divide by)

    Returns:
        The quotient (a / b)

    Raises:
        ValueError: If b is zero (division by zero is undefined)

    Example: divide(15, 3) returns 5.0
    """
    # Error handling is important! Always validate inputs.
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """
    Raise a number to a power (exponentiation).

    Args:
        base: The base number
        exponent: The power to raise the base to

    Returns:
        base raised to the power of exponent

    Example: power(2, 3) returns 8.0 (2^3 = 8)
    """
    return math.pow(base, exponent)


@mcp.tool()
def modulo(a: float, b: float) -> float:
    """
    Calculate the remainder of division (modulo operation).

    Args:
        a: The dividend
        b: The divisor

    Returns:
        The remainder when a is divided by b

    Raises:
        ValueError: If b is zero

    Example: modulo(17, 5) returns 2.0 (17 = 5*3 + 2)
    """
    if b == 0:
        raise ValueError("Cannot perform modulo with zero divisor")
    return a % b


@mcp.tool()
def square_root(number: float) -> float:
    """
    Calculate the square root of a number.

    Args:
        number: The number to find the square root of (must be non-negative)

    Returns:
        The square root of the number

    Raises:
        ValueError: If number is negative (no real square root)

    Example: square_root(16) returns 4.0
    """
    if number < 0:
        raise ValueError("Cannot calculate square root of a negative number")
    return math.sqrt(number)


# =============================================================================
# BONUS: Additional useful operations
# =============================================================================

@mcp.tool()
def absolute(number: float) -> float:
    """
    Get the absolute (non-negative) value of a number.

    Args:
        number: Any number

    Returns:
        The absolute value (distance from zero)

    Example: absolute(-5) returns 5.0
    """
    return abs(number)


@mcp.tool()
def percentage(value: float, percent: float) -> float:
    """
    Calculate a percentage of a value.

    Args:
        value: The base value
        percent: The percentage to calculate (e.g., 25 for 25%)

    Returns:
        The percentage of the value

    Example: percentage(200, 15) returns 30.0 (15% of 200)
    """
    return (value * percent) / 100


# =============================================================================
# RUNNING THE SERVER
# =============================================================================
# When this file is run directly, start the MCP server.
# The server uses stdio transport - it reads from stdin and writes to stdout.
# This is how Claude Desktop and other MCP clients communicate with it.

if __name__ == "__main__":
    # mcp.run() starts the server and handles the MCP protocol
    # It will:
    # 1. Listen for incoming requests on stdin
    # 2. Process tool calls and return results on stdout
    # 3. Handle the MCP handshake and protocol negotiation
    mcp.run()
