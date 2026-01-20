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

**Priority 1: Core Logic**
```python
def test_business_logic():
    node = ProcessNode()
    result = node.execute({"input": "critical"})
    assert result["output"] == expected
```

**Priority 2: Error Paths**
```python
def test_error_handling():
    node = RobustNode()
    result = node.execute({"input": "invalid"})
    assert "error" in result
```

**Priority 3: Edge Cases**
```python
@pytest.mark.parametrize("input_val", ["", "x"*1000, None])
def test_edge_cases(input_val):
    node = MyNode()
    result = node.execute({"input": input_val})
    assert result is not None
```

## Exclude from Coverage

```python
def utility():  # pragma: no cover
    """Not critical."""
    pass

if TYPE_CHECKING:  # pragma: no cover
    from typing import TYPE_CHECKING
```

## CI Integration

```yaml
# .github/workflows/test.yml
- name: Test with coverage
  run: |
    uv run pytest --cov=casts --cov-report=xml --cov-fail-under=80
```

