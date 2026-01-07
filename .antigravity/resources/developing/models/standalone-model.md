# Models

Models can be used standalone or within agents.

## Contents

- Initialize Models (OpenAI, Anthropic, Azure OpenAI, Google Gemini, AWS Bedrock)
- Common Parameters
- Usage in Agents
- Usage in Nodes (Standalone)

## Initialize Models

Approache: provider-specific classes.

### OpenAI

```python
# casts.{cast_name}.modules.models
from langchain_openai import ChatOpenAI

def get_openai_model_configured():
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=1000,
        timeout=30,
    )
```

### Anthropic

```python
# casts.{cast_name}.modules.models
from langchain_anthropic import ChatAnthropic

def get_anthropic_model_configured():
    return ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0.1,
        max_tokens=1000,
    )
```

### Azure OpenAI

```python
# casts.{cast_name}.modules.models
import os
from langchain_openai import AzureChatOpenAI

def get_azure_model_configured():
    return AzureChatOpenAI(
        model="gpt-4o",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
```

### Google Gemini

```python
# casts.{cast_name}.modules.models
from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini_model_configured():
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
```

### AWS Bedrock

```python
# casts.{cast_name}.modules.models
from langchain_aws import ChatBedrock

def get_bedrock_model_configured():
    return ChatBedrock(model="anthropic.claude-3-5-sonnet-20240620-v1:0")
```

---

## Common Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Model identifier (e.g., `"gpt-4o"`, `"openai:gpt-4o"`) |
| `api_key` | string | Provider API key (usually via env var) |
| `temperature` | number | Output randomness (0.0-1.0) |
| `max_tokens` | number | Maximum response tokens |
| `timeout` | number | Request timeout in seconds |
| `max_retries` | number | Retry attempts on failure |

---

## Usage in Agents

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .models import get_openai_model_configured

def set_sample_agent():
    return create_agent(
        model=get_openai_model_configured(),
        tools=[...],
    )
```

## Usage in Nodes (Standalone)

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from .models import get_openai_model_configured

class LLMNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.model = get_openai_model_configured()

    def execute(self, state):
        response = self.model.invoke(state["messages"])
        return {"messages": [response]}
```