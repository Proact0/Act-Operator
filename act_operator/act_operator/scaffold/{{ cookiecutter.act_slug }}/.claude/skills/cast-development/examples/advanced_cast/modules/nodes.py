"""Advanced Cast Nodes - Agent node with tool calling."""

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from casts.base_node import BaseNode


class AgentNode(BaseNode):
    """Agent node that can use tools.

    This node creates a LangChain agent with tools and processes
    the user's query. The agent decides whether to use tools or
    respond directly.

    Attributes:
        tools: List of tools available to the agent
        model: LLM model for the agent (can be configured)
    """

    def __init__(self, tools=None):
        super().__init__()
        self.tools = tools or []

    def execute(self, state):
        """Execute agent with tools.

        Args:
            state: Graph state with 'query' and 'messages'

        Returns:
            dict: State update with agent's message
        """
        query = state["query"]
        messages = state.get("messages", [])

        # If no messages yet, add user query
        if not messages:
            messages = [HumanMessage(content=query)]

        # Create agent with tools
        # NOTE: In real implementation, you'd configure the model
        # Example: model = init_chat_model("gpt-4", model_provider="openai")
        #
        # For this example, we'll simulate agent behavior:
        # agent = create_agent(model, self.tools, system_prompt="You are a helpful assistant.")
        # response = agent.invoke({"messages": messages})

        # Simulated response (replace with real agent call)
        from langchain_core.messages import AIMessage
        response = AIMessage(content=f"I'll help you with: {query}")

        return {"messages": [response]}
