"""Advanced Cast Example - Agent with tools and conditional routing.

This example demonstrates:
- Agent node with tool calling
- Conditional routing based on agent decisions
- Tool execution handling
- Multi-step conversations
"""

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from casts.base_graph import BaseGraph
from examples.advanced_cast.modules.nodes import AgentNode
from examples.advanced_cast.modules.state import InputState, OutputState, State
from examples.advanced_cast.modules.tools import calculator_tool, search_tool


def should_continue(state):
    """Route based on agent's tool calls.

    Args:
        state: Current graph state

    Returns:
        str: "tools" if agent called tools, "end" otherwise
    """
    messages = state["messages"]
    last_message = messages[-1]

    # If agent used tools, route to tool node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Otherwise finish
    return "end"


class AdvancedGraph(BaseGraph):
    """Advanced graph with agent and tools."""

    def __init__(self):
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        """Build graph with agent-tool loop."""
        builder = StateGraph(
            self.state,
            input_schema=self.input,
            output_schema=self.output
        )

        # Tools for the agent
        tools = [calculator_tool, search_tool]

        # Add nodes
        builder.add_node("agent", AgentNode(tools=tools))
        builder.add_node("tools", ToolNode(tools))

        # Graph flow
        builder.add_edge(START, "agent")

        # Conditional routing after agent
        builder.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",  # Execute tools
                "end": END         # Finish
            }
        )

        # After tools, return to agent
        builder.add_edge("tools", "agent")

        # Compile
        graph = builder.compile()
        graph.name = self.name
        return graph


# Export graph instance
advanced_graph = AdvancedGraph()
