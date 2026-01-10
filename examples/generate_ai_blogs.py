#!/usr/bin/env python3
"""Generate Anime x AI deep dive blogs.

Exploring the intersection of Japanese animation and artificial intelligence.
"""

import time
import warnings
from pathlib import Path

from openblog import Settings
from openblog.generator import BlogGenerator

warnings.filterwarnings("ignore", message="This package.*has been renamed")

# Anime x AI Deep Dives: Where Japanese Animation Meets Artificial Intelligence
# Exploring how anime predicted, influenced, and now collaborates with AI technology
BLOG_TOPICS = [
    # 1. AI-Powered Anime Production
    {
        "topic": "The AI Animation Revolution: How Studios Like WIT and MAPPA Are Using Machine Learning to Create Breathtaking Scenes",
        "tags": [
            "anime-production",
            "ai-animation",
            "machine-learning",
            "studio-workflows",
            "visual-effects",
        ],
        "categories": ["Anime Industry", "AI in Entertainment"],
        "cover_image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop",
    },
    # 2. Anime's AI Prophecies
    {
        "topic": "Ghost in the Shell to Psycho-Pass: How Anime Predicted AI's Ethical Dilemmas 30 Years Before ChatGPT",
        "tags": ["ghost-in-the-shell", "psycho-pass", "ai-ethics", "science-fiction", "cyberpunk"],
        "categories": ["Anime Analysis", "AI Philosophy"],
        "cover_image": "https://images.unsplash.com/photo-1535378437803-f30a90539653?q=80&w=2670&auto=format&fit=crop",
    },
    # 3. Virtual Idols & AI Companions
    {
        "topic": "From Hatsune Miku to AI Waifus: The Evolution of Virtual Characters and What It Means for Human Connection",
        "tags": ["vtubers", "virtual-idols", "ai-companions", "hatsune-miku", "character-ai"],
        "categories": ["Virtual Entertainment", "AI Psychology"],
        "cover_image": "https://images.unsplash.com/photo-1560750588-73207b1ef5b8?q=80&w=2670&auto=format&fit=crop",
    },
    # 4. AI Art & The Anime Style
    {
        "topic": "Why AI Art Models Are Obsessed With Anime: The Technical Reason Behind Stable Diffusion's 'Anime Style' Dominance",
        "tags": ["stable-diffusion", "ai-art", "anime-style", "training-data", "imagen-generation"],
        "categories": ["AI Art", "Anime Aesthetics"],
        "cover_image": "https://images.unsplash.com/photo-1633412802994-11765e8d5852?q=80&w=2670&auto=format&fit=crop",
    },
    # 5. The Tachikoma Paradox
    {
        "topic": "The Tachikoma Paradox: What Ghost in the Shell's Thinking Tanks Teach Us About Emergent AI Consciousness",
        "tags": [
            "tachikoma",
            "ghost-in-the-shell",
            "ai-consciousness",
            "emergent-behavior",
            "swarm-intelligence",
        ],
        "categories": ["Anime Philosophy", "AI Research"],
        "cover_image": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=2670&auto=format&fit=crop",
    },
    # 6. Anime Voice Synthesis
    {
        "topic": "AI Voice Cloning in Anime: How RVC and VITS Are Preserving Legendary Seiyuu Performances Forever",
        "tags": ["voice-synthesis", "seiyuu", "rvc", "vits", "voice-cloning"],
        "categories": ["Audio AI", "Anime Production"],
        "cover_image": "https://images.unsplash.com/photo-1478737270239-2f63b8608451?q=80&w=2670&auto=format&fit=crop",
    },
    # 7. Real-Time Anime Filters
    {
        "topic": "From Face to Anime: The Deep Learning Behind Real-Time Anime Filter Apps and VTuber Technology",
        "tags": ["face-tracking", "live2d", "vtuber-tech", "neural-style-transfer", "real-time-ai"],
        "categories": ["VTuber Technology", "Computer Vision"],
        "cover_image": "https://images.unsplash.com/photo-1483794344563-d27a8d18016e?q=80&w=2670&auto=format&fit=crop",
    },
    # 8. AI Dungeon Masters & Isekai
    {
        "topic": "Isekai for Everyone: How AI Game Masters Are Creating Infinite Anime-Inspired Fantasy Worlds",
        "tags": ["ai-dungeon", "isekai", "procedural-generation", "narrative-ai", "game-masters"],
        "categories": ["AI Gaming", "Anime Genres"],
        "cover_image": "https://images.unsplash.com/photo-1552820728-8b83bb6b773f?q=80&w=2670&auto=format&fit=crop",
    },
    # 9. The Evangelion Problem
    {
        "topic": "The Evangelion Problem: Why AI Still Cannot Write Psychologically Complex Anime Narratives",
        "tags": [
            "evangelion",
            "narrative-ai",
            "psychological-depth",
            "character-writing",
            "llm-limitations",
        ],
        "categories": ["Anime Writing", "AI Creativity"],
        "cover_image": "https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?q=80&w=2574&auto=format&fit=crop",
    },
    # 10. Anime Recommendation Engines
    {
        "topic": "Beyond MyAnimeList: How Modern AI Recommendation Systems Actually Understand Your Anime Taste",
        "tags": [
            "recommendation-systems",
            "collaborative-filtering",
            "myanimelist",
            "taste-modeling",
            "content-discovery",
        ],
        "categories": ["AI Applications", "Anime Community"],
        "cover_image": "https://images.unsplash.com/photo-1516110833967-0b5716ca1387?q=80&w=2574&auto=format&fit=crop",
    },
]


def main() -> None:
    """Generate AI agent tutorial blog posts."""

    # Create output directory
    output_dir = Path("./output/anime-ai-2026-blogs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create settings for long-form content
    settings = Settings(
        llm={
            "base_url": "http://localhost:3030/v1",
            "api_key": "dummy-key",
            "temperature": 0.5,  # Moderate temperature for balanced creativity/accuracy
            "max_tokens": 8192,
        },
        blog={
            "min_word_count": 3000,
            "max_word_count": 5000,
            "include_toc": True,
            "include_citations": True,
        },
        research={
            "max_search_results": 15,  # More research for deep dives
            "max_sources": 8,
        },
        hugo={
            "frontmatter_format": "yaml",
            "default_frontmatter": {
                "draft": False,
                "author": "Suhaib Bin Younis",
            },
        },
    )

    # Create generator
    generator = BlogGenerator(settings=settings)

    print("=" * 70)
    print("🎌 OpenBlog: Anime x AI Deep Dive Generator")
    print("=" * 70)
    print(f"📝 Generating {len(BLOG_TOPICS)} technical deep-dive posts...")
    print(f"📂 Output directory: {output_dir.absolute()}")
    print("=" * 70)

    successful = 0
    failed = 0

    for i, blog_config in enumerate(BLOG_TOPICS, 1):
        topic = blog_config["topic"]
        tags = blog_config["tags"]
        categories = blog_config["categories"]

        print(f"\n[{i}/{len(BLOG_TOPICS)}] Generating: {topic[:60]}...")

        # Simple progress callback
        def on_progress(msg: str) -> None:
            print(f"   ► {msg}")

        try:
            start_time = time.time()

            # Context for Anime x AI Deep Dives
            additional_context = """
            CRITICAL INSTRUCTIONS FOR ANIME x AI DEEP DIVES:

            This blog post must be a **rigorous, intellectual deep dive** exploring the fascinating intersection of Japanese animation (anime) and artificial intelligence.

            **Key Objectives:**
            1.  **Cultural & Technical Depth**: Respect the rich history of anime while explaining AI concepts. Reference specific anime titles, studios, directors (Mamoru Oshii, Hideaki Anno, Makoto Shinkai, etc.), and technical achievements.
            2.  **Dual Expertise**: Write for readers who love both anime AND technology. Balance otaku culture references with solid AI/ML explanations.
            3.  **No Shallow Takes**: Avoid surface-level "AI is cool" or "anime is art" statements. Dig into the HOW and WHY.
            4.  **Academic/Industry Rigor**: Reference actual papers, interviews with studio heads, technical breakdowns of animation software, and AI research from Japan and abroad.

            **Structure & Tone:**
            -   **Tone**: Passionate but analytical. Like a well-researched video essay from a channel like "Mother's Basement" or "Digibro" meets an AI researcher.
            -   **Cultural Sensitivity**: Acknowledge Japanese cultural context. Use proper terminology (sakuga, seiyuu, isekai) with brief explanations.
            -   **Content**:
                -   Start with an engaging hook that connects anime fans to the AI topic.
                -   Include a "Technical Breakdown" section with specifics.
                -   Include "Cultural Impact" analysis.
                -   End with "Future Implications" for both industries.

            **Negative Constraints (The "Veto"):**
            -   AVOID: Generic introductions ("Anime has always been popular...")
            -   AVOID: Shallow AI explanations ("AI is just machine learning...")
            -   AVOID: Dismissive takes on either anime or AI culture
            -   AVOID: Clickbait styling or unnecessary sensationalism

            Make it a piece that both anime fans and AI practitioners would bookmark and share.
            """

            blog = generator.generate(
                topic=topic,
                additional_context=additional_context,
                target_word_count=4000,
                tags=tags,
                categories=categories,
                author="Suhaib Bin Younis",
                draft=False,
                output_dir=output_dir,
                skip_research=False,
                cover_image=blog_config.get("cover_image"),
                progress_callback=on_progress,
            )

            elapsed = time.time() - start_time
            print(f"   ✅ Complete: {blog.word_count} words in {elapsed:.1f}s")
            print(f"   📄 Saved: {Path(blog.file_path).name}")
            successful += 1

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            failed += 1
            continue

        # Small delay between posts
        if i < len(BLOG_TOPICS):
            time.sleep(2)

    # Summary
    print("\n" + "=" * 70)
    print("📊 Generation Complete!")
    print("=" * 70)
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📂 Output: {output_dir.absolute()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
