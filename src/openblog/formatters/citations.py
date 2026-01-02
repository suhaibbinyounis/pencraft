"""Citation formatting for blog posts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Citation:
    """A single citation/source."""

    title: str
    url: str
    author: str = ""
    date: str = ""
    publisher: str = ""
    description: str = ""
    accessed: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "author": self.author,
            "date": self.date,
            "publisher": self.publisher,
            "description": self.description,
            "accessed": self.accessed,
        }


class CitationFormatter:
    """Formatter for citations and references.

    Supports multiple citation styles and formats.
    """

    def __init__(self, style: str = "markdown") -> None:
        """Initialize the citation formatter.

        Args:
            style: Citation style (markdown, apa, mla, chicago).
        """
        self.style = style.lower()
        self._citations: list[Citation] = []
        self._citation_counter = 0

    def add_citation(self, citation: Citation | dict[str, Any]) -> int:
        """Add a citation and return its reference number.

        Args:
            citation: Citation object or dictionary.

        Returns:
            Reference number for the citation.
        """
        if isinstance(citation, dict):
            citation = Citation(**citation)

        self._citations.append(citation)
        self._citation_counter += 1
        return self._citation_counter

    def add_citations(self, citations: list[Citation | dict[str, Any]]) -> list[int]:
        """Add multiple citations.

        Args:
            citations: List of citations.

        Returns:
            List of reference numbers.
        """
        return [self.add_citation(c) for c in citations]

    def get_inline_reference(self, ref_num: int) -> str:
        """Get inline reference for a citation.

        Args:
            ref_num: Reference number.

        Returns:
            Inline reference markdown.
        """
        if self.style == "markdown":
            return f"[^{ref_num}]"
        elif self.style == "numbered":
            return f"[{ref_num}]"
        else:
            # Default to superscript style
            return f"<sup>{ref_num}</sup>"

    def format_citation(self, citation: Citation, ref_num: int) -> str:
        """Format a single citation.

        Args:
            citation: Citation to format.
            ref_num: Reference number.

        Returns:
            Formatted citation string.
        """
        if self.style == "markdown":
            return self._format_markdown(citation, ref_num)
        elif self.style == "apa":
            return self._format_apa(citation, ref_num)
        elif self.style == "mla":
            return self._format_mla(citation, ref_num)
        elif self.style == "chicago":
            return self._format_chicago(citation, ref_num)
        else:
            return self._format_markdown(citation, ref_num)

    def _format_markdown(self, citation: Citation, ref_num: int) -> str:
        """Format citation in markdown footnote style.

        Args:
            citation: Citation to format.
            ref_num: Reference number.

        Returns:
            Markdown footnote definition.
        """
        parts = [f"[^{ref_num}]: [{citation.title}]({citation.url})"]

        if citation.author:
            parts.append(f" by {citation.author}")
        if citation.publisher:
            parts.append(f" ({citation.publisher})")
        if citation.date:
            parts.append(f", {citation.date}")

        parts.append(f". Accessed {citation.accessed}.")

        return "".join(parts)

    def _format_apa(self, citation: Citation, ref_num: int) -> str:
        """Format citation in APA style.

        Args:
            citation: Citation to format.
            ref_num: Reference number.

        Returns:
            APA-formatted citation.
        """
        parts = []

        if citation.author:
            parts.append(citation.author)
        else:
            parts.append(citation.title)

        if citation.date:
            parts.append(f"({citation.date})")
        else:
            parts.append("(n.d.)")

        if citation.author:
            parts.append(f"*{citation.title}*")

        if citation.publisher:
            parts.append(f"{citation.publisher}.")

        parts.append(f"Retrieved from {citation.url}")

        return f"{ref_num}. " + " ".join(parts)

    def _format_mla(self, citation: Citation, ref_num: int) -> str:
        """Format citation in MLA style.

        Args:
            citation: Citation to format.
            ref_num: Reference number.

        Returns:
            MLA-formatted citation.
        """
        parts = []

        if citation.author:
            parts.append(f"{citation.author}.")

        parts.append(f'"{citation.title}."')

        if citation.publisher:
            parts.append(f"*{citation.publisher}*,")

        if citation.date:
            parts.append(f"{citation.date}.")

        parts.append(f"{citation.url}.")
        parts.append(f"Accessed {citation.accessed}.")

        return f"{ref_num}. " + " ".join(parts)

    def _format_chicago(self, citation: Citation, ref_num: int) -> str:
        """Format citation in Chicago style.

        Args:
            citation: Citation to format.
            ref_num: Reference number.

        Returns:
            Chicago-formatted citation.
        """
        parts = []

        if citation.author:
            parts.append(f"{citation.author},")

        parts.append(f'"{citation.title},"')

        if citation.publisher:
            parts.append(f"{citation.publisher},")

        if citation.date:
            parts.append(f"{citation.date},")

        parts.append(f"{citation.url}")
        parts.append(f"(accessed {citation.accessed}).")

        return f"{ref_num}. " + " ".join(parts)

    def generate_references_section(self, heading: str = "References") -> str:
        """Generate the full references section.

        Args:
            heading: Section heading.

        Returns:
            Complete references section markdown.
        """
        if not self._citations:
            return ""

        lines = [f"## {heading}", ""]

        for i, citation in enumerate(self._citations, 1):
            lines.append(self.format_citation(citation, i))
            lines.append("")

        return "\n".join(lines)

    def generate_footnotes(self) -> str:
        """Generate footnotes for markdown style.

        Returns:
            Footnotes section.
        """
        if not self._citations or self.style != "markdown":
            return ""

        lines = []
        for i, citation in enumerate(self._citations, 1):
            lines.append(self._format_markdown(citation, i))

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all citations."""
        self._citations = []
        self._citation_counter = 0

    @property
    def citations(self) -> list[Citation]:
        """Get all citations."""
        return self._citations.copy()

    @classmethod
    def from_sources(
        cls,
        sources: list[dict[str, Any]],
        style: str = "markdown",
    ) -> "CitationFormatter":
        """Create formatter from a list of source dictionaries.

        Args:
            sources: List of source dictionaries.
            style: Citation style.

        Returns:
            CitationFormatter with citations added.
        """
        formatter = cls(style=style)

        for source in sources:
            citation = Citation(
                title=source.get("title", "Untitled"),
                url=source.get("url", ""),
                author=source.get("author", ""),
                date=source.get("date", ""),
                publisher=source.get("publisher", source.get("source", "")),
                description=source.get("description", source.get("snippet", "")),
            )
            formatter.add_citation(citation)

        return formatter
