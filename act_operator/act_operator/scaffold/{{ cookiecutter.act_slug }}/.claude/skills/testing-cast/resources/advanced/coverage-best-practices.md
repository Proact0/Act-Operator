# Coverage Best Practices

## When to Use This Resource
Read this for guidance on test coverage strategies and meaningful metrics.

## Running Coverage

```bash
# Basic coverage
pytest --cov=casts/{ cast_name } tests/

# With HTML report
pytest --cov=casts/{ cast_name } --cov-report=html tests/

# With branch coverage
pytest --cov=casts/{ cast_name } --cov-branch tests/
```

## Coverage Configuration

```ini
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=casts --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
branch = true
source = ["casts"]
omit = [
    "*/tests/*",
    "*/conftest.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

## Coverage Goals

**Recommended targets:**
- Nodes: 90%+ coverage
- State logic: 85%+ coverage
- Graph compilation: 80%+ coverage
- Integration: Focus on critical paths

**NOT a goal:**
- 100% coverage (diminishing returns)
- Covering defensive code paths
- Testing library code

## What to Cover

### Priority 1: Core Logic
```python
def test_core_business_logic():
    """Test main processing logic."""
    node = ProcessNode()
    result = node.execute({"input": "critical data"})
    assert result["output"] == expected_output
```

### Priority 2: Error Paths
```python
def test_error_handling():
    """Test error recovery."""
    node = RobustNode()
    result = node.execute({"input": "invalid"})
    assert "error" in result
```

### Priority 3: Edge Cases
```python
@pytest.mark.parametrize("input_val", [
    "",           # Empty
    "x" * 1000,   # Large
    None,         # Null
    {"special": "chars"},  # Complex
])
def test_edge_cases(input_val):
    """Test boundary conditions."""
    node = MyNode()
    result = node.execute({"input": input_val})
    assert result is not None
```

## Measuring Meaningful Coverage

**Good coverage:**
- Tests behavior, not just lines
- Includes error scenarios
- Tests state changes
- Verifies integration points

**Bad coverage:**
- Tests trivial getters/setters
- Covers code but not logic paths
- Achieves numbers without value

## Excluding Code from Coverage

```python
def utility_function():  # pragma: no cover
    """Not critical to test."""
    pass

if TYPE_CHECKING:  # pragma: no cover
    from typing import TYPE_CHECKING
```

## Coverage Reports

```bash
# View coverage in terminal
pytest --cov=casts --cov-report=term-missing

# Generate HTML for detailed view
pytest --cov=casts --cov-report=html
open htmlcov/index.html

# CI-friendly XML report
pytest --cov=casts --cov-report=xml
```

## Coverage in CI/CD

```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    pytest --cov=casts --cov-report=xml --cov-fail-under=80

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Improving Coverage

1. **Identify gaps:**
   ```bash
   pytest --cov=casts --cov-report=term-missing
   ```

2. **Add missing tests:**
   Focus on uncovered critical paths first

3. **Remove dead code:**
   If code is never executed, consider removing it

4. **Refactor for testability:**
   Break down complex functions

## Coverage Anti-Patterns

❌ **Testing for coverage numbers only**
❌ **Trivial tests that don't assert behavior**
❌ **Ignoring integration test coverage**
❌ **100% coverage as a hard requirement**

✅ **Test critical business logic thoroughly**
✅ **Focus on meaningful assertions**
✅ **Balance unit and integration coverage**
✅ **Use coverage to find gaps, not as goal**

## References
- Related: `testing-nodes.md` (node coverage)
- Related: `integration-testing.md` (integration coverage)
