# Mocking Strategies

## Mock LLM

### FakeListLLM
```python
from langchain_core.language_models.fake import FakeListLLM

def test_with_fake_llm():
    llm = FakeListLLM(responses=["First", "Second"])
    node = LLMNode()
    node.llm = llm
    
    result = node.execute({"input": "test"})
    assert "First" in result["output"]
```

### Custom Mock
```python
class MockLLM:
    def __init__(self, response="mocked"):
        self.response = response
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return {"content": self.response}

def test_tracks_calls():
    mock = MockLLM()
    node = MyNode()
    node.llm = mock
    
    node.execute({"messages": [{"role": "user", "content": "hi"}]})
    
    assert len(mock.calls) == 1
```

## Mock Tools

```python
def test_mock_tool(monkeypatch):
    def mock_search(query: str) -> str:
        return f"Mocked: {query}"
    
    monkeypatch.setattr("modules.tools.web_search", mock_search)
    
    node = ToolNode()
    result = node.execute({"query": "test"})
    
    assert "Mocked" in result["output"]
```

## Mock External APIs

```python
import responses

@responses.activate
def test_api_call():
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

## Mock Store

```python
class MockStore:
    def __init__(self):
        self.data = {}

    def get(self, namespace, key):
        return self.data.get((tuple(namespace), key))

    def put(self, namespace, key, value):
        self.data[(tuple(namespace), key)] = value

@pytest.fixture
def mock_store():
    return MockStore()

def test_with_store(mock_store):
    class MockRuntime:
        def __init__(self, store):
            self.store = store
    
    mock_store.put(("user", "123"), "prefs", {"theme": "dark"})
    
    node = MemoryNode()
    runtime = MockRuntime(mock_store)
    result = node.execute({"user_id": "123"}, runtime=runtime)
    
    assert result["preferences"]["theme"] == "dark"
```

## Mock Files

```python
def test_file_read(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    
    node = FileNode()
    result = node.execute({"path": str(test_file)})
    
    assert result["content"] == "content"
```

## Partial Mocking

```python
def test_mock_one_method(monkeypatch):
    node = ComplexNode()
    
    def mock_expensive(data):
        return "mocked"
    
    monkeypatch.setattr(node, "_expensive_operation", mock_expensive)
    
    result = node.execute({"input": "test"})
    assert result["output"] == "mocked"
```

