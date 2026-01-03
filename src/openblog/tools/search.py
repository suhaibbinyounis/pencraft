"""Web search tool using DuckDuckGo."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ddgs import DDGS

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str
    source: str = ""

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
        }


class SearchTool:
    """Web search tool using DuckDuckGo API.

    Provides search functionality without requiring API keys.
    """

    def __init__(
        self,
        max_results: int = 10,
        region: str = "wt-wt",
        safesearch: str = "moderate",
    ) -> None:
        """Initialize the search tool.

        Args:
            max_results: Maximum number of results to return.
            region: Region for search results (wt-wt = worldwide).
            safesearch: SafeSearch setting (off, moderate, strict).
        """
        self.max_results = max_results
        self.region = region
        self.safesearch = safesearch

    def search(
        self,
        query: str,
        *,
        max_results: int | None = None,
        time_range: str | None = None,
    ) -> list[SearchResult]:
        """Perform a web search.

        Args:
            query: Search query string.
            max_results: Override max results for this search.
            time_range: Time range filter (d=day, w=week, m=month, y=year).

        Returns:
            List of SearchResult objects.
        """
        max_results = max_results or self.max_results
        results: list[SearchResult] = []

        try:
            with DDGS() as ddgs:
                search_results = ddgs.text(
                    query,
                    region=self.region,
                    safesearch=self.safesearch,
                    timelimit=time_range,
                    max_results=max_results,
                )

                for result in search_results:
                    results.append(
                        SearchResult(
                            title=result.get("title", ""),
                            url=result.get("href", result.get("link", "")),
                            snippet=result.get("body", result.get("snippet", "")),
                            source=self._extract_source(result.get("href", "")),
                        )
                    )

            logger.info(f"Search for '{query}' returned {len(results)} results")

        except Exception as e:
            logger.error(f"Search error for '{query}': {e}")

        return results

    def search_news(
        self,
        query: str,
        *,
        max_results: int | None = None,
        time_range: str | None = None,
    ) -> list[SearchResult]:
        """Search for news articles.

        Args:
            query: Search query string.
            max_results: Override max results for this search.
            time_range: Time range filter (d=day, w=week, m=month).

        Returns:
            List of SearchResult objects.
        """
        max_results = max_results or self.max_results
        results: list[SearchResult] = []

        try:
            with DDGS() as ddgs:
                news_results = ddgs.news(
                    query,
                    region=self.region,
                    safesearch=self.safesearch,
                    timelimit=time_range,
                    max_results=max_results,
                )

                for result in news_results:
                    results.append(
                        SearchResult(
                            title=result.get("title", ""),
                            url=result.get("url", ""),
                            snippet=result.get("body", ""),
                            source=result.get("source", ""),
                        )
                    )

            logger.info(f"News search for '{query}' returned {len(results)} results")

        except Exception as e:
            logger.error(f"News search error for '{query}': {e}")

        return results

    def multi_search(
        self,
        queries: list[str],
        *,
        max_results_per_query: int = 5,
    ) -> dict[str, list[SearchResult]]:
        """Perform multiple searches and aggregate results.

        Args:
            queries: List of search queries.
            max_results_per_query: Max results per individual query.

        Returns:
            Dictionary mapping queries to their results.
        """
        all_results: dict[str, list[SearchResult]] = {}

        for query in queries:
            all_results[query] = self.search(query, max_results=max_results_per_query)

        return all_results

    def _extract_source(self, url: str) -> str:
        """Extract source domain from URL.

        Args:
            url: Full URL string.

        Returns:
            Domain name or empty string.
        """
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix if present
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    def format_results_for_llm(self, results: list[SearchResult]) -> str:
        """Format search results as text for LLM consumption.

        Args:
            results: List of search results.

        Returns:
            Formatted string of results.
        """
        if not results:
            return "No search results found."

        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"**[{i}] {result.title}**\n"
                f"Source: {result.source}\n"
                f"URL: {result.url}\n"
                f"Snippet: {result.snippet}\n"
            )

        return "\n".join(formatted)

    def to_langchain_tool(self) -> Any:
        """Convert to a LangChain-compatible tool.

        Returns:
            LangChain Tool object.
        """
        from langchain.tools import Tool

        def _search_wrapper(query: str) -> str:
            results = self.search(query)
            return self.format_results_for_llm(results)

        return Tool(
            name="web_search",
            description="Search the web for information on a topic. Input should be a search query.",
            func=_search_wrapper,
        )
