"""Act Operator 유틸리티 함수."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    )

    rendered_path = Path(rendered_path)

    if rendered_path.resolve() != target_dir.resolve():
        rendered_path.rename(target_dir)
