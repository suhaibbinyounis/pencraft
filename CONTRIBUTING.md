# Contributing to OpenBlog

First off, thank you for considering contributing to OpenBlog! It's people like you that make OpenBlog such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (config files, commands used)
- **Describe the behavior you observed and what you expected**
- **Include your environment details** (OS, Python version, OpenBlog version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the proposed enhancement**
- **Explain why this enhancement would be useful**
- **List any alternatives you've considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```
3. **Make your changes** and add tests if applicable
4. **Run the test suite:**
   ```bash
   pytest tests/ -v
   ```
5. **Run linting:**
   ```bash
   ruff check src/
   ruff format src/
   mypy src/
   ```
6. **Commit your changes** using conventional commits
7. **Push to your fork** and submit a pull request

## Development Setup

### Prerequisites

- Python 3.10+
- pip or Poetry

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/openblog.git
cd openblog

# Install in development mode
pip install -e ".[dev]"

# Or with Poetry
poetry install
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/openblog --cov-report=html

# Run specific test file
pytest tests/unit/test_settings.py -v
```

### Code Style

We use:
- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Google-style docstrings**

```bash
# Format code
ruff format src/ tests/

# Check linting
ruff check src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
openblog/
├── src/openblog/
│   ├── agents/       # AI agents (research, planner, writer)
│   ├── config/       # Configuration management
│   ├── formatters/   # Output formatters (markdown, frontmatter)
│   ├── llm/          # LLM client and prompts
│   ├── tools/        # Tools (search, scraper)
│   └── utils/        # Utilities (logging)
├── tests/
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
└── examples/         # Usage examples
```

## Commit Messages

We follow [Conventional Commits](https://conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Example: `feat: add support for TOML frontmatter`

## Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

Thank you for contributing! 🎉
