"""Act Operator 유틸리티 함수."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for older versions
    import tomli as tomllib  # type: ignore

import tempfile

from cookiecutter.main import cookiecutter


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
    The target_dir should already be set to use act.slug in the calling code.

    Args:
        template_dir: Path to the cookiecutter template directory.
        target_dir: Destination path for the rendered project.
        context: Cookiecutter context variables.
        directory: Optional subdirectory within template to use.

    Raises:
        FileNotFoundError: If template_dir doesn't exist.
        OSError: If rendering or moving files fails.
    """
    if target_dir.exists():
        shutil.rmtree(target_dir)

    output_root = target_dir.parent

    rendered_path = cookiecutter(
        str(template_dir),
        no_input=True,
        extra_context=context,
        output_dir=str(output_root),
        overwrite_if_exists=True,
        directory=directory,
    )

    rendered_path = Path(rendered_path)

    # Normally rendered_path should equal target_dir, but rename if needed
    if rendered_path.resolve() != target_dir.resolve():
        rendered_path.rename(target_dir)


def render_cookiecutter_cast_subproject(
    template_root: Path,
    target_dir: Path,
    context: dict[str, Any],
) -> None:
    """Render a Cast subproject from cookiecutter template.

    Args:
        template_root: Root path of the cookiecutter template.
        target_dir: Destination directory for the Cast.
        context: Cookiecutter context including cast_snake and other variables.

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

        source_cast_dir = rendered_path / "casts" / context["cast_snake"]
        if not source_cast_dir.exists():
            raise FileNotFoundError(
                f"Rendered cast directory not found: {source_cast_dir}"
            )

        # Ensure parent exists
        output_root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_cast_dir), str(target_dir))


def update_workspace_members(pyproject_path: Path, new_member: str) -> None:
    """Update the uv workspace members in pyproject.toml.

    Args:
        pyproject_path: Path to the pyproject.toml file.
        new_member: New workspace member path to add (e.g., "casts/new_cast").

    Raises:
        RuntimeError: If pyproject.toml is not found.
        OSError: If file operations fail.
    """
    if not pyproject_path.exists():
        raise RuntimeError(f"pyproject.toml not found: {pyproject_path}")

    content = pyproject_path.read_text(encoding="utf-8")
    data = tomllib.loads(content)

    workspace = data.get("tool", {}).get("uv", {}).get("workspace", {})
    members: list[str] = list(workspace.get("members", []))

    if new_member in members:
        return

    members.append(new_member)
    members.sort()

    member_lines = ",\n".join(f'    "{member}"' for member in members)
    formatted_members = f"members = [\n{member_lines}\n]"

    pattern = re.compile(
        r"(\[tool\.uv\.workspace\]\s*)(?:members\s*=\s*\[[^\]]*\])?", re.DOTALL
    )

    if "[tool.uv.workspace]" in content:

        def replacer(match: re.Match[str]) -> str:
            return f"{match.group(1)}{formatted_members}"

        content = pattern.sub(replacer, content, count=1)
    else:
        block = f"\n\n[tool.uv.workspace]\n{formatted_members}\n"
        content = content.rstrip() + block + "\n"

    pyproject_path.write_text(content, encoding="utf-8")


def update_langgraph_registry(
    langgraph_path: Path,
    cast_snake: str,
) -> None:
    """Update the LangGraph registry in langgraph.json.

    Args:
        langgraph_path: Path to the langgraph.json file.
        cast_snake: Snake-case name of the cast to register.

    Raises:
        RuntimeError: If langgraph.json is not found.
        json.JSONDecodeError: If langgraph.json is malformed.
        OSError: If file operations fail.
    """
    if not langgraph_path.exists():
        raise RuntimeError(f"langgraph.json not found: {langgraph_path}")

    payload: dict[str, Any] = json.loads(langgraph_path.read_text(encoding="utf-8"))

    dependencies = payload.setdefault("dependencies", ["."])
    cast_dependency = f"./casts/{cast_snake}"
    if cast_dependency not in dependencies:
        dependencies.append(cast_dependency)
        dependencies.sort()

    graphs = payload.setdefault("graphs", {})
    graph_reference = f"./casts/{cast_snake}/graph.py:{cast_snake}_graph"
    graphs.setdefault(cast_snake, graph_reference)

    langgraph_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
