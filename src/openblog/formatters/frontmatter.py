"""Frontmatter generation for Hugo-compatible markdown."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import yaml


class FrontmatterGenerator:
    """Generator for Hugo-compatible frontmatter.

    Creates properly formatted frontmatter in YAML, TOML, or JSON format
    with configurable fields.
    """

    def __init__(
        self,
        format: str = "yaml",
        default_fields: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the frontmatter generator.

        Args:
            format: Output format (yaml, toml, json).
            default_fields: Default fields to include in every frontmatter.
        """
        self.format = format.lower()
        self.default_fields = default_fields or {}

        if self.format not in ("yaml", "toml", "json"):
            raise ValueError(f"Unsupported format: {self.format}")

    def generate(
        self,
        title: str,
        *,
        description: str = "",
        date: datetime | str | None = None,
        draft: bool = False,
        tags: list[str] | None = None,
        categories: list[str] | None = None,
        author: str | None = None,
        slug: str | None = None,
        weight: int | None = None,
        featured_image: str | None = None,
        toc: bool = True,
        **extra_fields: Any,
    ) -> str:
        """Generate frontmatter string.

        Args:
            title: Post title.
            description: Meta description.
            date: Publication date (uses now if None).
            draft: Whether post is a draft.
            tags: List of tags.
            categories: List of categories.
            author: Author name.
            slug: URL slug.
            weight: Sort weight.
            featured_image: Featured image path.
            toc: Whether to show table of contents.
            **extra_fields: Additional frontmatter fields.

        Returns:
            Formatted frontmatter string with delimiters.
        """
        # Handle date
        if date is None:
            date = datetime.now(timezone.utc)
        if isinstance(date, datetime):
            # Format: 2026-01-10T10:48:53.098Z
            # Use 3 digits for milliseconds and always append Z (UTC)
            date_str = date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        else:
            date_str = date

        # Build frontmatter dictionary
        fm: dict[str, Any] = {
            "title": title,
            "date": date_str,
            "draft": draft,
        }

        if description:
            fm["description"] = description

        if tags:
            fm["tags"] = tags

        if categories:
            fm["categories"] = categories

        if author:
            fm["author"] = author

        if slug:
            fm["slug"] = slug

        if weight is not None:
            fm["weight"] = weight

        if featured_image:
            fm["featured_image"] = featured_image

        if toc:
            fm["toc"] = toc

        # Add default fields (only if not already set)
        for key, value in self.default_fields.items():
            if key not in fm:
                fm[key] = value

        # Add extra fields
        fm.update(extra_fields)

        # Format output
        return self._format_frontmatter(fm)

    def _format_frontmatter(self, data: dict[str, Any]) -> str:
        """Format frontmatter dictionary to string.

        Args:
            data: Frontmatter data.

        Returns:
            Formatted frontmatter with delimiters.
        """
        if self.format == "yaml":
            return self._format_yaml(data)
        elif self.format == "toml":
            return self._format_toml(data)
        else:  # json
            return self._format_json(data)

    def _format_yaml(self, data: dict[str, Any]) -> str:
        """Format as YAML frontmatter.

        Args:
            data: Frontmatter data.

        Returns:
            YAML frontmatter with --- delimiters.
        """

        # Custom Dumper to ensure proper list indentation for Hugo compatibility
        class HugoDumper(yaml.SafeDumper):
            pass

        # Force all strings to be unquoted single-line (no folding/literal blocks)
        def str_representer(dumper: yaml.Dumper, data: str) -> yaml.Node:
            # Replace newlines with spaces to force single line
            clean_data = data.replace("\n", " ").strip()
            return dumper.represent_scalar("tag:yaml.org,2002:str", clean_data)

        HugoDumper.add_representer(str, str_representer)

        yaml_str = yaml.dump(
            data,
            Dumper=HugoDumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=10000,  # Prevent line wrapping
        )

        # Post-process to fix list indentation for Hugo compatibility
        # Hugo expects:
        #   tags:
        #     - item1
        # But yaml.dump produces:
        #   tags:
        #   - item1
        lines = yaml_str.split("\n")
        fixed_lines = []
        in_list = False

        for line in lines:
            # Check if this line starts a list key (ends with just ':')
            if line and not line.startswith(" ") and line.endswith(":"):
                in_list = True
                fixed_lines.append(line)
                continue

            # If we're in a list and this is a list item, add indentation
            if in_list and line.startswith("- "):
                fixed_lines.append("  " + line)
                continue

            # If line doesn't start with space or dash, we're out of the list
            if line and not line.startswith(" ") and not line.startswith("-"):
                in_list = False

            fixed_lines.append(line)

        yaml_str = "\n".join(fixed_lines)
        return f"---\n{yaml_str}---\n"

    def _format_toml(self, data: dict[str, Any]) -> str:
        """Format as TOML frontmatter.

        Args:
            data: Frontmatter data.

        Returns:
            TOML frontmatter with +++ delimiters.
        """
        lines = []
        for key, value in data.items():
            if isinstance(value, bool):
                lines.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, int):
                lines.append(f"{key} = {value}")
            elif isinstance(value, list):
                items = ", ".join(f'"{item}"' for item in value)
                lines.append(f"{key} = [{items}]")
            else:
                # Escape quotes in string values
                escaped = str(value).replace('"', '\\"')
                lines.append(f'{key} = "{escaped}"')

        return "+++\n" + "\n".join(lines) + "\n+++\n"

    def _format_json(self, data: dict[str, Any]) -> str:
        """Format as JSON frontmatter.

        Args:
            data: Frontmatter data.

        Returns:
            JSON frontmatter with braces.
        """
        import json

        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        return json_str + "\n"

    def parse(self, content: str) -> tuple[dict[str, Any], str]:
        """Parse frontmatter from markdown content.

        Args:
            content: Full markdown content with frontmatter.

        Returns:
            Tuple of (frontmatter_dict, body_content).
        """
        content = content.strip()

        # Try YAML (---)
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                yaml_content = content[3:end].strip()
                body = content[end + 3 :].strip()
                try:
                    fm = yaml.safe_load(yaml_content) or {}
                    return fm, body
                except yaml.YAMLError:
                    pass

        # Try TOML (+++)
        if content.startswith("+++"):
            end = content.find("+++", 3)
            if end != -1:
                toml_content = content[3:end].strip()
                body = content[end + 3 :].strip()
                # Simple TOML parsing
                fm = self._parse_simple_toml(toml_content)
                return fm, body

        # Try JSON ({)
        if content.startswith("{"):
            # Find matching closing brace
            brace_count = 0
            end = 0
            for i, char in enumerate(content):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end = i
                        break

            if end > 0:
                import json

                json_content = content[: end + 1]
                body = content[end + 1 :].strip()
                try:
                    fm = json.loads(json_content)
                    return fm, body
                except json.JSONDecodeError:
                    pass

        # No frontmatter found
        return {}, content

    def _parse_simple_toml(self, content: str) -> dict[str, Any]:
        """Parse simple TOML content.

        Args:
            content: TOML content string.

        Returns:
            Parsed dictionary.
        """
        result: dict[str, Any] = {}

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Parse value type
                if value.lower() == "true":
                    result[key] = True
                elif value.lower() == "false":
                    result[key] = False
                elif value.startswith("[") and value.endswith("]"):
                    # Array
                    items = value[1:-1].split(",")
                    result[key] = [
                        item.strip().strip('"').strip("'") for item in items if item.strip()
                    ]
                elif (
                    value.startswith('"')
                    and value.endswith('"')
                    or value.startswith("'")
                    and value.endswith("'")
                ):
                    result[key] = value[1:-1]
                else:
                    try:
                        result[key] = int(value)
                    except ValueError:
                        try:
                            result[key] = float(value)
                        except ValueError:
                            result[key] = value

        return result

    def update_frontmatter(
        self,
        content: str,
        updates: dict[str, Any],
    ) -> str:
        """Update frontmatter in existing content.

        Args:
            content: Full markdown content with frontmatter.
            updates: Fields to update.

        Returns:
            Content with updated frontmatter.
        """
        fm, body = self.parse(content)
        fm.update(updates)
        new_fm = self._format_frontmatter(fm)
        return new_fm + "\n" + body
