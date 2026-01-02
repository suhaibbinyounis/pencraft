"""Pytest configuration and fixtures for OpenBlog tests."""

import pytest

from openblog.config.settings import Settings


@pytest.fixture
def settings() -> Settings:
    """Create test settings with default values."""
    return Settings(
        llm={
            "base_url": "http://localhost:3030",
            "api_key": "test-key",
            "model": "test-model",
            "temperature": 0.7,
        },
        verbose=False,
        debug=False,
    )


@pytest.fixture
def sample_research_summary() -> str:
    """Sample research summary for testing."""
    return """
# Research Summary: Python Programming

## Key Facts
- Python is a high-level, interpreted programming language
- Created by Guido van Rossum in 1991
- Known for its simple, readable syntax

## Statistics
- One of the most popular programming languages
- Used by millions of developers worldwide

## Sources
1. Python Official Documentation (python.org)
2. Stack Overflow Developer Survey 2024
"""


@pytest.fixture
def sample_outline_dict() -> dict:
    """Sample outline dictionary for testing."""
    return {
        "title": "Introduction to Python",
        "meta_description": "A comprehensive guide to Python programming",
        "sections": [
            {
                "title": "What is Python?",
                "key_points": ["History", "Features"],
                "subsections": [],
            },
            {
                "title": "Getting Started",
                "key_points": ["Installation", "First Program"],
                "subsections": [],
            },
        ],
        "tags": ["python", "programming"],
        "categories": ["Tutorial"],
        "target_word_count": 2000,
    }
