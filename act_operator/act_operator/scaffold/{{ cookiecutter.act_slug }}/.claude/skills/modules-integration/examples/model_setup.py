"""Model setup examples - LangChain model integration.

Demonstrates how to initialize and configure language models for use in nodes.
Supports multiple providers: OpenAI, Anthropic, Google, etc.

Common patterns:
- Model initialization with init_chat_model
- Temperature and parameter configuration
- Streaming and callbacks
- Model fallbacks
"""

from dataclasses import dataclass
from typing import Annotated, List

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph.message import add_messages

from casts.base_node import BaseNode

# Note: Uncomment these imports when using real models
# from langchain.chat_models import init_chat_model
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
# from langchain_google_genai import ChatGoogleGenerativeAI


# Define state
@dataclass(kw_only=True)
class ModelState:
    """State for model examples."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]


class BasicModelNode(BaseNode):
    """Node with basic model configuration.

    Use this pattern when you need:
    - Simple model integration
    - Default settings
    - Single model provider
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo", verbose: bool = False):
        """Initialize with model.

        Args:
            model_name: Name of the model to use
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.model_name = model_name

        # In production, initialize real model:
        # from langchain.chat_models import init_chat_model
        # self.model = init_chat_model(model_name)

        # For demo, use None
        self.model = None

    def execute(self, state) -> dict:
        """Execute with model.

        Args:
            state: Current state

        Returns:
            dict: State updates with model response
        """
        self.log(f"Using model: {self.model_name}")

        if self.model:
            # Real execution
            response = self.model.invoke(state.query)
            return {"messages": [response]}
        else:
            # Mock response
            return {
                "messages": [
                    AIMessage(
                        content=f"[Mock Response from {self.model_name}] Processed: {state.query}"
                    )
                ]
            }


class ConfiguredModelNode(BaseNode):
    """Node with detailed model configuration.

    Use this pattern when you need:
    - Custom temperature settings
    - Token limits
    - Specific model parameters
    """

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 500,
        verbose: bool = False,
    ):
        """Initialize with configuration.

        Args:
            model_name: Name of the model
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # In production:
        # from langchain.chat_models import init_chat_model
        # self.model = init_chat_model(
        #     model_name,
        #     temperature=temperature,
        #     max_tokens=max_tokens
        # )

        self.model = None

    def execute(self, state) -> dict:
        """Execute with configured model.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log(
            f"Model config: {self.model_name}, temp={self.temperature}, max_tokens={self.max_tokens}"
        )

        if self.model:
            response = self.model.invoke(state.query)
            return {"messages": [response]}
        else:
            return {
                "messages": [
                    AIMessage(
                        content=f"[Mock {self.model_name}] temp={self.temperature}, tokens≤{self.max_tokens}: {state.query}"
                    )
                ]
            }


class MultiProviderNode(BaseNode):
    """Node that can use models from different providers.

    Use this pattern when you need:
    - Provider flexibility
    - Model comparison
    - Fallback between providers
    """

    def __init__(self, provider: str = "openai", model: str = None, verbose: bool = False):
        """Initialize with provider selection.

        Args:
            provider: Provider name (openai, anthropic, google)
            model: Specific model name (optional)
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.provider = provider
        self.model_name = model or self._default_model(provider)

        # In production, initialize based on provider:
        # if provider == "openai":
        #     from langchain_openai import ChatOpenAI
        #     self.model = ChatOpenAI(model=self.model_name)
        # elif provider == "anthropic":
        #     from langchain_anthropic import ChatAnthropic
        #     self.model = ChatAnthropic(model=self.model_name)
        # elif provider == "google":
        #     from langchain_google_genai import ChatGoogleGenerativeAI
        #     self.model = ChatGoogleGenerativeAI(model=self.model_name)

        self.model = None

    def _default_model(self, provider: str) -> str:
        """Get default model for provider.

        Args:
            provider: Provider name

        Returns:
            Default model name
        """
        defaults = {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-sonnet-20240229",
            "google": "gemini-pro",
        }
        return defaults.get(provider, "gpt-3.5-turbo")

    def execute(self, state) -> dict:
        """Execute with provider-specific model.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log(f"Using {self.provider} model: {self.model_name}")

        if self.model:
            response = self.model.invoke(state.query)
            return {"messages": [response]}
        else:
            return {
                "messages": [
                    AIMessage(
                        content=f"[Mock {self.provider}/{self.model_name}] Response: {state.query}"
                    )
                ]
            }


class FallbackModelNode(BaseNode):
    """Node with model fallback logic.

    Use this pattern when you need:
    - High availability
    - Cost optimization (try cheap model first)
    - Graceful degradation
    """

    def __init__(
        self,
        primary_model: str = "gpt-4",
        fallback_model: str = "gpt-3.5-turbo",
        verbose: bool = False,
    ):
        """Initialize with fallback configuration.

        Args:
            primary_model: Primary model to try
            fallback_model: Fallback model if primary fails
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.primary_model_name = primary_model
        self.fallback_model_name = fallback_model

        # In production:
        # from langchain.chat_models import init_chat_model
        # self.primary_model = init_chat_model(primary_model)
        # self.fallback_model = init_chat_model(fallback_model)

        self.primary_model = None
        self.fallback_model = None

    def execute(self, state) -> dict:
        """Execute with fallback logic.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log(f"Trying primary model: {self.primary_model_name}")

        # Try primary model
        if self.primary_model:
            try:
                response = self.primary_model.invoke(state.query)
                self.log("Primary model succeeded")
                return {"messages": [response]}
            except Exception as e:
                self.log(f"Primary model failed: {e}, trying fallback", level="warning")

        # Try fallback model
        self.log(f"Using fallback model: {self.fallback_model_name}")

        if self.fallback_model:
            try:
                response = self.fallback_model.invoke(state.query)
                self.log("Fallback model succeeded")
                return {"messages": [response]}
            except Exception as e:
                self.log(f"Fallback model also failed: {e}", level="error")

        # Mock response
        return {
            "messages": [
                AIMessage(
                    content=f"[Mock Fallback from {self.fallback_model_name}] Response: {state.query}"
                )
            ]
        }


class StreamingModelNode(BaseNode):
    """Node with streaming support.

    Use this pattern when you need:
    - Real-time response streaming
    - Better user experience for long responses
    - Token-by-token output
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo", verbose: bool = False):
        """Initialize with streaming enabled.

        Args:
            model_name: Model to use
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.model_name = model_name

        # In production:
        # from langchain.chat_models import init_chat_model
        # self.model = init_chat_model(model_name, streaming=True)

        self.model = None

    def execute(self, state) -> dict:
        """Execute with streaming.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log(f"Streaming from model: {self.model_name}")

        if self.model:
            # Stream response
            chunks = []
            for chunk in self.model.stream(state.query):
                chunks.append(chunk.content)
                self.log(f"Streamed chunk: {chunk.content}")

            full_response = "".join(chunks)
            return {"messages": [AIMessage(content=full_response)]}
        else:
            # Mock streaming
            return {
                "messages": [
                    AIMessage(
                        content=f"[Mock Stream from {self.model_name}] Response: {state.query}"
                    )
                ]
            }


# Usage example
if __name__ == "__main__":
    print("=== Model Setup Examples ===\n")

    # Test BasicModelNode
    print("--- BasicModelNode ---")
    node = BasicModelNode(model_name="gpt-3.5-turbo", verbose=True)
    state = ModelState(query="What is LangGraph?", messages=[])
    result = node(state)
    print(f"Result: {result['messages'][-1].content}\n")

    # Test ConfiguredModelNode
    print("--- ConfiguredModelNode ---")
    node = ConfiguredModelNode(
        model_name="gpt-4", temperature=0.3, max_tokens=100, verbose=True
    )
    state = ModelState(query="Explain briefly", messages=[])
    result = node(state)
    print(f"Result: {result['messages'][-1].content}\n")

    # Test MultiProviderNode
    print("--- MultiProviderNode ---")
    for provider in ["openai", "anthropic", "google"]:
        print(f"\n{provider.upper()}:")
        node = MultiProviderNode(provider=provider, verbose=True)
        state = ModelState(query="Hello!", messages=[])
        result = node(state)
        print(f"Result: {result['messages'][-1].content}")

    # Test FallbackModelNode
    print("\n--- FallbackModelNode ---")
    node = FallbackModelNode(
        primary_model="gpt-4", fallback_model="gpt-3.5-turbo", verbose=True
    )
    state = ModelState(query="Test fallback", messages=[])
    result = node(state)
    print(f"Result: {result['messages'][-1].content}\n")

    # Test StreamingModelNode
    print("--- StreamingModelNode ---")
    node = StreamingModelNode(model_name="gpt-3.5-turbo", verbose=True)
    state = ModelState(query="Stream this response", messages=[])
    result = node(state)
    print(f"Result: {result['messages'][-1].content}\n")

    print("=" * 70)
    print("Model setup patterns are ideal for:")
    print("  - Flexible model configuration")
    print("  - Provider abstraction")
    print("  - Cost optimization")
    print("  - High availability (fallbacks)")
    print("  - Streaming responses")
    print("\nTo use real models:")
    print("  1. Install provider package (langchain-openai, etc.)")
    print("  2. Set API key environment variable")
    print("  3. Uncomment model initialization code")
    print("  4. Replace mock responses with real invocations")
    print("\nExample environment variables:")
    print("  export OPENAI_API_KEY='your-key'")
    print("  export ANTHROPIC_API_KEY='your-key'")
    print("  export GOOGLE_API_KEY='your-key'")
    print("=" * 70)
