# Mocking Strategies

## When to Use This Resource
Read this for comprehensive mocking patterns for LLMs, tools, APIs, databases, and Store.

## Mocking LLM Responses

### Using FakeListLLM

```python
from langchain_core.language_models.fake import FakeListLLM

class TestWithFakeLLM:
    def test_node_with_fake_llm(self):
        fake_responses = [
            "First response",
            "Second response"
        ]
        llm = FakeListLLM(responses=fake_responses)

        node = LLMNode()
        node.llm = llm

        result = node.execute({"input": "test"})
        assert "First response" in result["output"]
```

### Custom LLM Mock

```python
class MockLLM:
    def __init__(self, response="mocked"):
        self.response = response
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return {"content": self.response}

class TestWithCustomMock:
    def test_tracks_llm_calls(self):
        mock_llm = MockLLM(response="test response")
        node = MyNode()
        node.llm = mock_llm

        node.execute({"messages": [{"role": "user", "content": "hi"}]})

        assert len(mock_llm.calls) == 1
```

## Mocking Tools

```python
class TestToolMocking:
    def test_mock_tool_execution(self, monkeypatch):
        def mock_tool(query: str) -> str:
            return f"Mocked result for: {query}"

        monkeypatch.setattr("modules.tools.search_tools.web_search", mock_tool)

        node = ToolCallingNode()
        result = node.execute({"query": "test"})

        assert "Mocked result" in result["tool_output"]
```

## Mocking External APIs

```python
import responses

class TestAPIMocking:
    @responses.activate
    def test_api_call(self):
        responses.add(
            responses.GET,
            "https://api.example.com/data",
            json={"result": "mocked"},
            status=200
        )

        node = APINode()
        result = node.execute({"endpoint": "/data"})

        assert result["data"]["result"] == "mocked"
```

## Mocking Database

```python
class TestDatabaseMocking:
    @pytest.fixture
    def mock_db(self, monkeypatch):
        class MockDB:
            def query(self, sql):
                return [{"id": 1, "name": "test"}]

        mock = MockDB()
        monkeypatch.setattr("modules.db.get_connection", lambda: mock)
        return mock

    def test_with_mock_db(self, mock_db):
        node = DatabaseNode()
        result = node.execute({"query": "SELECT * FROM users"})

        assert len(result["rows"]) > 0
```

## Mocking Store

```python
class MockStore:
    def __init__(self):
        self.data = {}

    def get(self, namespace, key):
        return self.data.get((tuple(namespace), key))

    def put(self, namespace, key, value):
        self.data[(tuple(namespace), key)] = value

    def search(self, namespace_prefix):
        results = []
        prefix = tuple(namespace_prefix)
        for (ns, k), v in self.data.items():
            if ns[:len(prefix)] == prefix:
                results.append(type('Item', (), {'key': k, 'value': v})())
        return results

@pytest.fixture
def mock_store():
    return MockStore()

class TestWithMockStore:
    def test_node_uses_store(self, mock_store):
        class MockRuntime:
            def __init__(self, store):
                self.store = store

        node = MemoryNode()
        runtime = MockRuntime(mock_store)

        # Populate mock store
        mock_store.put(("user", "123"), "prefs", {"theme": "dark"})

        result = node.execute({"user_id": "123"}, runtime=runtime)

        assert result["preferences"]["theme"] == "dark"
```

## Mocking File Operations

```python
class TestFileMocking:
    def test_file_read(self, tmp_path):
        # Use tmp_path fixture for real temp files
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        node = FileReaderNode()
        result = node.execute({"file_path": str(test_file)})

        assert result["content"] == "test content"

    def test_file_write(self, tmp_path):
        output_file = tmp_path / "output.txt"

        node = FileWriterNode()
        node.execute({"path": str(output_file), "content": "data"})

        assert output_file.read_text() == "data"
```

## Partial Mocking

```python
class TestPartialMocking:
    def test_mock_one_method(self, monkeypatch):
        node = ComplexNode()

        # Mock only one method
        def mock_expensive_operation(data):
            return "mocked result"

        monkeypatch.setattr(node, "_expensive_operation", mock_expensive_operation)

        # Other methods still work normally
        result = node.execute({"input": "test"})

        assert result["output"] == "mocked result"
```

## References
- Related: `testing-nodes.md` (applying mocks to nodes)
- Related: `async-testing.md` (mocking async operations)
