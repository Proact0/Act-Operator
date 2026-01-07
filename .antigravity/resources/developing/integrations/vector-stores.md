# Vector Stores

Vector stores hold embedded data and perform similarity search.

## Contents

- Interface Methods
- Top Integrations (In-Memory, Chroma, FAISS, Pinecone, PGVector, Qdrant)
- Usage in Nodes

## Interface Methods

| Method | Description |
|--------|-------------|
| `add_documents(documents, ids)` | Add documents to store |
| `delete(ids)` | Remove documents by ID |
| `similarity_search(query, k, filter)` | Search for similar documents |

## Top Integrations

### In-Memory

```python
# casts.{cast_name}.modules.utils
from langchain_core.vectorstores import InMemoryVectorStore
from .utils import get_embeddings

def get_vector_store():
    return InMemoryVectorStore(embedding=get_embeddings())
```

### Chroma

```python
# casts.{cast_name}.modules.utils
from langchain_chroma import Chroma

def get_chroma_store():
    return Chroma(
        collection_name="my_collection",
        embedding_function=get_embeddings(),
        persist_directory="./chroma_db",
    )
```

### FAISS

```python
# casts.{cast_name}.modules.utils
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

def get_faiss_store():
    embeddings = get_embeddings()
    embedding_dim = len(embeddings.embed_query("test"))
    index = faiss.IndexFlatL2(embedding_dim)
    return FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
```

### Pinecone

```python
# casts.{cast_name}.modules.utils
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

def get_pinecone_store(api_key: str, index_name: str):
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    return PineconeVectorStore(embedding=get_embeddings(), index=index)
```

### PGVector

```python
# casts.{cast_name}.modules.utils
from langchain_postgres import PGVector

def get_pgvector_store(connection_string: str):
    return PGVector(
        embeddings=get_embeddings(),
        collection_name="my_docs",
        connection=connection_string,
    )
```

### Qdrant

```python
# casts.{cast_name}.modules.utils
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

def get_qdrant_store():
    client = QdrantClient(":memory:")
    embeddings = get_embeddings()
    vector_size = len(embeddings.embed_query("test"))
    
    if not client.collection_exists("my_collection"):
        client.create_collection(
            collection_name="my_collection",
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    return QdrantVectorStore(
        client=client,
        collection_name="my_collection",
        embedding=embeddings,
    )
```

---

## Usage in Nodes

```python
# casts.{cast_name}.modules.nodes
from langchain_core.documents import Document
from casts.base_node import BaseNode
from .utils import get_vector_store

class VectorStoreNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.store = get_vector_store()

    def execute(self, state):
        # Add documents
        docs = [Document(page_content=text) for text in state["texts"]]
        self.store.add_documents(docs)
        
        # Search
        results = self.store.similarity_search(
            state["query"],
            k=3,
            filter={"source": "docs"},  # Optional metadata filter
        )
        return {"results": [r.page_content for r in results]}
```
