"""Project-wide test fixtures for Act Operator projects.

Import in cast-specific conftest.py with:
    pytest_plugins = ["fixtures.conftest"]
"""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver


# =============================================================================
# Mock LLM Fixtures
# =============================================================================

class MockLLM:
    """Simple mock LLM that returns static responses."""

    def __init__(self, response="Mock response"):
        self.response = response
        self.call_count = 0

    def invoke(self, messages):
        """Return mock AI response."""
        self.call_count += 1
        return AIMessage(content=self.response)

    def bind_tools(self, tools):
        """Mock tool binding."""
        return self


class MockLLMWithTools:
    """Mock LLM that returns tool calls."""

    def __init__(self, tool_name="calculator", tool_args=None):
        self.tool_name = tool_name
        self.tool_args = tool_args or {"operation": "add", "a": 5, "b": 3}
        self.call_count = 0

    def invoke(self, messages):
        """Return mock response with tool calls."""
        self.call_count += 1
        return AIMessage(
            content="",
            tool_calls=[{
                "name": self.tool_name,
                "args": self.tool_args,
                "id": f"call_{self.call_count}"
            }]
        )

    def bind_tools(self, tools):
        """Mock tool binding."""
        return self


@pytest.fixture
def mock_llm():
    """Provide basic mock LLM."""
    return MockLLM()


@pytest.fixture
def mock_llm_with_tools():
    """Provide mock LLM that returns tool calls."""
    return MockLLMWithTools()


# =============================================================================
# Mock Store/Runtime Fixtures
# =============================================================================

class MockStore:
    """Mock Store for memory testing."""

    def __init__(self):
        self._data = {}

    def get(self, namespace, key):
        """Get value from store."""
        return self._data.get((tuple(namespace), key))

    def put(self, namespace, key, value):
        """Put value in store."""
        self._data[(tuple(namespace), key)] = value

    def search(self, namespace, query=None):
        """Search store by namespace."""
        items = [
            v for (ns, k), v in self._data.items()
            if tuple(ns) == tuple(namespace)
        ]
        return items

    def list(self, namespace):
        """List all items in namespace."""
        return [
            v for (ns, k), v in self._data.items()
            if tuple(ns) == tuple(namespace)
        ]

    def delete(self, namespace, key):
        """Delete from store."""
        self._data.pop((tuple(namespace), key), None)


class MockRuntime:
    """Mock Runtime for testing."""

    def __init__(self, store=None):
        self.store = store or MockStore()
        self.stream_writer = None


@pytest.fixture
def mock_store():
    """Provide mock Store."""
    return MockStore()


@pytest.fixture
def mock_runtime(mock_store):
    """Provide mock Runtime with Store."""
    return MockRuntime(store=mock_store)


# =============================================================================
# Config Fixtures
# =============================================================================

@pytest.fixture
def test_config():
    """Provide test config with thread_id."""
    return {"configurable": {"thread_id": "test-123"}}


@pytest.fixture
def test_thread_id():
    """Provide test thread_id."""
    return "test-123"


# =============================================================================
# Checkpointer Fixtures
# =============================================================================

@pytest.fixture
def memory_saver():
    """Provide MemorySaver checkpointer."""
    return MemorySaver()


# =============================================================================
# Message Fixtures
# =============================================================================

@pytest.fixture
def sample_human_message():
    """Provide sample HumanMessage."""
    return HumanMessage(content="Test message")


@pytest.fixture
def sample_ai_message():
    """Provide sample AIMessage."""
    return AIMessage(content="Test response")


@pytest.fixture
def sample_tool_message():
    """Provide sample ToolMessage."""
    return ToolMessage(
        content="Tool result",
        tool_call_id="call_123"
    )


@pytest.fixture
def sample_conversation():
    """Provide sample conversation history."""
    return [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!"),
        HumanMessage(content="How are you?"),
        AIMessage(content="I'm doing well, thank you!"),
    ]


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def temp_file(tmp_path):
    """Provide temporary file path."""
    file_path = tmp_path / "test_file.txt"
    yield file_path
    # Cleanup happens automatically with tmp_path


@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        "messages": [],
        "task": "test task",
        "count": 0,
        "data": {},
        "status": "pending"
    }
