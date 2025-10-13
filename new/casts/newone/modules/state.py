"""State definition shared across Newone workflows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class State:
    """Graph state container.

    Attributes:
        (Add fields that should persist across nodes. Example: `interview_topic`.)
    """
