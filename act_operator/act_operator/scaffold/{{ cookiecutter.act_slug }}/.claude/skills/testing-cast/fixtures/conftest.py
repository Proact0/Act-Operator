"""Reusable pytest fixtures for Act project testing.

Place this file in your cast's tests/ directory or in the project root tests/ directory.
"""

import pytest
from langgraph.checkpoint.memory import MemorySaver


# State Fixtures

@pytest.fixture
def empty_state():
    """Provides an empty state dict."""
    return {"input": "", "messages": [], "result": None}


@pytest.fixture
def populated_state():
    """Provides a populated state dict."""
    return {
        "input": "test query",
        "messages": [{"role": "user", "content": "hello"}],
        "context": {},
        "result": None
    }


@pytest.fixture
def mock_config():
    """Provides a standard test config."""
    return {"configurable": {"thread_id": "test-123", "user_id": "test-user"}}


# Mock Fixtures

@pytest.fixture
def mock_llm():
    """Provides a mock LLM for testing."""
    class MockLLM:
        def __init__(self, response="mocked response"):
            self.response = response
            self.calls = []

        def invoke(self, messages):
            self.calls.append(messages)
            return {"content": self.response}

        def bind_tools(self, tools):
            """Mock bind_tools method."""
            return self

    return MockLLM()


@pytest.fixture
def mock_store():
    """Provides a mock Store for testing memory operations."""
    class MockStore:
        def __init__(self):
            self.data = {}

        def get(self, namespace, key):
            return self.data.get((tuple(namespace), key))

        def put(self, namespace, key, value):
            self.data[(tuple(namespace), key)] = value

        def delete(self, namespace, key):
            self.data.pop((tuple(namespace), key), None)

        def search(self, namespace_prefix):
            results = []
            prefix = tuple(namespace_prefix)
            for (ns, k), v in self.data.items():
                if ns[:len(prefix)] == prefix:
                    # Create simple object with key and value
                    item = type('Item', (), {'key': k, 'value': v, 'namespace': ns})()
                    results.append(item)
            return results

    return MockStore()


@pytest.fixture
def mock_runtime(mock_store):
    """Provides a mock Runtime with Store."""
    class MockRuntime:
        def __init__(self, store):
            self.store = store
            self.stream_writer = None
            self.config = {}

    return MockRuntime(mock_store)


@pytest.fixture
def memory_saver():
    """Provides a MemorySaver checkpointer for testing."""
    return MemorySaver()


# Graph Fixtures (examples - customize per cast)

@pytest.fixture
def sample_graph():
    """Example graph fixture - customize for your cast."""
    # from casts.my_cast.graph import MyCastGraph
    # return MyCastGraph().build()
    pass


@pytest.fixture
def graph_with_memory(memory_saver):
    """Example graph with memory - customize for your cast."""
    # from casts.my_cast.graph import MyCastGraph
    # return MyCastGraph().build(checkpointer=memory_saver)
    pass


# Factory Fixtures

@pytest.fixture
def make_state():
    """Factory fixture for creating custom states."""
    def _make_state(**kwargs):
        default = {"input": "", "messages": [], "result": None}
        default.update(kwargs)
        return default
    return _make_state


@pytest.fixture
def make_config():
    """Factory fixture for creating custom configs."""
    def _make_config(thread_id="test-123", **kwargs):
        config = {"configurable": {"thread_id": thread_id}}
        config["configurable"].update(kwargs)
        return config
    return _make_config


# Async Fixtures

@pytest.fixture
async def async_mock_client():
    """Example async fixture - customize as needed."""
    class MockAsyncClient:
        async def get(self, url):
            return {"data": "mocked"}

        async def post(self, url, json):
            return {"status": "success"}

    return MockAsyncClient()


# Pytest Configuration Hooks

def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on location."""
    for item in items:
        # Auto-mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Auto-mark unit tests
        if "/tests/test_" in str(item.fspath) and "integration" not in str(item.fspath):
            item.add_marker(pytest.mark.unit)
