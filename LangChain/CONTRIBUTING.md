# Contributing to LangChain Learning Repository

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Issues

- Check existing issues before creating a new one
- Use clear, descriptive titles
- Include steps to reproduce bugs
- Mention your Python version and OS

### Submitting Changes

1. **Fork** the repository
2. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** following our coding standards
4. **Test** your changes thoroughly
5. **Commit** with clear messages:
   ```bash
   git commit -m "Add: brief description of changes"
   ```
6. **Push** and create a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Add docstrings to functions and classes
- Include type hints where appropriate
- Update README files when adding features
- Add `.env.example` for any new environment variables

### Adding New Projects

When adding a new project to the `Projects/` folder:

1. Create a dedicated folder with a clear name
2. Include these files:
   - `app.py` (or main entry point)
   - `requirements.txt`
   - `.env.example`
   - `README.md` with:
     - Project description
     - Features list
     - Installation steps
     - Usage instructions
     - Dependencies

### Adding New Scripts

When adding learning notebooks to `Script/`:

1. Use descriptive notebook names
2. Include markdown cells explaining concepts
3. Add comments in code cells
4. Test all cells work with a fresh kernel

## Questions?

Open an issue with the `question` label!

---

Thank you for contributing! 🙏
