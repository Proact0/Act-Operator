# Utilities Guide for Cast Development

Comprehensive guide to common helper functions, data transformation utilities, validation patterns, and reusable code for Cast development.

## Table of Contents

1. [Introduction](#introduction)
2. [Common Helper Functions](#common-helper-functions)
   - [State Helpers](#state-helpers)
   - [Message Helpers](#message-helpers)
   - [Validation Helpers](#validation-helpers)
3. [Data Transformation Utilities](#data-transformation-utilities)
   - [Message Formatting](#message-formatting)
   - [State Merging](#state-merging)
   - [Type Conversion](#type-conversion)
4. [Validation Patterns](#validation-patterns)
   - [Input Validation](#input-validation)
   - [State Validation](#state-validation)
   - [Schema Validation](#schema-validation)
5. [Reusable Code Snippets](#reusable-code-snippets)
   - [Error Handling](#error-handling)
   - [Logging](#logging)
   - [Timing and Performance](#timing-and-performance)
6. [Integration Helpers](#integration-helpers)
   - [API Clients](#api-clients)
   - [Database Helpers](#database-helpers)
   - [File Operations](#file-operations)
7. [Best Practices](#best-practices)
8. [References](#references)

---

## Introduction

This guide provides reusable utilities for Cast development, including helpers for common tasks, data transformations, and validation.

---

## Common Helper Functions

### State Helpers

```python
def get_last_message(state):
    """Get last message from state."""
    if not state.messages:
        return None
    return state.messages[-1]

def get_user_messages(state):
    """Get all user messages."""
    return [m for m in state.messages if m.type == "human"]

def get_ai_messages(state):
    """Get all AI messages."""
    return [m for m in state.messages if m.type == "ai"]

def count_messages(state):
    """Count messages in state."""
    return len(state.messages)

def get_message_by_index(state, index):
    """Get message at specific index."""
    try:
        return state.messages[index]
    except IndexError:
        return None
```

### Message Helpers

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def create_user_message(content: str) -> HumanMessage:
    """Create user message."""
    return HumanMessage(content=content)

def create_ai_message(content: str) -> AIMessage:
    """Create AI message."""
    return AIMessage(content=content)

def create_system_message(content: str) -> SystemMessage:
    """Create system message."""
    return SystemMessage(content=content)

def extract_content(messages):
    """Extract content from messages."""
    return [m.content for m in messages]

def format_messages_for_display(messages):
    """Format messages for display."""
    formatted = []
    for msg in messages:
        role = msg.type if hasattr(msg, 'type') else 'unknown'
        content = msg.content if hasattr(msg, 'content') else str(msg)
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)
```

### Validation Helpers

```python
def is_valid_email(email: str) -> bool:
    """Validate email address."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_url(url: str) -> bool:
    """Validate URL."""
    import re
    pattern = r'^https?://[^\s]+$'
    return bool(re.match(pattern, url))

def is_non_empty_string(value: any) -> bool:
    """Check if value is non-empty string."""
    return isinstance(value, str) and len(value.strip()) > 0

def validate_required_fields(data: dict, fields: list) -> tuple[bool, list]:
    """
    Validate required fields exist.

    Returns:
        (is_valid, missing_fields)
    """
    missing = [f for f in fields if f not in data or not data[f]]
    return len(missing) == 0, missing
```

---

## Data Transformation Utilities

### Message Formatting

```python
def messages_to_dict(messages):
    """Convert messages to dict format."""
    return [
        {
            "role": m.type,
            "content": m.content
        }
        for m in messages
    ]

def dict_to_messages(data):
    """Convert dict to message objects."""
    from langchain_core.messages import HumanMessage, AIMessage

    messages = []
    for item in data:
        role = item.get("role", "human")
        content = item.get("content", "")

        if role in ["human", "user"]:
            messages.append(HumanMessage(content=content))
        elif role in ["ai", "assistant"]:
            messages.append(AIMessage(content=content))

    return messages
```

### State Merging

```python
def merge_states(old_state: dict, new_state: dict) -> dict:
    """Merge new state into old state."""
    merged = old_state.copy()
    merged.update(new_state)
    return merged

def deep_merge(dict1: dict, dict2: dict) -> dict:
    """Deep merge two dictionaries."""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result
```

### Type Conversion

```python
def safe_int(value, default=0):
    """Safely convert to int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """Safely convert to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def to_bool(value):
    """Convert various types to bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'y')
    return bool(value)
```

---

## Validation Patterns

### Input Validation

```python
class InputValidator:
    """Validate user inputs."""

    @staticmethod
    def validate_query(query: str) -> tuple[bool, str]:
        """Validate query string."""
        if not query or not query.strip():
            return False, "Query cannot be empty"

        if len(query) > 1000:
            return False, "Query too long (max 1000 chars)"

        return True, ""

    @staticmethod
    def validate_config(config: dict) -> tuple[bool, str]:
        """Validate configuration."""
        required = ["model", "temperature"]
        missing = [f for f in required if f not in config]

        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"

        if not 0 <= config.get("temperature", 0) <= 1:
            return False, "Temperature must be between 0 and 1"

        return True, ""
```

### State Validation

```python
from dataclasses import dataclass, fields

def validate_state_schema(state, state_class):
    """Validate state matches schema."""
    required_fields = [f.name for f in fields(state_class) if f.default == dataclasses.MISSING]

    for field_name in required_fields:
        if not hasattr(state, field_name):
            raise ValueError(f"Missing required field: {field_name}")

    return True
```

### Schema Validation

```python
from pydantic import BaseModel, ValidationError

class QuerySchema(BaseModel):
    query: str
    max_results: int = 10
    include_metadata: bool = False

def validate_with_pydantic(data: dict, schema: type[BaseModel]):
    """Validate data against Pydantic schema."""
    try:
        validated = schema(**data)
        return True, validated
    except ValidationError as e:
        return False, str(e)
```

---

## Reusable Code Snippets

### Error Handling

```python
from functools import wraps

def handle_errors(default_return=None):
    """Decorator for error handling."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator

# Usage
@handle_errors(default_return={})
def risky_function():
    # Might raise exception
    return {"result": process()}
```

### Logging

```python
import logging

def get_logger(name):
    """Get configured logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger

# Usage
logger = get_logger(__name__)
logger.info("Processing started")
```

### Timing and Performance

```python
import time
from functools import wraps

def timing_decorator(func):
    """Measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

# Usage
@timing_decorator
def slow_function():
    time.sleep(2)
    return "done"
```

---

## Integration Helpers

### API Clients

```python
import requests
from typing import Optional

class APIClient:
    """Reusable API client."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

    def get(self, endpoint: str, params: dict = None):
        """GET request."""
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict = None):
        """POST request."""
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
```

### Database Helpers

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path: str):
    """Context manager for database connection."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Usage
with get_db_connection("data.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
```

### File Operations

```python
import json
from pathlib import Path

def read_json(file_path: str) -> dict:
    """Read JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json(file_path: str, data: dict):
    """Write JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def ensure_dir(path: str):
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)

def read_text(file_path: str) -> str:
    """Read text file."""
    with open(file_path, 'r') as f:
        return f.read()

def write_text(file_path: str, content: str):
    """Write text file."""
    with open(file_path, 'w') as f:
        f.write(content)
```

---

## Best Practices

1. **Keep utilities pure** - No side effects when possible
2. **Type hints** - Document parameter and return types
3. **Docstrings** - Explain what utility does
4. **Error handling** - Graceful failure handling
5. **Test utilities** - Unit test each helper
6. **Organize by purpose** - Group related utilities
7. **Version control** - Track utility changes
8. **Document dependencies** - List required packages

---

## References

- Python Standard Library: https://docs.python.org/3/library/
- Pydantic: https://docs.pydantic.dev/
- LangChain Utilities: https://python.langchain.com/docs/modules/
