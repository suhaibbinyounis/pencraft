"""Tests for formatters."""

import pytest

from openblog.formatters.citations import Citation, CitationFormatter
from openblog.formatters.frontmatter import FrontmatterGenerator
from openblog.formatters.markdown import MarkdownFormatter


class TestMarkdownFormatter:
    """Test cases for MarkdownFormatter."""

    def test_heading(self) -> None:
        """Test heading generation."""
        assert MarkdownFormatter.heading("Test", 1) == "# Test"
        assert MarkdownFormatter.heading("Test", 2) == "## Test"
        assert MarkdownFormatter.heading("Test", 3) == "### Test"

    def test_bold_italic(self) -> None:
        """Test bold and italic formatting."""
        assert MarkdownFormatter.bold("text") == "**text**"
        assert MarkdownFormatter.italic("text") == "*text*"

    def test_code(self) -> None:
        """Test code formatting."""
        assert MarkdownFormatter.code("print()") == "`print()`"
        assert "```python" in MarkdownFormatter.code_block("x = 1", "python")

    def test_link(self) -> None:
        """Test link generation."""
        assert MarkdownFormatter.link("text", "url") == "[text](url)"
        assert MarkdownFormatter.link("text", "url", "title") == '[text](url "title")'

    def test_image(self) -> None:
        """Test image generation."""
        assert MarkdownFormatter.image("alt", "url") == "![alt](url)"

    def test_blockquote(self) -> None:
        """Test blockquote generation."""
        assert MarkdownFormatter.blockquote("quote") == "> quote"

    def test_lists(self) -> None:
        """Test list generation."""
        assert "- a\n- b" in MarkdownFormatter.unordered_list(["a", "b"])
        assert "1. a\n2. b" in MarkdownFormatter.ordered_list(["a", "b"])

    def test_table(self) -> None:
        """Test table generation."""
        table = MarkdownFormatter.table(["A", "B"], [["1", "2"]])
        assert "| A | B |" in table
        assert "| 1 | 2 |" in table

    def test_slugify(self) -> None:
        """Test slugification."""
        assert MarkdownFormatter.slugify("Hello World") == "hello-world"
        assert MarkdownFormatter.slugify("Test!@#$%") == "test"
        assert MarkdownFormatter.slugify("  Multiple   Spaces  ") == "multiple-spaces"

    def test_extract_headings(self) -> None:
        """Test heading extraction."""
        content = "# Title\n## Section 1\n### Subsection\n## Section 2"
        headings = MarkdownFormatter.extract_headings(content)

        assert len(headings) == 4
        assert headings[0]["text"] == "Title"
        assert headings[0]["level"] == 1

    def test_generate_toc(self) -> None:
        """Test TOC generation."""
        content = "# Title\n## Section 1\n## Section 2"
        toc = MarkdownFormatter.generate_toc(content)

        assert "Table of Contents" in toc
        assert "[Title](#title)" in toc


class TestFrontmatterGenerator:
    """Test cases for FrontmatterGenerator."""

    def test_yaml_format(self) -> None:
        """Test YAML frontmatter generation."""
        gen = FrontmatterGenerator(format="yaml")
        fm = gen.generate(title="Test Post", description="Test")

        assert fm.startswith("---")
        assert "title: Test Post" in fm
        assert fm.strip().endswith("---")

    def test_toml_format(self) -> None:
        """Test TOML frontmatter generation."""
        gen = FrontmatterGenerator(format="toml")
        fm = gen.generate(title="Test Post")

        assert fm.startswith("+++")
        assert 'title = "Test Post"' in fm

    def test_with_tags_and_categories(self) -> None:
        """Test frontmatter with tags and categories."""
        gen = FrontmatterGenerator()
        fm = gen.generate(
            title="Test",
            tags=["python", "tutorial"],
            categories=["Programming"],
        )

        assert "tags:" in fm
        assert "python" in fm
        assert "categories:" in fm

    def test_parse_yaml(self) -> None:
        """Test YAML parsing."""
        gen = FrontmatterGenerator()
        content = """---
title: Test
tags:
  - python
---
Body content"""

        fm, body = gen.parse(content)

        assert fm["title"] == "Test"
        assert "python" in fm["tags"]
        assert body == "Body content"


class TestCitationFormatter:
    """Test cases for CitationFormatter."""

    def test_add_citation(self) -> None:
        """Test adding citations."""
        formatter = CitationFormatter()
        ref = formatter.add_citation(Citation(title="Test", url="http://test.com"))

        assert ref == 1
        assert len(formatter.citations) == 1

    def test_markdown_style(self) -> None:
        """Test markdown citation style."""
        formatter = CitationFormatter(style="markdown")
        formatter.add_citation(Citation(title="Test", url="http://test.com"))

        inline = formatter.get_inline_reference(1)
        assert inline == "[^1]"

    def test_references_section(self) -> None:
        """Test references section generation."""
        formatter = CitationFormatter()
        formatter.add_citation(Citation(title="Source 1", url="http://a.com"))
        formatter.add_citation(Citation(title="Source 2", url="http://b.com"))

        refs = formatter.generate_references_section()

        assert "References" in refs
        assert "Source 1" in refs
        assert "Source 2" in refs

    def test_from_sources(self) -> None:
        """Test creating formatter from sources list."""
        sources = [
            {"title": "A", "url": "http://a.com"},
            {"title": "B", "url": "http://b.com"},
        ]

        formatter = CitationFormatter.from_sources(sources)

        assert len(formatter.citations) == 2
