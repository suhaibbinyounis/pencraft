"""Configuration management for OpenBlog using Pydantic Settings."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from openblog.config.defaults import (
    DEFAULT_FRONTMATTER_TEMPLATE,
    DEFAULT_HUGO_FRONTMATTER_FORMAT,
    DEFAULT_LLM_BASE_URL,
    DEFAULT_LLM_MAX_TOKENS,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_MAX_SEARCH_RESULTS,
    DEFAULT_MAX_SOURCES,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_PLANNER_SYSTEM_PROMPT,
    DEFAULT_RESEARCH_SYSTEM_PROMPT,
    DEFAULT_SEARCH_DEPTH,
    DEFAULT_WRITER_SYSTEM_PROMPT,
)


class LLMSettings(BaseModel):
    """Settings for the LLM client."""

    base_url: str = Field(
        default=DEFAULT_LLM_BASE_URL,
        description="Base URL for the OpenAI-compatible API endpoint",
    )
    api_key: str = Field(
        default="dummy-api-key",
        description="API key for authentication (can be dummy for local endpoints)",
    )
    model: str = Field(
        default=DEFAULT_LLM_MODEL,
        description="Model to use for generation",
    )
    temperature: float = Field(
        default=DEFAULT_LLM_TEMPERATURE,
        ge=0.0,
        le=2.0,
        description="Temperature for generation (0.0-2.0)",
    )
    max_tokens: int = Field(
        default=DEFAULT_LLM_MAX_TOKENS,
        gt=0,
        description="Maximum tokens to generate",
    )
    timeout: float = Field(
        default=120.0,
        gt=0,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retries for failed requests",
    )


class ResearchSettings(BaseModel):
    """Settings for the research agent."""

    max_search_results: int = Field(
        default=DEFAULT_MAX_SEARCH_RESULTS,
        gt=0,
        description="Maximum number of search results to fetch",
    )
    max_sources: int = Field(
        default=DEFAULT_MAX_SOURCES,
        gt=0,
        description="Maximum number of sources to include in citations",
    )
    search_depth: int = Field(
        default=DEFAULT_SEARCH_DEPTH,
        ge=1,
        le=5,
        description="Depth of search (1-5, higher = more thorough)",
    )
    include_snippets: bool = Field(
        default=True,
        description="Include text snippets from sources",
    )


class OutputSettings(BaseModel):
    """Settings for output generation."""

    directory: str = Field(
        default=DEFAULT_OUTPUT_DIR,
        description="Output directory for generated blogs",
    )
    format: str = Field(
        default=DEFAULT_OUTPUT_FORMAT,
        description="Output format (markdown, html)",
    )
    create_subdirs: bool = Field(
        default=True,
        description="Create subdirectories for each blog post",
    )
    filename_template: str = Field(
        default="{slug}.md",
        description="Template for output filenames",
    )


class HugoSettings(BaseModel):
    """Hugo-specific settings."""

    frontmatter_format: str = Field(
        default=DEFAULT_HUGO_FRONTMATTER_FORMAT,
        description="Frontmatter format (yaml, toml, json)",
    )
    default_frontmatter: dict[str, Any] = Field(
        default_factory=lambda: DEFAULT_FRONTMATTER_TEMPLATE.copy(),
        description="Default frontmatter fields",
    )
    content_dir: str = Field(
        default="content/posts",
        description="Hugo content directory",
    )
    static_dir: str = Field(
        default="static",
        description="Hugo static directory for assets",
    )


class BlogSettings(BaseModel):
    """Settings for blog generation."""

    min_word_count: int = Field(
        default=1500,
        gt=0,
        description="Minimum word count for generated blogs",
    )
    max_word_count: int = Field(
        default=5000,
        gt=0,
        description="Maximum word count for generated blogs",
    )
    include_toc: bool = Field(
        default=True,
        description="Include table of contents",
    )
    include_citations: bool = Field(
        default=True,
        description="Include source citations at the end",
    )
    default_tags: list[str] = Field(
        default_factory=list,
        description="Default tags for all posts",
    )
    default_categories: list[str] = Field(
        default_factory=list,
        description="Default categories for all posts",
    )


class PromptSettings(BaseModel):
    """Custom prompt templates."""

    research_system: str = Field(
        default=DEFAULT_RESEARCH_SYSTEM_PROMPT,
        description="System prompt for research agent",
    )
    planner_system: str = Field(
        default=DEFAULT_PLANNER_SYSTEM_PROMPT,
        description="System prompt for planning agent",
    )
    writer_system: str = Field(
        default=DEFAULT_WRITER_SYSTEM_PROMPT,
        description="System prompt for writing agent",
    )


class Settings(BaseSettings):
    """Main settings class for OpenBlog."""

    model_config = SettingsConfigDict(
        env_prefix="OPENBLOG_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # Nested settings
    llm: LLMSettings = Field(default_factory=LLMSettings)
    research: ResearchSettings = Field(default_factory=ResearchSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)
    hugo: HugoSettings = Field(default_factory=HugoSettings)
    blog: BlogSettings = Field(default_factory=BlogSettings)
    prompts: PromptSettings = Field(default_factory=PromptSettings)

    # General settings
    verbose: bool = Field(
        default=False,
        description="Enable verbose output",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    log_file: str | None = Field(
        default=None,
        description="Path to log file (optional)",
    )

    @model_validator(mode="before")
    @classmethod
    def load_from_config_file(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Load settings from config file if specified."""
        config_file = values.get("config_file") or os.environ.get("OPENBLOG_CONFIG_FILE")

        if config_file:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, encoding="utf-8") as f:
                    if config_path.suffix in (".yaml", ".yml"):
                        file_config = yaml.safe_load(f) or {}
                    else:
                        raise ValueError(f"Unsupported config format: {config_path.suffix}")

                # Merge file config with provided values (provided values take precedence)
                for key, value in file_config.items():
                    if key not in values:
                        values[key] = value

        return values

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary."""
        return self.model_dump()

    def save_to_file(self, path: str | Path) -> None:
        """Save settings to a YAML file."""
        path = Path(path)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def load_settings(config_file: str | Path | None = None, **overrides: Any) -> Settings:
    """Load settings with optional config file and overrides."""
    if config_file:
        overrides["config_file"] = str(config_file)
    return Settings(**overrides)
