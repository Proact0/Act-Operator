"""[Optional] LLM tools or Model Context Protocol (MCP) adapters for the agents.

Guidelines:
    - Wrap side-effecting operations (API calls, filesystem access, etc.).
    - Register your tools or MCP adapters with agents for LLM integration.
    - If you use MCP adapters, you need langchain-mcp-adapters package installed. (`uv add langchain-mcp-adapters --package {{ cookiecutter.cast_slug }}`)

Official document URL:
    - Tools: https://docs.langchain.com/oss/python/langchain/tools
    - MCP Adapters: https://docs.langchain.com/oss/python/langchain/mcp
"""
