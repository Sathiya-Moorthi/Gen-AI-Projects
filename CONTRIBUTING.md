# Contributing to Gen-AI-Projects

Thank you for your interest in contributing to this repository! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Use a clear title** that describes the problem
3. **Provide details**: Include steps to reproduce, expected behavior, and actual behavior
4. **Include environment info**: Python version, OS, relevant package versions

### Suggesting Features

1. Open an issue with the `[Feature Request]` prefix
2. Describe the feature and its use case
3. Explain why it would benefit the project

### Submitting Code

1. **Fork** the repository
2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the code style guidelines below
4. **Test your changes** thoroughly
5. **Commit** with clear, descriptive messages:
   ```bash
   git commit -m "Add: Description of what you added"
   ```
6. **Push** to your fork and submit a **Pull Request**

## 📝 Code Style Guidelines

### Python

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Use type hints where appropriate

### Documentation

- Update README.md if your changes affect usage
- Add comments for complex logic
- Include examples for new features

### Commit Messages

Use clear, descriptive commit messages:
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for updates to existing functionality
- `Remove:` for removed features
- `Docs:` for documentation changes

## 📁 Project Structure

When adding new projects or scripts:

1. Place them in the appropriate directory
2. Include a `README.md` with:
   - Purpose and description
   - Setup instructions
   - Usage examples
   - Dependencies
3. Add a `requirements.txt` if there are dependencies
4. Update the parent directory's README if needed

## ⚠️ Important Notes

- **Never commit sensitive data** (API keys, passwords, tokens)
- Use `.env` files for secrets and add `.env` to `.gitignore`
- Provide `.env.example` files as templates
- Test your code before submitting

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve this project! 🙏
