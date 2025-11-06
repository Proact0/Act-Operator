"""Act Operator utility functions for project scaffolding and configuration.

This module provides utilities for:
- Name normalization and variant generation
- Cookiecutter template rendering
- Project configuration file updates (pyproject.toml, langgraph.json)
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found]

from cookiecutter.main import cookiecutter

# Constants
FILE_ENCODING = "utf-8"
MULTIPLE_SEPARATOR_PATTERN = r"(.)\1+"


@dataclass(slots=True)
class NameVariants:
    """Represents different naming conventions for a single identifier.

    Attributes:
        raw: Original input string (trimmed).
        slug: Kebab-case version (e.g., 'my-project').
        snake: Snake_case version (e.g., 'my_project').
        title: Title case version (e.g., 'My Project').
        pascal: PascalCase version (e.g., 'MyProject').
    """

    raw: str
    slug: str
    snake: str
    title: str
    pascal: str


def build_name_variants(raw: str) -> NameVariants:
    """Generate all naming convention variants from a raw string.

    Args:
        raw: The input string to normalize.

    Returns:
        NameVariants object containing all naming conventions.

    Raises:
        ValueError: If the input is empty or contains no valid characters.

    Example:
        >>> variants = build_name_variants("My Cool Project")
        >>> print(variants.slug)
        'my-cool-project'
    """
    normalized = raw.strip()
    if not normalized:
        raise ValueError("Empty string cannot be used.")

    slug = _normalize(normalized, "-")
    snake = _normalize(normalized, "_")
    title = normalized.replace("_", " ").replace("-", " ").title()
    pascal = title.replace(" ", "")

    if not slug or not snake:
        raise ValueError(
            "Please enter a name containing valid English characters."
        )

    return NameVariants(
        raw=normalized,
        slug=slug,
        snake=snake,
        title=title,
        pascal=pascal,
    )


def _normalize(value: str, separator: str) -> str:
    """Normalize a string to use only alphanumeric characters and separators.

    Converts all non-alphanumeric characters to the specified separator,
    collapses multiple consecutive separators, and strips leading/trailing
    separators.

    Args:
        value: The string to normalize.
        separator: The separator character to use (typically '-' or '_').

    Returns:
        Normalized string in lowercase.

    Example:
        >>> _normalize("Hello  World!", "-")
        'hello-world'
    """
    cleaned = [
        ch.lower() if ch.isalnum() else separator
        for ch in value
    ]
    collapsed = "".join(cleaned)

    # Use regex to collapse multiple consecutive separators
    pattern = re.escape(separator) + "{2,}"
    collapsed = re.sub(pattern, separator, collapsed)

    return collapsed.strip(separator)


def render_cookiecutter_template(
    template_dir: Path,
    target_dir: Path,
    context: dict[str, Any],
    *,
    directory: str | None = None,
) -> None:
    """Render a cookiecutter template to a target directory.

    The template folder should be named {{ cookiecutter.act_slug }}, which
    ensures the output directory uses the slug naming convention.

    Args:
        template_dir: Path to the cookiecutter template directory.
        target_dir: Destination path for the rendered project.
        context: Template variables to pass to cookiecutter.
        directory: Optional subdirectory within the template to render.

    Raises:
        FileExistsError: If target exists and cannot be overwritten.
        OSError: If directory operations fail.

    Note:
        If the target directory exists, it will be removed before rendering.
        The rendered path will be renamed to match target_dir if needed.
    """
    _ensure_clean_target(target_dir)
    output_root = target_dir.parent

    rendered_path = Path(
        cookiecutter(
            str(template_dir),
            no_input=True,
            extra_context=context,
            output_dir=str(output_root),
            overwrite_if_exists=True,
            directory=directory,
        )
    )

    _normalize_rendered_path(rendered_path, target_dir)


def render_cookiecutter_cast_subproject(
    template_root: Path,
    target_dir: Path,
    context: dict[str, Any],
) -> None:
    """Render a cast subproject from a cookiecutter template.

    Creates a new cast within an existing Act project by rendering only the
    cast subdirectory from the full project template.

    Args:
        template_root: Root path of the cookiecutter template.
        target_dir: Destination path for the rendered cast.
        context: Template variables including 'cast_snake' for the cast name.

    Raises:
        FileNotFoundError: If the rendered cast directory is not found.
        OSError: If directory operations fail.

    Note:
        Uses a temporary directory for rendering to extract only the cast
        subdirectory from the full project template.
    """
    _ensure_clean_target(target_dir)
    output_root = target_dir.parent
    project_slug = target_dir.name

    with tempfile.TemporaryDirectory(prefix="act_op_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        rendered_path = Path(
            cookiecutter(
                str(template_root),
                no_input=True,
                extra_context={"project_dir": project_slug, **context},
                output_dir=str(tmp_root),
                overwrite_if_exists=True,
            )
        )

        source_cast_dir = rendered_path / "casts" / context["cast_snake"]
        _validate_cast_directory(source_cast_dir)
        _move_cast_to_target(source_cast_dir, target_dir, output_root)


def update_workspace_members(
    pyproject_path: Path,
    new_member: str,
) -> None:
    """Add a new member to the uv workspace in pyproject.toml.

    Args:
        pyproject_path: Path to the pyproject.toml file.
        new_member: Workspace member path to add (e.g., 'casts/new_cast').

    Raises:
        RuntimeError: If pyproject.toml does not exist.
        OSError: If file operations fail.

    Note:
        Members are automatically sorted alphabetically. If the member
        already exists, no changes are made.
    """
    _validate_file_exists(pyproject_path, "pyproject.toml")

    content = pyproject_path.read_text(encoding=FILE_ENCODING)
    data = tomllib.loads(content)

    members = _extract_workspace_members(data)

    if new_member in members:
        return

    members.append(new_member)
    members.sort()

    updated_content = _update_workspace_section(content, members)
    pyproject_path.write_text(updated_content, encoding=FILE_ENCODING)


def update_langgraph_registry(
    langgraph_path: Path,
    cast_snake: str,
) -> None:
    """Register a new cast in the langgraph.json configuration.

    Args:
        langgraph_path: Path to the langgraph.json file.
        cast_snake: Snake_case name of the cast to register.

    Raises:
        RuntimeError: If langgraph.json does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        OSError: If file operations fail.

    Note:
        Adds the cast to both 'dependencies' and 'graphs' sections.
        Dependencies are automatically sorted alphabetically.
    """
    _validate_file_exists(langgraph_path, "langgraph.json")

    payload = _load_json_file(langgraph_path)

    _add_cast_dependency(payload, cast_snake)
    _add_cast_graph(payload, cast_snake)

    _save_json_file(langgraph_path, payload)


# Private helper functions for better separation of concerns


def _ensure_clean_target(target_dir: Path) -> None:
    """Remove target directory if it exists."""
    if target_dir.exists():
        shutil.rmtree(target_dir)


def _normalize_rendered_path(rendered_path: Path, target_dir: Path) -> None:
    """Rename rendered path to match target if they differ."""
    if rendered_path.resolve() != target_dir.resolve():
        rendered_path.rename(target_dir)


def _validate_cast_directory(cast_dir: Path) -> None:
    """Validate that the cast directory exists after rendering.

    Args:
        cast_dir: Path to the rendered cast directory.

    Raises:
        FileNotFoundError: If the cast directory does not exist.
    """
    if not cast_dir.exists():
        raise FileNotFoundError(
            f"Rendered cast directory not found: {cast_dir}"
        )


def _move_cast_to_target(
    source_dir: Path,
    target_dir: Path,
    output_root: Path,
) -> None:
    """Move the cast directory to the target location.

    Args:
        source_dir: Source cast directory path.
        target_dir: Target destination path.
        output_root: Parent directory for the target.
    """
    output_root.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_dir), str(target_dir))


def _validate_file_exists(file_path: Path, file_name: str) -> None:
    """Validate that a required file exists.

    Args:
        file_path: Path to the file to check.
        file_name: Human-readable name for error messages.

    Raises:
        RuntimeError: If the file does not exist.
    """
    if not file_path.exists():
        raise RuntimeError(f"{file_name} not found: {file_path}")


def _extract_workspace_members(data: dict[str, Any]) -> list[str]:
    """Extract workspace members list from pyproject.toml data.

    Args:
        data: Parsed TOML data structure.

    Returns:
        List of workspace member paths.
    """
    workspace = data.get("tool", {}).get("uv", {}).get("workspace", {})
    return list(workspace.get("members", []))


def _format_members_section(members: list[str]) -> str:
    """Format workspace members as a TOML array.

    Args:
        members: List of workspace member paths.

    Returns:
        Formatted TOML string for the members array.
    """
    member_lines = ",\n".join(f'    "{member}"' for member in members)
    return f"members = [\n{member_lines}\n]"


def _update_workspace_section(content: str, members: list[str]) -> str:
    """Update or add workspace members section in pyproject.toml.

    Args:
        content: Current content of pyproject.toml.
        members: List of workspace member paths.

    Returns:
        Updated content with new members section.
    """
    formatted_members = _format_members_section(members)
    pattern = re.compile(
        r"(\[tool\.uv\.workspace\]\s*)(?:members\s*=\s*\[[^\]]*\])?",
        re.DOTALL,
    )

    if "[tool.uv.workspace]" in content:
        content = pattern.sub(
            lambda m: f"{m.group(1)}{formatted_members}",
            content,
            count=1,
        )
    else:
        workspace_block = (
            f"\n\n[tool.uv.workspace]\n{formatted_members}\n"
        )
        content = content.rstrip() + workspace_block + "\n"

    return content


def _load_json_file(file_path: Path) -> dict[str, Any]:
    """Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        Parsed JSON data as a dictionary.
    """
    return json.loads(file_path.read_text(encoding=FILE_ENCODING))


def _save_json_file(file_path: Path, data: dict[str, Any]) -> None:
    """Save data to a JSON file with formatting.

    Args:
        file_path: Path to the JSON file.
        data: Data to serialize as JSON.
    """
    json_content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    file_path.write_text(json_content, encoding=FILE_ENCODING)


def _add_cast_dependency(payload: dict[str, Any], cast_snake: str) -> None:
    """Add cast dependency to langgraph.json if not present.

    Args:
        payload: Parsed langgraph.json data (modified in place).
        cast_snake: Snake_case name of the cast.
    """
    dependencies = payload.setdefault("dependencies", ["."])
    cast_dependency = f"./casts/{cast_snake}"

    if cast_dependency not in dependencies:
        dependencies.append(cast_dependency)
        dependencies.sort()


def _add_cast_graph(payload: dict[str, Any], cast_snake: str) -> None:
    """Add cast graph entry to langgraph.json if not present.

    Args:
        payload: Parsed langgraph.json data (modified in place).
        cast_snake: Snake_case name of the cast.
    """
    graphs = payload.setdefault("graphs", {})
    graph_reference = f"./casts/{cast_snake}/graph.py:{cast_snake}_graph"
    graphs.setdefault(cast_snake, graph_reference)
