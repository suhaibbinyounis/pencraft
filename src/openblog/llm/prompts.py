"""Prompt templates for OpenBlog agents."""

# Research prompts
RESEARCH_PROMPT = """Research the following topic thoroughly and gather relevant information:

**Topic:** {topic}

{additional_context}

Please provide:
1. Key facts and information about the topic
2. Important statistics or data points (if applicable)
3. Expert opinions or quotes (if available)
4. Historical context or background
5. Current trends or recent developments
6. Common misconceptions to address
7. Related subtopics worth exploring

For each piece of information, note the source if available.

Format your response as a structured research summary."""

# Planning prompts
OUTLINE_PROMPT = """Create a detailed blog post outline based on the following research:

**Topic:** {topic}

**Research Summary:**
{research_summary}

**Target Word Count:** {word_count} words

Please create:
1. A compelling title (SEO-optimized)
2. A meta description (150-160 characters)
3. Suggested tags and categories
4. A detailed outline with:
   - Introduction hook
   - Main sections (3-7 sections depending on topic depth)
   - Subsections for each main section
   - Key points to cover in each section
   - Suggested examples or case studies
   - Conclusion with call to action

Format as a structured outline with clear hierarchy."""

# Writing prompts
INTRODUCTION_PROMPT = """Write an engaging introduction for a blog post with the following details:

**Title:** {title}
**Topic:** {topic}
**Outline:**
{outline}

The introduction should:
1. Start with a hook that grabs attention
2. Establish relevance and importance of the topic
3. Preview what the reader will learn
4. Be 150-250 words

Use markdown formatting. Write in a professional but engaging tone."""

SECTION_PROMPT = """Write the following section for a blog post:

**Blog Title:** {title}
**Section Title:** {section_title}
**Section Outline:**
{section_outline}

**Previously Written Content:**
{previous_content}

**Research Notes:**
{research_notes}

Guidelines:
1. Write detailed, informative content
2. Use examples and explanations
3. Include relevant markdown formatting (lists, code blocks, etc.)
4. Maintain consistency with previous content
5. Target {word_count} words for this section
6. Include citations where appropriate using [^1] format

Write the section content only, without repeating the section title."""

CONCLUSION_PROMPT = """Write a conclusion for the following blog post:

**Title:** {title}
**Topic:** {topic}
**Main Points Covered:**
{main_points}

The conclusion should:
1. Summarize key takeaways (3-5 bullet points)
2. Provide actionable next steps for readers
3. End with a strong closing statement or call to action
4. Be 150-200 words

Use markdown formatting."""

# Citation generation
CITATION_PROMPT = """Based on the following sources used in the blog post, generate a properly formatted references section:

**Sources:**
{sources}

Format the references in a consistent style (e.g., numbered list with title, URL, and access date).
Include a brief description of what each source contributed to the article."""

# SEO optimization
SEO_PROMPT = """Review and optimize the following blog post for SEO:

**Target Keyword:** {keyword}
**Current Content:**
{content}

Provide suggestions for:
1. Keyword placement optimization
2. Header structure improvements
3. Meta description suggestions
4. Internal/external linking opportunities
5. Image alt text suggestions
6. Content gaps to address

Keep suggestions actionable and specific."""
