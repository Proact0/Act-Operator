"""[Optional] Middleware Classes for {{ cookiecutter.cast_name }} graphs.

Guidelines:
    - Use built-in middleware (e.g., PIIMiddleware) for common use cases.
    - Create custom middleware by subclassing AgentMiddleware or using decorators.
    - Middleware hooks:
      * before_agent: Before calling the agent (load memory, validate input)
      * before_model: Before each LLM call (update prompts, trim messages)
      * wrap_model_call: Around each LLM call (intercept/modify requests/responses)
      * wrap_tool_call: Around each tool call (intercept/modify tool execution)
      * after_model: After each LLM response (validate output, apply guardrails)
      * after_agent: After agent completes (save results, cleanup)
    - Register middleware in modules/agents.py `create_agent()`.

Official document URL:
    - Custom Middleware: https://docs.langchain.com/oss/python/langchain/middleware/custom
"""

# from typing import Callable
# from langchain.agents.middleware import AgentMiddleware, ModelRequest
# from langchain.agents.middleware.types import ModelResponse

# Example 1: Custom middleware using AgentMiddleware class
# class SampleMiddleware(AgentMiddleware):
#     """Sample custom middleware that logs model calls.
#
#     This middleware intercepts model calls and logs information
#     before and after the model execution.
#     """
#
#     def before_model(self, state, runtime):
#         """Called before each LLM call.
#
#         Args:
#             state: Current agent state.
#             runtime: Runtime context.
#
#         Returns:
#             dict: Optional state updates or None.
#         """
#         # Log or modify state before model call
#         print(f"About to call model with {len(state.get('messages', []))} messages")
#         return None
#
#     def after_model(self, state, runtime):
#         """Called after each LLM response.
#
#         Args:
#             state: Current agent state.
#             runtime: Runtime context.
#
#         Returns:
#             dict: Optional state updates or None.
#         """
#         # Log or validate after model call
#         messages = state.get("messages", [])
#         if messages:
#             last_message = messages[-1]
#             print(f"Model returned: {last_message.content[:100]}...")
#         return None
#
#     def wrap_model_call(
#         self,
#         request: ModelRequest,
#         handler: Callable[[ModelRequest], ModelResponse]
#     ) -> ModelResponse:
#         """Intercept and modify model requests/responses.
#
#         Args:
#             request: Model request object.
#             handler: Original handler function.
#
#         Returns:
#             ModelResponse: Model response.
#         """
#         # Modify request before calling handler
#         # request.model = ...  # Change model
#         # request.tools = ...  # Change tools
#         response = handler(request)
#         # Modify response after handler
#         return response

# Example 2: Custom middleware using decorators
# from langchain.agents.middleware import (
#     AgentState,
#     before_model,
#     after_model,
# )
# from typing_extensions import NotRequired
# from typing import Any
# from langgraph.runtime import Runtime

# class CustomState(AgentState):
#     """Extended state schema for middleware."""
#     model_call_count: NotRequired[int]
#     user_id: NotRequired[str]

# @before_model(state_schema=CustomState, can_jump_to=["end"])
# def check_call_limit(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
#     """Limit the number of model calls.
#
#     Args:
#         state: Current agent state.
#         runtime: Runtime context.
#
#     Returns:
#         dict: State updates or jump_to directive, or None.
#     """
#     count = state.get("model_call_count", 0)
#     if count > 10:
#         return {"jump_to": "end"}
#     return None

# @after_model(state_schema=CustomState)
# def increment_counter(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
#     """Increment model call counter.
#
#     Args:
#         state: Current agent state.
#         runtime: Runtime context.
#
#     Returns:
#         dict: State updates or None.
#     """
#     return {"model_call_count": state.get("model_call_count", 0) + 1}

# Usage with decorators:
# agent = create_agent(
#     model="gpt-4o",
#     middleware=[check_call_limit, increment_counter],
#     tools=[...],
# )
