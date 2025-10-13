"""Entry point for the Newone workflow.

Overview:
    * Extends :class:`BaseWorkflow` to build a LangGraph StateGraph.
    * Uses :class:`NewoneState` as the underlying state container.
    * Ships with a minimal start → end path that you can extend.

Guidelines:
    1. Call ``builder.add_node()`` with custom node classes.
    2. Connect nodes via ``builder.add_edge()`` or conditional edges when branching.
    3. Return the compiled graph to orchestrate LangGraph execution.
"""

from langgraph.graph import StateGraph

from casts.base_workflow import BaseWorkflow
from casts.newone.modules.state import State


class NewoneWorkflow(BaseWorkflow):
    """Workflow definition for Newone."""

    def __init__(self) -> None:
        super().__init__()
        self.state = State

    def build(self):
        """Builds and compiles the workflow graph.

        Returns:
            CompiledStateGraph: Compiled graph ready for execution.
        """
        builder = StateGraph(self.state)

        builder.add_edge("__start__", "__end__")

        workflow = builder.compile()
        workflow.name = self.name
        return workflow


newone_workflow = NewoneWorkflow()
