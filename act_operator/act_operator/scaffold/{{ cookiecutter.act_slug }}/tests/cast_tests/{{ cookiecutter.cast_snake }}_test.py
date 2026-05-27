"""Test the {{ cookiecutter.cast_name }} graph.

Official document URL:
    https://docs.langchain.com/oss/python/langgraph/test"""

from __future__ import annotations

from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph


def test_graph_produces_message() -> None:
    graph = {{ cookiecutter.cast_snake }}_graph()

    # Invoke with minimal state — OutputState filter exposes only the ``result`` key.
    result = graph.invoke({"query": "I'm joining Act"})

    # Verify SampleNode populated ``result``.
    assert "result" in result
    assert result["result"] == "Welcome to the Act!"
