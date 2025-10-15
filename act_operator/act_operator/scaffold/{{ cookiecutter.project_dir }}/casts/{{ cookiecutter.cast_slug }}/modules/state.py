"""[Required] State definition shared across {{ cookiecutter.cast_name }} workflows."""

from __future__ import annotations

from dataclasses import dataclass
from 

@dataclass(kw_only=True)
class InputState:
    """Input state container."""
    query: str


@dataclass(kw_only=True)
class OutputState:
    """Output state container."""
    message: add


@dataclass(kw_only=True)
class State:
    """Graph state container.

    Attributes:
        (Add fields that should persist across nodes. Example: `interview_topic`.)
    """
