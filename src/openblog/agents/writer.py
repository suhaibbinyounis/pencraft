"""Writer agent for generating blog content."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from openblog.agents.base import AgentResult, BaseAgent
from openblog.agents.planner import BlogOutline, Section
from openblog.llm.prompts import (
    CONCLUSION_PROMPT,
    INTRODUCTION_PROMPT,
    SECTION_PROMPT,
)

if TYPE_CHECKING:
    from openblog.config.settings import Settings
    from openblog.llm.client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class BlogPost:
    """A complete blog post."""

    title: str
    content: str
    meta_description: str = ""
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    word_count: int = 0
    sections: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "meta_description": self.meta_description,
            "tags": self.tags,
            "categories": self.categories,
            "sources": self.sources,
            "word_count": self.word_count,
        }


class WriterAgent(BaseAgent):
    """Agent for writing blog post content.

    Takes outlines and research data to generate
    complete, well-formatted blog posts.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        settings: Settings | None = None,
    ) -> None:
        """Initialize the writer agent.

        Args:
            llm_client: LLM client for AI operations.
            settings: Settings object.
        """
        super().__init__(llm_client, settings, name="WriterAgent")

    def execute(
        self,
        outline: BlogOutline,
        research_summary: str,
        *,
        sources: list[dict[str, Any]] | None = None,
        style_notes: str = "",
    ) -> AgentResult:
        """Write a complete blog post.

        Args:
            outline: Blog outline to follow.
            research_summary: Research data to incorporate.
            sources: Source citations to include.
            style_notes: Additional style guidance.

        Returns:
            AgentResult with BlogPost in metadata.
        """
        try:
            self.log(f"Writing blog post: {outline.title}")

            sources = sources or []
            sections: dict[str, str] = {}
            content_parts: list[str] = []

            # Calculate words per section
            num_sections = len(outline.sections) + 2  # +2 for intro/conclusion
            words_per_section = outline.target_word_count // num_sections

            # Write introduction
            self.log("Writing introduction...")
            intro = self._write_introduction(outline, words_per_section)
            sections["introduction"] = intro
            content_parts.append(intro)

            # Write each section
            previous_content = intro
            for i, section in enumerate(outline.sections):
                self.log(f"Writing section {i + 1}/{len(outline.sections)}: {section.title}")

                section_content = self._write_section(
                    outline=outline,
                    section=section,
                    research_summary=research_summary,
                    previous_content=previous_content,
                    target_words=words_per_section,
                )

                sections[section.title] = section_content
                content_parts.append(f"\n## {section.title}\n\n{section_content}")
                previous_content += section_content

            # Write conclusion
            self.log("Writing conclusion...")
            conclusion = self._write_conclusion(outline, content_parts)
            sections["conclusion"] = conclusion
            content_parts.append(f"\n## Conclusion\n\n{conclusion}")

            # Add sources/references if citations are enabled
            if self.settings.blog.include_citations and sources:
                references = self._format_references(sources)
                content_parts.append(f"\n## References\n\n{references}")

            # Combine all content
            full_content = "\n".join(content_parts)
            word_count = len(full_content.split())

            # Create blog post object
            blog_post = BlogPost(
                title=outline.title,
                content=full_content,
                meta_description=outline.meta_description,
                tags=outline.tags,
                categories=outline.categories,
                sources=sources,
                word_count=word_count,
                sections=sections,
            )

            self.log(f"Blog post complete: {word_count} words")

            return AgentResult(
                success=True,
                content=full_content,
                metadata={"blog_post": blog_post.to_dict()},
            )

        except Exception as e:
            return self._handle_error(e, "Writing failed")

    async def aexecute(
        self,
        outline: BlogOutline,
        research_summary: str,
        *,
        sources: list[dict[str, Any]] | None = None,
        style_notes: str = "",
    ) -> AgentResult:
        """Write a complete blog post asynchronously.

        Args:
            outline: Blog outline to follow.
            research_summary: Research data to incorporate.
            sources: Source citations to include.
            style_notes: Additional style guidance.

        Returns:
            AgentResult with BlogPost in metadata.
        """
        try:
            self.log(f"Writing blog post async: {outline.title}")

            sources = sources or []
            sections: dict[str, str] = {}
            content_parts: list[str] = []

            num_sections = len(outline.sections) + 2
            words_per_section = outline.target_word_count // num_sections

            # Write introduction
            intro = await self._awrite_introduction(outline, words_per_section)
            sections["introduction"] = intro
            content_parts.append(intro)

            # Write each section
            previous_content = intro
            for section in outline.sections:
                section_content = await self._awrite_section(
                    outline=outline,
                    section=section,
                    research_summary=research_summary,
                    previous_content=previous_content,
                    target_words=words_per_section,
                )

                sections[section.title] = section_content
                content_parts.append(f"\n## {section.title}\n\n{section_content}")
                previous_content += section_content

            # Write conclusion
            conclusion = await self._awrite_conclusion(outline, content_parts)
            sections["conclusion"] = conclusion
            content_parts.append(f"\n## Conclusion\n\n{conclusion}")

            # Add references
            if self.settings.blog.include_citations and sources:
                references = self._format_references(sources)
                content_parts.append(f"\n## References\n\n{references}")

            full_content = "\n".join(content_parts)
            word_count = len(full_content.split())

            blog_post = BlogPost(
                title=outline.title,
                content=full_content,
                meta_description=outline.meta_description,
                tags=outline.tags,
                categories=outline.categories,
                sources=sources,
                word_count=word_count,
                sections=sections,
            )

            return AgentResult(
                success=True,
                content=full_content,
                metadata={"blog_post": blog_post.to_dict()},
            )

        except Exception as e:
            return self._handle_error(e, "Async writing failed")

    def _write_introduction(self, outline: BlogOutline, target_words: int) -> str:
        """Write the introduction section.

        Args:
            outline: Blog outline.
            target_words: Target word count.

        Returns:
            Introduction content.
        """
        outline_summary = "\n".join(
            f"- {s.title}: {', '.join(s.key_points[:3])}" for s in outline.sections
        )

        prompt = INTRODUCTION_PROMPT.format(
            title=outline.title,
            topic=outline.title,
            outline=outline_summary,
        )

        return self._generate(
            prompt,
            system_prompt=self.settings.prompts.writer_system,
        )

    async def _awrite_introduction(self, outline: BlogOutline, target_words: int) -> str:
        """Write introduction asynchronously."""
        outline_summary = "\n".join(
            f"- {s.title}: {', '.join(s.key_points[:3])}" for s in outline.sections
        )

        prompt = INTRODUCTION_PROMPT.format(
            title=outline.title,
            topic=outline.title,
            outline=outline_summary,
        )

        return await self._agenerate(
            prompt,
            system_prompt=self.settings.prompts.writer_system,
        )

    def _write_section(
        self,
        outline: BlogOutline,
        section: Section,
        research_summary: str,
        previous_content: str,
        target_words: int,
    ) -> str:
        """Write a single section.

        Args:
            outline: Full blog outline.
            section: Section to write.
            research_summary: Research data.
            previous_content: Previously written content.
            target_words: Target word count.

        Returns:
            Section content.
        """
        section_outline = "\n".join(
            [f"Key points: {', '.join(section.key_points)}"]
            + [f"  - Subsection: {sub.title}" for sub in section.subsections]
        )

        # Truncate previous content to avoid token limits
        prev_summary = previous_content[-1500:] if len(previous_content) > 1500 else previous_content

        prompt = SECTION_PROMPT.format(
            title=outline.title,
            section_title=section.title,
            section_outline=section_outline,
            previous_content=prev_summary,
            research_notes=research_summary[:2000],
            word_count=target_words,
        )

        return self._generate(
            prompt,
            system_prompt=self.settings.prompts.writer_system,
        )

    async def _awrite_section(
        self,
        outline: BlogOutline,
        section: Section,
        research_summary: str,
        previous_content: str,
        target_words: int,
    ) -> str:
        """Write a section asynchronously."""
        section_outline = "\n".join(
            [f"Key points: {', '.join(section.key_points)}"]
            + [f"  - Subsection: {sub.title}" for sub in section.subsections]
        )

        prev_summary = previous_content[-1500:] if len(previous_content) > 1500 else previous_content

        prompt = SECTION_PROMPT.format(
            title=outline.title,
            section_title=section.title,
            section_outline=section_outline,
            previous_content=prev_summary,
            research_notes=research_summary[:2000],
            word_count=target_words,
        )

        return await self._agenerate(
            prompt,
            system_prompt=self.settings.prompts.writer_system,
        )

    def _write_conclusion(self, outline: BlogOutline, content_parts: list[str]) -> str:
        """Write the conclusion.

        Args:
            outline: Blog outline.
            content_parts: Written content parts.

        Returns:
            Conclusion content.
        """
        # Extract main points from sections
        main_points = "\n".join(f"- {s.title}" for s in outline.sections)

        prompt = CONCLUSION_PROMPT.format(
            title=outline.title,
            topic=outline.title,
            main_points=main_points,
        )

        return self._generate(
            prompt,
            system_prompt=self.settings.prompts.writer_system,
        )

    async def _awrite_conclusion(self, outline: BlogOutline, content_parts: list[str]) -> str:
        """Write conclusion asynchronously."""
        main_points = "\n".join(f"- {s.title}" for s in outline.sections)

        prompt = CONCLUSION_PROMPT.format(
            title=outline.title,
            topic=outline.title,
            main_points=main_points,
        )

        return await self._agenerate(
            prompt,
            system_prompt=self.settings.prompts.writer_system,
        )

    def _format_references(self, sources: list[dict[str, Any]]) -> str:
        """Format sources as references section.

        Args:
            sources: List of source dictionaries.

        Returns:
            Formatted references markdown.
        """
        if not sources:
            return ""

        references = []
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Untitled")
            url = source.get("url", "")
            description = source.get("description", "")

            ref_line = f"{i}. [{title}]({url})"
            if description:
                ref_line += f" - {description[:100]}..."

            references.append(ref_line)

        return "\n".join(references)

    def write_section_only(
        self,
        section_title: str,
        key_points: list[str],
        context: str,
        target_words: int = 500,
    ) -> str:
        """Write a single standalone section.

        Args:
            section_title: Title of the section.
            key_points: Points to cover.
            context: Context for the section.
            target_words: Target word count.

        Returns:
            Section content.
        """
        prompt = f"""Write a detailed blog section with the following details:

**Section Title:** {section_title}

**Key Points to Cover:**
{chr(10).join(f'- {p}' for p in key_points)}

**Context:**
{context}

**Target Length:** {target_words} words

Write engaging, informative content using proper markdown formatting."""

        return self._generate(
            prompt,
            system_prompt=self.settings.prompts.writer_system,
        )
