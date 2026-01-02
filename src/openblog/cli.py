"""Command-line interface for OpenBlog."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

app = typer.Typer(
    name="openblog",
    help="AI-powered blog writing toolkit",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from openblog import __version__

        console.print(f"[bold blue]OpenBlog[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """OpenBlog - AI-powered blog writing toolkit.

    Generate professional, well-researched blog posts with AI.
    """
    pass


@app.command()
def write(
    topic: Annotated[str, typer.Argument(help="Topic for the blog post")],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output directory"),
    ] = Path("./output"),
    words: Annotated[
        int,
        typer.Option("--words", "-w", help="Target word count"),
    ] = 2000,
    tags: Annotated[
        Optional[str],
        typer.Option("--tags", "-t", help="Comma-separated tags"),
    ] = None,
    categories: Annotated[
        Optional[str],
        typer.Option("--categories", "-c", help="Comma-separated categories"),
    ] = None,
    author: Annotated[
        Optional[str],
        typer.Option("--author", "-a", help="Author name"),
    ] = None,
    draft: Annotated[
        bool,
        typer.Option("--draft", "-d", help="Mark as draft"),
    ] = False,
    skip_research: Annotated[
        bool,
        typer.Option("--skip-research", help="Skip research phase"),
    ] = False,
    config_file: Annotated[
        Optional[Path],
        typer.Option("--config", help="Path to config file"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Enable verbose output"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug mode"),
    ] = False,
) -> None:
    """Generate a complete blog post on the given topic.

    Example:
        openblog write "Introduction to Python" --words 3000 --tags python,programming
    """
    from openblog.config.settings import load_settings
    from openblog.generator import BlogGenerator
    from openblog.utils.logging import configure_logging

    # Configure logging
    configure_logging(verbose=verbose, debug=debug)

    # Parse tags and categories
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    category_list = [c.strip() for c in categories.split(",")] if categories else None

    # Load settings
    settings = load_settings(config_file=config_file, verbose=verbose, debug=debug)

    console.print(
        Panel(
            f"[bold]Generating blog post[/bold]\n\n"
            f"Topic: [cyan]{topic}[/cyan]\n"
            f"Target: [yellow]{words}[/yellow] words\n"
            f"Output: [green]{output}[/green]",
            title="[bold blue]OpenBlog[/bold blue]",
            border_style="blue",
        )
    )

    try:
        generator = BlogGenerator(settings=settings)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Generating blog post...", total=None)

            blog = generator.generate(
                topic=topic,
                target_word_count=words,
                tags=tag_list,
                categories=category_list,
                author=author,
                draft=draft,
                output_dir=output,
                skip_research=skip_research,
            )

            progress.update(task, completed=True)

        # Display results
        console.print()
        console.print(
            Panel(
                f"[bold green]✓ Blog post generated successfully![/bold green]\n\n"
                f"Title: [bold]{blog.title}[/bold]\n"
                f"Words: [yellow]{blog.word_count}[/yellow]\n"
                f"Time: [cyan]{blog.generation_time:.2f}s[/cyan]\n"
                f"File: [blue]{blog.file_path}[/blue]",
                title="[bold green]Complete[/bold green]",
                border_style="green",
            )
        )

        if blog.sources:
            console.print(f"\n[dim]Sources used: {len(blog.sources)}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def research(
    topic: Annotated[str, typer.Argument(help="Topic to research")],
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Save research to file"),
    ] = None,
    config_file: Annotated[
        Optional[Path],
        typer.Option("--config", help="Path to config file"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Enable verbose output"),
    ] = False,
) -> None:
    """Research a topic without generating a blog post.

    Example:
        openblog research "Machine Learning trends 2024"
    """
    from openblog.config.settings import load_settings
    from openblog.generator import BlogGenerator
    from openblog.utils.logging import configure_logging

    configure_logging(verbose=verbose)
    settings = load_settings(config_file=config_file)

    console.print(f"[bold]Researching:[/bold] [cyan]{topic}[/cyan]\n")

    try:
        generator = BlogGenerator(settings=settings)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("Researching...", total=None)
            research_summary = generator.research_only(topic)

        console.print(Panel(research_summary, title="Research Summary", border_style="blue"))

        if output:
            output.write_text(research_summary, encoding="utf-8")
            console.print(f"\n[green]Saved to:[/green] {output}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def outline(
    topic: Annotated[str, typer.Argument(help="Topic for the outline")],
    words: Annotated[
        int,
        typer.Option("--words", "-w", help="Target word count"),
    ] = 2000,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Save outline to file"),
    ] = None,
    config_file: Annotated[
        Optional[Path],
        typer.Option("--config", help="Path to config file"),
    ] = None,
) -> None:
    """Generate a blog outline without writing content.

    Example:
        openblog outline "Getting Started with Docker" --words 3000
    """
    from openblog.config.settings import load_settings
    from openblog.generator import BlogGenerator
    from openblog.utils.logging import configure_logging

    configure_logging()
    settings = load_settings(config_file=config_file)

    console.print(f"[bold]Creating outline for:[/bold] [cyan]{topic}[/cyan]\n")

    try:
        generator = BlogGenerator(settings=settings)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("Creating outline...", total=None)
            blog_outline = generator.outline_only(topic, target_word_count=words)

        console.print(Panel(blog_outline.to_markdown(), title="Blog Outline", border_style="blue"))

        if output:
            output.write_text(blog_outline.to_markdown(), encoding="utf-8")
            console.print(f"\n[green]Saved to:[/green] {output}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(name="config")
def show_config(
    show: Annotated[
        bool,
        typer.Option("--show", "-s", help="Show current configuration"),
    ] = True,
    init: Annotated[
        bool,
        typer.Option("--init", "-i", help="Create a new config file"),
    ] = False,
    path: Annotated[
        Path,
        typer.Option("--path", "-p", help="Config file path for init"),
    ] = Path("openblog.yaml"),
) -> None:
    """Show or create configuration.

    Example:
        openblog config --show
        openblog config --init --path my-config.yaml
    """
    from openblog.config.settings import Settings

    if init:
        settings = Settings()
        settings.save_to_file(path)
        console.print(f"[green]Config file created:[/green] {path}")
        return

    if show:
        settings = Settings()

        table = Table(title="OpenBlog Configuration", show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        # LLM settings
        table.add_row("LLM Base URL", settings.llm.base_url)
        table.add_row("LLM Model", settings.llm.model)
        table.add_row("LLM Temperature", str(settings.llm.temperature))
        table.add_row("LLM Max Tokens", str(settings.llm.max_tokens))

        table.add_row("", "")  # Spacer

        # Research settings
        table.add_row("Max Search Results", str(settings.research.max_search_results))
        table.add_row("Max Sources", str(settings.research.max_sources))

        table.add_row("", "")  # Spacer

        # Output settings
        table.add_row("Output Directory", settings.output.directory)
        table.add_row("Output Format", settings.output.format)

        table.add_row("", "")  # Spacer

        # Blog settings
        table.add_row("Min Word Count", str(settings.blog.min_word_count))
        table.add_row("Max Word Count", str(settings.blog.max_word_count))
        table.add_row("Include TOC", str(settings.blog.include_toc))
        table.add_row("Include Citations", str(settings.blog.include_citations))

        console.print(table)


if __name__ == "__main__":
    app()
