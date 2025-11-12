"""Test fixtures for reusable test components.

This module provides pytest fixtures that can be shared across test files.
Place this in tests/conftest.py or import from your test files.

Usage:
    1. Copy to tests/conftest.py for automatic discovery
    2. Or import fixtures from this module in your tests
    3. Use fixtures by adding them as function parameters
"""

from dataclasses import dataclass
from typing import Annotated, Any, List

import pytest
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph.message import add_messages


# ============================================================================
# State Fixtures
# ============================================================================


@dataclass(kw_only=True)
class TestState:
    """Standard test state matching graph state.

    Update this to match your actual graph state.
    """

    query: str
    messages: Annotated[list[AnyMessage], add_messages]


@pytest.fixture
def empty_state():
    """Provide empty initial state.

    Returns:
        Empty state dict
    """
    return {"query": "", "messages": []}


@pytest.fixture
def sample_state():
    """Provide sample state with typical values.

    Returns:
        Sample state dict
    """
    return {"query": "sample query", "messages": []}


@pytest.fixture
def state_with_messages():
    """Provide state with existing messages.

    Returns:
        State dict with message history
    """
    return {
        "query": "new query",
        "messages": [
            HumanMessage(content="Previous user message"),
            AIMessage(content="Previous assistant message"),
        ],
    }


@pytest.fixture
def state_with_long_query():
    """Provide state with long query.

    Returns:
        State dict with long query
    """
    return {
        "query": "word " * 100,  # 100 words
        "messages": [],
    }


# ============================================================================
# Message Fixtures
# ============================================================================


@pytest.fixture
def human_message():
    """Provide sample human message.

    Returns:
        HumanMessage instance
    """
    return HumanMessage(content="Hello, I need help")


@pytest.fixture
def ai_message():
    """Provide sample AI message.

    Returns:
        AIMessage instance
    """
    return AIMessage(content="I'm here to help!")


@pytest.fixture
def message_history():
    """Provide sample message history.

    Returns:
        List of messages
    """
    return [
        HumanMessage(content="First question"),
        AIMessage(content="First answer"),
        HumanMessage(content="Follow-up question"),
        AIMessage(content="Follow-up answer"),
    ]


# ============================================================================
# Graph Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def compiled_graph():
    """Provide compiled graph instance (session-scoped for performance).

    Returns:
        Compiled graph instance
    """
    # Import and build your graph
    # from casts.your_cast.graph import your_cast_graph
    # return your_cast_graph.build()

    # Mock for template
    class MockGraph:
        def invoke(self, state):
            return state

        def stream(self, state):
            yield state

    return MockGraph()


@pytest.fixture
def graph():
    """Provide fresh graph instance (function-scoped).

    Returns:
        Compiled graph instance
    """
    # Import and build your graph
    # from casts.your_cast.graph import your_cast_graph
    # return your_cast_graph.build()

    # Mock for template
    class MockGraph:
        def invoke(self, state):
            return state

        def stream(self, state):
            yield state

    return MockGraph()


# ============================================================================
# Node Fixtures
# ============================================================================


@pytest.fixture
def sample_node():
    """Provide sample node instance.

    Returns:
        Node instance
    """
    # Import your node
    # from casts.your_cast.modules.nodes import YourNode
    # return YourNode()

    # Mock for template
    class MockNode:
        def __call__(self, state):
            return {"messages": [AIMessage(content="Mock response")]}

    return MockNode()


@pytest.fixture
def verbose_node():
    """Provide node with verbose logging enabled.

    Returns:
        Node instance with verbose=True
    """
    # Import your node
    # from casts.your_cast.modules.nodes import YourNode
    # return YourNode(verbose=True)

    # Mock for template
    class MockNode:
        def __init__(self):
            self.verbose = True

        def __call__(self, state):
            return {"messages": [AIMessage(content="Verbose mock response")]}

    return MockNode()


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def basic_config():
    """Provide basic configuration.

    Returns:
        Config dict
    """
    return {"configurable": {"thread_id": "test-thread-123"}}


@pytest.fixture
def config_with_tags():
    """Provide configuration with tags.

    Returns:
        Config dict with tags
    """
    return {
        "configurable": {"thread_id": "test-thread-123"},
        "tags": ["test", "integration"],
    }


@pytest.fixture
def production_config():
    """Provide production-like configuration.

    Returns:
        Config dict for production testing
    """
    return {
        "configurable": {
            "thread_id": "prod-thread-123",
            "checkpoint_id": "checkpoint-001",
        },
        "tags": ["production", "important"],
    }


# ============================================================================
# Mock Data Fixtures
# ============================================================================


@pytest.fixture
def mock_api_response():
    """Provide mock API response.

    Returns:
        Mock API response data
    """
    return {
        "status": "success",
        "data": {"result": "mock data", "confidence": 0.95},
        "metadata": {"timestamp": "2024-01-01T00:00:00Z"},
    }


@pytest.fixture
def mock_database_data():
    """Provide mock database data.

    Returns:
        Mock database records
    """
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
    ]


# ============================================================================
# Utility Fixtures
# ============================================================================


@pytest.fixture
def temp_directory(tmp_path):
    """Provide temporary directory for tests.

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path to temporary directory
    """
    return tmp_path


@pytest.fixture
def mock_environment(monkeypatch):
    """Set up mock environment variables.

    Args:
        monkeypatch: pytest's monkeypatch fixture

    Returns:
        Function to set environment variables
    """

    def set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)

    # Set some default test environment variables
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    return set_env


# ============================================================================
# Parameterized Test Data
# ============================================================================


@pytest.fixture(
    params=[
        "simple query",
        "query with multiple words",
        "query with special chars: !@#$%",
    ]
)
def various_queries(request):
    """Provide various query strings for parameterized tests.

    Args:
        request: pytest request object

    Returns:
        Query string
    """
    return request.param


@pytest.fixture(
    params=[
        {"query": "test1", "expected": "result1"},
        {"query": "test2", "expected": "result2"},
        {"query": "test3", "expected": "result3"},
    ]
)
def query_expectation_pairs(request):
    """Provide query-expectation pairs for parameterized tests.

    Args:
        request: pytest request object

    Returns:
        Dict with query and expected result
    """
    return request.param


# ============================================================================
# Setup/Teardown Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def reset_state():
    """Automatically reset state before/after each test.

    This fixture runs automatically for every test.
    """
    # Setup
    # Add any setup code here
    yield
    # Teardown
    # Add any cleanup code here


@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown():
    """Setup/teardown for entire test session.

    This runs once at the start and end of the test session.
    """
    # Session setup
    print("\n=== Starting Test Session ===")

    yield

    # Session teardown
    print("\n=== Ending Test Session ===")


# ============================================================================
# Markers and Helpers
# ============================================================================


def pytest_configure(config):
    """Configure custom pytest markers.

    Args:
        config: pytest config object
    """
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line(
        "markers", "requires_api: marks tests that require API access"
    )


# ============================================================================
# Usage Examples
# ============================================================================

"""
Example usage in test files:

# tests/unit_tests/test_example.py
def test_with_sample_state(sample_state):
    # sample_state is automatically provided
    assert sample_state["query"] == "sample query"

def test_with_compiled_graph(compiled_graph, sample_state):
    # Both fixtures are provided
    result = compiled_graph.invoke(sample_state)
    assert isinstance(result, dict)

def test_with_multiple_queries(various_queries):
    # This test runs once for each query in various_queries
    assert isinstance(various_queries, str)

@pytest.mark.slow
def test_slow_operation(sample_state):
    # Marked as slow test
    # Run only slow tests: pytest -m slow
    # Skip slow tests: pytest -m "not slow"
    pass
"""
