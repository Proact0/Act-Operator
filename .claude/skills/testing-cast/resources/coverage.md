# Coverage and Quality

## Coverage Targets

**Recommended:**
- Nodes: 90%+ coverage
- Graphs: 80%+ coverage
- Tools: 90%+ coverage
- Conditions: 100% coverage

**Focus on meaningful tests, not arbitrary percentages.**

## Running Coverage

```bash
# Basic coverage
pytest --cov=casts.my_agent

# With missing lines
pytest --cov=casts.my_agent --cov-report=term-missing

# HTML report
pytest --cov=casts.my_agent --cov-report=html
open htmlcov/index.html

# Fail if below threshold
pytest --cov=casts.my_agent --cov-fail-under=80
```

## What to Test

✅ **DO test:**
- Business logic
- Error handling
- Edge cases
- State transitions
- Integration points

❌ **DON'T test:**
- Framework code
- Third-party libraries
- Trivial getters/setters
- Generated code

## Quality Metrics

**Good test:**
- Tests one thing
- Clear name
- Independent
- Fast
- Meaningful assertions

**Coverage reports show:**
- Which lines executed
- Which branches taken
- Which functions called

**But they don't show:**
- Quality of assertions
- Edge cases coverage
- Business logic correctness

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=casts --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Quick Reference

**Run with coverage:**
```bash
pytest --cov=module --cov-report=term-missing
```

**Target thresholds:**
- Critical paths: 100%
- Business logic: 90%+
- Integration: 80%+

**Focus:** Meaningful tests > high coverage

## References

- Testing philosophy: `testing-philosophy.md`
- Node testing: `node-testing.md`
