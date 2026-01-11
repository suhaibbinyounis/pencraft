"""Blog enhancer for improving existing blog posts."""

from __future__ import annotations

import json
import logging
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pencraft.agents.enhancement_prompts import (
    CONTENT_ANALYSIS_PROMPT,
    CONTENT_ENHANCEMENT_PROMPT,
    META_DESCRIPTION_PROMPT,
    TAGS_SUGGESTION_PROMPT,
)
from pencraft.formatters.frontmatter import FrontmatterGenerator
from pencraft.llm.client import LLMClient
from pencraft.tools.trends import TrendsData, TrendsTool

if TYPE_CHECKING:
    from pencraft.config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class EnhancedBlog:
    """Result of blog enhancement."""

    file_path: Path
    original_word_count: int
    enhanced_word_count: int
    original_content: str
    enhanced_content: str
    backup_path: Path | None = None
    improvements_made: list[str] = field(default_factory=list)
    trends_data: TrendsData | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": str(self.file_path),
            "original_word_count": self.original_word_count,
            "enhanced_word_count": self.enhanced_word_count,
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "improvements_made": self.improvements_made,
            "error": self.error,
        }


@dataclass
class ContentAnalysis:
    """Analysis of existing blog content."""

    title: str
    word_count: int
    thin_sections: list[str] = field(default_factory=list)
    seo_issues: list[str] = field(default_factory=list)
    quality_issues: list[str] = field(default_factory=list)
    frontmatter_issues: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    suggestions: str = ""


class BlogEnhancer:
    """Enhance existing blog posts for SEO, quality, and revenue.

    This class processes existing markdown blog posts and improves them
    through AI-powered analysis and rewriting. Features include:

    - SEO optimization (keywords, meta descriptions, headings)
    - Content expansion for thin/short sections
    - Google Trends integration for trending keywords
    - Grammar and style fixes
    - Frontmatter corrections
    - AdSense optimization with high-CPC keyword integration
    """

    def __init__(
        self,
        settings: Settings | None = None,
        llm_client: LLMClient | None = None,
        trends_tool: TrendsTool | None = None,
        on_progress: Any | None = None,
    ) -> None:
        """Initialize the blog enhancer.

        Args:
            settings: Settings object.
            llm_client: LLM client (creates one from settings if None).
            trends_tool: Google Trends tool (creates one if None).
            on_progress: Callback for progress updates.
        """
        # Import here to avoid circular imports
        from pencraft.config.settings import Settings as SettingsClass

        self.settings = settings or SettingsClass()
        self.llm_client = llm_client or LLMClient(self.settings)
        self.trends_tool = trends_tool or TrendsTool()
        self.frontmatter_gen = FrontmatterGenerator(
            format=self.settings.hugo.frontmatter_format
        )
        self.on_progress = on_progress or (lambda _msg: None)

    def _report_progress(self, message: str) -> None:
        """Report progress to callback."""
        logger.info(message)
        if self.on_progress:
            self.on_progress(message)

    def _count_words(self, text: str) -> int:
        """Count words in text, excluding code blocks."""
        # Remove code blocks
        text_no_code = re.sub(r"```[\s\S]*?```", "", text)
        text_no_code = re.sub(r"`[^`]+`", "", text_no_code)
        # Count words
        words = text_no_code.split()
        return len(words)

    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from frontmatter or first heading."""
        # Try frontmatter
        frontmatter, _ = self.frontmatter_gen.parse(content)
        if frontmatter and "title" in frontmatter:
            return frontmatter["title"]

        # Try first H1
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

        return "Untitled"

    def _backup_file(self, file_path: Path, backup_dir: Path) -> Path:
        """Create backup of original file.

        Args:
            file_path: Original file path.
            backup_dir: Directory to store backups.

        Returns:
            Path to backup file.
        """
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backed up to: {backup_path}")
        return backup_path

    def _get_trends_context(self, title: str) -> tuple[TrendsData | None, str]:
        """Fetch Google Trends data for topic.

        Args:
            title: Blog title/topic.

        Returns:
            Tuple of (TrendsData, formatted context string).
        """
        try:
            self._report_progress("Fetching Google Trends data...")
            # Extract key terms from title
            # Remove common words to get better trend matches
            stopwords = {
                "the", "a", "an", "is", "are", "how", "to", "what", "why",
                "when", "your", "you", "and", "or", "for", "with", "from",
                "in", "on", "at", "by", "of", "that", "this", "it",
            }
            words = title.lower().split()
            keywords = [w for w in words if w not in stopwords and len(w) > 2]

            # Use first 2-3 meaningful keywords
            search_term = " ".join(keywords[:3])
            trends_data = self.trends_tool.get_trends_data(search_term)

            if trends_data.error:
                logger.warning(f"Trends error: {trends_data.error}")
                return None, "No Google Trends data available."

            context = trends_data.to_research_context()
            return trends_data, context

        except Exception as e:
            logger.warning(f"Failed to fetch trends: {e}")
            return None, "No Google Trends data available."

    def _analyze_content(
        self,
        content: str,
        title: str,
        target_word_count: int,
        trends_data: str,
    ) -> ContentAnalysis:
        """Analyze blog content for improvement opportunities.

        Args:
            content: Blog content.
            title: Blog title.
            target_word_count: Target word count.
            trends_data: Formatted trends context.

        Returns:
            ContentAnalysis with identified issues.
        """
        self._report_progress("Analyzing content for improvements...")

        word_count = self._count_words(content)

        prompt = CONTENT_ANALYSIS_PROMPT.format(
            title=title,
            word_count=word_count,
            target_word_count=target_word_count,
            content=content[:15000],  # Limit content size
            trends_data=trends_data,
        )

        response = self.llm_client.complete(prompt)

        return ContentAnalysis(
            title=title,
            word_count=word_count,
            suggestions=response,
        )

    def _enhance_content(
        self,
        _original_content: str,
        body_content: str,
        analysis: ContentAnalysis,
        trends_data: str,
        target_word_count: int,
        trending_keywords: list[str],
    ) -> str:
        """Enhance blog content using LLM.

        Args:
            original_content: Full original content with frontmatter.
            body_content: Body content without frontmatter.
            analysis: Content analysis results.
            trends_data: Formatted trends context.
            target_word_count: Target word count.
            trending_keywords: Keywords to integrate.

        Returns:
            Enhanced markdown content (body only).
        """
        self._report_progress("Enhancing content...")

        # Extract specific issues from analysis
        specific_issues = analysis.suggestions[:3000]  # Limit size

        prompt = CONTENT_ENHANCEMENT_PROMPT.format(
            original_content=body_content[:12000],  # Limit content size
            analysis_results=specific_issues,
            trends_data=trends_data,
            target_word_count=target_word_count,
            current_word_count=analysis.word_count,
            trending_keywords=", ".join(trending_keywords[:10]),
            specific_issues=specific_issues,
        )

        enhanced = self.llm_client.complete(prompt)

        # Clean up any artifacts
        enhanced = self._clean_enhanced_content(enhanced)

        return enhanced

    def _clean_enhanced_content(self, content: str) -> str:
        """Remove LLM artifacts from enhanced content.

        Args:
            content: Raw enhanced content.

        Returns:
            Cleaned content.
        """
        # Remove any accidental frontmatter
        if content.startswith("---"):
            # Find end of frontmatter
            end_match = re.search(r"\n---\n", content[3:])
            if end_match:
                content = content[end_match.end() + 3:]

        # Remove title if it was duplicated
        content = re.sub(r"^#\s+.+\n+", "", content)

        # Remove common LLM artifacts
        artifacts = [
            r"^Here'?s? (?:is )?the enhanced (?:blog |content|version).*?:\n+",
            r"^I've enhanced.*?:\n+",
            r"^Below is the.*?:\n+",
            r"\n*---\n*$",
        ]
        for pattern in artifacts:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE | re.MULTILINE)

        return content.strip()

    def _generate_meta_description(
        self,
        title: str,
        content: str,
        keywords: list[str],
    ) -> str:
        """Generate SEO-optimized meta description.

        Args:
            title: Blog title.
            content: Blog content.
            keywords: Primary keywords.

        Returns:
            Meta description string.
        """
        # Get first 500 chars as summary
        content_summary = content[:500].replace("\n", " ")

        prompt = META_DESCRIPTION_PROMPT.format(
            title=title,
            content_summary=content_summary,
            keywords=", ".join(keywords[:5]),
        )

        description = self.llm_client.complete(prompt)

        # Clean and truncate
        description = description.strip().strip('"').strip()
        if len(description) > 160:
            description = description[:157] + "..."

        return description

    def _suggest_tags(
        self,
        title: str,
        content: str,
        trends_data: TrendsData | None,
        current_tags: list[str],
        current_categories: list[str],
    ) -> tuple[list[str], list[str]]:
        """Suggest improved tags and categories.

        Args:
            title: Blog title.
            content: Blog content.
            trends_data: Google Trends data.
            current_tags: Existing tags.
            current_categories: Existing categories.

        Returns:
            Tuple of (tags, categories).
        """
        # Extract topics from content
        topics = content[:1000].replace("\n", " ")

        rising_keywords = []
        if trends_data:
            rising_keywords = trends_data.rising_queries[:5]

        prompt = TAGS_SUGGESTION_PROMPT.format(
            title=title,
            topics=topics,
            rising_keywords=", ".join(rising_keywords) if rising_keywords else "None",
            current_tags=", ".join(current_tags) if current_tags else "None",
            current_categories=", ".join(current_categories) if current_categories else "None",
        )

        response = self.llm_client.complete(prompt)

        # Parse JSON response
        try:
            # Find JSON in response
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
                return (
                    data.get("tags", current_tags),
                    data.get("categories", current_categories),
                )
        except json.JSONDecodeError:
            logger.warning("Failed to parse tags suggestion")

        return current_tags, current_categories

    def _fix_frontmatter(
        self,
        frontmatter: dict[str, Any],
        title: str,
        description: str,
        tags: list[str],
        categories: list[str],
    ) -> dict[str, Any]:
        """Fix and improve frontmatter.

        Args:
            frontmatter: Original frontmatter dict.
            title: Blog title.
            description: Meta description.
            tags: Updated tags.
            categories: Updated categories.

        Returns:
            Fixed frontmatter dict.
        """
        fixed = dict(frontmatter)

        # Ensure required fields
        fixed["title"] = title
        fixed["description"] = description

        # Fix date if missing or invalid
        if "date" not in fixed or not fixed["date"]:
            fixed["date"] = datetime.now(timezone.utc)

        # Update tags and categories
        if tags:
            fixed["tags"] = tags
        if categories:
            fixed["categories"] = categories

        # Ensure draft is False for enhanced content
        fixed["draft"] = False

        # Add lastmod
        fixed["lastmod"] = datetime.now(timezone.utc)

        return fixed

    def enhance(
        self,
        file_path: Path,
        *,
        target_word_count: int | None = None,
        improve_seo: bool = True,
        use_trends: bool = True,
        fix_frontmatter: bool = True,
        backup: bool = True,
        backup_dir: Path | None = None,
    ) -> EnhancedBlog:
        """Enhance a single blog post.

        Args:
            file_path: Path to markdown file.
            target_word_count: Minimum target word count.
            improve_seo: Whether to optimize SEO.
            use_trends: Whether to fetch Google Trends data.
            fix_frontmatter: Whether to fix frontmatter issues.
            backup: Whether to backup original file.
            backup_dir: Directory for backups (defaults to .backup/).

        Returns:
            EnhancedBlog with results.
        """
        file_path = Path(file_path)
        self._report_progress(f"Enhancing: {file_path.name}")

        # Set defaults
        target_word_count = target_word_count or self.settings.blog.min_word_count or 3000
        backup_dir = backup_dir or file_path.parent / ".backup"

        improvements_made: list[str] = []
        backup_path = None

        try:
            # Read original content
            original_content = file_path.read_text(encoding="utf-8")
            original_word_count = self._count_words(original_content)

            # Parse frontmatter and body
            frontmatter, body_content = self.frontmatter_gen.parse(original_content)
            title = frontmatter.get("title", self._extract_title_from_content(original_content))

            # Backup if requested
            if backup:
                backup_path = self._backup_file(file_path, backup_dir)
                improvements_made.append("Created backup")

            # Fetch trends data if requested
            trends_data = None
            trends_context = "No Google Trends data."
            trending_keywords: list[str] = []
            if use_trends:
                trends_data, trends_context = self._get_trends_context(title)
                if trends_data:
                    trending_keywords = (
                        trends_data.rising_queries[:5] +
                        trends_data.related_queries[:5]
                    )
                    improvements_made.append("Integrated Google Trends data")

            # Analyze content
            analysis = self._analyze_content(
                body_content, title, target_word_count, trends_context
            )

            # Enhance content
            enhanced_body = self._enhance_content(
                original_content,
                body_content,
                analysis,
                trends_context,
                target_word_count,
                trending_keywords,
            )
            improvements_made.append("Enhanced content quality")

            # Generate/improve meta description if SEO enabled
            description = frontmatter.get("description", "")
            if improve_seo:
                description = self._generate_meta_description(
                    title, enhanced_body, trending_keywords
                )
                improvements_made.append("Optimized meta description")

            # Suggest improved tags
            current_tags = frontmatter.get("tags", [])
            current_categories = frontmatter.get("categories", [])
            new_tags, new_categories = self._suggest_tags(
                title, enhanced_body, trends_data, current_tags, current_categories
            )
            if new_tags != current_tags or new_categories != current_categories:
                improvements_made.append("Updated tags/categories")

            # Fix frontmatter
            if fix_frontmatter:
                fixed_frontmatter = self._fix_frontmatter(
                    frontmatter, title, description, new_tags, new_categories
                )
                improvements_made.append("Fixed frontmatter")
            else:
                fixed_frontmatter = frontmatter

            # Generate new frontmatter string
            new_frontmatter = self.frontmatter_gen.generate(
                title=fixed_frontmatter.get("title", title),
                description=fixed_frontmatter.get("description", description),
                date=fixed_frontmatter.get("date"),
                draft=fixed_frontmatter.get("draft", False),
                tags=fixed_frontmatter.get("tags", []),
                categories=fixed_frontmatter.get("categories", []),
                author=fixed_frontmatter.get("author"),
                slug=fixed_frontmatter.get("slug"),
                featured_image=fixed_frontmatter.get("featured_image"),
                toc=fixed_frontmatter.get("toc", True),
                lastmod=fixed_frontmatter.get("lastmod"),
            )

            # Combine frontmatter and enhanced body
            enhanced_content = f"{new_frontmatter}\n{enhanced_body}"
            enhanced_word_count = self._count_words(enhanced_content)

            # Write enhanced content
            file_path.write_text(enhanced_content, encoding="utf-8")

            self._report_progress(
                f"Enhanced: {original_word_count} → {enhanced_word_count} words"
            )

            return EnhancedBlog(
                file_path=file_path,
                original_word_count=original_word_count,
                enhanced_word_count=enhanced_word_count,
                original_content=original_content,
                enhanced_content=enhanced_content,
                backup_path=backup_path,
                improvements_made=improvements_made,
                trends_data=trends_data,
            )

        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            return EnhancedBlog(
                file_path=file_path,
                original_word_count=0,
                enhanced_word_count=0,
                original_content="",
                enhanced_content="",
                backup_path=backup_path,
                error=str(e),
            )

    def enhance_directory(
        self,
        directory: Path,
        *,
        pattern: str = "*.md",
        recursive: bool = False,
        skip_on_error: bool = True,
        delay_seconds: float = 2.0,
        **enhance_kwargs: Any,
    ) -> list[EnhancedBlog]:
        """Enhance all matching files in a directory.

        Args:
            directory: Directory containing blog files.
            pattern: Glob pattern for matching files.
            recursive: Whether to search subdirectories.
            skip_on_error: Whether to continue if one file fails.
            delay_seconds: Delay between processing files.
            **enhance_kwargs: Additional arguments for enhance().

        Returns:
            List of EnhancedBlog results.
        """
        import time

        directory = Path(directory)
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        # Find matching files
        files = (
            list(directory.rglob(pattern)) if recursive else list(directory.glob(pattern))
        )

        # Sort for consistent ordering
        files = sorted(files)

        self._report_progress(f"Found {len(files)} files to enhance")

        results: list[EnhancedBlog] = []

        for i, file_path in enumerate(files, 1):
            self._report_progress(f"[{i}/{len(files)}] Processing: {file_path.name}")

            try:
                result = self.enhance(file_path, **enhance_kwargs)
                results.append(result)

                if result.error:
                    logger.error(f"Error enhancing {file_path.name}: {result.error}")
                    if not skip_on_error:
                        break
                else:
                    self._report_progress(
                        f"✓ {file_path.name}: "
                        f"{result.original_word_count} → {result.enhanced_word_count} words"
                    )

            except Exception as e:
                logger.error(f"Failed to enhance {file_path.name}: {e}")
                if not skip_on_error:
                    raise

                results.append(
                    EnhancedBlog(
                        file_path=file_path,
                        original_word_count=0,
                        enhanced_word_count=0,
                        original_content="",
                        enhanced_content="",
                        error=str(e),
                    )
                )

            # Delay between files to be nice to APIs
            if i < len(files) and delay_seconds > 0:
                time.sleep(delay_seconds)

        # Summary
        successful = sum(1 for r in results if not r.error)
        failed = len(results) - successful
        total_original = sum(r.original_word_count for r in results if not r.error)
        total_enhanced = sum(r.enhanced_word_count for r in results if not r.error)

        self._report_progress(
            f"Complete: {successful} enhanced, {failed} failed. "
            f"Total words: {total_original} → {total_enhanced}"
        )

        return results
