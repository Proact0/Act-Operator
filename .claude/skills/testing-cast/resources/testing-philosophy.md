# Testing Philosophy

## Core Principles

**1. Test Behavior, Not Implementation**

Tests should verify what code does, not how it does it.

❌ Bad: `assert node._internal_count == 5`
✓ Good: `assert result["count"] == 5`

**2. Fast Tests Encourage Frequent Running**

Use mocks to keep unit tests fast (< 1s each).

- Unit tests: < 1 second
- Integration tests: < 10 seconds
- E2E tests: < 60 seconds

**3. Coverage is a Means, Not an End**

Aim for meaningful tests, not arbitrary percentages.

- 100% coverage ≠ bug-free code
- Focus on critical paths and edge cases
- Test behavior, not lines of code

**4. Tests Are Documentation**

Well-written tests explain how code should behave.

```python
def test_node_retries_on_network_error():
    """Node should retry up to 3 times on network errors."""
    # Test shows expected behavior clearly
```

**5. Independence and Isolation**

Each test should run independently.

- No shared state between tests
- Use function-scoped fixtures
- Tests should pass in any order

## Test Categories

**Unit Tests:**
- Test individual nodes
- Mock all dependencies
- Fast (< 1s each)
- High coverage (90%+)

**Integration Tests:**
- Test graphs and workflows
- Use real dependencies (with mocks for external)
- Slower (< 10s each)
- Validate component interaction

**End-to-End Tests:**
- Test complete user flows
- Use real infrastructure (test environment)
- Slowest (< 60s each)
- Validate system behavior

## What to Test

✅ **DO test:**
- Business logic
- Edge cases and error handling
- State transitions
- Integration between components
- Critical paths

❌ **DON'T test:**
- Framework internals
- Third-party libraries
- Trivial code (getters/setters)
- Generated code

## Testing Pyramid

```
    /\      E2E (few, slow, expensive)
   /  \
  /____\    Integration (some, medium speed)
 /      \
/________\  Unit (many, fast, cheap)
```

Most tests should be fast unit tests.

## Quality Over Quantity

**One good test beats five mediocre tests.**

Good test:
- Clear name explaining what it tests
- Isolated and independent
- Tests one thing
- Easy to understand
- Fast

## When Tests Fail

**Failing tests should:**
- Give clear error messages
- Point to exact failure location
- Help debug the issue

**Good test failure:**
```
AssertionError: Expected status='completed', got status='error'
  File "test_node.py", line 42, in test_process_node
    assert result["status"] == "completed"
```

## Test Naming

**Pattern:** `test_<what>_<condition>_<expected>`

Examples:
- `test_node_processes_valid_input_successfully`
- `test_graph_handles_network_error_with_retry`
- `test_state_accumulates_messages_correctly`

## References

- Node testing: `node-testing.md`
- Graph testing: `graph-testing.md`
- Coverage: `coverage.md`
