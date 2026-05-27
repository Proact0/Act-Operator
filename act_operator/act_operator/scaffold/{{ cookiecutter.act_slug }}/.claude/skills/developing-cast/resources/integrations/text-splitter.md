# Text Splitters

Break large documents into smaller retrievable chunks.

## Recommended: RecursiveCharacterTextSplitter

Best default for most use cases. Preserves natural language structure.

```python
# casts.{cast_name}.modules.utils
from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
```

## Splitting Strategies

### Text Structure-Based

Maintains hierarchy: paragraphs → sentences → words.

```python
# casts.{cast_name}.modules.utils
from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_recursive_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=0,
    )
```

### Token-Based

Splits by token count (useful for LLM context limits).

```python
# casts.{cast_name}.modules.utils
from langchain_text_splitters import CharacterTextSplitter

def get_token_splitter():
    return CharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=100,
        chunk_overlap=0,
    )
```

### Document Structure-Based

For structured documents (Markdown, HTML, JSON, Code).

| Type | Splitter |
|------|----------|
| Markdown | Split by headers (#, ##, ###) |
| HTML | Split by tags |
| JSON | Split by objects/arrays |
| Code | Split by functions/classes |

---

## Usage in Nodes

```python
# casts.{cast_name}.modules.nodes
from langchain_core.documents import Document
from casts.base_node import BaseNode
from .utils import get_text_splitter, get_vector_store

class DocumentProcessorNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.splitter = get_text_splitter()
        self.store = get_vector_store()

    def execute(self, state):
        # Split documents
        docs = [Document(page_content=text) for text in state["texts"]]
        chunks = self.splitter.split_documents(docs)
        
        # Store chunks
        self.store.add_documents(chunks)
        
        return {"chunk_count": len(chunks)}
```
