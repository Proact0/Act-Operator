"""Act Operator utility functions for project scaffolding and management."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
import tomllib  # Python 3.11+
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from cookiecutter.main import cookiecutter

# Constants
CASTS_DIR = "casts"
CAST_PATH_PREFIX = "./casts/"
PYPROJECT_FILE = "pyproject.toml"
LANGGRAPH_FILE = "langgraph.json"
ENCODING_UTF8 = "utf-8"


class Language(str, Enum):
    """Supported template languages."""

    ENGLISH = "en"
    KOREAN = "kr"

    @property
    def display_name(self) -> str:
        """Get the display name for the language."""
        match self:
            case Language.ENGLISH:
                return "English"
            case Language.KOREAN:
                return "한국어"

    @classmethod
    def from_string(cls, value: str | None) -> Language:
        """Convert string to Language enum.

        Args:
            value: Language code string ("en" or "kr").

        Returns:
            Language enum value.

        Raises:
            ValueError: If value is not a valid language code.
        """
        if not value:
            return cls.ENGLISH

        val = value.strip().lower()
        match val:
            case "en" | "english":
                return cls.ENGLISH
            case "kr" | "korean" | "ko":
                return cls.KOREAN
            case _:
                raise ValueError(
                    f"Unsupported language: '{val}'. Please use 'en' or 'kr'."
                )


@dataclass(slots=True, frozen=True)
class NameVariants:
    """Name variants for Act/Cast projects.

    Attributes:
        raw: Original input string.
        slug: Hyphen-separated lowercase (e.g., "my-project").
        snake: Underscore-separated lowercase (e.g., "my_project").
        title: Title case with spaces (e.g., "My Project").
        pascal: PascalCase without separators (e.g., "MyProject").
    """

    raw: str
    slug: str
    snake: str
    title: str
    pascal: str


def build_name_variants(raw: str) -> NameVariants:
    normalized = raw.strip()
    if not normalized:
        raise ValueError("Empty string cannot be used.")

    # Validate: only allow letters, numbers, spaces, hyphens, and underscores
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9 _-]*$", normalized):
        raise ValueError(
            "Invalid name format. Name must:\n"
            "  - Start with a letter (a-z, A-Z)\n"
            "  - Contain only letters, numbers, spaces, hyphens, and underscores\n"
            "  - Not contain special characters like #, $, %, etc."
        )

    slug = _normalize(normalized, "-")
    snake = _normalize(normalized, "_")
    title = normalized.replace("_", " ").replace("-", " ").title()
    # PascalCase: remove spaces, hyphens, underscores and capitalize each word
    pascal = title.replace(" ", "")

    if not slug or not snake:
        raise ValueError("Please enter a name containing valid English characters.")

    # Additional validation: ensure pascal is a valid Python identifier
    if not pascal.isidentifier():
        raise ValueError(
            f"Name '{normalized}' cannot be converted to a valid Python class name.\n"
            f"Generated class name '{pascal}' is not a valid identifier."
        )

    return NameVariants(
        raw=normalized, slug=slug, snake=snake, title=title, pascal=pascal
    )


def _normalize(value: str, sep: str) -> str:
    """Normalize a string by replacing non-alphanumeric characters with separator.

    Args:
        value: String to normalize.
        sep: Separator character to use ("-" or "_").

    Returns:
        Normalized lowercase string with separator.

    Example:
        >>> _normalize("My Project!", "-")
        'my-project'
        >>> _normalize("My Project!", "_")
        'my_project'
    """
    cleaned = [ch.lower() if ch.isalnum() else sep for ch in value]
    collapsed = "".join(cleaned)
    # Remove consecutive separators
    while sep * 2 in collapsed:
        collapsed = collapsed.replace(sep * 2, sep)
    return collapsed.strip(sep)


def render_cookiecutter_template(
    template_dir: Path,
    target_dir: Path,
    context: dict[str, Any],
    *,
    directory: str | None = None,
) -> None:
    """Render a cookiecutter template.

    The template folder is named {{ cookiecutter.act_slug }}, which ensures
    the output directory uses hyphens (e.g., 'my-act').

    If target_dir already exists, the rendered contents will be moved into it.

    Args:
        template_dir: Path to the cookiecutter template directory.
        target_dir: Destination path for the rendered project.
        context: Cookiecutter context variables.
        directory: Optional subdirectory within template to use.

    Raises:
        FileNotFoundError: If template_dir doesn't exist.
        OSError: If rendering or moving files fails.
    """
    target_dir_exists = target_dir.exists()
    output_root = (
        target_dir.parent
        if not target_dir_exists
        else tempfile.mkdtemp(prefix="act_op_")
    )

    try:
        rendered_path = cookiecutter(
            str(template_dir),
            no_input=True,
            extra_context=context,
            output_dir=str(output_root),
            overwrite_if_exists=True,
            directory=directory,
        )

        rendered_path = Path(rendered_path)

        # If target_dir exists (e.g., current directory), move contents into it
        if target_dir_exists:
            for item in rendered_path.iterdir():
                dest = target_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))
            shutil.rmtree(rendered_path)
        # Otherwise, rename rendered directory to target
        elif rendered_path.resolve() != target_dir.resolve():
            rendered_path.rename(target_dir)
    finally:
        # Clean up temporary directory if we created one
        if target_dir_exists and Path(output_root).exists():
            try:
                shutil.rmtree(output_root)
            except Exception:
                pass


def _get_rendered_cast_dir(rendered_path: Path, cast_snake: str) -> Path:
    """Get the rendered cast directory path.

    Args:
        rendered_path: Root path of rendered project.
        cast_snake: Snake-case name of the cast.

    Returns:
        Path to the rendered cast directory.

    Raises:
        FileNotFoundError: If rendered cast directory is not found.
    """
    source_cast_dir = rendered_path / CASTS_DIR / cast_snake
    if not source_cast_dir.exists():
        raise FileNotFoundError(f"Rendered cast directory not found: {source_cast_dir}")
    return source_cast_dir


def render_cookiecutter_cast_subproject(
    template_root: Path,
    target_dir: Path,
    context: dict[str, Any],
    *,
    post_process: Callable[[Path], None] | None = None,
) -> None:
    """Render a Cast subproject from cookiecutter template.

    Args:
        template_root: Root path of the cookiecutter template.
        target_dir: Destination directory for the Cast.
        context: Cookiecutter context including cast_snake and other variables.
        post_process: Optional callback executed with the rendered root before cleanup.

    Raises:
        FileNotFoundError: If rendered cast directory is not found.
        OSError: If moving files fails.
    """
    if target_dir.exists():
        shutil.rmtree(target_dir)

    output_root = target_dir.parent
    project_slug = target_dir.name

    with tempfile.TemporaryDirectory(prefix="act_op_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        rendered_path = cookiecutter(
            str(template_root),
            no_input=True,
            extra_context={"project_dir": project_slug, **context},
            output_dir=str(tmp_root),
            overwrite_if_exists=True,
        )

        rendered_path = Path(rendered_path)
        source_cast_dir = _get_rendered_cast_dir(rendered_path, context["cast_snake"])

        output_root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_cast_dir), str(target_dir))

        if post_process:
            post_process(rendered_path)


def _read_pyproject_members(pyproject_path: Path) -> list[str]:
    """Read workspace members from pyproject.toml.

    Args:
        pyproject_path: Path to the pyproject.toml file.

    Returns:
        List of workspace member paths.

    Raises:
        RuntimeError: If pyproject.toml is not found.
    """
    if not pyproject_path.exists():
        raise RuntimeError(f"pyproject.toml not found: {pyproject_path}")

    content = pyproject_path.read_text(encoding=ENCODING_UTF8)
    data = tomllib.loads(content)
    workspace = data.get("tool", {}).get("uv", {}).get("workspace", {})
    return list(workspace.get("members", []))


def _format_workspace_members(members: list[str]) -> str:
    """Format workspace members for TOML file.

    Args:
        members: List of workspace member paths.

    Returns:
        Formatted TOML members string.
    """
    member_lines = ",\n".join(f'    "{member}"' for member in members)
    return f"members = [\n{member_lines}\n]"


def _update_pyproject_content(content: str, formatted_members: str) -> str:
    """Update pyproject.toml content with new members.

    Args:
        content: Original pyproject.toml content.
        formatted_members: Formatted members string.

    Returns:
        Updated pyproject.toml content.
    """
    workspace_section = "[tool.uv.workspace]"
    pattern = re.compile(
        r"(\[tool\.uv\.workspace\]\s*)(?:members\s*=\s*\[[^\]]*\])?",
        re.DOTALL,
    )

    if workspace_section in content:
        return pattern.sub(
            lambda match: f"{match.group(1)}{formatted_members}",
            content,
            count=1,
        )

    block = f"\n\n{workspace_section}\n{formatted_members}\n"
    return content.rstrip() + block + "\n"


def update_workspace_members(pyproject_path: Path, new_member: str) -> None:
    """Update the uv workspace members in pyproject.toml.

    Args:
        pyproject_path: Path to the pyproject.toml file.
        new_member: New workspace member path to add (e.g., "casts/new_cast").

    Raises:
        RuntimeError: If pyproject.toml is not found.
        OSError: If file operations fail.
    """
    members = _read_pyproject_members(pyproject_path)

    if new_member in members:
        return

    members.append(new_member)
    members.sort()

    formatted_members = _format_workspace_members(members)
    content = pyproject_path.read_text(encoding=ENCODING_UTF8)
    updated_content = _update_pyproject_content(content, formatted_members)
    pyproject_path.write_text(updated_content, encoding=ENCODING_UTF8)


def _build_graph_reference(cast_snake: str) -> str:
    """Build LangGraph graph reference path.

    Args:
        cast_snake: Snake-case name of the cast.

    Returns:
        Graph reference path string.
    """
    return f"{CAST_PATH_PREFIX}{cast_snake}/graph.py:{cast_snake}_graph"


def select_drawkit_by_language(target_dir: Path, language: str) -> None:
    """Select the appropriate drawkit file based on language and rename to drawkit.xml.

    This function selects drawkit_{language}.xml and renames it to drawkit.xml,
    then removes the other language variant.

    Args:
        target_dir: Root directory of the rendered Act project.
        language: Language code ("en" or "kr").

    Raises:
        FileNotFoundError: If the source drawkit file doesn't exist.
        OSError: If file operations fail.
    """
    source_file = target_dir / f"drawkit_{language}.xml"
    target_file = target_dir / "drawkit.xml"

    # Determine the other language file to remove
    other_lang = "kr" if language == "en" else "en"
    other_file = target_dir / f"drawkit_{other_lang}.xml"

    if not source_file.exists():
        raise FileNotFoundError(f"Drawkit file not found: {source_file}")

    # Rename the selected language file to drawkit.xml
    if target_file.exists():
        target_file.unlink()
    source_file.rename(target_file)

    # Remove the other language file if it exists
    if other_file.exists():
        other_file.unlink()


def update_langgraph_registry(
    langgraph_path: Path,
    cast_slug: str,
    cast_snake: str,
) -> None:
    """Update the LangGraph registry in langgraph.json.

    Note: This function only updates the graphs section. Dependencies are
    expected to use wildcard patterns like [".", "casts/*"] in the template.

    Args:
        langgraph_path: Path to the langgraph.json file.
        cast_slug: Hyphenated cast name used as the graph key.
        cast_snake: Snake-case cast name used in the graph path.

    Raises:
        RuntimeError: If langgraph.json is not found.
        json.JSONDecodeError: If langgraph.json is malformed.
        OSError: If file operations fail.
    """
    if not langgraph_path.exists():
        raise RuntimeError(f"langgraph.json not found: {langgraph_path}")

    content = langgraph_path.read_text(encoding=ENCODING_UTF8)
    payload: dict[str, Any] = json.loads(content)

    # Update graphs only (dependencies use wildcard patterns)
    graphs = payload.setdefault("graphs", {})
    graph_reference = _build_graph_reference(cast_snake)
    graphs.setdefault(cast_slug, graph_reference)

    # Write updated content
    updated_content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    langgraph_path.write_text(updated_content, encoding=ENCODING_UTF8)
