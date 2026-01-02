"""Markdown formatting utilities for OpenBlog."""

from __future__ import annotations

import re
from typing import Any


class MarkdownFormatter:
    """Utility class for markdown formatting.

    Provides methods for creating various markdown elements
    and ensures consistent formatting across the project.
    """

    @staticmethod
    def heading(text: str, level: int = 1) -> str:
        """Create a heading.

        Args:
            text: Heading text.
            level: Heading level (1-6).

        Returns:
            Markdown heading.
        """
        level = max(1, min(6, level))
        return f"{'#' * level} {text}"

    @staticmethod
    def bold(text: str) -> str:
        """Make text bold.

        Args:
            text: Text to bold.

        Returns:
            Bold markdown text.
        """
        return f"**{text}**"

    @staticmethod
    def italic(text: str) -> str:
        """Make text italic.

        Args:
            text: Text to italicize.

        Returns:
            Italic markdown text.
        """
        return f"*{text}*"

    @staticmethod
    def code(text: str) -> str:
        """Create inline code.

        Args:
            text: Code text.

        Returns:
            Inline code markdown.
        """
        return f"`{text}`"

    @staticmethod
    def code_block(code: str, language: str = "") -> str:
        """Create a fenced code block.

        Args:
            code: Code content.
            language: Programming language for syntax highlighting.

        Returns:
            Fenced code block markdown.
        """
        return f"```{language}\n{code}\n```"

    @staticmethod
    def link(text: str, url: str, title: str | None = None) -> str:
        """Create a link.

        Args:
            text: Link text.
            url: Link URL.
            title: Optional link title.

        Returns:
            Markdown link.
        """
        if title:
            return f'[{text}]({url} "{title}")'
        return f"[{text}]({url})"

    @staticmethod
    def image(alt: str, url: str, title: str | None = None) -> str:
        """Create an image.

        Args:
            alt: Alt text.
            url: Image URL.
            title: Optional image title.

        Returns:
            Markdown image.
        """
        if title:
            return f'![{alt}]({url} "{title}")'
        return f"![{alt}]({url})"

    @staticmethod
    def blockquote(text: str) -> str:
        """Create a blockquote.

        Args:
            text: Quote text.

        Returns:
            Markdown blockquote.
        """
        lines = text.split("\n")
        return "\n".join(f"> {line}" for line in lines)

    @staticmethod
    def unordered_list(items: list[str], indent: int = 0) -> str:
        """Create an unordered list.

        Args:
            items: List items.
            indent: Indentation level.

        Returns:
            Markdown unordered list.
        """
        prefix = "  " * indent
        return "\n".join(f"{prefix}- {item}" for item in items)

    @staticmethod
    def ordered_list(items: list[str], start: int = 1) -> str:
        """Create an ordered list.

        Args:
            items: List items.
            start: Starting number.

        Returns:
            Markdown ordered list.
        """
        return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start))

    @staticmethod
    def task_list(items: list[tuple[str, bool]]) -> str:
        """Create a task list.

        Args:
            items: List of (item_text, is_checked) tuples.

        Returns:
            Markdown task list.
        """
        lines = []
        for text, checked in items:
            checkbox = "[x]" if checked else "[ ]"
            lines.append(f"- {checkbox} {text}")
        return "\n".join(lines)

    @staticmethod
    def table(headers: list[str], rows: list[list[str]], alignment: list[str] | None = None) -> str:
        """Create a table.

        Args:
            headers: Column headers.
            rows: Table rows.
            alignment: Column alignment ('left', 'center', 'right').

        Returns:
            Markdown table.
        """
        if alignment is None:
            alignment = ["left"] * len(headers)

        # Header row
        header_row = "| " + " | ".join(headers) + " |"

        # Separator row with alignment
        sep_parts = []
        for align in alignment:
            if align == "center":
                sep_parts.append(":---:")
            elif align == "right":
                sep_parts.append("---:")
            else:
                sep_parts.append("---")
        separator_row = "| " + " | ".join(sep_parts) + " |"

        # Data rows
        data_rows = []
        for row in rows:
            # Pad row if needed
            padded_row = row + [""] * (len(headers) - len(row))
            data_rows.append("| " + " | ".join(padded_row[: len(headers)]) + " |")

        return "\n".join([header_row, separator_row] + data_rows)

    @staticmethod
    def horizontal_rule() -> str:
        """Create a horizontal rule.

        Returns:
            Markdown horizontal rule.
        """
        return "---"

    @staticmethod
    def footnote(id: str, text: str) -> str:
        """Create a footnote reference.

        Args:
            id: Footnote identifier.
            text: Footnote text.

        Returns:
            Markdown footnote definition.
        """
        return f"[^{id}]: {text}"

    @staticmethod
    def footnote_ref(id: str) -> str:
        """Create a footnote reference link.

        Args:
            id: Footnote identifier.

        Returns:
            Footnote reference.
        """
        return f"[^{id}]"

    @staticmethod
    def details(summary: str, content: str) -> str:
        """Create a collapsible details section (HTML in markdown).

        Args:
            summary: Summary text (visible when collapsed).
            content: Hidden content.

        Returns:
            HTML details element.
        """
        return f"<details>\n<summary>{summary}</summary>\n\n{content}\n\n</details>"

    @staticmethod
    def callout(type: str, text: str) -> str:
        """Create a callout/admonition (Hugo shortcode style).

        Args:
            type: Callout type (note, tip, warning, danger).
            text: Callout content.

        Returns:
            Callout markdown (blockquote with type prefix).
        """
        # Use GitHub-style alerts
        type_map = {
            "note": "NOTE",
            "tip": "TIP",
            "warning": "WARNING",
            "danger": "CAUTION",
            "important": "IMPORTANT",
        }
        alert_type = type_map.get(type.lower(), "NOTE")
        return f"> [!{alert_type}]\n> {text}"

    @staticmethod
    def toc_placeholder() -> str:
        """Create a table of contents placeholder.

        Returns:
            TOC placeholder for Hugo.
        """
        return "{{< toc >}}"

    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to URL-friendly slug.

        Args:
            text: Text to slugify.

        Returns:
            URL-friendly slug.
        """
        # Convert to lowercase
        slug = text.lower()
        # Replace spaces with hyphens
        slug = re.sub(r"\s+", "-", slug)
        # Remove non-alphanumeric characters except hyphens
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        # Strip leading/trailing hyphens
        slug = slug.strip("-")
        return slug

    @staticmethod
    def clean_content(content: str) -> str:
        """Clean and normalize markdown content.

        Args:
            content: Raw markdown content.

        Returns:
            Cleaned markdown content.
        """
        # Normalize line endings
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        # Remove excessive blank lines (more than 2 in a row)
        content = re.sub(r"\n{4,}", "\n\n\n", content)

        # Ensure single newline at end
        content = content.strip() + "\n"

        return content

    @staticmethod
    def extract_headings(content: str) -> list[dict[str, Any]]:
        """Extract headings from markdown content.

        Args:
            content: Markdown content.

        Returns:
            List of heading dictionaries with level, text, and slug.
        """
        headings = []
        pattern = r"^(#{1,6})\s+(.+)$"

        for match in re.finditer(pattern, content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append(
                {
                    "level": level,
                    "text": text,
                    "slug": MarkdownFormatter.slugify(text),
                }
            )

        return headings

    @classmethod
    def generate_toc(cls, content: str, max_level: int = 3) -> str:
        """Generate a table of contents from markdown content.

        Args:
            content: Markdown content.
            max_level: Maximum heading level to include.

        Returns:
            Markdown table of contents.
        """
        headings = cls.extract_headings(content)
        toc_lines = ["## Table of Contents", ""]

        for heading in headings:
            if heading["level"] > max_level:
                continue

            indent = "  " * (heading["level"] - 1)
            link = cls.link(heading["text"], f"#{heading['slug']}")
            toc_lines.append(f"{indent}- {link}")

        return "\n".join(toc_lines)
