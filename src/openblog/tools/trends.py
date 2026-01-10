"""Google Trends tool using pytrends for topic research and validation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from pytrends.request import TrendReq
from urllib3.util import retry

# Monkeypatch Retry to support method_whitelist (deprecated in urllib3 2.0)
if not hasattr(retry.Retry, "method_whitelist"):
    _original_init = retry.Retry.__init__

    def _new_init(self, *args, **kwargs):
        if "method_whitelist" in kwargs:
            kwargs["allowed_methods"] = kwargs.pop("method_whitelist")
        _original_init(self, *args, **kwargs)

    retry.Retry.__init__ = _new_init

logger = logging.getLogger(__name__)


@dataclass
class TrendsData:
    """Google Trends data for a topic."""

    topic: str
    interest_score: int = 0  # 0-100, average interest over time
    is_trending: bool = False
    related_queries: list[str] = field(default_factory=list)
    rising_queries: list[str] = field(default_factory=list)
    related_topics: list[str] = field(default_factory=list)
    rising_topics: list[str] = field(default_factory=list)
    regional_interest: dict[str, int] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "topic": self.topic,
            "interest_score": self.interest_score,
            "is_trending": self.is_trending,
            "related_queries": self.related_queries,
            "rising_queries": self.rising_queries,
            "related_topics": self.related_topics,
            "rising_topics": self.rising_topics,
            "regional_interest": self.regional_interest,
        }

    def to_research_context(self) -> str:
        """Format trends data as context for research agent."""
        lines = [f"## Google Trends Data for: {self.topic}", ""]

        if self.interest_score > 0:
            lines.append(f"**Interest Score:** {self.interest_score}/100")
            if self.is_trending:
                lines.append("**Status:** 📈 Currently trending")
            lines.append("")

        if self.rising_queries:
            lines.append("**Rising Searches (hot topics to cover):**")
            for q in self.rising_queries[:5]:
                lines.append(f"- {q}")
            lines.append("")

        if self.related_queries:
            lines.append("**Related Searches (what people also search):**")
            for q in self.related_queries[:5]:
                lines.append(f"- {q}")
            lines.append("")

        if self.rising_topics:
            lines.append("**Rising Topics:**")
            for t in self.rising_topics[:3]:
                lines.append(f"- {t}")
            lines.append("")

        if self.regional_interest:
            top_regions = sorted(self.regional_interest.items(), key=lambda x: x[1], reverse=True)[
                :5
            ]
            if top_regions:
                lines.append("**Top Regions:**")
                for region, score in top_regions:
                    lines.append(f"- {region}: {score}%")

        return "\n".join(lines)


class TrendsTool:
    """Google Trends tool for topic research and validation.

    Uses pytrends to fetch real-time Google search trends data.
    Useful for:
    - Validating topic interest before writing
    - Discovering related/rising queries for better sections
    - Finding trending subtopics
    - Geographic targeting insights
    """

    def __init__(
        self,
        language: str = "en-US",
        timezone: int = 360,
        retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        """Initialize the trends tool.

        Args:
            language: Language for Google Trends (e.g., 'en-US').
            timezone: Timezone offset in minutes from UTC.
            retries: Number of retries for failed requests.
            backoff_factor: Backoff factor for retries.
        """
        self.language = language
        self.timezone = timezone
        self.retries = retries
        self.backoff_factor = backoff_factor
        self._pytrends: TrendReq | None = None

    def _get_client(self) -> TrendReq:
        """Get or create the pytrends client."""
        if self._pytrends is None:
            self._pytrends = TrendReq(
                hl=self.language,
                tz=self.timezone,
                retries=self.retries,
                backoff_factor=self.backoff_factor,
            )
        return self._pytrends

    def get_trends_data(
        self,
        topic: str,
        *,
        timeframe: str = "today 3-m",
        geo: str = "",
        include_regional: bool = True,
    ) -> TrendsData:
        """Fetch comprehensive trends data for a topic.

        Args:
            topic: Topic to research.
            timeframe: Time range (e.g., 'today 3-m', 'today 12-m', 'now 7-d').
            geo: Geographic region (e.g., 'US', 'GB', '' for worldwide).
            include_regional: Whether to fetch regional interest data.

        Returns:
            TrendsData object with all available trends information.
        """
        trends_data = TrendsData(topic=topic)

        try:
            pytrends = self._get_client()

            # Build payload for the topic
            pytrends.build_payload([topic], timeframe=timeframe, geo=geo)

            # Get interest over time
            try:
                interest_df = pytrends.interest_over_time()
                if not interest_df.empty and topic in interest_df.columns:
                    # Calculate average interest score
                    trends_data.interest_score = int(interest_df[topic].mean())
                    # Check if trending (recent values higher than average)
                    recent = interest_df[topic].tail(4).mean()
                    overall = interest_df[topic].mean()
                    trends_data.is_trending = recent > overall * 1.2
                    logger.info(f"Interest score for '{topic}': {trends_data.interest_score}")
            except Exception as e:
                logger.warning(f"Could not fetch interest over time: {e}")

            # Get related queries
            try:
                related = pytrends.related_queries()
                if topic in related and related[topic]:
                    # Top queries
                    top_df = related[topic].get("top")
                    if top_df is not None and not top_df.empty:
                        trends_data.related_queries = top_df["query"].tolist()[:10]

                    # Rising queries
                    rising_df = related[topic].get("rising")
                    if rising_df is not None and not rising_df.empty:
                        trends_data.rising_queries = rising_df["query"].tolist()[:10]
                        logger.info(f"Found {len(trends_data.rising_queries)} rising queries")
            except Exception as e:
                logger.warning(f"Could not fetch related queries: {e}")

            # Get related topics
            try:
                topics = pytrends.related_topics()
                if topic in topics and topics[topic]:
                    # Top topics
                    top_topics_df = topics[topic].get("top")
                    if (
                        top_topics_df is not None
                        and not top_topics_df.empty
                        and "topic_title" in top_topics_df.columns
                    ):
                        trends_data.related_topics = top_topics_df["topic_title"].tolist()[:5]

                    # Rising topics
                    rising_topics_df = topics[topic].get("rising")
                    if (
                        rising_topics_df is not None
                        and not rising_topics_df.empty
                        and "topic_title" in rising_topics_df.columns
                    ):
                        trends_data.rising_topics = rising_topics_df["topic_title"].tolist()[:5]
            except IndexError:
                logger.info("No related topics found (empty response).")
            except Exception as e:
                logger.warning(f"Could not fetch related topics: {e}")

            # Get regional interest
            if include_regional:
                try:
                    regional_df = pytrends.interest_by_region(resolution="COUNTRY")
                    if not regional_df.empty and topic in regional_df.columns:
                        # Filter to regions with some interest
                        regional_series = regional_df[topic]
                        regional_with_interest = regional_series[regional_series > 0]
                        trends_data.regional_interest = regional_with_interest.to_dict()
                except Exception as e:
                    logger.warning(f"Could not fetch regional interest: {e}")

        except Exception as e:
            logger.error(f"Trends lookup failed for '{topic}': {e}")
            trends_data.error = str(e)

        return trends_data

    def get_related_queries(self, topic: str) -> list[str]:
        """Get related search queries for a topic.

        Args:
            topic: Topic to get related queries for.

        Returns:
            List of related query strings.
        """
        data = self.get_trends_data(topic, include_regional=False)
        return data.related_queries + data.rising_queries

    def get_rising_topics(self, topic: str) -> list[str]:
        """Get rising/trending topics related to a subject.

        Args:
            topic: Topic to analyze.

        Returns:
            List of rising topic names.
        """
        data = self.get_trends_data(topic, include_regional=False)
        return data.rising_topics + data.rising_queries

    def validate_topic_interest(
        self,
        topic: str,
        min_score: int = 10,
    ) -> tuple[bool, int, str]:
        """Validate if a topic has sufficient search interest.

        Args:
            topic: Topic to validate.
            min_score: Minimum interest score (0-100) to consider valid.

        Returns:
            Tuple of (is_valid, score, message).
        """
        data = self.get_trends_data(topic, include_regional=False)

        if data.error:
            return True, 0, f"⚠️ Could not validate topic interest: {data.error}"

        if data.interest_score == 0:
            return True, 0, "⚠️ No Google Trends data found - topic may be niche or new"

        if data.interest_score < min_score:
            return (
                False,
                data.interest_score,
                f"⚠️ Low interest score ({data.interest_score}/100). Consider a different topic.",
            )

        trend_emoji = "📈" if data.is_trending else "📊"
        return (
            True,
            data.interest_score,
            f"{trend_emoji} Interest score: {data.interest_score}/100"
            + (" (trending!)" if data.is_trending else ""),
        )

    def format_for_research(self, topic: str) -> str:
        """Format trends data as research context.

        Args:
            topic: Topic to research.

        Returns:
            Formatted string for inclusion in research summary.
        """
        data = self.get_trends_data(topic)
        return data.to_research_context()
