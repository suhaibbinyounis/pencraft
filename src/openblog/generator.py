"""Main blog generator that orchestrates all agents."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from openblog.agents.planner import BlogOutline, PlannerAgent
from openblog.agents.research import ResearchAgent
from openblog.agents.writer import BlogPost, WriterAgent
from openblog.formatters.citations import CitationFormatter
from openblog.formatters.frontmatter import FrontmatterGenerator
from openblog.formatters.markdown import MarkdownFormatter
from openblog.llm.client import LLMClient

if TYPE_CHECKING:
    from openblog.config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class GeneratedBlog:
    """Complete generated blog with all metadata."""

    title: str
    content: str
    frontmatter: str
    full_content: str
    file_path: str | None = None
    outline: BlogOutline | None = None
    research_summary: str = ""
    sources: list[dict[str, Any]] = field(default_factory=list)
    word_count: int = 0
    generation_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "frontmatter": self.frontmatter,
            "file_path": self.file_path,
            "research_summary": self.research_summary,
            "sources": self.sources,
            "word_count": self.word_count,
            "generation_time": self.generation_time,
        }


class BlogGenerator:
    """Main generator that orchestrates research, planning, and writing.

    This is the primary interface for generating complete blog posts
    from a given topic.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        """Initialize the blog generator.

        Args:
            settings: Settings object.
            llm_client: LLM client (creates one from settings if None).
        """
        if settings is None:
            from openblog.config.settings import get_settings

            settings = get_settings()

        self.settings = settings

        if llm_client is None:
            llm_client = LLMClient(settings=settings.llm)

        self.llm = llm_client

        # Initialize agents
        self.research_agent = ResearchAgent(llm_client=self.llm, settings=settings)
        self.planner_agent = PlannerAgent(llm_client=self.llm, settings=settings)
        self.writer_agent = WriterAgent(llm_client=self.llm, settings=settings)

        # Initialize formatters
        self.frontmatter_gen = FrontmatterGenerator(
            format=settings.hugo.frontmatter_format,
            default_fields=settings.hugo.default_frontmatter,
        )
        self.md_formatter = MarkdownFormatter()

    def generate(
        self,
        topic: str,
        *,
        additional_context: str = "",
        target_word_count: int | None = None,
        tags: list[str] | None = None,
        categories: list[str] | None = None,
        author: str | None = None,
        draft: bool = False,
        output_dir: str | Path | None = None,
        filename: str | None = None,
        skip_research: bool = False,
        custom_outline: BlogOutline | None = None,
        custom_research: str | None = None,
    ) -> GeneratedBlog:
        """Generate a complete blog post.

        Args:
            topic: Blog topic.
            additional_context: Extra context for research.
            target_word_count: Target word count.
            tags: Tags for the post.
            categories: Categories for the post.
            author: Author name.
            draft: Whether to mark as draft.
            output_dir: Output directory (uses settings default if None).
            filename: Output filename (auto-generated if None).
            skip_research: Skip research phase (use custom_research).
            custom_outline: Skip planning, use this outline.
            custom_research: Skip research, use this summary.

        Returns:
            GeneratedBlog with complete content.
        """
        import time

        start_time = time.time()

        logger.info(f"Starting blog generation for: {topic}")

        target_word_count = target_word_count or self.settings.blog.min_word_count
        tags = tags or self.settings.blog.default_tags.copy()
        categories = categories or self.settings.blog.default_categories.copy()

        # Phase 1: Research
        if custom_research:
            research_summary = custom_research
            sources: list[dict[str, Any]] = []
            logger.info("Using provided custom research")
        elif skip_research:
            research_summary = f"Topic: {topic}\n\n{additional_context}"
            sources = []
            logger.info("Skipping research phase")
        else:
            logger.info("Phase 1: Researching topic...")
            research_result = self.research_agent.execute(
                topic=topic,
                additional_context=additional_context,
            )
            if not research_result.success:
                raise RuntimeError(f"Research failed: {research_result.error}")

            research_summary = research_result.content
            sources = research_result.metadata.get("research_data", {}).get("sources", [])
            logger.info(f"Research complete: {len(sources)} sources found")

        # Phase 2: Planning
        if custom_outline:
            outline = custom_outline
            logger.info("Using provided custom outline")
        else:
            logger.info("Phase 2: Creating outline...")
            outline_result = self.planner_agent.execute(
                topic=topic,
                research_summary=research_summary,
                target_word_count=target_word_count,
                suggested_tags=tags,
                suggested_categories=categories,
            )
            if not outline_result.success:
                raise RuntimeError(f"Planning failed: {outline_result.error}")

            outline_data = outline_result.metadata.get("outline", {})
            outline = self._dict_to_outline(outline_data)
            logger.info(f"Outline created: {len(outline.sections)} sections")

        # Phase 3: Writing
        logger.info("Phase 3: Writing content...")
        write_result = self.writer_agent.execute(
            outline=outline,
            research_summary=research_summary,
            sources=sources,
        )
        if not write_result.success:
            raise RuntimeError(f"Writing failed: {write_result.error}")

        blog_content = write_result.content
        word_count = len(blog_content.split())
        logger.info(f"Writing complete: {word_count} words")

        # Generate frontmatter
        frontmatter = self.frontmatter_gen.generate(
            title=outline.title,
            description=outline.meta_description,
            date=datetime.now(),
            draft=draft,
            tags=outline.tags or tags,
            categories=outline.categories or categories,
            author=author,
            slug=self.md_formatter.slugify(outline.title),
            toc=self.settings.blog.include_toc,
        )

        # Add optional TOC
        if self.settings.blog.include_toc:
            toc = self.md_formatter.generate_toc(blog_content)
            blog_content = f"# {outline.title}\n\n{toc}\n\n{blog_content}"
        else:
            blog_content = f"# {outline.title}\n\n{blog_content}"

        # Combine frontmatter and content
        full_content = frontmatter + "\n" + blog_content

        # Clean up content
        full_content = self.md_formatter.clean_content(full_content)

        # Save to file if output directory provided
        file_path = None
        if output_dir:
            file_path = self._save_to_file(
                content=full_content,
                title=outline.title,
                output_dir=Path(output_dir),
                filename=filename,
            )
            logger.info(f"Saved to: {file_path}")

        generation_time = time.time() - start_time

        logger.info(f"Blog generation complete in {generation_time:.2f}s")

        return GeneratedBlog(
            title=outline.title,
            content=blog_content,
            frontmatter=frontmatter,
            full_content=full_content,
            file_path=str(file_path) if file_path else None,
            outline=outline,
            research_summary=research_summary,
            sources=sources,
            word_count=word_count,
            generation_time=generation_time,
        )

    async def agenerate(
        self,
        topic: str,
        *,
        additional_context: str = "",
        target_word_count: int | None = None,
        tags: list[str] | None = None,
        categories: list[str] | None = None,
        author: str | None = None,
        draft: bool = False,
        output_dir: str | Path | None = None,
        filename: str | None = None,
        skip_research: bool = False,
        custom_outline: BlogOutline | None = None,
        custom_research: str | None = None,
    ) -> GeneratedBlog:
        """Generate a blog post asynchronously.

        Same args as generate().
        """
        import time

        start_time = time.time()

        logger.info(f"Starting async blog generation for: {topic}")

        target_word_count = target_word_count or self.settings.blog.min_word_count
        tags = tags or self.settings.blog.default_tags.copy()
        categories = categories or self.settings.blog.default_categories.copy()

        # Phase 1: Research
        if custom_research:
            research_summary = custom_research
            sources: list[dict[str, Any]] = []
        elif skip_research:
            research_summary = f"Topic: {topic}\n\n{additional_context}"
            sources = []
        else:
            research_result = await self.research_agent.aexecute(
                topic=topic,
                additional_context=additional_context,
            )
            if not research_result.success:
                raise RuntimeError(f"Research failed: {research_result.error}")

            research_summary = research_result.content
            sources = research_result.metadata.get("research_data", {}).get("sources", [])

        # Phase 2: Planning
        if custom_outline:
            outline = custom_outline
        else:
            outline_result = await self.planner_agent.aexecute(
                topic=topic,
                research_summary=research_summary,
                target_word_count=target_word_count,
                suggested_tags=tags,
                suggested_categories=categories,
            )
            if not outline_result.success:
                raise RuntimeError(f"Planning failed: {outline_result.error}")

            outline_data = outline_result.metadata.get("outline", {})
            outline = self._dict_to_outline(outline_data)

        # Phase 3: Writing
        write_result = await self.writer_agent.aexecute(
            outline=outline,
            research_summary=research_summary,
            sources=sources,
        )
        if not write_result.success:
            raise RuntimeError(f"Writing failed: {write_result.error}")

        blog_content = write_result.content
        word_count = len(blog_content.split())

        # Generate frontmatter
        frontmatter = self.frontmatter_gen.generate(
            title=outline.title,
            description=outline.meta_description,
            date=datetime.now(),
            draft=draft,
            tags=outline.tags or tags,
            categories=outline.categories or categories,
            author=author,
            slug=self.md_formatter.slugify(outline.title),
            toc=self.settings.blog.include_toc,
        )

        # Add TOC if enabled
        if self.settings.blog.include_toc:
            toc = self.md_formatter.generate_toc(blog_content)
            blog_content = f"# {outline.title}\n\n{toc}\n\n{blog_content}"
        else:
            blog_content = f"# {outline.title}\n\n{blog_content}"

        full_content = frontmatter + "\n" + blog_content
        full_content = self.md_formatter.clean_content(full_content)

        file_path = None
        if output_dir:
            file_path = self._save_to_file(
                content=full_content,
                title=outline.title,
                output_dir=Path(output_dir),
                filename=filename,
            )

        generation_time = time.time() - start_time

        return GeneratedBlog(
            title=outline.title,
            content=blog_content,
            frontmatter=frontmatter,
            full_content=full_content,
            file_path=str(file_path) if file_path else None,
            outline=outline,
            research_summary=research_summary,
            sources=sources,
            word_count=word_count,
            generation_time=generation_time,
        )

    def _save_to_file(
        self,
        content: str,
        title: str,
        output_dir: Path,
        filename: str | None = None,
    ) -> Path:
        """Save content to file.

        Args:
            content: Blog content.
            title: Blog title.
            output_dir: Output directory.
            filename: Optional filename.

        Returns:
            Path to saved file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            slug = self.md_formatter.slugify(title)
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_prefix}-{slug}.md"

        file_path = output_dir / filename
        file_path.write_text(content, encoding="utf-8")

        return file_path

    def _dict_to_outline(self, data: dict[str, Any]) -> BlogOutline:
        """Convert dictionary to BlogOutline.

        Args:
            data: Outline dictionary.

        Returns:
            BlogOutline object.
        """
        from openblog.agents.planner import Section

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

        return BlogOutline(
            title=data.get("title", "Untitled"),
            meta_description=data.get("meta_description", ""),
            sections=sections,
            tags=data.get("tags", []),
            categories=data.get("categories", []),
            target_word_count=data.get("target_word_count", 2000),
            seo_keywords=data.get("seo_keywords", []),
        )

    def research_only(
        self,
        topic: str,
        additional_context: str = "",
    ) -> str:
        """Perform research only.

        Args:
            topic: Topic to research.
            additional_context: Additional context.

        Returns:
            Research summary.
        """
        result = self.research_agent.execute(
            topic=topic,
            additional_context=additional_context,
        )
        if not result.success:
            raise RuntimeError(f"Research failed: {result.error}")
        return result.content

    def outline_only(
        self,
        topic: str,
        research_summary: str = "",
        target_word_count: int | None = None,
    ) -> BlogOutline:
        """Create outline only.

        Args:
            topic: Blog topic.
            research_summary: Optional research summary.
            target_word_count: Target word count.

        Returns:
            BlogOutline object.
        """
        if not research_summary:
            research_summary = f"Topic: {topic}"

        result = self.planner_agent.execute(
            topic=topic,
            research_summary=research_summary,
            target_word_count=target_word_count,
        )
        if not result.success:
            raise RuntimeError(f"Planning failed: {result.error}")

        return self._dict_to_outline(result.metadata.get("outline", {}))
