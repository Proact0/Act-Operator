# Testing State

## When to Use This Resource
Read this when testing state schemas, reducers, and state flow through graphs.

## Testing State Schemas

```python
# tests/test_state.py
import pytest
from casts.{ cast_name }.state import MyCastState

class TestMyCastState:
    def test_state_structure(self):
        """State should have expected fields."""
        state: MyCastState = {
            "input": "test",
            "messages": [],
            "result": None
        }

        assert "input" in state
        assert "messages" in state
        assert "result" in state

    def test_state_types(self):
        """State fields should have correct types."""
        state: MyCastState = {
            "input": "test",
            "messages": [],
            "result": None
        }

        assert isinstance(state["input"], str)
        assert isinstance(state["messages"], list)
        assert state["result"] is None or isinstance(state["result"], str)
```

## Testing Reducers

```python
from langgraph.graph import add

class TestReducers:
    def test_add_reducer_appends(self):
        """add reducer should append to list."""
        existing = [1, 2, 3]
        new = [4, 5]

        result = add(existing, new)

        assert result == [1, 2, 3, 4, 5]

    def test_custom_reducer(self):
        """Custom reducer merges dicts."""
        def merge_dicts(existing: dict, new: dict) -> dict:
            return {**existing, **new}

        existing = {"a": 1, "b": 2}
        new = {"b": 3, "c": 4}

        result = merge_dicts(existing, new)

        assert result == {"a": 1, "b": 3, "c": 4}
```

## Testing State Updates in Nodes

```python
class TestStateUpdates:
    def test_node_updates_state(self):
        """Node should update specific state fields."""
        from casts.{ cast_name }.nodes import ProcessNode

        node = ProcessNode()
        initial_state = {"input": "test", "processed": False}

        updates = node.execute(initial_state)

        assert "processed" in updates
        assert updates["processed"] is True

    def test_node_preserves_existing(self):
        """Node updates should not overwrite unrelated fields."""
        node = ProcessNode()
        state = {"input": "test", "other_field": "preserve"}

        updates = node.execute(state)

        # Node should only return updates, not full state
        assert "other_field" not in updates
```

## Testing State Flow

```python
class TestStateFlow:
    def test_state_accumulates_through_graph(self, graph):
        """State should accumulate updates from each node."""
        initial = {"input": "test", "step": 0}

        final = graph.invoke(initial)

        # Each node should have added to state
        assert final["step"] > 0
        assert "result" in final

    def test_message_accumulation(self, graph):
        """Messages should accumulate with add reducer."""
        initial = {"input": "test", "messages": []}

        final = graph.invoke(initial)

        # Messages should have been appended
        assert len(final["messages"]) > 0
```

## Testing State with Pydantic

```python
from pydantic import BaseModel, ValidationError

class TestPydanticState:
    def test_valid_state(self):
        """Pydantic state validates correct data."""
        class MyState(BaseModel):
            input: str
            count: int = 0

        state = MyState(input="test", count=5)

        assert state.input == "test"
        assert state.count == 5

    def test_invalid_state_raises(self):
        """Invalid state should raise ValidationError."""
        class MyState(BaseModel):
            input: str
            count: int

        with pytest.raises(ValidationError):
            MyState(input="test", count="not a number")

    def test_pydantic_defaults(self):
        """Pydantic should apply defaults."""
        class MyState(BaseModel):
            input: str
            count: int = 0

        state = MyState(input="test")

        assert state.count == 0
```

## Testing State Immutability

```python
class TestStateImmutability:
    def test_node_does_not_mutate_input(self):
        """Nodes should not mutate input state."""
        node = MyNode()
        state = {"input": "test", "data": [1, 2, 3]}
        original_data = state["data"].copy()

        node.execute(state)

        # Original state should be unchanged
        assert state["data"] == original_data

    def test_returns_new_dict(self):
        """Node should return new dict, not modify input."""
        node = MyNode()
        state = {"input": "test"}

        result = node.execute(state)

        assert result is not state
        assert isinstance(result, dict)
```

## Testing State Channels

```python
class TestChannels:
    def test_channel_with_reducer(self):
        """Channel with reducer accumulates values."""
        from typing import Annotated
        from langgraph.graph import add

        # Simulate channel behavior
        messages: Annotated[list[dict], add] = []

        # First update
        messages = add(messages, [{"role": "user", "content": "hi"}])
        assert len(messages) == 1

        # Second update appends
        messages = add(messages, [{"role": "ai", "content": "hello"}])
        assert len(messages) == 2

    def test_channel_without_reducer(self):
        """Channel without reducer replaces value."""
        result = None

        # First update
        result = "first"
        assert result == "first"

        # Second update replaces
        result = "second"
        assert result == "second"
```

## Fixtures for State Testing

```python
# conftest.py
@pytest.fixture
def empty_state():
    """Provides empty state."""
    return {"input": "", "messages": [], "result": None}

@pytest.fixture
def populated_state():
    """Provides state with data."""
    return {
        "input": "test query",
        "messages": [{"role": "user", "content": "hello"}],
        "result": None
    }
```

## Common Patterns

### Pattern: Test State Transitions
```python
def test_state_transitions(self, graph):
    """Test state changes through graph execution."""
    states = []

    for chunk in graph.stream({"input": "test"}, stream_mode="values"):
        states.append(chunk.copy())

    # Verify state evolved
    assert states[0] != states[-1]
    assert "result" in states[-1]
```

## References
- Related: `testing-nodes.md` (node state updates)
- Related: `testing-graphs.md` (state flow through graph)
