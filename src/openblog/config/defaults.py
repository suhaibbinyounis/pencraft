"""Default configuration values and templates for OpenBlog."""

from typing import Any

# Default LLM settings
DEFAULT_LLM_BASE_URL = "http://localhost:3030"
DEFAULT_LLM_MODEL = "gpt-4.1"
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

# Default prompt templates
DEFAULT_RESEARCH_SYSTEM_PROMPT = """You are a professional research assistant. Your task is to:
1. Search for relevant information on the given topic
2. Extract key facts, statistics, and insights
3. Identify credible sources and citations
4. Summarize findings in a structured format

Be thorough, accurate, and always cite your sources."""

DEFAULT_PLANNER_SYSTEM_PROMPT = """You are an expert blog content strategist. Your task is to:
1. Analyze the research provided
2. Create a comprehensive blog outline with clear sections
3. Suggest compelling headlines and subheadings
4. Plan for SEO optimization with keywords
5. Structure content for maximum reader engagement

Create detailed, actionable outlines that writers can follow."""

DEFAULT_WRITER_SYSTEM_PROMPT = """You are a professional blog writer and content creator. Your task is to:
1. Write engaging, detailed blog content following the provided outline
2. Use proper markdown formatting (headers, lists, code blocks, etc.)
3. Include citations and references where appropriate
4. Maintain a consistent, professional tone
5. Optimize for readability and SEO

Write comprehensive, well-researched content that provides real value to readers."""

# Section-specific writing prompts
SECTION_PROMPTS = {
    "introduction": "Write an engaging introduction that hooks the reader and previews the main points.",
    "body": "Write detailed, informative content with examples and explanations.",
    "conclusion": "Summarize key takeaways and provide actionable next steps for the reader.",
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
