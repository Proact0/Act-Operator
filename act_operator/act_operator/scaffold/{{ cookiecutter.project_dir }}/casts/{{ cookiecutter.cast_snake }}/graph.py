"""Entry point for the {{ cookiecutter.cast_name }} graph.

Overview:
    * Extends :class:`BaseGraph` to build a LangGraph StateGraph.
    * Uses :class:`{{ cookiecutter.cast_snake | title | replace(" ", "") }}State` as the underlying state container.
    * Ships with a minimal start → end path that you can extend.

Guidelines:
    1. Call ``builder.add_node()`` with custom node classes.
    2. Connect nodes via ``builder.add_edge()`` or ``builder.add_conditional_edges()`` when branching.
    3. Return the compiled graph to orchestrate LangGraph execution.

Official document URL: 
    - Graph API: https://docs.langchain.com/oss/python/langgraph/graph-api
    - Graph API Usage: https://docs.langchain.com/oss/python/langgraph/use-graph-api
"""

from langgraph.graph import StateGraph, START, END

from casts.base_graph import BaseGraph
from casts.{{ cookiecutter.cast_snake }}.modules.nodes import SampleNode
from casts.{{ cookiecutter.cast_snake }}.modules.state import InputState, OutputState, State


class {{ cookiecutter.cast_snake | title | replace(" ", "") }}Graph(BaseGraph):
    """Graph definition for {{ cookiecutter.cast_name }}."""

    def __init__(self) -> None:
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        """Builds and compiles the graph graph.

        Returns:
            CompiledStateGraph: Compiled graph ready for execution.
        """
        builder = StateGraph(self.state, input_schema=self.input, output_schema=self.output)

        builder.add_node("sample", SampleNode)
        builder.add_edge(START, "sample")
        builder.add_edge("sample", END)

        graph = builder.compile()
        graph.name = self.name
        return graph


{{ cookiecutter.cast_snake }}_graph = {{ cookiecutter.cast_snake | title | replace(" ", "") }}Graph()
