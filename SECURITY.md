# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability within OpenBlog, please follow these steps:

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Email your findings to [suhaib@suhaib.in](mailto:suhaib@suhaib.in)
3. Include detailed steps to reproduce the vulnerability
4. Allow up to 48 hours for an initial response

### What to include in your report

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

### What to expect

- Acknowledgment of your report within 48 hours
- Regular updates on the progress
- Credit in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices for Users

When using OpenBlog:

1. **API Keys**: Never commit API keys to version control
2. **Local LLM**: Consider using local LLM endpoints for sensitive content
3. **Output Review**: Always review AI-generated content before publishing
4. **Dependencies**: Keep dependencies updated with `pip install --upgrade`

Thank you for helping keep OpenBlog and its users safe!
