# Models Guide for LangGraph Applications

Comprehensive guide to LLM initialization, configuration, and usage with `init_chat_model()` and direct model APIs.

## Table of Contents

1. [Introduction](#introduction)
2. [init_chat_model() Usage](#init_chat_model-usage)
   - [Basic Usage](#basic-usage)
   - [Provider Selection](#provider-selection)
   - [Model Configuration](#model-configuration)
   - [Environment Variables](#environment-variables)
3. [Model Providers](#model-providers)
   - [Anthropic (Claude)](#anthropic-claude)
   - [OpenAI (GPT)](#openai-gpt)
   - [Google (Gemini)](#google-gemini)
   - [Other Providers](#other-providers)
4. [Model Configuration and Parameters](#model-configuration-and-parameters)
   - [Temperature](#temperature)
   - [Max Tokens](#max-tokens)
   - [Top P](#top-p)
   - [Stop Sequences](#stop-sequences)
5. [Streaming Responses](#streaming-responses)
   - [Sync Streaming](#sync-streaming)
   - [Async Streaming](#async-streaming)
   - [Streaming in Nodes](#streaming-in-nodes)
6. [Error Handling and Retries](#error-handling-and-retries)
   - [API Error Handling](#api-error-handling)
   - [Retry Logic](#retry-logic)
   - [Fallback Models](#fallback-models)
7. [Model Selection Patterns](#model-selection-patterns)
   - [Task-Based Selection](#task-based-selection)
   - [Cost Optimization](#cost-optimization)
   - [Performance Trade-offs](#performance-trade-offs)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [References](#references)

---

## Introduction

LangChain provides `init_chat_model()` for unified model initialization across providers. This guide covers model selection, configuration, and best practices.

**Key concepts:**
- **init_chat_model()**: Unified model initialization
- **Provider**: Model API provider (Anthropic, OpenAI, etc.)
- **Configuration**: Model parameters (temperature, max_tokens)
- **Streaming**: Real-time token-by-token responses

---

## init_chat_model() Usage

### Basic Usage

```python
from langchain_core.language_models import init_chat_model

# Initialize with model name
llm = init_chat_model("claude-3-5-sonnet-20241022")

# Or with provider
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    model_provider="anthropic"
)

# Invoke
from langchain_core.messages import HumanMessage
response = llm.invoke([HumanMessage(content="Hello!")])
```

### Provider Selection

```python
# Anthropic
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    model_provider="anthropic"
)

# OpenAI
llm = init_chat_model(
    "gpt-4",
    model_provider="openai"
)

# Auto-detect from model name
llm = init_chat_model("gpt-4")  # Detects OpenAI

# Environment-based
import os
provider = os.getenv("MODEL_PROVIDER", "anthropic")
model_name = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
llm = init_chat_model(model_name, model_provider=provider)
```

### Model Configuration

```python
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    model_provider="anthropic",
    temperature=0.7,
    max_tokens=2048,
    timeout=30.0
)

# With all parameters
llm = init_chat_model(
    model="claude-3-5-sonnet-20241022",
    model_provider="anthropic",
    temperature=0.7,
    max_tokens=2048,
    top_p=0.9,
    timeout=30.0,
    max_retries=3,
    api_key="sk-ant-..."  # Or from env
)
```

### Environment Variables

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-3-5-sonnet-20241022
```

```python
# Auto-loads from environment
llm = init_chat_model("claude-3-5-sonnet-20241022")
# Uses ANTHROPIC_API_KEY from env

# Override
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    api_key="custom-key"
)
```

---

## Model Providers

### Anthropic (Claude)

```python
from langchain_anthropic import ChatAnthropic

# Direct usage
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0,
    max_tokens=4096
)

# With init_chat_model
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    model_provider="anthropic",
    temperature=0
)

# Available models
models = [
    "claude-3-5-sonnet-20241022",  # Latest, most capable
    "claude-3-5-haiku-20241022",   # Fast, cost-effective
    "claude-3-opus-20240229",      # Most capable (older)
]
```

### OpenAI (GPT)

```python
from langchain_openai import ChatOpenAI

# Direct usage
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    max_tokens=2048
)

# With init_chat_model
llm = init_chat_model(
    "gpt-4",
    model_provider="openai"
)

# Available models
models = [
    "gpt-4-turbo-preview",
    "gpt-4",
    "gpt-3.5-turbo",
]
```

### Google (Gemini)

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.7
)

# With init_chat_model
llm = init_chat_model(
    "gemini-pro",
    model_provider="google"
)
```

### Other Providers

```python
# Azure OpenAI
llm = init_chat_model(
    "gpt-4",
    model_provider="azure_openai",
    azure_endpoint="https://...",
    api_version="2023-05-15"
)

# Cohere
llm = init_chat_model(
    "command",
    model_provider="cohere"
)

# Hugging Face
llm = init_chat_model(
    "meta-llama/Llama-2-70b-chat-hf",
    model_provider="huggingface"
)
```

---

## Model Configuration and Parameters

### Temperature

Controls randomness (0-1):

```python
# Deterministic (0)
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    temperature=0
)
# Same input → same output

# Balanced (0.7)
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    temperature=0.7
)
# Creative but consistent

# Very creative (1)
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    temperature=1
)
# Maximum creativity
```

**Guidelines:**
- **0-0.3**: Factual, deterministic tasks
- **0.7**: General purpose, balanced
- **0.9-1**: Creative writing, brainstorming

### Max Tokens

Maximum output length:

```python
# Short responses
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    max_tokens=512
)

# Standard
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    max_tokens=2048
)

# Long-form
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    max_tokens=4096
)
```

**Model limits:**
- Claude 3: Up to 4096 output tokens
- GPT-4: Up to 4096 output tokens
- GPT-3.5: Up to 4096 output tokens

### Top P

Nucleus sampling (0-1):

```python
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    top_p=0.9
)
```

**Note:** Usually use `temperature` OR `top_p`, not both.

### Stop Sequences

Stop generation at specific strings:

```python
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
)
```

---

## Streaming Responses

### Sync Streaming

```python
llm = init_chat_model("claude-3-5-sonnet-20241022")

# Stream tokens
for chunk in llm.stream("Write a poem"):
    print(chunk.content, end="", flush=True)
```

### Async Streaming

```python
llm = init_chat_model("claude-3-5-sonnet-20241022")

async def stream_response():
    async for chunk in llm.astream("Write a poem"):
        print(chunk.content, end="", flush=True)

await stream_response()
```

### Streaming in Nodes

```python
from act_operator_lib.base_node import AsyncBaseNode

class StreamingNode(AsyncBaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm = init_chat_model("claude-3-5-sonnet-20241022")
    
    async def execute(self, state, runtime):
        chunks = []
        
        async for chunk in self.llm.astream(state.messages):
            chunks.append(chunk)
            
            # Stream to runtime if available
            if runtime and runtime.stream:
                runtime.stream.send(chunk.content)
        
        # Combine chunks
        full_response = chunks[-1]
        
        return {"messages": [full_response]}
```

---

## Error Handling and Retries

### API Error Handling

```python
from langchain_core.exceptions import LLMException

class RobustModelNode(BaseNode):
    def execute(self, state):
        try:
            response = self.llm.invoke(state.messages)
            return {"messages": [response]}
            
        except LLMException as e:
            self.logger.error(f"LLM error: {e}")
            return {
                "messages": [AIMessage(content="I'm having trouble responding right now.")],
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RetryModelNode(BaseNode):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def execute(self, state):
        response = self.llm.invoke(state.messages)
        return {"messages": [response]}
```

### Fallback Models

```python
class FallbackModelNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.primary_llm = init_chat_model("claude-3-5-sonnet-20241022")
        self.fallback_llm = init_chat_model("claude-3-5-haiku-20241022")
    
    def execute(self, state):
        try:
            response = self.primary_llm.invoke(state.messages)
            return {"messages": [response]}
        except Exception as e:
            self.logger.warning(f"Primary model failed: {e}, using fallback")
            response = self.fallback_llm.invoke(state.messages)
            return {"messages": [response]}
```

---

## Model Selection Patterns

### Task-Based Selection

```python
class TaskBasedModelNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.simple_llm = init_chat_model("claude-3-5-haiku-20241022")
        self.complex_llm = init_chat_model("claude-3-5-sonnet-20241022")
    
    def execute(self, state):
        # Simple task
        if len(state.query) < 50 and not state.get("complex"):
            llm = self.simple_llm
        else:
            llm = self.complex_llm
        
        response = llm.invoke(state.messages)
        return {"messages": [response]}
```

### Cost Optimization

```python
class CostOptimizedNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Fast, cheap model
        self.fast_llm = init_chat_model(
            "claude-3-5-haiku-20241022",
            max_tokens=1024
        )
        # Powerful, expensive model
        self.strong_llm = init_chat_model(
            "claude-3-5-sonnet-20241022",
            max_tokens=4096
        )
    
    def execute(self, state):
        # Try fast model first
        response = self.fast_llm.invoke(state.messages)
        
        # Check if needs stronger model
        if "I need more context" in response.content:
            response = self.strong_llm.invoke(state.messages)
        
        return {"messages": [response]}
```

### Performance Trade-offs

```python
# Fast, less capable
fast_llm = init_chat_model(
    "claude-3-5-haiku-20241022",
    temperature=0,
    max_tokens=1024
)

# Balanced
balanced_llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    temperature=0.7,
    max_tokens=2048
)

# Slow, most capable
powerful_llm = init_chat_model(
    "claude-3-opus-20240229",
    temperature=0,
    max_tokens=4096
)
```

---

## Best Practices

1. **Use environment variables** - Don't hardcode API keys
2. **Set appropriate temperature** - 0 for factual, 0.7 for creative
3. **Limit max_tokens** - Control costs and latency
4. **Handle errors gracefully** - Retry or use fallbacks
5. **Use streaming** - Better UX for long responses
6. **Choose right model** - Balance cost/performance
7. **Monitor usage** - Track API costs
8. **Test with different models** - Find best fit
9. **Cache when possible** - Avoid duplicate calls
10. **Log model calls** - Debug and monitor

---

## Troubleshooting

**API Key errors:**
```python
# Check env var
import os
print("API Key set:", bool(os.getenv("ANTHROPIC_API_KEY")))

# Verify in init
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY") or "fallback"
)
```

**Rate limits:**
```python
# Add retry logic
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=2, min=4, max=60))
def call_llm(messages):
    return llm.invoke(messages)
```

**Timeout issues:**
```python
# Increase timeout
llm = init_chat_model(
    "claude-3-5-sonnet-20241022",
    timeout=60.0  # 60 seconds
)
```

---

## References

- LangChain Models: https://python.langchain.com/docs/modules/model_io/models
- init_chat_model: https://python.langchain.com/docs/modules/model_io/chat/
- Anthropic Docs: https://docs.anthropic.com/
- OpenAI Docs: https://platform.openai.com/docs
