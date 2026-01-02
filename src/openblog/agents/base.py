"""Base agent class for OpenBlog."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openblog.config.settings import Settings
    from openblog.llm.client import LLMClient


logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from an agent execution."""

    success: bool
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def __bool__(self) -> bool:
        """Return success status."""
        return self.success


class BaseAgent(ABC):
    """Abstract base class for all agents.

    Provides common functionality for agent execution including:
    - LLM client access
    - Settings management
    - Logging
    - Error handling
    """

    def __init__(
        self,
        llm_client: LLMClient,
        settings: Settings | None = None,
        name: str | None = None,
    ) -> None:
        """Initialize the base agent.

        Args:
            llm_client: LLM client instance for API calls.
            settings: Settings object. If None, uses global settings.
            name: Agent name for logging. Defaults to class name.
        """
        self.llm = llm_client
        self._settings = settings
        self.name = name or self.__class__.__name__

        self._logger = logging.getLogger(f"openblog.agents.{self.name}")

    @property
    def settings(self) -> Settings:
        """Get settings, loading from global if not provided."""
        if self._settings is None:
            from openblog.config.settings import get_settings

            self._settings = get_settings()
        return self._settings

    @abstractmethod
    def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the agent's main task.

        Subclasses must implement this method.

        Args:
            **kwargs: Agent-specific arguments.

        Returns:
            AgentResult containing the execution result.
        """
        ...

    @abstractmethod
    async def aexecute(self, **kwargs: Any) -> AgentResult:
        """Execute the agent's main task asynchronously.

        Subclasses must implement this method.

        Args:
            **kwargs: Agent-specific arguments.

        Returns:
            AgentResult containing the execution result.
        """
        ...

    def log(self, message: str, level: int = logging.INFO) -> None:
        """Log a message with the agent's logger.

        Args:
            message: Message to log.
            level: Logging level.
        """
        self._logger.log(level, f"[{self.name}] {message}")

    def _handle_error(self, error: Exception, context: str = "") -> AgentResult:
        """Handle an error and return a failure result.

        Args:
            error: The exception that occurred.
            context: Additional context about where the error occurred.

        Returns:
            AgentResult with failure status and error details.
        """
        error_msg = f"{context}: {error}" if context else str(error)
        self._logger.error(f"[{self.name}] Error: {error_msg}", exc_info=True)

        return AgentResult(
            success=False,
            content="",
            error=error_msg,
        )

    def _generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate content using the LLM.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional arguments for the LLM.

        Returns:
            Generated content string.
        """
        self.log(f"Generating content (prompt length: {len(prompt)} chars)")
        return self.llm.generate(prompt, system_prompt=system_prompt, **kwargs)

    async def _agenerate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate content using the LLM asynchronously.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional arguments for the LLM.

        Returns:
            Generated content string.
        """
        self.log(f"Generating content async (prompt length: {len(prompt)} chars)")
        return await self.llm.agenerate(prompt, system_prompt=system_prompt, **kwargs)
