"""Visual output utilities for context engineering demos."""

from colorama import init, Fore, Back, Style
from typing import Dict, List, Any

# Initialize colorama for Windows support
init(autoreset=True)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(80)}{Style.RESET_ALL}")
    print("=" * 80 + "\n")


def print_section(title: str):
    """Print a formatted section title."""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{'-' * 80}")
    print(f"{title}")
    print(f"{'-' * 80}{Style.RESET_ALL}\n")


def visualize_tokens(used_tokens: int, max_tokens: int, label: str = "Context Usage"):
    """
    Visualize token usage with a progress bar.

    Args:
        used_tokens: Number of tokens used
        max_tokens: Maximum tokens available
        label: Label for the visualization
    """
    percentage = (used_tokens / max_tokens) * 100
    bar_length = 50
    filled_length = int(bar_length * used_tokens // max_tokens)

    # Color based on usage percentage
    if percentage < 50:
        color = Fore.GREEN
    elif percentage < 80:
        color = Fore.YELLOW
    else:
        color = Fore.RED

    bar = '#' * filled_length + '-' * (bar_length - filled_length)

    print(f"{Fore.CYAN}{label}:{Style.RESET_ALL}")
    print(f"{color}{bar}{Style.RESET_ALL} {percentage:.1f}%")
    print(f"Tokens: {used_tokens:,} / {max_tokens:,}\n")


def print_comparison(before: Dict[str, Any], after: Dict[str, Any]):
    """
    Print a before/after comparison of token usage.

    Args:
        before: Dictionary with 'tokens', 'messages' keys
        after: Dictionary with 'tokens', 'messages' keys
    """
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}COMPARISON:{Style.RESET_ALL}")
    print(f"{'-' * 80}")

    # Before
    print(f"\n{Fore.RED}BEFORE:{Style.RESET_ALL}")
    print(f"  Messages: {before.get('messages', 0)}")
    print(f"  Tokens: {before.get('tokens', 0):,}")

    # After
    print(f"\n{Fore.GREEN}AFTER:{Style.RESET_ALL}")
    print(f"  Messages: {after.get('messages', 0)}")
    print(f"  Tokens: {after.get('tokens', 0):,}")

    # Savings
    token_savings = before.get('tokens', 0) - after.get('tokens', 0)
    percentage_saved = (token_savings / before.get('tokens', 1)) * 100

    print(f"\n{Fore.CYAN}SAVINGS:{Style.RESET_ALL}")
    print(f"  Tokens Saved: {token_savings:,} ({percentage_saved:.1f}%)")
    print(f"{'-' * 80}\n")


def print_message(message: Dict[str, str], show_tokens: bool = False, model: str = "gpt-3.5-turbo"):
    """
    Print a formatted message.

    Args:
        message: Message dictionary with 'role' and 'content' keys
        show_tokens: Whether to show token count
        model: Model name for token counting
    """
    role = message.get('role', 'unknown')
    content = message.get('content', '')

    # Color based on role
    if role == 'user':
        role_color = Fore.GREEN
    elif role == 'assistant':
        role_color = Fore.BLUE
    elif role == 'system':
        role_color = Fore.MAGENTA
    else:
        role_color = Fore.WHITE

    print(f"{role_color}{Style.BRIGHT}[{role.upper()}]{Style.RESET_ALL}")
    print(f"{content}")

    if show_tokens:
        from .token_counter import count_tokens
        tokens = count_tokens(content, model)
        print(f"{Fore.CYAN}Tokens: {tokens}{Style.RESET_ALL}")

    print()


def print_messages(messages: List[Dict[str, str]], title: str = "Messages", model: str = "gpt-3.5-turbo"):
    """
    Print a list of messages with formatting.

    Args:
        messages: List of message dictionaries
        title: Title for the message list
        model: Model name for token counting
    """
    from .token_counter import estimate_tokens_for_messages

    print_section(f"{title} ({len(messages)} messages)")

    total_tokens = estimate_tokens_for_messages(messages, model)

    for i, msg in enumerate(messages, 1):
        print(f"{Fore.YELLOW}Message {i}:{Style.RESET_ALL}")
        print_message(msg, show_tokens=True, model=model)

    print(f"{Fore.CYAN}{Style.BRIGHT}Total tokens for all messages: {total_tokens:,}{Style.RESET_ALL}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{Fore.GREEN}{Style.BRIGHT}[OK] {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Fore.RED}{Style.BRIGHT}[X] {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Fore.CYAN}[i] {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Fore.YELLOW}[!] {message}{Style.RESET_ALL}")
