"""Entry point for the Rrrr workflow.

Overview:
    * Extends :class:`BaseWorkflow` to build a LangGraph StateGraph.
    * Uses :class:`RrrrState` as the underlying state container.
    * Ships with a minimal start → end path that you can extend.

Guidelines:
    1. Call ``builder.add_node()`` with custom node classes.
    2. Connect nodes via ``builder.add_edge()`` or conditional edges when branching.
    3. Return the compiled graph to orchestrate LangGraph execution.
"""

from langgraph.graph import StateGraph

from casts.base_workflow import BaseWorkflow
from casts.rrrr.modules.nodes import SampleNode
from casts.rrrr.modules.state import InputState, OutputState, State


class RrrrWorkflow(BaseWorkflow):
    """Workflow definition for Rrrr."""

    def __init__(self) -> None:
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        """Builds and compiles the workflow graph.

        Returns:
            CompiledStateGraph: Compiled graph ready for execution.
        """
        builder = StateGraph(self.state, input_schema=self.input, output_schema=self.output)

        builder.add_node("sample", SampleNode)
        builder.add_edge("__start__", "sample")
        builder.add_edge("sample", "__end__")

        workflow = builder.compile()
        workflow.name = self.name
        return workflow


rrrr_workflow = RrrrWorkflow()
