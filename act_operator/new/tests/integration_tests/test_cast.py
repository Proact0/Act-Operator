"""Test the New Enw graph.

Official document URL: 
    https://docs.langchain.com/oss/python/langgraph/test"""

from __future__ import annotations

from importlib import import_module


def test_graph_produces_message() -> None:
    module = import_module("casts.new_enw.graph")
    graph = getattr(module, "new_enw_graph")

    # 최소 상태로 그래프 실행
    result = graph.invoke({})

    # SampleNode가 message 키를 생성하는지 확인
    assert "message" in result
    assert result["message"] == "Welcome to the Act!"


