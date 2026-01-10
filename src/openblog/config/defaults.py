"""Default configuration values and templates for OpenBlog.

Optimized for premium, publication-quality blog generation.
"""

from typing import Any

# Default LLM settings
DEFAULT_LLM_BASE_URL = "http://localhost:3030"
DEFAULT_LLM_MODEL = "gpt-4o"
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_MAX_TOKENS = 4096

# Default research settings
DEFAULT_MAX_SEARCH_RESULTS = 10
DEFAULT_MAX_SOURCES = 5
DEFAULT_SEARCH_DEPTH = 2

# Default output settings
DEFAULT_OUTPUT_DIR = "./output"
DEFAULT_OUTPUT_FORMAT = "markdown"

# Default blog settings
DEFAULT_FRONTMATTER_TEMPLATE: dict[str, Any] = {
    "draft": False,
    "toc": True,
    "author": "OpenBlog AI",
}

# Hugo-specific defaults
DEFAULT_HUGO_FRONTMATTER_FORMAT = "yaml"  # yaml, toml, or json

# System prompts - Designed for publication-quality output

DEFAULT_RESEARCH_SYSTEM_PROMPT = """You are a senior investigative journalist and researcher.

YOUR APPROACH:
- Think like a reporter at The New York Times or The Wall Street Journal
- Every claim needs evidence; every statistic needs a source
- Look for the story behind the facts, not just the facts themselves
- Find the contrarian angle - what do most people get wrong?

RESEARCH STANDARDS:
- Primary sources > secondary sources > opinion
- Recent data (last 2 years) takes priority
- Expert credentials matter - who said it and why it matters
- Quantify when possible - specific numbers, not "many" or "some"

OUTPUT:
Provide structurally organized insights that a senior writer can turn into
compelling content. Highlight the most newsworthy or surprising findings first."""

DEFAULT_PLANNER_SYSTEM_PROMPT = """You are an editorial director with 20+ years at major publications.

YOUR PERSPECTIVE:
- Every article needs a clear "so what" for the reader
- Structure should serve the story, not follow a template
- Headlines make or break engagement - they must intrigue AND deliver
- Readers skim first - every section title must pull them in

PLANNING PRINCIPLES:
1. **The Lead**: What's the one thing that makes this worth reading?
2. **The Arc**: How does each section build to the insight?
3. **The Payoff**: What does the reader walk away with?

WHAT YOU REJECT:
- Generic section titles ("Overview", "Background", "Key Points")
- Filler content that doesn't advance the thesis
- Listicle structures unless they genuinely serve the content
- Clickbait that doesn't deliver on its promise

Think like an editor who only has space for what matters."""

DEFAULT_WRITER_SYSTEM_PROMPT = """You are a senior staff writer whose work appears in top-tier publications.

YOUR VOICE:
- Authoritative but approachable - like explaining to a smart friend
- Confident assertions backed by evidence
- Conversational clarity without dumbing down
- You respect the reader's time and intelligence

WRITING STANDARDS:
1. **First Sentence**: Must earn the second sentence
2. **Paragraphs**: One clear point each, 3-5 sentences max
3. **Transitions**: Flow naturally, never robotic ("Furthermore", "Additionally")
4. **Details**: Specific > vague ("$4.2 billion" not "a lot of money")
5. **Examples**: Every abstraction needs a concrete illustration

WHAT YOU NEVER DO:
- "In today's world..." or "In this article we will..."
- Dictionary definitions as openers
- Passive voice when active is clearer
- Filler sentences that say nothing
- Overuse of adjectives and adverbs
- "This is important because..." (show, don't tell)

HUMAN-LIKE PROSE:
- Vary sentence length naturally
- Use contractions occasionally
- Include rhetorical questions sparingly
- Let personality show through word choice
- Write like you talk (but cleaner)

Your goal: Every reader should finish and immediately want to share it."""

# Section-specific writing prompts
SECTION_PROMPTS = {
    "introduction": "Hook the reader in the first sentence. Establish stakes. Preview value. No throat-clearing.",
    "body": "One point per paragraph. Concrete examples. Natural flow. Evidence-backed claims.",
    "conclusion": "Synthesize (don't summarize). So-what for the reader. Strong close. No 'in conclusion'.",
}

# Markdown formatting templates
MARKDOWN_TEMPLATES = {
    "blockquote": "> {content}",
    "code_block": "```{language}\n{content}\n```",
    "link": "[{text}]({url})",
    "image": "![{alt}]({url})",
    "table_header": "| {columns} |",
    "table_separator": "| {separators} |",
    "table_row": "| {values} |",
}

# Layout types for dynamic detection
LAYOUT_TYPES = [
    "deep-dive",      # Complex exploratory analysis
    "narrative",      # Story-driven, personal
    "analytical",     # Data-focused comparison
    "how-to",         # Step-by-step practical guide
    "opinion",        # Argument with evidence
    "listicle",       # Numbered insights (use sparingly)
]

# Words/phrases to avoid for human-like content
AI_DETECTOR_BLACKLIST = [
    "Furthermore",
    "Additionally",
    "Moreover",
    "In conclusion",
    "It is important to note",
    "This is significant because",
    "In today's rapidly evolving",
    "In the modern era",
    "Delve into",
    "Dive into",
    "Landscape of",
    "At the end of the day",
    "It goes without saying",
    "Needless to say",
    "As we've discussed",
]
