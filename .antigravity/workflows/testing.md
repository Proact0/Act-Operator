---
description: cast 노드 또는 casts(그래프)용 pytest 작성, LLM/API/Store 호출 모킹 전략, 테스트 픽스처 설정, sync/async 테스트 스위트 구성 시 사용. 효과적인 cast 검증을 위한 종합 패턴 제공.
---

# Cast 테스트

Backand Act의 cast를 위한 효과적인 pytest 테스트 작성.

## 사용하지 말 것

- 구현 작성 → `developing`
- 아키텍처 설계 → `architecting`
- 프로젝트 설정 → `engineering`

## 빠른 참조

```bash
# 테스트 실행
uv run pytest                              # 전체 테스트
uv run pytest tests/test_nodes.py          # 특정 파일
uv run pytest -k "test_my_function"        # 이름 매칭
uv run pytest -v                           # 상세 출력
uv run pytest -x                           # 첫 실패 시 중지
uv run pytest --lf                         # 마지막 실패만

# 커버리지 포함
uv run pytest --cov=casts --cov-report=html
```

## 리소스

| 작업 | 리소스 |
|------|--------|
| 노드 테스트 (sync/async) | `resources/testing-nodes.md` |
| 그래프 테스트 | `resources/testing-graphs.md` |
| LLM, API, Store 모킹 | `resources/mocking.md` |
| 재사용 가능한 픽스처 | `resources/fixtures.md` |
| 커버리지 전략 | `resources/coverage.md` |

## 테스트 패턴

### 노드 테스트
```python
class TestMyNode:
    def test_execute(self):
        node = MyNode()
        result = node.execute({"input": "test"})
        assert "output" in result
```

### 비동기 노드 테스트
```python
@pytest.mark.asyncio
async def test_async_node():
    node = AsyncNode()
    result = await node.execute({"query": "test"})
    assert "data" in result
```

### 그래프 테스트
```python
def test_graph_invoke(graph):
    result = graph.invoke({"input": "test"})
    assert result is not None
```

### LLM 모킹
```python
def test_with_mock(monkeypatch):
    class MockLLM:
        def invoke(self, messages):
            return {"content": "mocked"}
    
    node = LLMNode()
    monkeypatch.setattr(node, "llm", MockLLM())
    result = node.execute({"messages": []})
```

## 테스트 구조

```
casts/{cast_name}/
└── tests/
    ├── conftest.py      # 픽스처
    ├── test_nodes.py    # 노드 테스트
    └── test_graph.py    # 그래프 테스트
```

## 모범 사례

**DO:**
- 구현이 아닌 동작 테스트
- 설명적인 이름 사용
- Arrange-Act-Assert 패턴
- 외부 의존성 모킹
- 에러 경로 테스트

**DON'T:**
- 프라이빗 메서드 테스트
- 순서 의존적 테스트
- 타이밍에 `sleep()` 사용
- 100% 커버리지 목표
