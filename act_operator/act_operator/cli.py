"""Act Operator CLI entrypoints."""

from __future__ import annotations

from pathlib import Path

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
    help="Display name of the initial Cast",
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


def _resolve_path(path_option: Path | None) -> tuple[Path, bool]:
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
    if value:
        return value.strip()
    while True:
        prompted = typer.prompt(prompt_message).strip()
        if prompted:
            return prompted
        console.print("[red]A value is required.[/red]")


def _generate_project(
    *,
    path: Path | None,
    act_name: str | None,
    cast_name: str | None,
) -> None:
    target_dir, path_was_custom = _resolve_path(path)

    if target_dir.exists() and any(target_dir.iterdir()):
        console.print(
            "❌ The specified directory already exists and is not empty. Aborting to prevent overwriting files.",
            style="red",
        )
        raise typer.Exit(code=1)

    if act_name is None and path_was_custom:
        derived_name = target_dir.name or target_dir.resolve().name
        act_name = derived_name

    act_raw = _resolve_name("🚀 Please enter a name for the new Act", act_name)
    cast_raw = _resolve_name("🌟 Please enter a name for the first Cast", cast_name)

    try:
        act = build_name_variants(act_raw)
        cast = build_name_variants(cast_raw)
    except ValueError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        console.print(f"[red]Unable to create target directory: {error}[/red]")
        raise typer.Exit(code=1) from error

    scaffold_root = Path(__file__).resolve().parent / "scaffold"
    if not scaffold_root.exists():
        console.print("[red]Scaffold resources not found.[/red]")
        raise typer.Exit(code=1)

    console.print("[bold green]Starting Act project scaffolding...[/bold green]")

    context = {
        "act_name": act.title,
        "act_slug": act.slug,
        "act_snake": act.snake,
        "cast_name": cast.title,
        # 캐스트 디렉터리는 snake_case 사용
        "cast_slug": cast.slug,
        "cast_snake": cast.snake,
    }

    try:
        render_cookiecutter_template(scaffold_root, target_dir, context)
    except FileExistsError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    # 캐스트 디렉터리가 하이픈으로 생성된 경우 언더스코어로 교정
    casts_dir = target_dir / "casts"
    old_cast_dir = casts_dir / cast.slug
    new_cast_dir = casts_dir / cast.snake
    try:
        if old_cast_dir.exists() and not new_cast_dir.exists():
            old_cast_dir.rename(new_cast_dir)

            # pyproject.toml 경로 교정
            project_pyproject = target_dir / "pyproject.toml"
            if project_pyproject.exists():
                content = project_pyproject.read_text(encoding="utf-8")
                content = content.replace(f"casts/{cast.slug}", f"casts/{cast.snake}")
                project_pyproject.write_text(content, encoding="utf-8")

            # langgraph.json 경로 및 그래프 키 교정
            project_langgraph = target_dir / "langgraph.json"
            if project_langgraph.exists():
                lg = project_langgraph.read_text(encoding="utf-8")
                lg = lg.replace(f'"{cast.slug}"', f'"{cast.snake}"')
                lg = lg.replace(f"/casts/{cast.slug}/", f"/casts/{cast.snake}/")
                project_langgraph.write_text(lg, encoding="utf-8")
    except OSError as error:
        console.print(f"[red]Failed to normalize cast directory: {error}[/red]")
        raise typer.Exit(code=1) from error

    table = Table(show_header=False)
    table.add_row("Act", act.title)
    table.add_row("Cast", cast.title)
    table.add_row("Location", str(target_dir))
    console.print(table)
    console.print("[bold green]Act project created successfully![/bold green]")
    try:
        casts_dir = target_dir / "casts"
        if casts_dir.exists():
            entries = ", ".join(sorted(p.name for p in casts_dir.iterdir()))
            console.print(f"[dim]casts dir entries: {entries}[/dim]")
    except Exception:
        pass


@app.callback()
def root(  # type: ignore[override]
    ctx: typer.Context,
    path: Path | None = PATH_OPTION,
    act_name: str | None = ACT_NAME_OPTION,
    cast_name: str | None = CAST_NAME_OPTION,
) -> None:
    ctx.obj = {"path": path, "act_name": act_name, "cast_name": cast_name}
    if ctx.invoked_subcommand is not None:
        return
    _generate_project(path=path, act_name=act_name, cast_name=cast_name)


@app.command("new")
def new_command(
    ctx: typer.Context,
    path: Path | None = PATH_OPTION,
    act_name: str | None = ACT_NAME_OPTION,
    cast_name: str | None = CAST_NAME_OPTION,
) -> None:
    parent = ctx.parent.obj if ctx.parent and ctx.parent.obj else {}
    path = path or parent.get("path")
    act_name = act_name or parent.get("act_name")
    cast_name = cast_name or parent.get("cast_name")
    _generate_project(path=path, act_name=act_name, cast_name=cast_name)


def _ensure_act_project(act_path: Path) -> None:
    expected = [
        act_path / "pyproject.toml",
        act_path / "langgraph.json",
        act_path / "casts",
        act_path / "casts" / "base_node.py",
        act_path / "casts" / "base_graph.py",
    ]
    for path in expected:
        if not path.exists():
            console.print(
                f"[red]The path does not look like a valid Act project: {path}[/red]"
            )
            raise typer.Exit(code=1)


def _generate_cast_project(
    *,
    act_path: Path,
    cast_name: str,
) -> None:
    act_variants = build_name_variants(act_path.name)
    casts_dir = act_path / "casts"
    cast_variants = build_name_variants(cast_name)
    # 캐스트 디렉터리는 snake_case로 강제
    target_dir = casts_dir / cast_variants.snake

    if target_dir.exists() and any(target_dir.iterdir()):
        console.print(
            "❌ The specified cast directory already exists and is not empty. Aborting to prevent overwriting files.",
            style="red",
        )
        raise typer.Exit(code=1)

    scaffold_root = Path(__file__).resolve().parent / "scaffold"
    template_root = scaffold_root

    render_cookiecutter_cast_subproject(
        template_root,
        target_dir,
        {
            "act_name": act_variants.title,
            "act_slug": act_variants.slug,
            "act_snake": act_variants.snake,
            "cast_name": cast_variants.title,
            "cast_snake": cast_variants.snake,
            "cast_snake": cast_variants.snake,
        },
    )

    workspace_member = f"casts/{cast_variants.snake}"
    try:
        update_workspace_members(act_path / "pyproject.toml", workspace_member)
    except RuntimeError as error:
        console.print(f"[red]Failed to update pyproject.toml: {error}[/red]")
        raise typer.Exit(code=1) from error

    try:
        update_langgraph_registry(
            act_path / "langgraph.json",
            cast_variants.snake,
        )
    except RuntimeError as error:
        console.print(f"[red]Failed to update langgraph.json: {error}[/red]")
        raise typer.Exit(code=1) from error

    console.print(
        f"[bold green]Cast '{cast_variants.snake}' added successfully![/bold green]"
    )


@app.command("cast")
def cast_command(
    act_path: Path = CAST_ACT_PATH_OPTION,
    cast_name: str | None = NEW_CAST_NAME_OPTION,
) -> None:
    act_path = act_path.resolve()
    _ensure_act_project(act_path)

    cast_raw = _resolve_name("🌟 Please enter a name for the new Cast", cast_name)
    _generate_cast_project(act_path=act_path, cast_name=cast_raw)


def main() -> None:
    app()
