"""Research agent for gathering information on topics."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from openblog.agents.base import AgentResult, BaseAgent
from openblog.llm.prompts import RESEARCH_PROMPT
from openblog.tools.scraper import ScrapedContent, WebScraper
from openblog.tools.search import SearchResult, SearchTool

if TYPE_CHECKING:
    from openblog.config.settings import Settings
    from openblog.llm.client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class ResearchData:
    """Collected research data for a topic."""

    topic: str
    summary: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    key_points: list[str] = field(default_factory=list)
    search_results: list[SearchResult] = field(default_factory=list)
    scraped_content: list[ScrapedContent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "topic": self.topic,
            "summary": self.summary,
            "sources": self.sources,
            "key_points": self.key_points,
            "search_results": [r.to_dict() for r in self.search_results],
            "scraped_content": [c.to_dict() for c in self.scraped_content],
        }


class ResearchAgent(BaseAgent):
    """Agent for researching topics and gathering information.

    Uses web search and content scraping to gather comprehensive
    research data for blog post creation.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        settings: Settings | None = None,
        search_tool: SearchTool | None = None,
        scraper: WebScraper | None = None,
    ) -> None:
        """Initialize the research agent.

        Args:
            llm_client: LLM client for AI operations.
            settings: Settings object.
            search_tool: Custom search tool (uses default if None).
            scraper: Custom web scraper (uses default if None).
        """
        super().__init__(llm_client, settings, name="ResearchAgent")

        self.search_tool = search_tool or SearchTool(
            max_results=self.settings.research.max_search_results
        )
        self.scraper = scraper or WebScraper()

    def execute(
        self,
        topic: str,
        *,
        additional_context: str = "",
        search_queries: list[str] | None = None,
        scrape_top_n: int = 3,
    ) -> AgentResult:
        """Execute research on a topic.

        Args:
            topic: Topic to research.
            additional_context: Additional context or requirements.
            search_queries: Custom search queries (auto-generated if None).
            scrape_top_n: Number of top results to scrape for content.

        Returns:
            AgentResult with ResearchData in metadata.
        """
        try:
            self.log(f"Starting research on: {topic}")

            # Generate search queries if not provided
            if not search_queries:
                search_queries = self._generate_search_queries(topic)

            # Perform searches
            all_results: list[SearchResult] = []
            for query in search_queries:
                results = self.search_tool.search(query)
                all_results.extend(results)
                self.log(f"Search '{query}': {len(results)} results")

            # Deduplicate by URL
            seen_urls: set[str] = set()
            unique_results: list[SearchResult] = []
            for result in all_results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    unique_results.append(result)

            self.log(f"Total unique results: {len(unique_results)}")

            # Scrape top results for full content
            scraped_content: list[ScrapedContent] = []
            for result in unique_results[:scrape_top_n]:
                content = self.scraper.scrape(result.url)
                if content.success:
                    scraped_content.append(content)
                    self.log(f"Scraped {result.url}: {content.word_count} words")

            # Synthesize research using LLM
            research_summary = self._synthesize_research(
                topic=topic,
                search_results=unique_results,
                scraped_content=scraped_content,
                additional_context=additional_context,
            )

            # Extract sources for citations
            sources = self._extract_sources(unique_results, scraped_content)

            # Create research data
            research_data = ResearchData(
                topic=topic,
                summary=research_summary,
                sources=sources,
                search_results=unique_results[: self.settings.research.max_sources],
                scraped_content=scraped_content,
            )

            self.log("Research completed successfully")

            return AgentResult(
                success=True,
                content=research_summary,
                metadata={"research_data": research_data.to_dict()},
            )

        except Exception as e:
            return self._handle_error(e, "Research execution failed")

    async def aexecute(
        self,
        topic: str,
        *,
        additional_context: str = "",
        search_queries: list[str] | None = None,
        scrape_top_n: int = 3,
    ) -> AgentResult:
        """Execute research asynchronously.

        Args:
            topic: Topic to research.
            additional_context: Additional context or requirements.
            search_queries: Custom search queries (auto-generated if None).
            scrape_top_n: Number of top results to scrape for content.

        Returns:
            AgentResult with ResearchData in metadata.
        """
        try:
            self.log(f"Starting async research on: {topic}")

            # Generate search queries if not provided
            if not search_queries:
                search_queries = await self._agenerate_search_queries(topic)

            # Perform searches (sync for now, DuckDuckGo doesn't have async)
            all_results: list[SearchResult] = []
            for query in search_queries:
                results = self.search_tool.search(query)
                all_results.extend(results)

            # Deduplicate
            seen_urls: set[str] = set()
            unique_results: list[SearchResult] = []
            for result in all_results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    unique_results.append(result)

            # Scrape asynchronously
            scraped_content: list[ScrapedContent] = []
            for result in unique_results[:scrape_top_n]:
                content = await self.scraper.ascrape(result.url)
                if content.success:
                    scraped_content.append(content)

            # Synthesize research
            research_summary = await self._asynthesize_research(
                topic=topic,
                search_results=unique_results,
                scraped_content=scraped_content,
                additional_context=additional_context,
            )

            sources = self._extract_sources(unique_results, scraped_content)

            research_data = ResearchData(
                topic=topic,
                summary=research_summary,
                sources=sources,
                search_results=unique_results[: self.settings.research.max_sources],
                scraped_content=scraped_content,
            )

            return AgentResult(
                success=True,
                content=research_summary,
                metadata={"research_data": research_data.to_dict()},
            )

        except Exception as e:
            return self._handle_error(e, "Async research execution failed")

    def _generate_search_queries(self, topic: str) -> list[str]:
        """Generate search queries for a topic.

        Args:
            topic: Main topic.

        Returns:
            List of search queries.
        """
        # Use LLM to generate diverse search queries
        prompt = f"""Generate 3-5 diverse search queries to research the following topic comprehensively:

Topic: {topic}

Return only the search queries, one per line, without numbering or explanation."""

        try:
            response = self._generate(prompt)
            queries = [q.strip() for q in response.strip().split("\n") if q.strip()]
            return queries[:5] if queries else [topic]
        except Exception:
            # Fallback to basic queries
            return [
                topic,
                f"{topic} guide",
                f"{topic} best practices",
            ]

    async def _agenerate_search_queries(self, topic: str) -> list[str]:
        """Generate search queries asynchronously."""
        prompt = f"""Generate 3-5 diverse search queries to research the following topic comprehensively:

Topic: {topic}

Return only the search queries, one per line, without numbering or explanation."""

        try:
            response = await self._agenerate(prompt)
            queries = [q.strip() for q in response.strip().split("\n") if q.strip()]
            return queries[:5] if queries else [topic]
        except Exception:
            return [topic, f"{topic} guide", f"{topic} best practices"]

    def _synthesize_research(
        self,
        topic: str,
        search_results: list[SearchResult],
        scraped_content: list[ScrapedContent],
        additional_context: str,
    ) -> str:
        """Synthesize research data into a summary.

        Args:
            topic: Research topic.
            search_results: Search results.
            scraped_content: Scraped web content.
            additional_context: Additional context.

        Returns:
            Synthesized research summary.
        """
        # Prepare context from search results
        search_context = self.search_tool.format_results_for_llm(search_results[:10])

        # Prepare context from scraped content
        scraped_context = "\n\n".join(
            f"**Source: {c.title}** ({c.url})\n{c.content[:2000]}..."
            for c in scraped_content
            if c.success
        )

        prompt = RESEARCH_PROMPT.format(
            topic=topic,
            additional_context=additional_context or "No additional context provided.",
        )

        full_prompt = f"""{prompt}

## Search Results:
{search_context}

## Scraped Content:
{scraped_context}"""

        return self._generate(
            full_prompt,
            system_prompt=self.settings.prompts.research_system,
        )

    async def _asynthesize_research(
        self,
        topic: str,
        search_results: list[SearchResult],
        scraped_content: list[ScrapedContent],
        additional_context: str,
    ) -> str:
        """Synthesize research asynchronously."""
        search_context = self.search_tool.format_results_for_llm(search_results[:10])

        scraped_context = "\n\n".join(
            f"**Source: {c.title}** ({c.url})\n{c.content[:2000]}..."
            for c in scraped_content
            if c.success
        )

        prompt = RESEARCH_PROMPT.format(
            topic=topic,
            additional_context=additional_context or "No additional context provided.",
        )

        full_prompt = f"""{prompt}

## Search Results:
{search_context}

## Scraped Content:
{scraped_context}"""

        return await self._agenerate(
            full_prompt,
            system_prompt=self.settings.prompts.research_system,
        )

    def _extract_sources(
        self,
        search_results: list[SearchResult],
        scraped_content: list[ScrapedContent],
    ) -> list[dict[str, Any]]:
        """Extract source information for citations.

        Args:
            search_results: Search results.
            scraped_content: Scraped content.

        Returns:
            List of source dictionaries.
        """
        sources: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        # Add sources from scraped content first (more reliable)
        for content in scraped_content:
            if content.success and content.url not in seen_urls:
                sources.append({
                    "title": content.title,
                    "url": content.url,
                    "description": content.meta_description,
                })
                seen_urls.add(content.url)

        # Add sources from search results
        for result in search_results:
            if result.url not in seen_urls:
                sources.append({
                    "title": result.title,
                    "url": result.url,
                    "description": result.snippet,
                })
                seen_urls.add(result.url)

            if len(sources) >= self.settings.research.max_sources:
                break

        return sources
