"""Test the {{ cookiecutter.cast_name }} graph.

Official document URL:
    https://docs.langchain.com/oss/python/langgraph/test"""

from __future__ import annotations

from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph


def test_graph_produces_message() -> None:
    graph = {{ cookiecutter.cast_snake }}_graph()

    # 최소 상태로 그래프 실행
    result = graph.invoke({"query": "I'm joining Act"})

    # SampleNode가 message 키를 생성하는지 확인
    assert "messages" in result
    assert result["messages"] == "Welcome to the Act!"
