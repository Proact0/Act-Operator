#!/usr/bin/env python3
"""
Create a new cast with full boilerplate structure.

This script extends `act cast -c [name]` by adding all module files
with proper imports and type hints.

Usage:
    uv run python .claude/skills/engineering-act/scripts/create_cast.py "My Cast Name"
    uv run python .claude/skills/engineering-act/scripts/create_cast.py "My Cast" --minimal
"""

import argparse
import subprocess
import sys
from pathlib import Path


def to_snake_case(name: str) -> str:
    """Convert display name to snake_case."""
    import re
    # Replace non-alphanumeric with underscore
    s = re.sub(r'[^a-zA-Z0-9]+', '_', name)
    # Insert underscore before uppercase letters
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
    # Lowercase and remove multiple underscores
    s = re.sub(r'_+', '_', s.lower())
    return s.strip('_')


def to_pascal_case(name: str) -> str:
    """Convert display name to PascalCase."""
    import re
    # Split on non-alphanumeric
    words = re.split(r'[^a-zA-Z0-9]+', name)
    # Capitalize each word
    return ''.join(word.capitalize() for word in words if word)


def create_module_file(cast_dir: Path, module_name: str, content: str):
    """Create a module file with given content."""
    module_path = cast_dir / "modules" / f"{module_name}.py"
    module_path.write_text(content)
    print(f"  ✓ Created modules/{module_name}.py")


def create_full_cast(cast_name: str, minimal: bool = False):
    """Create cast with full boilerplate."""

    # Convert name variations
    cast_snake = to_snake_case(cast_name)
    cast_pascal = to_pascal_case(cast_name)

    print(f"\n🎬 Creating cast: {cast_name}")
    print(f"   Snake case: {cast_snake}")
    print(f"   Pascal case: {cast_pascal}\n")

    # Run act cast command
    print("📦 Running act cast scaffolding...")
    try:
        result = subprocess.run(
            ["uv", "run", "act", "cast", "-c", cast_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running act cast: {e.stderr}", file=sys.stderr)
        sys.exit(1)

    cast_dir = Path.cwd() / "casts" / cast_snake

    if not cast_dir.exists():
        print(f"❌ Cast directory not found: {cast_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\n📝 Adding boilerplate modules...")

    # State module
    state_content = f'''"""State definitions for {cast_name} cast."""

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class {cast_pascal}State(TypedDict):
    """State schema for {cast_name} graph.

    Attributes:
        messages: Conversation messages (accumulated with add_messages reducer)
        # Add your state fields here
    """
    messages: Annotated[list[BaseMessage], add_messages]
    # Example fields (customize as needed):
    # current_step: str
    # iteration: int
    # result: str | None
'''
    create_module_file(cast_dir, "state", state_content)

    # Models module
    models_content = '''"""LLM model configurations."""

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


def get_default_model():
    """Get the default LLM model.

    Returns:
        ChatAnthropic: Default model instance
    """
    return ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
    )


def get_openai_model():
    """Get OpenAI model.

    Returns:
        ChatOpenAI: OpenAI model instance
    """
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
    )
'''
    create_module_file(cast_dir, "models", models_content)

    if not minimal:
        # Agents module
        agents_content = '''"""Agent node implementations."""

from ..base_node import BaseNode


class ExampleAgentNode(BaseNode):
    """Example agent node.

    Replace with your actual agent logic.
    """

    def execute(self, state):
        """Execute agent logic.

        Args:
            state: Current graph state

        Returns:
            dict: State updates
        """
        messages = state.get("messages", [])

        # TODO: Implement agent logic
        # Example:
        # llm = get_default_model()
        # response = llm.invoke(messages)

        return {
            "messages": ["Agent response placeholder"]
        }
'''
        create_module_file(cast_dir, "agents", agents_content)

        # Tools module
        tools_content = '''"""Tool definitions for agents."""

from langchain_core.tools import tool


@tool
def example_tool(query: str) -> str:
    """Example tool that processes a query.

    Args:
        query: The input query to process

    Returns:
        str: Processed result
    """
    # TODO: Implement tool logic
    return f"Processed: {query}"


# List of all available tools
TOOLS = [
    example_tool,
]
'''
        create_module_file(cast_dir, "tools", tools_content)

        # Prompts module
        prompts_content = '''"""Prompt templates."""

from langchain_core.prompts import ChatPromptTemplate


SYSTEM_PROMPT = """You are a helpful assistant."""


def get_agent_prompt():
    """Get the main agent prompt template.

    Returns:
        ChatPromptTemplate: Agent prompt template
    """
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{messages}"),
    ])
'''
        create_module_file(cast_dir, "prompts", prompts_content)

        # Utils module
        utils_content = '''"""Utility functions."""


def format_messages(messages: list) -> str:
    """Format messages for display.

    Args:
        messages: List of messages

    Returns:
        str: Formatted messages
    """
    return "\\n".join(str(msg) for msg in messages)
'''
        create_module_file(cast_dir, "utils", utils_content)

        # Middlewares module
        middlewares_content = '''"""Middleware functions for graph execution."""


def logging_middleware(state, next_step):
    """Log state before and after execution.

    Args:
        state: Current state
        next_step: Next execution step

    Returns:
        Updated state
    """
    print(f"Before: {list(state.keys())}")
    result = next_step(state)
    print(f"After: {list(result.keys())}")
    return result
'''
        create_module_file(cast_dir, "middlewares", middlewares_content)

    print(f"\n✅ Cast '{cast_name}' created successfully!")
    print(f"\n📁 Location: {cast_dir}")
    print(f"\n📝 Next steps:")
    print(f"   1. Edit {cast_dir}/graph.py to implement your graph")
    print(f"   2. Customize modules/state.py with your state schema")
    print(f"   3. Implement nodes in modules/agents.py")
    print(f"   4. Add tools in modules/tools.py if needed")
    print(f"\n💡 See architecting-act skill output (CLAUDE.md) for architecture guidance")


def main():
    parser = argparse.ArgumentParser(
        description="Create a new cast with full boilerplate",
        epilog="Example: uv run python .claude/skills/engineering-act/scripts/create_cast.py \"My Graph\""
    )
    parser.add_argument(
        "cast_name",
        help="Display name of the cast (e.g., 'My Graph')"
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Create minimal boilerplate (state and models only)"
    )

    args = parser.parse_args()

    create_full_cast(args.cast_name, args.minimal)


if __name__ == "__main__":
    main()
