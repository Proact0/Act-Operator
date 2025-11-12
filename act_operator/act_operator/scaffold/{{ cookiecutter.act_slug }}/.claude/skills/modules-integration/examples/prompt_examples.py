"""Prompt template examples - LangChain prompt integration.

Demonstrates how to use LangChain prompt templates in nodes.
Prompts structure interactions with language models.

Common patterns:
- ChatPromptTemplate for conversations
- Few-shot prompting
- System and user message templates
"""

from dataclasses import dataclass
from typing import Annotated, List

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages

from casts.base_node import BaseNode


# Define state
@dataclass(kw_only=True)
class PromptState:
    """State for prompt examples."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    context: str = ""


class SimplePromptNode(BaseNode):
    """Node that uses a simple prompt template.

    Use this pattern when you need:
    - Basic prompt formatting
    - Simple text substitution
    - Consistent message structure
    """

    def __init__(self, verbose: bool = False):
        """Initialize with prompt template.

        Args:
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)

        # Create simple prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant."),
                ("user", "{query}"),
            ]
        )

    def execute(self, state) -> dict:
        """Execute with simple prompt.

        Args:
            state: Current state

        Returns:
            dict: State updates with formatted prompt
        """
        self.log(f"Formatting prompt for: {state.query}")

        # Format prompt
        messages = self.prompt.format_messages(query=state.query)

        self.log(f"Generated {len(messages)} messages")

        # For demonstration, return the formatted prompt
        # In production, you would pass this to a language model
        response = f"Formatted prompt:\n"
        for msg in messages:
            response += f"  {msg.__class__.__name__}: {msg.content}\n"

        return {"messages": [AIMessage(content=response)]}


class ContextualPromptNode(BaseNode):
    """Node that uses context in prompts.

    Use this pattern when you need:
    - Context-aware responses
    - RAG (Retrieval Augmented Generation) patterns
    - Background information injection
    """

    def __init__(self, verbose: bool = False):
        """Initialize with contextual prompt.

        Args:
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)

        # Create contextual prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant. Use the following context to answer questions:\n\nContext: {context}"),
                ("user", "{query}"),
            ]
        )

    def execute(self, state) -> dict:
        """Execute with contextual prompt.

        Args:
            state: Current state with context

        Returns:
            dict: State updates
        """
        self.log(f"Creating contextual prompt for: {state.query}")

        # Format prompt with context
        messages = self.prompt.format_messages(
            context=state.context or "No context provided", query=state.query
        )

        self.log(f"Included context: {len(state.context or '')} characters")

        response = f"Contextual prompt:\n"
        for msg in messages:
            response += f"  {msg.__class__.__name__}: {msg.content[:100]}...\n"

        return {"messages": [AIMessage(content=response)]}


class FewShotPromptNode(BaseNode):
    """Node that uses few-shot prompting.

    Use this pattern when you need:
    - Example-based learning
    - Consistent output format
    - Demonstrated behavior
    """

    def __init__(self, examples: List[tuple] = None, verbose: bool = False):
        """Initialize with few-shot examples.

        Args:
            examples: List of (input, output) example tuples
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)

        # Default examples
        self.examples = examples or [
            ("What is 2+2?", "The answer is 4."),
            ("What is the capital of France?", "The capital of France is Paris."),
        ]

        # Build prompt with examples
        messages = [("system", "You are a helpful assistant. Here are some examples:")]

        for user_ex, assistant_ex in self.examples:
            messages.append(("user", user_ex))
            messages.append(("assistant", assistant_ex))

        messages.append(("user", "{query}"))

        self.prompt = ChatPromptTemplate.from_messages(messages)

    def execute(self, state) -> dict:
        """Execute with few-shot prompt.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log(f"Creating few-shot prompt with {len(self.examples)} examples")

        # Format prompt
        messages = self.prompt.format_messages(query=state.query)

        self.log(f"Generated {len(messages)} messages")

        response = f"Few-shot prompt with {len(self.examples)} examples:\n"
        for i, msg in enumerate(messages[:4]):  # Show first few
            response += f"  {i+1}. {msg.__class__.__name__}: {msg.content[:50]}...\n"
        response += f"  ... and {len(messages) - 4} more messages"

        return {"messages": [AIMessage(content=response)]}


class ConversationPromptNode(BaseNode):
    """Node that maintains conversation history.

    Use this pattern when you need:
    - Multi-turn conversations
    - Message history management
    - Context from previous interactions
    """

    def __init__(self, verbose: bool = False):
        """Initialize with conversation prompt.

        Args:
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)

        # Create prompt with message history placeholder
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful conversational assistant."),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{query}"),
            ]
        )

    def execute(self, state) -> dict:
        """Execute with conversation history.

        Args:
            state: Current state with message history

        Returns:
            dict: State updates
        """
        self.log(f"Creating prompt with {len(state.messages or [])} history messages")

        # Format prompt with history
        messages = self.prompt.format_messages(
            history=state.messages or [], query=state.query
        )

        self.log(f"Total messages in prompt: {len(messages)}")

        response = f"Conversation prompt:\n"
        response += f"  History messages: {len(state.messages or [])}\n"
        response += f"  Total prompt messages: {len(messages)}\n"
        response += f"  Current query: {state.query}"

        return {"messages": [AIMessage(content=response)]}


class StructuredOutputPromptNode(BaseNode):
    """Node that requests structured output.

    Use this pattern when you need:
    - JSON or structured responses
    - Consistent output format
    - Parseable results
    """

    def __init__(self, output_schema: dict = None, verbose: bool = False):
        """Initialize with output schema.

        Args:
            output_schema: Expected output structure
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)

        self.output_schema = output_schema or {
            "answer": "string",
            "confidence": "float",
            "sources": "list[string]",
        }

        # Create prompt requesting structured output
        schema_str = "\n".join(
            f"  - {k}: {v}" for k, v in self.output_schema.items()
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"You are a helpful assistant. Always respond with JSON matching this schema:\n{schema_str}",
                ),
                ("user", "{query}"),
            ]
        )

    def execute(self, state) -> dict:
        """Execute with structured output prompt.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Creating structured output prompt")

        # Format prompt
        messages = self.prompt.format_messages(query=state.query)

        response = f"Structured output prompt:\n"
        response += f"  Expected schema: {self.output_schema}\n"
        response += f"  Query: {state.query}"

        return {"messages": [AIMessage(content=response)]}


# Usage example
if __name__ == "__main__":
    print("=== Prompt Template Examples ===\n")

    # Test SimplePromptNode
    print("--- SimplePromptNode ---")
    node = SimplePromptNode(verbose=True)
    state = PromptState(query="What is LangGraph?", messages=[])
    result = node(state)
    print(f"Result:\n{result['messages'][-1].content}\n")

    # Test ContextualPromptNode
    print("--- ContextualPromptNode ---")
    node = ContextualPromptNode(verbose=True)
    state = PromptState(
        query="What is the product name?",
        messages=[],
        context="Our company sells a product called SuperWidget that helps with automation.",
    )
    result = node(state)
    print(f"Result:\n{result['messages'][-1].content}\n")

    # Test FewShotPromptNode
    print("--- FewShotPromptNode ---")
    examples = [
        ("Translate 'hello' to Spanish", "Spanish: hola"),
        ("Translate 'goodbye' to Spanish", "Spanish: adiós"),
    ]
    node = FewShotPromptNode(examples=examples, verbose=True)
    state = PromptState(query="Translate 'thank you' to Spanish", messages=[])
    result = node(state)
    print(f"Result:\n{result['messages'][-1].content}\n")

    # Test ConversationPromptNode
    print("--- ConversationPromptNode ---")
    node = ConversationPromptNode(verbose=True)
    history = [
        HumanMessage(content="Hi, my name is Alice"),
        AIMessage(content="Hello Alice! How can I help you?"),
    ]
    state = PromptState(query="What is my name?", messages=history)
    result = node(state)
    print(f"Result:\n{result['messages'][-1].content}\n")

    # Test StructuredOutputPromptNode
    print("--- StructuredOutputPromptNode ---")
    schema = {"category": "string", "priority": "int", "tags": "list[string]"}
    node = StructuredOutputPromptNode(output_schema=schema, verbose=True)
    state = PromptState(query="Classify this urgent bug report", messages=[])
    result = node(state)
    print(f"Result:\n{result['messages'][-1].content}\n")

    print("=" * 70)
    print("Prompt template patterns are ideal for:")
    print("  - Consistent model interactions")
    print("  - Context injection (RAG)")
    print("  - Few-shot learning")
    print("  - Conversation management")
    print("  - Structured output generation")
    print("\nBest practices:")
    print("  - Use system messages for role/behavior")
    print("  - Include examples for consistent formatting")
    print("  - Use placeholders for dynamic content")
    print("  - Keep prompts concise and clear")
    print("=" * 70)
