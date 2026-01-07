# Chat Models

## Featured Providers

| Model Class | Tool Calling | Structured Output | JSON Mode | Multimodal |
|-------------|--------------|-------------------|-----------|------------|
| `ChatOpenAI` | ✅ | ✅ | ✅ | ✅ |
| `ChatAnthropic` | ✅ | ✅ | ❌ | ✅ |
| `AzureChatOpenAI` | ✅ | ✅ | ✅ | ✅ |
| `ChatGoogleGenerativeAI` | ✅ | ✅ | ❌ | ✅ |
| `ChatVertexAI` | ✅ | ✅ | ❌ | ✅ |
| `ChatBedrock` | ✅ | ✅ | ❌ | ❌ |
| `ChatGroq` | ✅ | ✅ | ✅ | ❌ |
| `ChatMistralAI` | ✅ | ✅ | ❌ | ❌ |
| `ChatOllama` | ✅ | ✅ | ✅ | ❌ |
| `ChatHuggingFace` | ✅ | ✅ | ❌ | ❌ |

## OpenAI-Compatible Endpoints

Use `ChatOpenAI` with custom `base_url` for compatible providers.

```python
# casts.{cast_name}.modules.models
# write api key in .env
from langchain_openai import ChatOpenAI

def get_openrouter_model():
    return ChatOpenAI(
        model="...",  # Model available on OpenRouter
        base_url="https://openrouter.ai/api/v1",
    )
```