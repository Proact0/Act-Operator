"""[Optional] Middleware Classes for Sam graphs.

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
    - Built-in Middleware: https://docs.langchain.com/oss/python/langchain/middleware/built-in
    - Custom Middleware: https://docs.langchain.com/oss/python/langchain/middleware/custom
"""
