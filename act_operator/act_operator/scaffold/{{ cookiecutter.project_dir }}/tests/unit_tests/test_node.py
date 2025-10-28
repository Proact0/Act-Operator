"""Test the nodes for the {{ cookiecutter.cast_name }} graph.

Official document URL: https://docs.langchain.com/oss/python/langgraph/test"""

from __future__ import annotations

from casts.{{ cookiecutter.cast_snake }}.modules.nodes import SampleNode, AsyncSampleNode

def test_base_node_calls_execute() -> None:
    node = SampleNode(verbose=True)
    result = node()
    assert result == {"message": "Welcome to the Act!"}


async def test_async_base_node_calls_execute() -> None:
    node = AsyncSampleNode(verbose=True)
    result = await node()
    assert result == {"message": "Welcome to the Act!"}

