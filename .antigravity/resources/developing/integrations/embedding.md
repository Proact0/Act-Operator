# Embedding Models

Embedding models transform text into fixed-length vectors for semantic similarity search.

## Top Integrations

| Model | Package |
|-------|---------|
| `OpenAIEmbeddings` | `langchain-openai` |
| `AzureOpenAIEmbeddings` | `langchain-openai` |
| `GoogleGenerativeAIEmbeddings` | `langchain-google-genai` |
| `OllamaEmbeddings` | `langchain-ollama` |
| `CohereEmbeddings` | `langchain-cohere` |
| `MistralAIEmbeddings` | `langchain-mistralai` |

## Basic Usage

```python
# casts.{cast_name}.modules.utils
from langchain_openai import OpenAIEmbeddings

def get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")
```

## Interface Methods

| Method | Description |
|--------|-------------|
| `embed_documents(texts)` | Embed list of texts → `List[List[float]]` |
| `embed_query(text)` | Embed single query → `List[float]` |

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from .utils import get_embeddings

class EmbeddingNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.embeddings = get_embeddings()

    def execute(self, state):
        vectors = self.embeddings.embed_documents(state["documents"])
        query_vector = self.embeddings.embed_query(state["query"])
        return {"vectors": vectors, "query_vector": query_vector}
```

## Caching

```python
# casts.{cast_name}.modules.utils
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore
from langchain_openai import OpenAIEmbeddings

def get_cached_embeddings():
    underlying = OpenAIEmbeddings(model="text-embedding-3-small")
    store = LocalFileStore("./cache/")
    return CacheBackedEmbeddings.from_bytes_store(
        underlying,
        store,
        namespace=underlying.model,
    )
```

**Important:** Always set `namespace` to avoid collisions between different models.
