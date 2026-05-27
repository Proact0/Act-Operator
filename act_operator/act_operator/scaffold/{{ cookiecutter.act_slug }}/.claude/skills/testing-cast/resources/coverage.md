# Coverage

## Commands

```bash
# Basic coverage
uv run pytest --cov=casts/{cast_name} tests/

# With HTML report
uv run pytest --cov=casts/{cast_name} --cov-report=html tests/

# With branch coverage
uv run pytest --cov=casts/{cast_name} --cov-branch tests/

# Show missing lines
uv run pytest --cov=casts --cov-report=term-missing
```

## Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=casts --cov-report=term-missing"

[tool.coverage.run]
branch = true
source = ["casts"]
omit = ["*/tests/*", "*/conftest.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

## Coverage Goals

| Component | Target |
|-----------|--------|
| Nodes | 90%+ |
| State logic | 85%+ |
| Graph compilation | 80%+ |
| Integration | Critical paths |

**NOT a goal:** 100% coverage

## What to Cover

Test code lives in `casts/{cast_name}/tests/test_*.py`.

**Priority 1: Core Logic**

```python
# casts/{cast_name}/tests/test_nodes.py
from casts.{cast_name}.modules.nodes import ProcessNode


def test_business_logic():
    node = ProcessNode()
    result = node.execute({"input": "critical"})
    assert result["output"] == expected
```

**Priority 2: Error Paths**

```python
# casts/{cast_name}/tests/test_nodes.py
from casts.{cast_name}.modules.nodes import RobustNode


def test_error_handling():
    node = RobustNode()
    result = node.execute({"input": "invalid"})
    assert "error" in result
```

**Priority 3: Edge Cases**

```python
# casts/{cast_name}/tests/test_nodes.py
import pytest

from casts.{cast_name}.modules.nodes import MyNode


@pytest.mark.parametrize("input_val", ["", "x" * 1000, None])
def test_edge_cases(input_val):
    node = MyNode()
    result = node.execute({"input": input_val})
    assert result is not None
```

## Exclude from Coverage

Apply `# pragma: no cover` to product code, not tests — keeps the coverage report honest:

```python
# casts/{cast_name}/modules/<anywhere>.py
from typing import TYPE_CHECKING


def utility():  # pragma: no cover
    """Not critical."""
    pass


if TYPE_CHECKING:  # pragma: no cover
    pass
```

## CI Integration

```yaml
# .github/workflows/test.yml
- name: Test with coverage
  run: |
    uv run pytest --cov=casts --cov-report=xml --cov-fail-under=80
```

