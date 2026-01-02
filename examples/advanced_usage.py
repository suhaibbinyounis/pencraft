#!/usr/bin/env python3
"""Advanced example demonstrating all OpenBlog features.

This example shows:
- Custom configuration
- Step-by-step generation (research -> outline -> write)
- Async generation
- Custom prompts
- Multiple output formats
"""

import asyncio
from pathlib import Path

from openblog import Settings
from openblog.agents.planner import PlannerAgent
from openblog.agents.research import ResearchAgent
from openblog.agents.writer import WriterAgent
from openblog.formatters.citations import CitationFormatter
from openblog.formatters.frontmatter import FrontmatterGenerator
from openblog.generator import BlogGenerator
from openblog.llm.client import LLMClient


def step_by_step_generation() -> None:
    """Generate a blog post step by step with more control."""

    print("=" * 60)
    print("Step-by-Step Blog Generation")
    print("=" * 60)

    # Create LLM client
    llm = LLMClient(
        base_url="http://localhost:3030",
        api_key="dummy-key",
        model="gpt-4",
    )

    topic = "Best Practices for REST API Design"

    # Step 1: Research
    print("\n📚 Step 1: Researching topic...")
    research_agent = ResearchAgent(llm_client=llm)
    research_result = research_agent.execute(
        topic=topic,
        additional_context="Focus on modern best practices and common mistakes to avoid.",
    )

    if not research_result.success:
        print(f"❌ Research failed: {research_result.error}")
        return

    print(f"   Found {len(research_result.metadata['research_data']['sources'])} sources")

    # Step 2: Create outline
    print("\n📝 Step 2: Creating outline...")
    planner_agent = PlannerAgent(llm_client=llm)
    outline_result = planner_agent.execute(
        topic=topic,
        research_summary=research_result.content,
        target_word_count=3000,
        suggested_tags=["api", "rest", "design", "best-practices"],
    )

    if not outline_result.success:
        print(f"❌ Planning failed: {outline_result.error}")
        return

    outline = outline_result.metadata["outline"]
    print(f"   Created outline with {len(outline['sections'])} sections")

    # Step 3: Write content
    print("\n✍️ Step 3: Writing content...")
    writer_agent = WriterAgent(llm_client=llm)
    from openblog.agents.planner import BlogOutline, Section

    blog_outline = BlogOutline(
        title=outline["title"],
        meta_description=outline["meta_description"],
        sections=[
            Section(title=s["title"], key_points=s["key_points"])
            for s in outline["sections"]
        ],
        tags=outline.get("tags", []),
        categories=outline.get("categories", []),
    )

    write_result = writer_agent.execute(
        outline=blog_outline,
        research_summary=research_result.content,
        sources=research_result.metadata["research_data"]["sources"],
    )

    if not write_result.success:
        print(f"❌ Writing failed: {write_result.error}")
        return

    # Step 4: Format and save
    print("\n💾 Step 4: Formatting and saving...")
    fm_generator = FrontmatterGenerator(format="yaml")
    frontmatter = fm_generator.generate(
        title=blog_outline.title,
        description=blog_outline.meta_description,
        tags=blog_outline.tags,
        categories=blog_outline.categories,
        author="OpenBlog",
    )

    full_content = frontmatter + "\n" + write_result.content

    output_path = Path("./output/step-by-step-blog.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(full_content, encoding="utf-8")

    word_count = len(write_result.content.split())
    print(f"\n✅ Complete!")
    print(f"   Title: {blog_outline.title}")
    print(f"   Words: {word_count}")
    print(f"   File: {output_path}")


async def async_generation() -> None:
    """Generate a blog post asynchronously."""

    print("\n" + "=" * 60)
    print("Async Blog Generation")
    print("=" * 60)

    settings = Settings(
        llm={"base_url": "http://localhost:3030", "api_key": "dummy-key"},
    )

    generator = BlogGenerator(settings=settings)

    print("\n🚀 Generating blog post asynchronously...")

    blog = await generator.agenerate(
        topic="Introduction to Async Programming in Python",
        target_word_count=2000,
        tags=["python", "async", "asyncio", "concurrency"],
        output_dir=Path("./output"),
    )

    print(f"\n✅ Complete!")
    print(f"   Title: {blog.title}")
    print(f"   Words: {blog.word_count}")
    print(f"   Time: {blog.generation_time:.2f}s")


def custom_citation_styles() -> None:
    """Demonstrate different citation styles."""

    print("\n" + "=" * 60)
    print("Citation Style Examples")
    print("=" * 60)

    sources = [
        {
            "title": "REST API Design Best Practices",
            "url": "https://example.com/rest-api-guide",
            "author": "John Smith",
            "date": "2024",
            "publisher": "Tech Blog",
        },
        {
            "title": "HTTP Methods Explained",
            "url": "https://example.com/http-methods",
            "author": "Jane Doe",
            "date": "2023",
            "publisher": "Developer Magazine",
        },
    ]

    for style in ["markdown", "apa", "mla", "chicago"]:
        print(f"\n{style.upper()} Style:")
        print("-" * 40)
        formatter = CitationFormatter.from_sources(sources, style=style)
        print(formatter.generate_references_section())


def main() -> None:
    """Run all examples."""

    print("\n🎯 OpenBlog Advanced Examples\n")

    # Step-by-step generation
    step_by_step_generation()

    # Citation styles
    custom_citation_styles()

    # Async generation (uncomment to run)
    # asyncio.run(async_generation())

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
