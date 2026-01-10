#!/usr/bin/env python3
"""Simple example of using OpenBlog to generate a blog post.

This example demonstrates the basic usage of the OpenBlog library
to generate a complete blog post from a topic.
"""

from pathlib import Path

from openblog import Settings
from openblog.generator import BlogGenerator


def main() -> None:
    """Generate a simple blog post."""

    # Create custom settings (optional - uses defaults if not provided)
    settings = Settings(
        llm={
            "base_url": "http://localhost:3030",  # Your local LLM endpoint
            "api_key": "dummy-key",  # API key (can be dummy for local)
            "model": "gpt-4",
            "temperature": 0.7,
        },
        blog={
            "min_word_count": 1500,
            "include_toc": True,
            "include_citations": True,
        },
        hugo={
            "frontmatter_format": "yaml",
            "default_frontmatter": {
                "draft": False,
                "author": "Your Name",
            },
        },
    )

    # Create the generator
    generator = BlogGenerator(settings=settings)

    # Generate a blog post
    print("🚀 Starting blog generation...")

    blog = generator.generate(
        topic="Introduction to Python for Beginners",
        target_word_count=2000,
        tags=["python", "programming", "tutorial", "beginners"],
        categories=["Programming", "Tutorials"],
        author="OpenBlog",
        draft=False,
        output_dir=Path("./output"),
    )

    # Display results
    print("\n✅ Blog generated successfully!")
    print(f"   Title: {blog.title}")
    print(f"   Words: {blog.word_count}")
    print(f"   Time: {blog.generation_time:.2f}s")
    print(f"   File: {blog.file_path}")
    print(f"   Sources: {len(blog.sources)}")


if __name__ == "__main__":
    main()
