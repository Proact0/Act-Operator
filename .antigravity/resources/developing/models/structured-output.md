# Model Structured Output

Request standalone models to return structured data using Pydantic schemas.

## Contents

- Basic Usage
- Node Usage
- Include Raw Response
- Nested Structures
- Method Parameter

## Basic Usage

```python
# casts.{cast_name}.modules.models
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

class Movie(BaseModel):
    """A movie with details."""
    title: str = Field(description="Movie title")
    year: int = Field(description="Release year")
    director: str = Field(description="Director name")
    rating: float = Field(description="Rating out of 10")

def get_structured_model():
    model = ChatOpenAI(model="gpt-4o")
    return model.with_structured_output(Movie)
```

## Node Usage

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from .models import get_structured_model

class MovieExtractorNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.model = get_structured_model()

    def execute(self, state):
        result = self.model.invoke(state["query"])
        # result is Movie instance
        return {"movie": result.model_dump()}
```

## Include Raw Response

Access both parsed output and raw AIMessage (for metadata like token counts):

```python
# casts.{cast_name}.modules.models
def get_structured_model_with_raw():
    model = ChatOpenAI(model="gpt-4o")
    return model.with_structured_output(Movie, include_raw=True)
```

```python
# casts.{cast_name}.modules.nodes
class MovieExtractorWithMetaNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.model = get_structured_model_with_raw()

    def execute(self, state):
        result = self.model.invoke(state["query"])
        # result = {"raw": AIMessage(...), "parsed": Movie(...), "parsing_error": None}
        return {
            "movie": result["parsed"].model_dump(),
            "tokens": result["raw"].usage_metadata,
        }
  ```

## Nested Structures

```python
# casts.{cast_name}.modules.models
    from pydantic import BaseModel, Field

    class Actor(BaseModel):
        name: str
        role: str

    class MovieDetails(BaseModel):
        title: str
        year: int
        cast: list[Actor]
        genres: list[str]
        budget: float | None = Field(None, description="Budget in millions USD")

def get_detailed_movie_model():
    model = ChatOpenAI(model="gpt-4o")
    return model.with_structured_output(MovieDetails)
    ```

## Method Parameter

Some providers support different structured output methods:

| Method | Description |
|--------|-------------|
| `json_schema` | Provider's dedicated structured output |
| `function_calling` | Tool call-based structured output |
| `json_mode` | Valid JSON (schema in prompt) |

```python
# casts.{cast_name}.modules.models
def get_function_calling_model():
    model = ChatOpenAI(model="gpt-4o")
    return model.with_structured_output(Movie, method="function_calling")
```
