"""OpenAI-compatible LLM client wrapper for OpenBlog."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generator

from openai import AsyncOpenAI, OpenAI

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletion, ChatCompletionChunk

from openblog.config.settings import LLMSettings, get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI-compatible LLM client with configurable endpoint.

    This client wraps the OpenAI SDK to support any OpenAI-compatible API,
    including local endpoints like LM Studio, Ollama, or custom servers.
    """

    def __init__(
        self,
        settings: LLMSettings | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        """Initialize the LLM client.

        Args:
            settings: LLM settings object. If not provided, uses global settings.
            base_url: Override base URL (takes precedence over settings).
            api_key: Override API key (takes precedence over settings).
            model: Override model name (takes precedence over settings).
        """
        if settings is None:
            settings = get_settings().llm

        self.base_url = base_url or settings.base_url
        self.api_key = api_key or settings.api_key
        self.model = model or settings.model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens
        self.timeout = settings.timeout
        self.max_retries = settings.max_retries

        # Initialize sync client
        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

        # Initialize async client
        self._async_client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

        logger.debug(f"LLM client initialized with base_url={self.base_url}, model={self.model}")

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> ChatCompletion:
        """Send a chat completion request.

        Args:
            messages: List of chat messages with 'role' and 'content'.
            model: Override model for this request.
            temperature: Override temperature for this request.
            max_tokens: Override max_tokens for this request.
            **kwargs: Additional arguments passed to the API.

        Returns:
            ChatCompletion response object.
        """
        response = self._client.chat.completions.create(
            model=model or self.model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            **kwargs,
        )
        return response

    async def achat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> ChatCompletion:
        """Send an async chat completion request.

        Args:
            messages: List of chat messages with 'role' and 'content'.
            model: Override model for this request.
            temperature: Override temperature for this request.
            max_tokens: Override max_tokens for this request.
            **kwargs: Additional arguments passed to the API.

        Returns:
            ChatCompletion response object.
        """
        response = await self._async_client.chat.completions.create(
            model=model or self.model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            **kwargs,
        )
        return response

    def chat_stream(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> Generator[ChatCompletionChunk, None, None]:
        """Send a streaming chat completion request.

        Args:
            messages: List of chat messages with 'role' and 'content'.
            model: Override model for this request.
            temperature: Override temperature for this request.
            max_tokens: Override max_tokens for this request.
            **kwargs: Additional arguments passed to the API.

        Yields:
            ChatCompletionChunk objects as they arrive.
        """
        stream = self._client.chat.completions.create(
            model=model or self.model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stream=True,
            **kwargs,
        )
        yield from stream  # type: ignore[misc]

    async def achat_stream(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Send an async streaming chat completion request.

        Args:
            messages: List of chat messages with 'role' and 'content'.
            model: Override model for this request.
            temperature: Override temperature for this request.
            max_tokens: Override max_tokens for this request.
            **kwargs: Additional arguments passed to the API.

        Yields:
            ChatCompletionChunk objects as they arrive.
        """
        stream = await self._async_client.chat.completions.create(
            model=model or self.model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:  # type: ignore[union-attr]
            yield chunk

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from a simple prompt.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional arguments passed to chat().

        Returns:
            Generated text content.
        """
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.chat(messages, **kwargs)
        return response.choices[0].message.content or ""

    async def agenerate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from a simple prompt asynchronously.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional arguments passed to achat().

        Returns:
            Generated text content.
        """
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.achat(messages, **kwargs)
        return response.choices[0].message.content or ""

    def close(self) -> None:
        """Close the client connections."""
        self._client.close()

    async def aclose(self) -> None:
        """Close the async client connections."""
        await self._async_client.close()

    def __enter__(self) -> "LLMClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "LLMClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.aclose()
