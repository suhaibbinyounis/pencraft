<div align="center">

# 🚀 OpenBlog

**AI-powered blog writing toolkit that automates research, planning, and content creation**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/suhaibbinyounis/openblog/actions/workflows/ci.yml/badge.svg)](https://github.com/suhaibbinyounis/openblog/actions/workflows/ci.yml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Configuration](#%EF%B8%8F-configuration) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Automated Research** | Gathers information from the web with source citations |
| 📝 **Smart Outlining** | Creates structured, SEO-optimized blog outlines |
| ✍️ **AI Content Generation** | Generates detailed content section by section |
| 📄 **Hugo Compatible** | Outputs markdown with YAML/TOML/JSON frontmatter |
| ⚙️ **Fully Configurable** | Custom API endpoints, models, prompts, and more |
| 🔌 **OpenAI Compatible** | Works with any OpenAI-compatible API (local or cloud) |
| 🎨 **Beautiful CLI** | Rich terminal output with progress indicators |

## 📦 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/suhaibbinyounis/openblog.git
cd openblog

# Install the package
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### From PyPI (Coming Soon)

```bash
pip install openblog
```

## 🚀 Quick Start

### CLI Usage

```bash
# Generate a complete blog post
openblog write "Introduction to Machine Learning" --words 2500 --output ./blogs

# Research a topic only
openblog research "AI in Healthcare"

# Generate an outline only
openblog outline "Getting Started with Docker"

# View current configuration
openblog config --show

# Create a config file
openblog config --init
```

### Python API

```python
from openblog import Settings
from openblog.generator import BlogGenerator

# Create generator with custom settings
generator = BlogGenerator(settings=Settings(
    llm={"base_url": "http://localhost:3030/v1", "api_key": "your-key"}
))

# Generate a blog post
blog = generator.generate(
    topic="Introduction to Python",
    target_word_count=2000,
    tags=["python", "programming"],
    output_dir="./output"
)

print(f"Generated: {blog.title} ({blog.word_count} words)")
print(f"Saved to: {blog.file_path}")
```

## ⚙️ Configuration

OpenBlog supports multiple configuration methods:

### 1. Environment Variables

```bash
export OPENBLOG_LLM__BASE_URL="http://localhost:3030/v1"
export OPENBLOG_LLM__API_KEY="your-api-key"
export OPENBLOG_LLM__MODEL="gpt-4"
```

### 2. Configuration File

Create `openblog.yaml`:

```yaml
llm:
  base_url: "http://localhost:3030/v1"
  api_key: "your-api-key"
  model: "gpt-4"
  temperature: 0.7

blog:
  min_word_count: 1500
  include_toc: true
  include_citations: true

hugo:
  frontmatter_format: "yaml"
```

Use with: `openblog write "Topic" --config openblog.yaml`

### LLM Provider Setup

<details>
<summary><b>LM Studio</b></summary>

1. Download [LM Studio](https://lmstudio.ai/)
2. Load a model and start the local server
3. Configure: `base_url: "http://localhost:1234/v1"`
</details>

<details>
<summary><b>Ollama</b></summary>

1. Install [Ollama](https://ollama.ai/)
2. Run: `ollama run llama2`
3. Configure: `base_url: "http://localhost:11434/v1"`
</details>

<details>
<summary><b>OpenAI</b></summary>

```yaml
llm:
  base_url: "https://api.openai.com/v1"
  api_key: "sk-your-key"
  model: "gpt-4"
```
</details>

## 📖 Documentation

### Project Structure

```
openblog/
├── src/openblog/
│   ├── agents/         # AI agents (research, planner, writer)
│   ├── config/         # Configuration management
│   ├── formatters/     # Markdown, frontmatter, citations
│   ├── llm/            # OpenAI-compatible client
│   ├── tools/          # DuckDuckGo search, web scraper
│   ├── cli.py          # CLI interface
│   └── generator.py    # Main orchestrator
├── tests/              # Unit tests
├── examples/           # Usage examples
└── pyproject.toml      # Project configuration
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `openblog write <topic>` | Generate a complete blog post |
| `openblog research <topic>` | Research a topic only |
| `openblog outline <topic>` | Create a blog outline |
| `openblog config --show` | Display current settings |
| `openblog config --init` | Create a config file |

### Output Example

Generated blogs include proper Hugo frontmatter:

```markdown
---
title: "Introduction to Machine Learning"
date: 2024-01-15T10:30:00+00:00
draft: false
tags: ["machine-learning", "ai", "tutorial"]
categories: ["Technology"]
toc: true
author: "OpenBlog"
---

# Introduction to Machine Learning

## Table of Contents
- [What is Machine Learning?](#what-is-machine-learning)
- [Types of Machine Learning](#types-of-machine-learning)
...

## What is Machine Learning?

Machine learning is a subset of artificial intelligence...

## References

1. [Machine Learning Basics](https://example.com) - Official documentation
```

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check src/ tests/
ruff format src/ tests/

# Type checking
mypy src/
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com) for AI orchestration
- CLI powered by [Typer](https://typer.tiangolo.com) and [Rich](https://rich.readthedocs.io)
- Web search via [DuckDuckGo](https://duckduckgo.com)

---

<div align="center">

**[⬆ Back to Top](#-openblog)**

Made with ❤️ by [Suhaib Bin Younis](https://github.com/suhaibbinyounis)

</div>
