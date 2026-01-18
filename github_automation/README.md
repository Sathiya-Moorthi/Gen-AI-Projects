# GitHub Automation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Git](https://img.shields.io/badge/Git-Required-orange.svg)](https://git-scm.com/)

Scripts for automating GitHub and Git interactions, including repository management and automated commits.

## Project Structure

```
github_automation/
├── git_automation.py                                  # Comprehensive git automation
├── push_to_github.py                                  # Helper for pushing changes
├── pushing_changes_from_local_repo_to_github_repo.py  # Local to remote sync
├── .gitignore
└── README.md
```

## Scripts Overview

| Script | Description | Use Case |
|--------|-------------|----------|
| `git_automation.py` | Full git workflow automation | Batch operations, scheduled commits |
| `push_to_github.py` | Simplified push helper | Quick pushes with messages |
| `pushing_changes_from_local_repo_to_github_repo.py` | Local-to-remote sync | Initial repo setup, bulk sync |

## Prerequisites

- Python 3.8 or higher
- Git installed and configured
- GitHub account with SSH key or Personal Access Token

## Installation

1. Navigate to this directory:
   ```bash
   cd github_automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Git credentials:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

## Usage

### Git Automation Script
```bash
python git_automation.py --repo /path/to/repo --message "Commit message"
```

### Push to GitHub
```bash
python push_to_github.py
```

### Sync Local to Remote
```bash
python pushing_changes_from_local_repo_to_github_repo.py
```

## Configuration

Create a `.env` file for sensitive configurations:

```env
GITHUB_TOKEN=your_personal_access_token
GITHUB_USERNAME=your_username
DEFAULT_BRANCH=main
```

## Security Warning

- **Never commit credentials** to version control
- Use SSH keys or Personal Access Tokens (PAT)
- Store tokens in environment variables
- Rotate tokens regularly
- Use tokens with minimum required permissions

### Recommended Token Scopes

| Scope | Permission |
|-------|------------|
| `repo` | Full repository access |
| `workflow` | GitHub Actions (if needed) |

## Best Practices

1. Always review changes before automated commits
2. Use meaningful commit messages
3. Test scripts on non-critical repositories first
4. Set up branch protection rules on important branches

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.
