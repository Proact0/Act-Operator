"""Act Operator 유틸리티 함수."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for older versions
    import tomli as tomllib  # type: ignore

import tempfile

from cookiecutter.main import cookiecutter


@dataclass(slots=True)
class NameVariants:
    raw: str
    slug: str
    snake: str
    title: str


def build_name_variants(raw: str) -> NameVariants:
    normalized = raw.strip()
    if not normalized:
        raise ValueError("Empty string cannot be used.")

    slug = _normalize(normalized, "-")
    snake = _normalize(normalized, "_")
    title = normalized.replace("_", " ").replace("-", " ").title()

    if not slug or not snake:
        raise ValueError("Please enter a name containing valid English characters.")

    return NameVariants(raw=normalized, slug=slug, snake=snake, title=title)


def _normalize(value: str, sep: str) -> str:
    cleaned = [ch.lower() if ch.isalnum() else sep for ch in value]
    collapsed = "".join(cleaned)
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
    if target_dir.exists():
        shutil.rmtree(target_dir)

    output_root = target_dir.parent
    project_slug = target_dir.name

    rendered_path = cookiecutter(
        str(template_dir),
        no_input=True,
        extra_context={"project_dir": project_slug, **context},
        output_dir=str(output_root),
        overwrite_if_exists=True,
        directory=directory,
    )

    rendered_path = Path(rendered_path)

    if rendered_path.resolve() != target_dir.resolve():
        rendered_path.rename(target_dir)


def render_cookiecutter_cast_subproject(
    template_root: Path,
    target_dir: Path,
    context: dict[str, Any],
) -> None:
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
