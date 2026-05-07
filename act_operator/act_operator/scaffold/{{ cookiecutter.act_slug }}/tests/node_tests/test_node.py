"""Test the nodes for the Sam graph.

Official document URL: https://docs.langchain.com/oss/python/langgraph/test"""

from __future__ import annotations

from casts.{{ cookiecutter.cast_snake }}.modules.nodes import AsyncSampleNode, SampleNode


def test_base_node_calls_execute() -> None:
    node = SampleNode()
    result = node.execute({"query": "I'm joining Act"})
    assert result == {"message": "Welcome to the Act!"}


async def test_async_base_node_calls_execute() -> None:
    node = AsyncSampleNode()
    result = await node.execute({"query": "I'm joining Act"})
    assert result == {"message": "Welcome to the Act!"}
