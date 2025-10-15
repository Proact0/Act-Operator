"""Expose the {{ cookiecutter.cast_name }} workflow."""

from casts.{{ cookiecutter.cast_slug }}.workflow import {{ cookiecutter.cast_snake }}_workflow

__all__ = ["{{ cookiecutter.cast_snake }}_workflow"]
