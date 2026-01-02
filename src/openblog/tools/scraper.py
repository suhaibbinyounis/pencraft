"""Web scraping tool for content extraction."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class ScrapedContent:
    """Scraped content from a web page."""

    url: str
    title: str
    content: str
    meta_description: str = ""
    headings: list[str] | None = None
    word_count: int = 0
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "meta_description": self.meta_description,
            "headings": self.headings,
            "word_count": self.word_count,
            "success": self.success,
            "error": self.error,
        }


class WebScraper:
    """Web scraper for extracting content from URLs.

    Focuses on extracting clean, readable text content
    from web pages for use in research.
    """

    # Common elements to remove that don't contain main content
    REMOVE_SELECTORS = [
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "aside",
        "advertisement",
        ".ad",
        ".ads",
        ".sidebar",
        ".navigation",
        ".menu",
        ".cookie",
        ".popup",
        ".modal",
        "#comments",
        ".comments",
        ".social-share",
        ".related-posts",
    ]

    def __init__(
        self,
        timeout: float = 30.0,
        max_content_length: int = 50000,
        user_agent: str | None = None,
    ) -> None:
        """Initialize the web scraper.

        Args:
            timeout: Request timeout in seconds.
            max_content_length: Maximum content length to extract.
            user_agent: Custom user agent string.
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.user_agent = user_agent or (
            "Mozilla/5.0 (compatible; OpenBlog/1.0; +https://github.com/suhaibbinyounis/openblog)"
        )

        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
        )

    def scrape(self, url: str) -> ScrapedContent:
        """Scrape content from a URL.

        Args:
            url: URL to scrape.

        Returns:
            ScrapedContent object with extracted content.
        """
        try:
            response = self._client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title = self._extract_title(soup)

            # Extract meta description
            meta_description = self._extract_meta_description(soup)

            # Extract headings
            headings = self._extract_headings(soup)

            # Remove unwanted elements
            for selector in self.REMOVE_SELECTORS:
                for element in soup.select(selector):
                    element.decompose()

            # Extract main content
            content = self._extract_content(soup)

            # Truncate if too long
            if len(content) > self.max_content_length:
                content = content[: self.max_content_length] + "..."

            word_count = len(content.split())

            logger.info(f"Scraped {url}: {word_count} words")

            return ScrapedContent(
                url=url,
                title=title,
                content=content,
                meta_description=meta_description,
                headings=headings,
                word_count=word_count,
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping {url}: {e}")
            return ScrapedContent(
                url=url,
                title="",
                content="",
                success=False,
                error=f"HTTP error: {e}",
            )
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return ScrapedContent(
                url=url,
                title="",
                content="",
                success=False,
                error=str(e),
            )

    async def ascrape(self, url: str) -> ScrapedContent:
        """Scrape content from a URL asynchronously.

        Args:
            url: URL to scrape.

        Returns:
            ScrapedContent object with extracted content.
        """
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={"User-Agent": self.user_agent},
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                title = self._extract_title(soup)
                meta_description = self._extract_meta_description(soup)
                headings = self._extract_headings(soup)

                for selector in self.REMOVE_SELECTORS:
                    for element in soup.select(selector):
                        element.decompose()

                content = self._extract_content(soup)

                if len(content) > self.max_content_length:
                    content = content[: self.max_content_length] + "..."

                word_count = len(content.split())

                logger.info(f"Scraped async {url}: {word_count} words")

                return ScrapedContent(
                    url=url,
                    title=title,
                    content=content,
                    meta_description=meta_description,
                    headings=headings,
                    word_count=word_count,
                )

        except Exception as e:
            logger.error(f"Error async scraping {url}: {e}")
            return ScrapedContent(
                url=url,
                title="",
                content="",
                success=False,
                error=str(e),
            )

    def scrape_multiple(self, urls: list[str]) -> list[ScrapedContent]:
        """Scrape multiple URLs.

        Args:
            urls: List of URLs to scrape.

        Returns:
            List of ScrapedContent objects.
        """
        return [self.scrape(url) for url in urls]

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title.

        Args:
            soup: BeautifulSoup object.

        Returns:
            Page title or empty string.
        """
        # Try og:title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return str(og_title.get("content", ""))

        # Try title tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()

        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return ""

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description.

        Args:
            soup: BeautifulSoup object.

        Returns:
            Meta description or empty string.
        """
        # Try og:description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return str(og_desc.get("content", ""))

        # Try meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return str(meta_desc.get("content", ""))

        return ""

    def _extract_headings(self, soup: BeautifulSoup) -> list[str]:
        """Extract all headings.

        Args:
            soup: BeautifulSoup object.

        Returns:
            List of heading texts.
        """
        headings = []
        for tag in ["h1", "h2", "h3"]:
            for heading in soup.find_all(tag):
                text = heading.get_text(strip=True)
                if text:
                    headings.append(text)
        return headings

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content text.

        Args:
            soup: BeautifulSoup object.

        Returns:
            Cleaned content text.
        """
        # Try common article containers
        article = soup.find("article")
        if article:
            text = article.get_text(separator="\n", strip=True)
        else:
            # Try main tag
            main = soup.find("main")
            if main:
                text = main.get_text(separator="\n", strip=True)
            else:
                # Fall back to body
                body = soup.find("body")
                if body:
                    text = body.get_text(separator="\n", strip=True)
                else:
                    text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        return text.strip()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "WebScraper":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
