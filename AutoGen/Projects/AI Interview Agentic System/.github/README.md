# GitHub Repository Structure

This directory contains GitHub-specific configuration files for automation, templates, and best practices.

## Structure

```
.github/
├── workflows/
│   └── ci.yml              # CI/CD pipeline for automated testing and builds
├── ISSUE_TEMPLATE/
│   ├── bug_report.md       # Template for bug reports
│   └── feature_request.md  # Template for feature requests
├── PULL_REQUEST_TEMPLATE.md # Template for pull requests
├── dependabot.yml          # Automated dependency updates
├── CODEOWNERS              # Code ownership rules
└── README.md               # This file
```

## Workflows

### CI/CD Pipeline (`workflows/ci.yml`)

Automated pipeline that runs on every push and pull request:

- **Backend Tests**: Python linting, unit tests, and coverage
- **Frontend Tests**: Node.js linting, build, and tests
- **Docker Build**: Validates Docker images build correctly
- **Security Scan**: Trivy vulnerability scanning

## Issue Templates

Standardized templates for:
- Bug reports with structured information
- Feature requests with use cases

## Pull Request Template

Structured PR template ensuring:
- Clear descriptions
- Type of change classification
- Testing verification
- Checklist completion

## Automation

- **Dependabot**: Weekly dependency updates for Python, Node.js, Docker, and GitHub Actions
- **Code Owners**: Automatic review requests for specific directories

## Best Practices

1. All PRs must pass CI checks
2. Use issue templates for bug reports and features
3. Follow conventional commits
4. Keep PRs focused and well-documented
5. Update documentation with code changes

