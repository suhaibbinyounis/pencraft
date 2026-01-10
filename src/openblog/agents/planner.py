"""Planner agent for creating blog outlines."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from openblog.agents.base import AgentResult, BaseAgent
from openblog.llm.prompts import OUTLINE_PROMPT

if TYPE_CHECKING:
    from openblog.config.settings import Settings
    from openblog.llm.client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class Section:
    """A section in the blog outline."""

    title: str
    key_points: list[str] = field(default_factory=list)
    subsections: list[Section] = field(default_factory=list)
    estimated_words: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "key_points": self.key_points,
            "subsections": [s.to_dict() for s in self.subsections],
            "estimated_words": self.estimated_words,
        }


@dataclass
class BlogOutline:
    """Complete blog post outline."""

    title: str
    meta_description: str
    sections: list[Section] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    target_word_count: int = 2000
    seo_keywords: list[str] = field(default_factory=list)
    layout_type: str = "deep-dive"  # deep-dive, narrative, analytical, how-to, opinion, listicle
    raw_outline: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "meta_description": self.meta_description,
            "sections": [s.to_dict() for s in self.sections],
            "tags": self.tags,
            "categories": self.categories,
            "target_word_count": self.target_word_count,
            "seo_keywords": self.seo_keywords,
            "layout_type": self.layout_type,
        }

    def to_markdown(self) -> str:
        """Convert outline to markdown format."""
        lines = [
            f"# {self.title}",
            "",
            f"**Meta Description:** {self.meta_description}",
            "",
            f"**Layout:** {self.layout_type}",
            f"**Tags:** {', '.join(self.tags)}",
            f"**Categories:** {', '.join(self.categories)}",
            f"**Target Word Count:** {self.target_word_count}",
            "",
            "## Outline",
            "",
        ]

        for i, section in enumerate(self.sections, 1):
            lines.append(f"### {i}. {section.title}")
            for point in section.key_points:
                lines.append(f"- {point}")
            for j, subsection in enumerate(section.subsections, 1):
                lines.append(f"#### {i}.{j}. {subsection.title}")
                for point in subsection.key_points:
                    lines.append(f"  - {point}")
            lines.append("")

        return "\n".join(lines)


class PlannerAgent(BaseAgent):
    """Agent for creating detailed blog post outlines.

    Takes research data and creates structured outlines
    with SEO optimization and content strategy.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        settings: Settings | None = None,
        on_progress: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize the planner agent.

        Args:
            llm_client: LLM client for AI operations.
            settings: Settings object.
            on_progress: Callback for progress updates.
        """
        super().__init__(llm_client, settings, name="PlannerAgent", on_progress=on_progress)

    def execute(
        self,
        topic: str,
        research_summary: str,
        *,
        target_word_count: int | None = None,
        suggested_tags: list[str] | None = None,
        suggested_categories: list[str] | None = None,
    ) -> AgentResult:
        """Create a blog outline from research.

        Args:
            topic: Blog topic.
            research_summary: Summary from research agent.
            target_word_count: Target word count (uses settings default if None).
            suggested_tags: Suggested tags for the post.
            suggested_categories: Suggested categories.

        Returns:
            AgentResult with BlogOutline in metadata.
        """
        try:
            self.log(f"Creating outline for: {topic}")

            word_count = target_word_count or self.settings.blog.min_word_count

            # Generate outline using LLM
            prompt = OUTLINE_PROMPT.format(
                topic=topic,
                research_summary=research_summary,
                word_count=word_count,
            )

            raw_outline = self._generate(
                prompt,
                system_prompt=self.settings.prompts.planner_system,
            )

            # Parse the outline
            outline = self._parse_outline(
                raw_outline=raw_outline,
                topic=topic,
                target_word_count=word_count,
                suggested_tags=suggested_tags or [],
                suggested_categories=suggested_categories or [],
            )

            self.log(f"Created outline with {len(outline.sections)} sections")

            return AgentResult(
                success=True,
                content=outline.to_markdown(),
                metadata={"outline": outline.to_dict(), "raw_outline": raw_outline},
            )

        except Exception as e:
            return self._handle_error(e, "Outline creation failed")

    async def aexecute(
        self,
        topic: str,
        research_summary: str,
        *,
        target_word_count: int | None = None,
        suggested_tags: list[str] | None = None,
        suggested_categories: list[str] | None = None,
    ) -> AgentResult:
        """Create a blog outline asynchronously.

        Args:
            topic: Blog topic.
            research_summary: Summary from research agent.
            target_word_count: Target word count.
            suggested_tags: Suggested tags.
            suggested_categories: Suggested categories.

        Returns:
            AgentResult with BlogOutline in metadata.
        """
        try:
            self.log(f"Creating outline async for: {topic}")

            word_count = target_word_count or self.settings.blog.min_word_count

            prompt = OUTLINE_PROMPT.format(
                topic=topic,
                research_summary=research_summary,
                word_count=word_count,
            )

            raw_outline = await self._agenerate(
                prompt,
                system_prompt=self.settings.prompts.planner_system,
            )

            outline = self._parse_outline(
                raw_outline=raw_outline,
                topic=topic,
                target_word_count=word_count,
                suggested_tags=suggested_tags or [],
                suggested_categories=suggested_categories or [],
            )

            return AgentResult(
                success=True,
                content=outline.to_markdown(),
                metadata={"outline": outline.to_dict(), "raw_outline": raw_outline},
            )

        except Exception as e:
            return self._handle_error(e, "Async outline creation failed")

    def _parse_outline(
        self,
        raw_outline: str,
        topic: str,
        target_word_count: int,
        suggested_tags: list[str],
        suggested_categories: list[str],
    ) -> BlogOutline:
        """Parse LLM output into structured outline.

        Args:
            raw_outline: Raw outline text from LLM.
            topic: Original topic.
            target_word_count: Target word count.
            suggested_tags: Suggested tags.
            suggested_categories: Suggested categories.

        Returns:
            Structured BlogOutline object.
        """
        # Try to extract structured data with another LLM call
        structure_prompt = f"""Extract the following from this blog outline and return as JSON:

Outline:
{raw_outline}

Return a JSON object with these fields:
- title: The blog post title
- meta_description: The meta description (150-160 chars)
- layout_type: The optimal layout (deep-dive, narrative, analytical, how-to, opinion, listicle)
- tags: Array of relevant tags
- categories: Array of categories
- seo_keywords: Array of SEO keywords
- sections: Array of section objects, each with:
  - title: Section title
  - key_points: Array of key points to cover
  - subsections: Array of subsection objects (same structure)

Return only valid JSON, no other text."""

        try:
            json_response = self._generate(structure_prompt, temperature=0.3)

            # Clean up response - extract JSON if wrapped in markdown
            json_str = json_response.strip()
            if json_str.startswith("```"):
                # Remove markdown code block
                lines = json_str.split("\n")
                json_str = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            data = json.loads(json_str)

            sections = []
            for section_data in data.get("sections", []):
                subsections = []
                for sub_data in section_data.get("subsections", []):
                    subsections.append(
                        Section(
                            title=sub_data.get("title", ""),
                            key_points=sub_data.get("key_points", []),
                        )
                    )
                sections.append(
                    Section(
                        title=section_data.get("title", ""),
                        key_points=section_data.get("key_points", []),
                        subsections=subsections,
                    )
                )

            # Merge suggested with extracted tags/categories
            tags = list(set(data.get("tags", []) + suggested_tags))
            categories = list(set(data.get("categories", []) + suggested_categories))

            return BlogOutline(
                title=data.get("title", topic),
                meta_description=data.get("meta_description", ""),
                sections=sections,
                tags=tags,
                categories=categories,
                target_word_count=target_word_count,
                seo_keywords=data.get("seo_keywords", []),
                layout_type=data.get("layout_type", "deep-dive"),
                raw_outline=raw_outline,
            )

        except (json.JSONDecodeError, KeyError) as e:
            self.log(f"Failed to parse structured outline: {e}", logging.WARNING)

            # Fallback: create basic outline from raw text
            return BlogOutline(
                title=topic,
                meta_description=f"A comprehensive guide to {topic}.",
                sections=[
                    Section(title="Introduction", key_points=["Set the context"]),
                    Section(title="Main Content", key_points=["Core information"]),
                    Section(title="Conclusion", key_points=["Summarize key points"]),
                ],
                tags=suggested_tags or [topic.lower().replace(" ", "-")],
                categories=suggested_categories or ["general"],
                target_word_count=target_word_count,
                layout_type="deep-dive",
                raw_outline=raw_outline,
            )

    def refine_outline(
        self,
        outline: BlogOutline,
        feedback: str,
    ) -> AgentResult:
        """Refine an existing outline based on feedback.

        Args:
            outline: Existing outline to refine.
            feedback: User feedback for refinement.

        Returns:
            AgentResult with refined BlogOutline.
        """
        prompt = f"""Refine the following blog outline based on the feedback provided:

Current Outline:
{outline.to_markdown()}

Feedback:
{feedback}

Provide an improved outline that addresses the feedback while maintaining the original structure where appropriate."""

        try:
            raw_outline = self._generate(
                prompt,
                system_prompt=self.settings.prompts.planner_system,
            )

            refined = self._parse_outline(
                raw_outline=raw_outline,
                topic=outline.title,
                target_word_count=outline.target_word_count,
                suggested_tags=outline.tags,
                suggested_categories=outline.categories,
            )

            return AgentResult(
                success=True,
                content=refined.to_markdown(),
                metadata={"outline": refined.to_dict()},
            )

        except Exception as e:
            return self._handle_error(e, "Outline refinement failed")
