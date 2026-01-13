"""Act Operator CLI entrypoints for managing Act projects and Casts."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .utils import (
    CASTS_DIR,
    LANGGRAPH_FILE,
    PYPROJECT_FILE,
    Language,
    NameVariants,
    build_name_variants,
    render_cookiecutter_cast_subproject,
    render_cookiecutter_template,
    select_drawkit_by_language,
    update_langgraph_registry,
)

# Constants
EXIT_CODE_ERROR = 1
SCAFFOLD_DIR = "scaffold"
BASE_NODE_FILE = "base_node.py"
BASE_GRAPH_FILE = "base_graph.py"
DEFAULT_LANGUAGE_CHOICE = 1
ENCODING_UTF8 = "utf-8"

console = Console()
app = typer.Typer(help="Act Operator", invoke_without_command=True)

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
    "en",
    "--lang",
    "-l",
    help="Language for scaffolded cast docs (en|kr)",
)


def _resolve_path(path_option: Path | None) -> tuple[Path, bool]:
    """Resolve the target path for project creation.

    Args:
        path_option: Optional path provided via CLI option.

    Returns:
        Tuple of (resolved_path, is_custom_path).
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


def _validate_name(name: str) -> None:
    """Validate a name using build_name_variants.

    Args:
        name: Name to validate.

    Raises:
        typer.Exit: If name is invalid.
    """
    try:
        build_name_variants(name)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from e


def _check_cast_conflict(cast_snake: str, act_snake: str, act_title: str) -> bool:
    """Check if cast name conflicts with act name.

    Args:
        cast_snake: Snake case version of Cast name.
        act_snake: Snake case version of Act name.
        act_title: Title case version of Act name.

    Returns:
        True if there's a conflict, False otherwise.
    """
    if cast_snake == act_snake:
        console.print(
            f"[red]❌ Cast name conflicts with Act name '{act_title}'.[/red]\n"
            f"[yellow]Both resolve to the same workspace member: '{cast_snake}'[/yellow]\n"
            "[yellow]Please choose a different name for the Cast.[/yellow]"
        )
        return True
    return False


def _resolve_name(prompt_message: str, value: str | None) -> str:
    """Resolve Act or Cast name from option or prompt with validation.

    Args:
        prompt_message: Message to display when prompting user.
        value: Optional name value from CLI option.

    Returns:
        Validated name string.
    """
    if value:
        value = value.strip()
        _validate_name(value)
        return value

    # Interactive prompt with immediate validation
    while True:
        prompted = typer.prompt(prompt_message).strip()
        if not prompted:
            console.print("[red]A value is required.[/red]")
            continue

        try:
            build_name_variants(prompted)
            return prompted
        except ValueError as e:
            console.print(f"[red]❌ {e}[/red]")
            console.print("[yellow]Please try again with a valid name.[/yellow]")


def _resolve_cast_name(
    prompt_message: str,
    value: str | None,
    act_snake: str,
    act_title: str,
) -> str:
    """Resolve Cast name with validation and conflict checking against Act name.

    Args:
        prompt_message: Message to display when prompting user.
        value: Optional name value from CLI option.
        act_snake: Snake case version of Act name.
        act_title: Title case version of Act name.

    Returns:
        Validated Cast name string.
    """
    if value:
        value = value.strip()
        _validate_name(value)
        cast_variants = build_name_variants(value)
        if _check_cast_conflict(cast_variants.snake, act_snake, act_title):
            raise typer.Exit(code=EXIT_CODE_ERROR)
        return value

    # Interactive prompt with immediate validation and conflict checking
    while True:
        prompted = typer.prompt(prompt_message).strip()
        if not prompted:
            console.print("[red]A value is required.[/red]")
            continue

        try:
            cast_variants = build_name_variants(prompted)
            if _check_cast_conflict(cast_variants.snake, act_snake, act_title):
                continue
            return prompted
        except ValueError as e:
            console.print(f"[red]❌ {e}[/red]")
            console.print("[yellow]Please try again with a valid name.[/yellow]")


def _normalize_lang(value: str | None) -> str:
    """Normalize language value to language code string.

    Args:
        value: Language code or None.

    Returns:
        Language code string ("en" or "kr").
    """
    try:
        lang = Language.from_string(value)
        return lang.value
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from e


def _select_language_menu() -> str:
    """Display interactive language selection menu.

    Returns:
        Language code string ("en" or "kr").
    """
    console.print(
        "🌐 Choose template language - This option sets the language for "
        "the entire scaffolded template content.\n"
        f"1. {Language.ENGLISH.display_name} ({Language.ENGLISH.value.upper()})\n"
        f"2. {Language.KOREAN.display_name} ({Language.KOREAN.value.upper()})"
    )
    options = {1: Language.ENGLISH, 2: Language.KOREAN}
    while True:
        choice: int = typer.prompt(
            "Enter the number of your language choice (default is 1)",
            default=DEFAULT_LANGUAGE_CHOICE,
            type=int,
        )
        if choice in options:
            return options[choice].value
        console.print("[red]❌ Invalid choice. Please try again.[/red]")


def _resolve_language(language: str | None) -> str:
    """Resolve language to language code.

    Args:
        language: Language code string or None.

    Returns:
        Language code string ("en" or "kr").
    """
    # If language is provided, validate and return language code
    if language and language.strip():
        try:
            lang = Language.from_string(language)
            return lang.value
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(code=EXIT_CODE_ERROR) from e

    # No language provided - show menu
    return _select_language_menu()


def _determine_target_directory(
    base_dir: Path, path_was_custom: bool, act_slug: str
) -> Path:
    """Determine the target directory for the new Act project.

    Args:
        base_dir: Base directory from user input.
        path_was_custom: Whether user specified a custom path.
        act_slug: Hyphenated slug version of Act name.

    Returns:
        Target directory path for the project.
    """
    # If user used default path ('.'), create project in current directory
    if not path_was_custom:
        return Path.cwd()

    # For custom paths, create subdirectory with act-slug name
    if base_dir != Path.cwd():
        return base_dir.parent / act_slug
    return Path.cwd() / act_slug


def _validate_and_create_directory(target_dir: Path) -> None:
    """Validate and create target directory.

    Args:
        target_dir: Directory to create.

    Raises:
        typer.Exit: If directory exists and is not empty, or creation fails.
    """
    if target_dir.exists() and any(target_dir.iterdir()):
        console.print(
            "❌ The specified directory already exists and is not empty. "
            "Aborting to prevent overwriting files.",
            style="red",
        )
        raise typer.Exit(code=EXIT_CODE_ERROR)

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        console.print(f"[red]Unable to create target directory: {error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error


def _get_scaffold_root() -> Path:
    """Get the scaffold directory path.

    Returns:
        Path to scaffold directory.

    Raises:
        typer.Exit: If scaffold resources not found.
    """
    scaffold_root = Path(__file__).resolve().parent / SCAFFOLD_DIR
    if not scaffold_root.exists():
        console.print("[red]Scaffold resources not found.[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR)
    return scaffold_root


def _build_template_context(
    act: NameVariants, cast: NameVariants, language: str
) -> dict[str, str]:
    """Build the template context for cookiecutter.

    Args:
        act: Act name variants.
        cast: Cast name variants.
        language: Language display name.

    Returns:
        Dictionary of template context variables.
    """
    return {
        "act_name": act.title,
        "act_slug": act.slug,
        "act_snake": act.snake,
        "cast_name": cast.title,
        # Cast directory uses snake_case
        "cast_slug": cast.slug,
        "cast_snake": cast.snake,
        "cast_pascal": cast.pascal,
        "language": language,
    }


def _normalize_cast_directory(target_dir: Path, cast: NameVariants) -> None:
    """Normalize cast directory from hyphenated to snake_case if needed.

    Args:
        target_dir: Root directory of the Act project.
        cast: Cast name variants.

    Raises:
        typer.Exit: If normalization fails.
    """
    casts_dir = target_dir / CASTS_DIR
    old_cast_dir = casts_dir / cast.slug
    new_cast_dir = casts_dir / cast.snake

    if not (old_cast_dir.exists() and not new_cast_dir.exists()):
        return

    try:
        old_cast_dir.rename(new_cast_dir)

        # Fix pyproject.toml path references
        project_pyproject = target_dir / PYPROJECT_FILE
        if project_pyproject.exists():
            content = project_pyproject.read_text(encoding=ENCODING_UTF8)
            content = content.replace(
                f"{CASTS_DIR}/{cast.slug}", f"{CASTS_DIR}/{cast.snake}"
            )
            project_pyproject.write_text(content, encoding=ENCODING_UTF8)

        # Fix langgraph.json path and graph key references
        project_langgraph = target_dir / LANGGRAPH_FILE
        if project_langgraph.exists():
            lg = project_langgraph.read_text(encoding=ENCODING_UTF8)
            lg = lg.replace(f'"{cast.slug}"', f'"{cast.snake}"')
            lg = lg.replace(
                f"/{CASTS_DIR}/{cast.slug}/",
                f"/{CASTS_DIR}/{cast.snake}/",
            )
            project_langgraph.write_text(lg, encoding=ENCODING_UTF8)
    except OSError as error:
        console.print(f"[red]Failed to normalize cast directory: {error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error


def _display_project_summary(
    act_title: str, cast_title: str, language: str, target_dir: Path
) -> None:
    """Display project creation summary table.

    Args:
        act_title: Act name in title case.
        cast_title: Cast name in title case.
        language: Language code ("en" or "kr").
        target_dir: Project directory path.
    """
    lang_display = Language.from_string(language).display_name
    table = Table(show_header=False)
    table.add_row("Act", act_title)
    table.add_row("Cast", cast_title)
    table.add_row("Language", lang_display)
    table.add_row("Location", str(target_dir))
    console.print(table)
    console.print("[bold green]Act project created successfully![/bold green]")

    try:
        if target_dir.exists():
            entries = ", ".join(sorted(p.name for p in target_dir.iterdir()))
            console.print(f"[dim]act project entries: {entries}[/dim]")
    except Exception:
        pass


def _generate_project(
    *,
    path: Path | None,
    act_name: str | None,
    cast_name: str | None,
    language: str | None,
) -> None:
    """Generate a new Act project with initial Cast.

    Args:
        path: Optional path for project creation.
        act_name: Optional Act name.
        cast_name: Optional Cast name.
        language: Optional language code.

    Raises:
        typer.Exit: If project creation fails.
    """
    base_dir, path_was_custom = _resolve_path(path)

    # If using current directory (.), check if it's empty before proceeding
    if not path_was_custom:
        if Path.cwd().exists() and any(Path.cwd().iterdir()):
            console.print(
                "❌ The current directory is not empty. "
                "Please use an empty directory to create a new Act project.",
                style="red",
            )
            raise typer.Exit(code=EXIT_CODE_ERROR)

    # If user provided a path as act name, use it as the display name
    if act_name is None and path_was_custom:
        derived_name = base_dir.name or base_dir.resolve().name
        act_name = derived_name

    # Resolve and validate names
    act_raw = _resolve_name("🚀 Please enter a name for the new Act", act_name)
    act = build_name_variants(act_raw)

    cast_raw = _resolve_cast_name(
        "🌟 Please enter a name for the first Cast",
        cast_name,
        act.snake,
        act.title,
    )
    cast = build_name_variants(cast_raw)

    lang = _resolve_language(language)

    # Prepare directories
    target_dir = _determine_target_directory(base_dir, path_was_custom, act.slug)
    _validate_and_create_directory(target_dir)
    scaffold_root = _get_scaffold_root()

    console.print("[bold green]Starting Act project scaffolding...[/bold green]")

    # Render template
    context = _build_template_context(act, cast, lang)
    try:
        render_cookiecutter_template(scaffold_root, target_dir, context)
    except FileExistsError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error

    # Normalize cast directory naming
    _normalize_cast_directory(target_dir, cast)

    # Select appropriate drawkit file based on language
    try:
        select_drawkit_by_language(target_dir, lang)
    except FileNotFoundError as error:
        console.print(f"[yellow]Warning: {error}[/yellow]")
    except OSError as error:
        console.print(f"[red]Failed to process drawkit file: {error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error

    # Display summary
    _display_project_summary(act.title, cast.title, lang, target_dir)


@app.callback()
def root(
    ctx: typer.Context,
    path: Path | None = PATH_OPTION,
    act_name: str | None = ACT_NAME_OPTION,
    cast_name: str | None = CAST_NAME_OPTION,
    lang: str | None = LANG_OPTION,
) -> None:
    """Act Operator root command callback.

    Args:
        ctx: Typer context for command invocation.
        path: Optional path for project creation.
        act_name: Optional Act name.
        cast_name: Optional Cast name.
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
    _generate_project(path=path, act_name=act_name, cast_name=cast_name, language=lang)


@app.command("new")
def new_command(
    ctx: typer.Context,
    path: Path | None = PATH_OPTION,
    act_name: str | None = ACT_NAME_OPTION,
    cast_name: str | None = CAST_NAME_OPTION,
    lang: str | None = LANG_OPTION,
) -> None:
    """Create a new Act project (explicit command).

    Args:
        ctx: Typer context for command invocation.
        path: Optional path for project creation.
        act_name: Optional Act name.
        cast_name: Optional Cast name.
        lang: Optional language code.
    """
    parent = ctx.parent.obj if ctx.parent and ctx.parent.obj else {}
    path = path or parent.get("path")
    act_name = act_name or parent.get("act_name")
    cast_name = cast_name or parent.get("cast_name")
    lang = lang or parent.get("lang")
    _generate_project(path=path, act_name=act_name, cast_name=cast_name, language=lang)


def _ensure_act_project(act_path: Path) -> None:
    """Validate that the path is a valid Act project.

    Args:
        act_path: Path to validate.

    Raises:
        typer.Exit: If path is not a valid Act project.
    """
    expected = [
        act_path / PYPROJECT_FILE,
        act_path / LANGGRAPH_FILE,
        act_path / CASTS_DIR,
        act_path / CASTS_DIR / BASE_NODE_FILE,
        act_path / CASTS_DIR / BASE_GRAPH_FILE,
    ]
    for path in expected:
        if not path.exists():
            console.print(
                f"[red]The path does not look like a valid Act project: {path}[/red]"
            )
            raise typer.Exit(code=EXIT_CODE_ERROR)


def _validate_cast_directory(target_dir: Path) -> None:
    """Validate that cast directory doesn't exist or is empty.

    Args:
        target_dir: Cast directory to validate.

    Raises:
        typer.Exit: If directory exists and is not empty.
    """
    if target_dir.exists() and any(target_dir.iterdir()):
        console.print(
            "❌ The specified cast directory already exists and is not empty. "
            "Aborting to prevent overwriting files.",
            style="red",
        )
        raise typer.Exit(code=EXIT_CODE_ERROR)


def _generate_cast_project(
    *,
    act_path: Path,
    cast_name: str,
    language: str,
) -> None:
    """Generate a new Cast within an existing Act project.

    Args:
        act_path: Path to the Act project.
        cast_name: Name of the new Cast.
        language: Language code for the Cast.

    Raises:
        typer.Exit: If Cast creation fails.
    """
    act_variants = build_name_variants(act_path.name)
    cast_variants = build_name_variants(cast_name)

    # Cast directory uses snake_case
    casts_dir = act_path / CASTS_DIR
    target_dir = casts_dir / cast_variants.snake

    _validate_cast_directory(target_dir)

    scaffold_root = _get_scaffold_root()

    def _copy_cast_test(rendered_root: Path) -> None:
        """Copy rendered cast test into the project tests directory."""
        template_test = (
            rendered_root / "tests" / "cast_tests" / f"{cast_variants.snake}_test.py"
        )
        if not template_test.exists():
            console.print(
                "[red]Generated cast test template not found. Aborting cast creation.[/red]"
            )
            raise typer.Exit(code=EXIT_CODE_ERROR)

        dest_dir = act_path / "tests" / "cast_tests"
        dest_dir.mkdir(parents=True, exist_ok=True)
        destination = dest_dir / template_test.name

        if destination.exists():
            console.print(
                f"[red]Cast test '{destination.name}' already exists. "
                "Remove it or rename before creating a new cast.[/red]"
            )
            raise typer.Exit(code=EXIT_CODE_ERROR)

        shutil.copy2(template_test, destination)
        console.print(
            f"[green]Cast test '{destination.name}' created in tests/cast_tests.[/green]"
        )

    render_cookiecutter_cast_subproject(
        scaffold_root,
        target_dir,
        {
            "act_name": act_variants.title,
            "act_slug": act_variants.slug,
            "act_snake": act_variants.snake,
            "cast_name": cast_variants.title,
            "cast_slug": cast_variants.slug,
            "cast_snake": cast_variants.snake,
            "cast_pascal": cast_variants.pascal,
            "language": _normalize_lang(language),
        },
        post_process=_copy_cast_test,
    )

    # Update project configuration files
    # Note: workspace members and dependencies use wildcard patterns (casts/*)
    # so we only need to update the graphs registry
    try:
        update_langgraph_registry(
            act_path / LANGGRAPH_FILE,
            cast_variants.slug,
            cast_variants.snake,
        )
    except RuntimeError as error:
        console.print(f"[red]Failed to update langgraph.json: {error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error

    console.print(
        f"[bold green]Cast '{cast_variants.snake}' added successfully![/bold green]"
    )


@app.command("cast")
def cast_command(
    act_path: Path = CAST_ACT_PATH_OPTION,
    cast_name: str | None = NEW_CAST_NAME_OPTION,
    lang: str = NEW_CAST_LANG_OPTION,
) -> None:
    """Add a new Cast to an existing Act project.

    Args:
        act_path: Path to the existing Act project.
        cast_name: Optional Cast name.
        lang: Language code for the Cast.
    """
    act_path = act_path.resolve()
    _ensure_act_project(act_path)

    # Build act variants first for conflict checking
    act_variants = build_name_variants(act_path.name)

    # Resolve cast name with immediate conflict checking
    cast_raw = _resolve_cast_name(
        "🌟 Please enter a name for the new Cast",
        cast_name,
        act_variants.snake,
        act_variants.title,
    )
    _generate_cast_project(act_path=act_path, cast_name=cast_raw, language=lang)


def main() -> None:
    """Entry point for the Act Operator CLI."""
    app()
