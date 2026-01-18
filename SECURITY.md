# Security Policy

## Supported Versions

The following versions of Gen-AI-Projects are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously in this project. If you discover a security vulnerability, please follow the responsible disclosure process below.

### How to Report

1. **Do NOT create a public GitHub issue** for security vulnerabilities
2. **Email the maintainer directly** with details about the vulnerability
3. Include the following information in your report:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Any suggested fixes (if available)

### What to Expect

- **Acknowledgment**: You will receive an acknowledgment within 48 hours of your report
- **Assessment**: We will assess the vulnerability and determine its severity within 7 days
- **Resolution**: Critical vulnerabilities will be addressed as quickly as possible
- **Disclosure**: Once fixed, we will coordinate with you on public disclosure timing

### Scope

The following are considered in-scope for security reports:

- Authentication/authorization vulnerabilities
- Data exposure risks
- Code injection vulnerabilities
- Dependency vulnerabilities
- Credential/API key exposure
- Insecure configurations

### Out of Scope

- Issues in third-party dependencies (report to the respective maintainers)
- Social engineering attacks
- Denial of service attacks
- Issues requiring physical access to user's device

## Security Best Practices

When using projects in this repository:

1. **Never commit credentials**: Always use environment variables or `.env` files (which are gitignored)
2. **Keep dependencies updated**: Regularly update pip packages to patch known vulnerabilities
3. **Use virtual environments**: Isolate project dependencies
4. **Review API permissions**: Only grant necessary permissions when using API keys
5. **Validate inputs**: Always sanitize user inputs in web applications

## Known Security Considerations

### API Keys and Credentials

Many projects in this repository require API keys (OpenAI, Anthropic, Neo4j, etc.). Please:

- Store credentials in `.env` files (not committed to git)
- Use `.env.example` templates provided in each project
- Rotate keys if you suspect they've been exposed

### Web Applications

For Flask and Streamlit applications:

- Run in development mode only for local testing
- Configure proper CORS settings for production
- Use HTTPS in production environments

## Acknowledgments

We appreciate the security research community's efforts in helping keep this project secure. Contributors who report valid vulnerabilities will be acknowledged (with permission) in our release notes.

---

Thank you for helping keep Gen-AI-Projects and its users safe!
