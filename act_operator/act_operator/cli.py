"""Act Operator CLI entrypoints.

This module provides command-line interface functionality for:
- Creating new Act projects with scaffolding
- Adding Cast subprojects to existing Act projects
- Managing project configuration and templates
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import typer
from rich.console import Console
from rich.table import Table

from .utils import (
    build_name_variants,
    render_cookiecutter_cast_subproject,
    render_cookiecutter_template,
    update_langgraph_registry,
    update_workspace_members,
)

# Constants
SUPPORTED_LANGUAGES: Final[tuple[str, ...]] = ("en", "kr")
DEFAULT_LANGUAGE: Final[str] = "en"
LANGUAGE_DISPLAY_NAMES: Final[dict[str, str]] = {
    "en": "English",
    "kr": "한국어",
}

REQUIRED_ACT_FILES: Final[tuple[str, ...]] = (
    "pyproject.toml",
    "langgraph.json",
    "casts",
    "casts/base_node.py",
    "casts/base_graph.py",
)

# Console for rich output
console = Console()
app = typer.Typer(help="Act Operator", invoke_without_command=True)

# Typer options
PATH_OPTION = typer.Option(
    None,
    "--path",
    "-p",
    help="Directory where the new Act project will be created",
    file_okay=False,
    dir_okay=True,
    writable=True,
    resolve_path=True,
)
ACT_NAME_OPTION = typer.Option(
    None,
    "--act-name",
    "-a",
    help="Display name of the Act project",
)
CAST_NAME_OPTION = typer.Option(
    None,
    "--cast-name",
    "-c",
    help="Display name of the initial Cast Graph",
)
LANG_OPTION = typer.Option(
    None,
    "--lang",
    "-l",
    help="Language for scaffolded docs (en|kr)",
)

CAST_ACT_PATH_OPTION = typer.Option(
    Path.cwd(),
    "--path",
    "-p",
    help="Path to an existing Act project",
    file_okay=False,
    dir_okay=True,
    exists=True,
    resolve_path=True,
)
NEW_CAST_NAME_OPTION = typer.Option(
    None,
    "--cast-name",
    "-c",
    help="Display name of the Cast to add",
)
NEW_CAST_LANG_OPTION = typer.Option(
    DEFAULT_LANGUAGE,
    "--lang",
    "-l",
    help="Language for scaffolded cast docs (en|kr)",
)


# Error handling utilities


def _exit_with_error(message: str, code: int = 1) -> None:
    """Display an error message and exit with a non-zero status code.

    Args:
        message: Error message to display.
        code: Exit status code (default: 1).
    """
    console.print(f"[red]{message}[/red]")
    raise typer.Exit(code=code)


def _handle_value_error(error: ValueError) -> None:
    """Handle ValueError by displaying the error and exiting.

    Args:
        error: The ValueError to handle.
    """
    _exit_with_error(str(error))


def _handle_os_error(message: str, error: OSError) -> None:
    """Handle OSError by displaying context and exiting.

    Args:
        message: Context message describing the operation that failed.
        error: The OSError that occurred.
    """
    _exit_with_error(f"{message}: {error}")


# Input resolution utilities


def _resolve_path(path_option: Path | None) -> tuple[Path, bool]:
    """Resolve the target path for project creation.

    Args:
        path_option: Optional path provided via command-line option.

    Returns:
        Tuple of (resolved_path, was_custom_path).
        was_custom_path is True if the user provided a non-default path.
    """
    if path_option is not None:
        return path_option.expanduser().resolve(), True

    value = typer.prompt(
        "📂 Please specify the path to create the new Act project",
        default=".",
        show_default=True,
    )
    is_custom = value != "."
    path = Path(value).expanduser().resolve()
    return path, is_custom


def _resolve_name(prompt_message: str, value: str | None) -> str:
    """Resolve a required string value by prompting if not provided.

    Args:
        prompt_message: Message to display when prompting.
        value: Optional pre-provided value.

    Returns:
        The resolved string value (guaranteed non-empty).
    """
    if value:
        return value.strip()

    while True:
        prompted = typer.prompt(prompt_message).strip()
        if prompted:
            return prompted
        console.print("[red]A value is required.[/red]")


def _normalize_lang(value: str | None) -> str:
    """Normalize and validate a language code.

    Args:
        value: Optional language code to normalize.

    Returns:
        Normalized language code (lowercase).

    Raises:
        typer.Exit: If the language code is unsupported.
    """
    if not value:
        return DEFAULT_LANGUAGE

    normalized = value.strip().lower()
    if normalized in SUPPORTED_LANGUAGES:
        return normalized

    _exit_with_error(
        f"Unsupported language: '{normalized}'. "
        f"Please use {' or '.join(repr(lang) for lang in SUPPORTED_LANGUAGES)}."
    )


def _resolve_language(language: str | None) -> str:
    """Resolve the language by validating or using default.

    Args:
        language: Optional language code provided.

    Returns:
        Display name of the selected language.

    Raises:
        typer.Exit: If the provided language is unsupported.
    """
    # Default to English if no language is provided
    if language is None or not language.strip():
        return LANGUAGE_DISPLAY_NAMES[DEFAULT_LANGUAGE]

    if language in SUPPORTED_LANGUAGES:
        return LANGUAGE_DISPLAY_NAMES[language]

    _exit_with_error(
        f"Unsupported language: '{language}'. "
        f"Please use {' or '.join(repr(lang) for lang in SUPPORTED_LANGUAGES)}."
    )


# Path and directory utilities


def _compute_target_directory(
    base_dir: Path,
    act_slug: str,
    path_was_custom: bool,
) -> Path:
    """Compute the target directory for the new project.

    Args:
        base_dir: Base directory provided by user.
        act_slug: Slug (kebab-case) name for the Act project.
        path_was_custom: Whether the user provided a custom path.

    Returns:
        Resolved target directory path.
    """
    if path_was_custom and base_dir != Path.cwd():
        return base_dir.parent / act_slug
    return Path.cwd() / act_slug


def _ensure_directory_is_empty(directory: Path) -> None:
    """Ensure a directory is empty before using it.

    Args:
        directory: Directory to check.

    Raises:
        typer.Exit: If the directory exists and is not empty.
    """
    if directory.exists() and any(directory.iterdir()):
        _exit_with_error(
            "❌ The specified directory already exists and is not empty. "
            "Aborting to prevent overwriting files."
        )


def _create_directory(directory: Path) -> None:
    """Create a directory, handling errors gracefully.

    Args:
        directory: Directory to create.

    Raises:
        typer.Exit: If directory creation fails.
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        _handle_os_error("Unable to create target directory", error)


def _validate_scaffold_root() -> Path:
    """Validate that scaffold resources exist.

    Returns:
        Path to the scaffold root directory.

    Raises:
        typer.Exit: If scaffold resources are not found.
    """
    scaffold_root = Path(__file__).resolve().parent / "scaffold"
    if not scaffold_root.exists():
        _exit_with_error("Scaffold resources not found.")
    return scaffold_root


# Project generation utilities


def _build_project_context(
    act_raw: str,
    cast_raw: str,
    language: str,
) -> tuple[dict[str, str], str, str, str]:
    """Build context dictionary for template rendering.

    Args:
        act_raw: Raw Act name.
        cast_raw: Raw Cast name.
        language: Display language name.

    Returns:
        Tuple of (context_dict, act_slug, cast_slug, cast_snake).

    Raises:
        typer.Exit: If name validation fails.
    """
    try:
        act = build_name_variants(act_raw)
        cast = build_name_variants(cast_raw)
    except ValueError as error:
        _handle_value_error(error)

    context = {
        "act_name": act.title,
        "act_slug": act.slug,
        "act_snake": act.snake,
        "cast_name": cast.title,
        "cast_slug": cast.slug,
        "cast_snake": cast.snake,
        "cast_pascal": cast.pascal,
        "language": language,
    }

    return context, act.slug, cast.slug, cast.snake


def _normalize_cast_directory(
    target_dir: Path,
    cast_slug: str,
    cast_snake: str,
) -> None:
    """Normalize cast directory name from hyphenated to underscored.

    Cookiecutter may generate hyphenated directory names, but we prefer
    snake_case for Python package directories.

    Args:
        target_dir: Root directory of the generated project.
        cast_slug: Hyphenated cast name.
        cast_snake: Snake_case cast name.

    Raises:
        typer.Exit: If directory operations fail.
    """
    casts_dir = target_dir / "casts"
    old_cast_dir = casts_dir / cast_slug
    new_cast_dir = casts_dir / cast_snake

    if not (old_cast_dir.exists() and not new_cast_dir.exists()):
        return

    try:
        old_cast_dir.rename(new_cast_dir)
        _update_pyproject_cast_path(target_dir, cast_slug, cast_snake)
        _update_langgraph_cast_path(target_dir, cast_slug, cast_snake)
    except OSError as error:
        _handle_os_error("Failed to normalize cast directory", error)


def _update_pyproject_cast_path(
    target_dir: Path,
    old_name: str,
    new_name: str,
) -> None:
    """Update cast path references in pyproject.toml.

    Args:
        target_dir: Project root directory.
        old_name: Old cast directory name.
        new_name: New cast directory name.
    """
    pyproject = target_dir / "pyproject.toml"
    if not pyproject.exists():
        return

    content = pyproject.read_text(encoding="utf-8")
    updated = content.replace(f"casts/{old_name}", f"casts/{new_name}")
    pyproject.write_text(updated, encoding="utf-8")


def _update_langgraph_cast_path(
    target_dir: Path,
    old_name: str,
    new_name: str,
) -> None:
    """Update cast path and graph key references in langgraph.json.

    Args:
        target_dir: Project root directory.
        old_name: Old cast directory name.
        new_name: New cast directory name.
    """
    langgraph = target_dir / "langgraph.json"
    if not langgraph.exists():
        return

    content = langgraph.read_text(encoding="utf-8")
    # Update both the graph key and the path references
    updated = content.replace(f'"{old_name}"', f'"{new_name}"')
    updated = updated.replace(f"/casts/{old_name}/", f"/casts/{new_name}/")
    langgraph.write_text(updated, encoding="utf-8")


def _display_project_summary(
    target_dir: Path,
    act_title: str,
    cast_title: str,
    language: str,
) -> None:
    """Display a summary table of the created project.

    Args:
        target_dir: Path where the project was created.
        act_title: Display name of the Act.
        cast_title: Display name of the Cast.
        language: Display language name.
    """
    table = Table(show_header=False)
    table.add_row("Act", act_title)
    table.add_row("Cast", cast_title)
    table.add_row("Language", language)
    table.add_row("Location", str(target_dir))
    console.print(table)
    console.print("[bold green]Act project created successfully![/bold green]")

    _display_project_contents(target_dir)


def _display_project_contents(target_dir: Path) -> None:
    """Display the contents of the created project directory.

    Args:
        target_dir: Path to the project directory.
    """
    try:
        if target_dir.exists():
            entries = ", ".join(sorted(p.name for p in target_dir.iterdir()))
            console.print(f"[dim]act project entries: {entries}[/dim]")
    except Exception:
        # Silently ignore if we can't list directory contents
        pass


def _generate_project(
    *,
    path: Path | None,
    act_name: str | None,
    cast_name: str | None,
    language: str | None,
) -> None:
    """Generate a new Act project with scaffolding.

    Args:
        path: Optional custom path for the project.
        act_name: Optional display name for the Act.
        cast_name: Optional display name for the initial Cast.
        language: Optional language code for templates.

    Raises:
        typer.Exit: If any step of project generation fails.
    """
    base_dir, path_was_custom = _resolve_path(path)

    # Derive act name from directory if custom path provided
    if act_name is None and path_was_custom:
        derived_name = base_dir.name or base_dir.resolve().name
        act_name = derived_name

    act_raw = _resolve_name("🚀 Please enter a name for the new Act", act_name)
    cast_raw = _resolve_name(
        "🌟 Please enter a name for the first Cast",
        cast_name,
    )
    lang = _resolve_language(language)

    context, act_slug, cast_slug, cast_snake = _build_project_context(
        act_raw,
        cast_raw,
        lang,
    )

    target_dir = _compute_target_directory(base_dir, act_slug, path_was_custom)
    _ensure_directory_is_empty(target_dir)
    _create_directory(target_dir)

    scaffold_root = _validate_scaffold_root()

    console.print("[bold green]Starting Act project scaffolding...[/bold green]")

    try:
        render_cookiecutter_template(scaffold_root, target_dir, context)
    except FileExistsError as error:
        _exit_with_error(str(error))

    _normalize_cast_directory(target_dir, cast_slug, cast_snake)
    _display_project_summary(target_dir, context["act_name"], context["cast_name"], lang)


# Cast generation utilities


def _ensure_act_project(act_path: Path) -> None:
    """Validate that a directory is a valid Act project.

    Args:
        act_path: Path to check.

    Raises:
        typer.Exit: If required files/directories are missing.
    """
    for relative_path in REQUIRED_ACT_FILES:
        full_path = act_path / relative_path
        if not full_path.exists():
            _exit_with_error(
                f"The path does not look like a valid Act project: {full_path}"
            )


def _generate_cast_project(
    *,
    act_path: Path,
    cast_name: str,
    language: str,
) -> None:
    """Generate a new Cast subproject within an existing Act project.

    Args:
        act_path: Path to the Act project root.
        cast_name: Display name for the new Cast.
        language: Language code for templates.

    Raises:
        typer.Exit: If any step of cast generation fails.
    """
    act_variants = build_name_variants(act_path.name)
    cast_variants = build_name_variants(cast_name)

    casts_dir = act_path / "casts"
    target_dir = casts_dir / cast_variants.snake

    _ensure_directory_is_empty(target_dir)

    scaffold_root = _validate_scaffold_root()

    context = {
        "act_name": act_variants.title,
        "act_slug": act_variants.slug,
        "act_snake": act_variants.snake,
        "cast_name": cast_variants.title,
        "cast_snake": cast_variants.snake,
        "cast_pascal": cast_variants.pascal,
        "language": _normalize_lang(language),
    }

    render_cookiecutter_cast_subproject(scaffold_root, target_dir, context)

    workspace_member = f"casts/{cast_variants.snake}"
    _update_workspace(act_path, workspace_member)
    _update_langgraph(act_path, cast_variants.snake)

    console.print(
        f"[bold green]Cast '{cast_variants.snake}' "
        "added successfully![/bold green]"
    )


def _update_workspace(act_path: Path, member: str) -> None:
    """Update workspace members in pyproject.toml.

    Args:
        act_path: Path to the Act project root.
        member: Workspace member path to add.

    Raises:
        typer.Exit: If the update fails.
    """
    try:
        update_workspace_members(act_path / "pyproject.toml", member)
    except RuntimeError as error:
        _exit_with_error(f"Failed to update pyproject.toml: {error}")


def _update_langgraph(act_path: Path, cast_snake: str) -> None:
    """Update langgraph.json with the new cast.

    Args:
        act_path: Path to the Act project root.
        cast_snake: Snake_case name of the cast.

    Raises:
        typer.Exit: If the update fails.
    """
    try:
        update_langgraph_registry(act_path / "langgraph.json", cast_snake)
    except RuntimeError as error:
        _exit_with_error(f"Failed to update langgraph.json: {error}")


# CLI Commands


@app.callback()
def root(
    ctx: typer.Context,
    path: Path | None = PATH_OPTION,
    act_name: str | None = ACT_NAME_OPTION,
    cast_name: str | None = CAST_NAME_OPTION,
    lang: str | None = LANG_OPTION,
) -> None:
    """Act Operator CLI root callback.

    Stores options in context and generates a project if no subcommand is invoked.

    Args:
        ctx: Typer context for passing data to subcommands.
        path: Optional custom path for project creation.
        act_name: Optional Act display name.
        cast_name: Optional initial Cast display name.
        lang: Optional language code.
    """
    ctx.obj = {
        "path": path,
        "act_name": act_name,
        "cast_name": cast_name,
        "lang": lang,
    }

    if ctx.invoked_subcommand is not None:
        return

    _generate_project(
        path=path,
        act_name=act_name,
        cast_name=cast_name,
        language=lang,
    )


@app.command("new")
def new_command(
    ctx: typer.Context,
    path: Path | None = PATH_OPTION,
    act_name: str | None = ACT_NAME_OPTION,
    cast_name: str | None = CAST_NAME_OPTION,
    lang: str | None = LANG_OPTION,
) -> None:
    """Create a new Act project with scaffolding.

    Args:
        ctx: Typer context containing parent options.
        path: Optional custom path for project creation.
        act_name: Optional Act display name.
        cast_name: Optional initial Cast display name.
        lang: Optional language code.
    """
    parent = ctx.parent.obj if ctx.parent and ctx.parent.obj else {}

    _generate_project(
        path=path or parent.get("path"),
        act_name=act_name or parent.get("act_name"),
        cast_name=cast_name or parent.get("cast_name"),
        language=lang or parent.get("lang"),
    )


@app.command("cast")
def cast_command(
    act_path: Path = CAST_ACT_PATH_OPTION,
    cast_name: str | None = NEW_CAST_NAME_OPTION,
    lang: str = NEW_CAST_LANG_OPTION,
) -> None:
    """Add a new Cast subproject to an existing Act project.

    Args:
        act_path: Path to the Act project root.
        cast_name: Optional display name for the new Cast.
        lang: Language code for templates.
    """
    act_path = act_path.resolve()
    _ensure_act_project(act_path)

    cast_raw = _resolve_name(
        "🌟 Please enter a name for the new Cast",
        cast_name,
    )
    _generate_cast_project(act_path=act_path, cast_name=cast_raw, language=lang)


def main() -> None:
    """Entry point for the Act Operator CLI."""
    app()
