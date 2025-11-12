# Logging and Tracing Guide for LangGraph Applications

Comprehensive guide to logging best practices, LangSmith integration, debug output, and production logging strategies for LangGraph applications in Act-Operator.

## Table of Contents

1. [Introduction](#introduction)
2. [Logging Fundamentals](#logging-fundamentals)
   - [Python logging Module](#python-logging-module)
   - [Log Levels](#log-levels)
   - [Logger Hierarchy](#logger-hierarchy)
   - [Basic Configuration](#basic-configuration)
3. [LangGraph Logging Best Practices](#langgraph-logging-best-practices)
   - [Logging in Nodes](#logging-in-nodes)
   - [State Logging](#state-logging)
   - [Execution Flow Logging](#execution-flow-logging)
   - [Error Logging](#error-logging)
4. [LangSmith Integration](#langsmith-integration)
   - [Setting Up LangSmith](#setting-up-langsmith)
   - [Automatic Tracing](#automatic-tracing)
   - [Custom Run Names](#custom-run-names)
   - [Adding Metadata](#adding-metadata)
   - [Viewing Traces](#viewing-traces)
5. [Debug Output Patterns](#debug-output-patterns)
   - [Development vs Production](#development-vs-production)
   - [Verbose Mode](#verbose-mode)
   - [Debug Decorators](#debug-decorators)
   - [Conditional Debugging](#conditional-debugging)
6. [Production Logging Strategies](#production-logging-strategies)
   - [Log Aggregation](#log-aggregation)
   - [Performance Monitoring](#performance-monitoring)
   - [Error Tracking](#error-tracking)
   - [Security Considerations](#security-considerations)
7. [Structured Logging](#structured-logging)
   - [JSON Logging](#json-logging)
   - [Context Managers](#context-managers)
   - [Request ID Tracking](#request-id-tracking)
   - [Correlation IDs](#correlation-ids)
8. [Log Configuration](#log-configuration)
   - [Configuration Files](#configuration-files)
   - [Environment-Based Config](#environment-based-config)
   - [Dynamic Configuration](#dynamic-configuration)
   - [Log Rotation](#log-rotation)
9. [Advanced Techniques](#advanced-techniques)
   - [Custom Log Handlers](#custom-log-handlers)
   - [Log Filtering](#log-filtering)
   - [Performance Profiling](#performance-profiling)
   - [Distributed Tracing](#distributed-tracing)
10. [Integration Patterns](#integration-patterns)
    - [LangSmith + CloudWatch](#langsmith--cloudwatch)
    - [LangSmith + Datadog](#langsmith--datadog)
    - [LangSmith + Sentry](#langsmith--sentry)
    - [Custom Integrations](#custom-integrations)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)
13. [References](#references)

---

## Introduction

Effective logging and tracing are essential for understanding, debugging, and monitoring LangGraph applications. This guide covers:

- **Logging**: Capturing events, errors, and state during execution
- **Tracing**: Following execution flow through LangSmith
- **Debugging**: Development-time visibility into operations
- **Monitoring**: Production observability and alerting

**Why logging matters:**
- Debug issues in development
- Monitor performance in production
- Track errors and exceptions
- Audit system behavior
- Understand user interactions
- Optimize graph execution

---

## Logging Fundamentals

### Python logging Module

**Basic setup:**
```python
import logging

# Get logger
logger = logging.getLogger(__name__)

# Log messages
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

**In Cast nodes:**
```python
from act_operator_lib.base_node import BaseNode
import logging

class MyNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def execute(self, state):
        self.logger.info("Processing query: %s", state.query)

        try:
            result = self.process(state.query)
            self.logger.debug("Result: %s", result)
            return {"result": result}
        except Exception as e:
            self.logger.error("Processing failed: %s", e, exc_info=True)
            raise
```

### Log Levels

**Standard levels:**
```python
# DEBUG (10): Detailed diagnostic info
logger.debug("State: %s", state)

# INFO (20): Confirmation things work as expected
logger.info("Agent completed successfully")

# WARNING (30): Something unexpected, but working
logger.warning("High iteration count: %d", count)

# ERROR (40): Error occurred, operation failed
logger.error("API call failed: %s", error)

# CRITICAL (50): Severe error, program may not continue
logger.critical("Database connection lost")
```

**Setting level:**
```python
# Only show INFO and above
logging.basicConfig(level=logging.INFO)

# Only show WARNING and above (production)
logging.basicConfig(level=logging.WARNING)

# Show everything (development)
logging.basicConfig(level=logging.DEBUG)
```

**Level hierarchy:**
```
CRITICAL (50)
ERROR (40)
WARNING (30)
INFO (20)
DEBUG (10)
NOTSET (0)

If level = INFO:
✓ CRITICAL, ERROR, WARNING, INFO
✗ DEBUG
```

### Logger Hierarchy

**Module-based loggers:**
```python
# {{ cookiecutter.python_package }}/nodes/agent.py
logger = logging.getLogger(__name__)
# Logger name: "{{ cookiecutter.python_package }}.nodes.agent"

# {{ cookiecutter.python_package }}/nodes/tools.py
logger = logging.getLogger(__name__)
# Logger name: "{{ cookiecutter.python_package }}.nodes.tools"

# Configure parent logger
logging.getLogger("{{ cookiecutter.python_package }}").setLevel(logging.INFO)
# All child loggers inherit this level
```

**Hierarchy example:**
```
root
└─ {{ cookiecutter.python_package }}
   ├─ nodes
   │  ├─ agent
   │  └─ tools
   └─ graph

# Set level on parent affects all children
logging.getLogger("{{ cookiecutter.python_package }}.nodes").setLevel(logging.DEBUG)
# Both agent and tools loggers now at DEBUG level
```

### Basic Configuration

**Simple configuration:**
```python
import logging

# Basic setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Advanced configuration:**
```python
import logging
import sys

# Configure with handlers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
```

**Configuration file:**
```python
# logging.conf
[loggers]
keys=root,{{ cookiecutter.python_package }}

[handlers]
keys=console,file

[formatters]
keys=standard

[logger_root]
level=WARNING
handlers=console

[logger_{{ cookiecutter.python_package }}]
level=INFO
handlers=console,file
qualname={{ cookiecutter.python_package }}
propagate=0

[handler_console]
class=StreamHandler
level=INFO
formatter=standard
args=(sys.stdout,)

[handler_file]
class=FileHandler
level=DEBUG
formatter=standard
args=('app.log', 'a')

[formatter_standard]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Load configuration:**
```python
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)
```

---

## LangGraph Logging Best Practices

### Logging in Nodes

**BaseNode logging:**
```python
from act_operator_lib.base_node import BaseNode

class AgentNode(BaseNode):
    def execute(self, state):
        # Use built-in logging (only if verbose=True)
        self.log("Processing query:", state.query)

        result = self.process(state)

        self.log("Generated result:", result=result)
        return {"result": result}

# Enable verbose logging
node = AgentNode(verbose=True)
```

**Custom logger:**
```python
import logging

class AgentNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def execute(self, state):
        # Always logs (based on log level)
        self.logger.info("Processing query: %s", state.query)

        # Debug details
        self.logger.debug("State details: %s", state)

        try:
            result = self.process(state)
            self.logger.info("Completed successfully")
            return {"result": result}

        except Exception as e:
            # Log with full traceback
            self.logger.error(
                "Processing failed: %s",
                e,
                exc_info=True,
                extra={
                    "query": state.query,
                    "iteration": state.iteration
                }
            )
            raise
```

**Combining both:**
```python
class AgentNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def execute(self, state):
        # Production logging (always on)
        self.logger.info("Agent starting")

        # Development logging (only if verbose=True)
        self.log("Detailed state:", state=state)

        # Process
        result = self.process(state)

        # Production
        self.logger.info("Agent completed")

        # Development
        self.log("Result details:", result=result)

        return {"result": result}
```

### State Logging

**Log state changes:**
```python
class StateLoggingNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def execute(self, state):
        # Log input state
        self.logger.info(
            "Node input",
            extra={
                "query": state.query,
                "iteration": state.iteration,
                "message_count": len(state.messages)
            }
        )

        # Process
        result = self.process(state)

        # Log output state (what changed)
        self.logger.info(
            "Node output",
            extra={
                "result_length": len(result.get("result", "")),
                "fields_updated": list(result.keys())
            }
        )

        return result
```

**State diff logging:**
```python
class DiffLoggingNode(BaseNode):
    def execute(self, state):
        # Capture input
        input_snapshot = {
            "iteration": state.iteration,
            "message_count": len(state.messages)
        }

        # Process
        result = self.process(state)

        # Log changes
        self.logger.info(
            "State changes",
            extra={
                "before": input_snapshot,
                "after": result,
                "iteration_delta": result.get("iteration", 0) - input_snapshot["iteration"]
            }
        )

        return result
```

### Execution Flow Logging

**Entry/exit logging:**
```python
class FlowLoggingNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def execute(self, state):
        self.logger.info(f"→ Entering {self.name}")

        try:
            result = self.process(state)
            self.logger.info(f"← Exiting {self.name} (success)")
            return result

        except Exception as e:
            self.logger.error(f"← Exiting {self.name} (error: {e})")
            raise
```

**Timing logging:**
```python
import time

class TimedNode(BaseNode):
    def execute(self, state):
        start_time = time.time()
        self.logger.info(f"{self.name} started")

        try:
            result = self.process(state)

            duration = time.time() - start_time
            self.logger.info(
                f"{self.name} completed",
                extra={
                    "duration_ms": duration * 1000,
                    "duration_seconds": duration
                }
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"{self.name} failed after {duration:.2f}s: {e}"
            )
            raise
```

### Error Logging

**Comprehensive error logging:**
```python
class ErrorLoggingNode(BaseNode):
    def execute(self, state):
        try:
            result = self.risky_operation(state)
            return {"result": result}

        except ValueError as e:
            # Expected error - INFO level
            self.logger.info(
                "Validation error",
                extra={
                    "error_type": "ValueError",
                    "error": str(e),
                    "query": state.query
                }
            )
            return {"error": str(e)}

        except TimeoutError as e:
            # External issue - WARNING level
            self.logger.warning(
                "Timeout occurred",
                extra={
                    "error_type": "TimeoutError",
                    "error": str(e),
                    "query": state.query
                }
            )
            return {"error": "timeout"}

        except Exception as e:
            # Unexpected error - ERROR level with traceback
            self.logger.error(
                "Unexpected error",
                exc_info=True,
                extra={
                    "error_type": type(e).__name__,
                    "error": str(e),
                    "query": state.query,
                    "state": str(state)
                }
            )
            raise
```

**Error context:**
```python
class ContextualErrorLogging(BaseNode):
    def execute(self, state):
        try:
            return self.process(state)

        except Exception as e:
            # Log with full context
            self.logger.error(
                "Node execution failed",
                exc_info=True,
                extra={
                    "node": self.name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "state_query": state.query,
                    "state_iteration": state.iteration,
                    "state_message_count": len(state.messages),
                    "timestamp": time.time()
                }
            )

            # Re-raise or return error state
            raise
```

---

## LangSmith Integration

### Setting Up LangSmith

**Environment variables:**
```bash
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_api_key_here
LANGCHAIN_PROJECT=my-cast-project
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

**In code:**
```python
import os

# Ensure tracing enabled
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."
os.environ["LANGCHAIN_PROJECT"] = "{{ cookiecutter.act_slug }}"
```

**Verify setup:**
```python
from langsmith import Client

client = Client()
print("LangSmith connected:", client.info)
```

### Automatic Tracing

**LangGraph automatic tracing:**
```python
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage

# Build graph
builder = StateGraph(State)
builder.add_node("agent", agent_node)
graph = builder.compile()

# Invoke - automatically traced if LANGCHAIN_TRACING_V2=true
result = graph.invoke({
    "messages": [HumanMessage(content="Hello")]
})

# Trace appears in LangSmith automatically
```

**What gets traced:**
- Graph invocation
- Each node execution
- LLM calls
- Tool calls
- State changes
- Errors and exceptions
- Timing information

**View traces:**
```
1. Go to https://smith.langchain.com/
2. Navigate to your project
3. See traces in chronological order
4. Click trace to see detailed view
```

### Custom Run Names

**Named runs:**
```python
from langchain_core.runnables import RunnableConfig

# Custom run name
config = RunnableConfig(
    run_name="Agent Query: Weather in SF",
    tags=["weather", "production"]
)

result = graph.invoke(
    {"messages": [HumanMessage(content="Weather in SF")]},
    config=config
)

# Appears in LangSmith with custom name
```

**Dynamic run names:**
```python
def get_run_name(state):
    """Generate descriptive run name from state."""
    query = state.get("query", "unknown")
    return f"Query: {query[:50]}"

# Use in invocation
config = RunnableConfig(
    run_name=get_run_name(input_state)
)
result = graph.invoke(input_state, config=config)
```

### Adding Metadata

**Run metadata:**
```python
config = RunnableConfig(
    run_name="Customer Support Query",
    tags=["support", "production", "high-priority"],
    metadata={
        "user_id": "user-123",
        "session_id": "session-456",
        "channel": "web",
        "priority": "high",
        "environment": "production"
    }
)

result = graph.invoke(input_state, config=config)
```

**In nodes:**
```python
from langsmith import traceable

class TracedNode(BaseNode):
    @traceable(
        run_type="chain",
        name="agent_node",
        metadata={"node_type": "agent"}
    )
    def execute(self, state):
        # Execution traced with metadata
        result = self.process(state)
        return {"result": result}
```

**Adding tags dynamically:**
```python
def execute(self, state, config):
    # Get existing tags
    tags = config.get("tags", []) if config else []

    # Add dynamic tags
    if state.iteration > 5:
        tags.append("high-iteration")

    if state.get("error"):
        tags.append("has-error")

    # Update config
    config = config or {}
    config["tags"] = tags

    # Process with updated tags
    result = self.process(state)
    return {"result": result}
```

### Viewing Traces

**Trace structure in LangSmith:**
```
Run: Agent Query: Weather in SF
├─ Graph Invocation
│  ├─ Node: agent
│  │  ├─ LLM Call (ChatAnthropic)
│  │  │  Input: "Weather in SF"
│  │  │  Output: [Tool Call: get_weather]
│  │  └─ Duration: 1.2s
│  ├─ Node: tools
│  │  ├─ Tool: get_weather
│  │  │  Input: {location: "San Francisco"}
│  │  │  Output: {temp: 72, conditions: "sunny"}
│  │  └─ Duration: 0.8s
│  └─ Node: agent
│     ├─ LLM Call (ChatAnthropic)
│     │  Input: [Previous + Tool Result]
│     │  Output: "It's 72°F and sunny in SF"
│     └─ Duration: 1.1s
└─ Total Duration: 3.1s
```

**Filtering traces:**
```
In LangSmith UI:
- Filter by tags: "production"
- Filter by metadata: user_id = "user-123"
- Filter by status: Error, Success
- Filter by duration: > 5 seconds
- Search by run name
```

**Trace analysis:**
```
Per trace:
- View inputs/outputs at each step
- See state changes
- Inspect LLM prompts and responses
- View tool calls and results
- Check error stack traces
- Compare with other runs
```

---

## Debug Output Patterns

### Development vs Production

**Environment-based configuration:**
```python
import os
import logging

# Determine environment
env = os.getenv("ENV", "development")

# Configure based on environment
if env == "development":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
elif env == "production":
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
```

**Conditional debugging:**
```python
class SmartLoggingNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        self.is_dev = os.getenv("ENV") == "development"

    def execute(self, state):
        # Always log in production
        self.logger.info("Processing query")

        # Detailed debug only in development
        if self.is_dev:
            self.logger.debug(f"Full state: {state}")
            self.logger.debug(f"Query: {state.query}")

        result = self.process(state)
        return {"result": result}
```

### Verbose Mode

**Using BaseNode verbose:**
```python
class VerboseNode(BaseNode):
    def execute(self, state):
        # Only logs if verbose=True
        self.log("Starting processing")
        self.log("Query:", state.query)

        result = self.process(state)

        self.log("Result:", result=result)
        return {"result": result}

# Development
node = VerboseNode(verbose=True)  # Logs enabled

# Production
node = VerboseNode(verbose=False)  # Logs disabled
```

**Environment-based verbose:**
```python
import os

class AutoVerboseNode(BaseNode):
    def __init__(self, **kwargs):
        # Auto-enable verbose in development
        if "verbose" not in kwargs:
            kwargs["verbose"] = os.getenv("ENV") == "development"
        super().__init__(**kwargs)

    def execute(self, state):
        self.log("Processing...")  # Auto-enabled in dev
        return self.process(state)
```

### Debug Decorators

**Custom debug decorator:**
```python
import functools
import logging

def debug_node(func):
    """Decorator to log node execution."""
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    def wrapper(self, state, *args, **kwargs):
        logger.debug(f"→ Entering {func.__name__}")
        logger.debug(f"  State: {state}")

        try:
            result = func(self, state, *args, **kwargs)
            logger.debug(f"← Exiting {func.__name__}")
            logger.debug(f"  Result: {result}")
            return result

        except Exception as e:
            logger.error(f"✗ Error in {func.__name__}: {e}")
            raise

    return wrapper

# Usage
class MyNode(BaseNode):
    @debug_node
    def execute(self, state):
        return {"result": "value"}
```

**Timing decorator:**
```python
import time

def timed_execution(func):
    """Log execution time."""
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start

            logger.info(
                f"{func.__name__} completed",
                extra={"duration_ms": duration * 1000}
            )

            return result

        except Exception as e:
            duration = time.time() - start
            logger.error(
                f"{func.__name__} failed after {duration:.2f}s: {e}"
            )
            raise

    return wrapper
```

### Conditional Debugging

**Debug based on state:**
```python
class ConditionalDebugNode(BaseNode):
    def execute(self, state):
        # Enable debug for specific conditions
        debug = (
            state.iteration > 5 or
            state.get("error") or
            os.getenv("FORCE_DEBUG") == "true"
        )

        if debug:
            self.logger.debug("Debug mode activated")
            self.logger.debug(f"State: {state}")

        result = self.process(state)

        if debug:
            self.logger.debug(f"Result: {result}")

        return result
```

**Per-user debugging:**
```python
class UserDebugNode(BaseNode):
    DEBUG_USERS = {"user-123", "user-456"}

    def execute(self, state, config):
        # Extract user from config
        user_id = None
        if config and "metadata" in config:
            user_id = config["metadata"].get("user_id")

        # Debug for specific users
        if user_id in self.DEBUG_USERS:
            self.logger.debug(f"[User {user_id}] Full state: {state}")

        result = self.process(state)
        return {"result": result}
```

---

## Production Logging Strategies

### Log Aggregation

**CloudWatch integration:**
```python
import boto3
from logging.handlers import WatchedFileHandler

# Configure CloudWatch handler
import watchtower

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add CloudWatch handler
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group="/aws/langgraph/{{ cookiecutter.act_slug }}",
    stream_name="production",
    boto3_client=boto3.client("logs")
))
```

**Structured JSON logging:**
```python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### Performance Monitoring

**Performance tracking:**
```python
class PerformanceNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def execute(self, state):
        import time

        # Track timing
        start = time.time()

        # Track memory (optional)
        import tracemalloc
        tracemalloc.start()

        try:
            result = self.process(state)

            # Log performance metrics
            duration = time.time() - start
            memory = tracemalloc.get_traced_memory()

            self.logger.info(
                "Performance metrics",
                extra={
                    "node": self.name,
                    "duration_ms": duration * 1000,
                    "memory_current_mb": memory[0] / 1024 / 1024,
                    "memory_peak_mb": memory[1] / 1024 / 1024,
                }
            )

            # Alert if slow
            if duration > 5.0:
                self.logger.warning(
                    f"Slow execution: {self.name} took {duration:.2f}s"
                )

            return result

        finally:
            tracemalloc.stop()
```

### Error Tracking

**Sentry integration:**
```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Initialize Sentry
sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
    ],
    traces_sample_rate=0.1,
    environment=os.getenv("ENV", "development")
)

# Errors automatically sent to Sentry
class ErrorTrackedNode(BaseNode):
    def execute(self, state):
        try:
            return self.process(state)
        except Exception as e:
            # Auto-captured by Sentry
            self.logger.error("Processing failed", exc_info=True)

            # Add context
            sentry_sdk.set_context("state", {
                "query": state.query,
                "iteration": state.iteration
            })

            raise
```

### Security Considerations

**Sanitizing logs:**
```python
import re

class SecureLoggingNode(BaseNode):
    SENSITIVE_PATTERNS = [
        (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)', re.I), 'API_KEY_REDACTED'),
        (re.compile(r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)', re.I), 'PASSWORD_REDACTED'),
        (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), 'CARD_REDACTED'),
    ]

    def sanitize(self, text):
        """Remove sensitive data from log text."""
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            text = pattern.sub(replacement, text)
        return text

    def execute(self, state):
        # Sanitize before logging
        safe_query = self.sanitize(state.query)
        self.logger.info(f"Query: {safe_query}")

        result = self.process(state)
        return result
```

**PII filtering:**
```python
class PIIFilteredLogging(BaseNode):
    def filter_pii(self, data):
        """Remove PII from data."""
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if key in {"email", "phone", "ssn", "address"}:
                    filtered[key] = "[REDACTED]"
                elif isinstance(value, (dict, list)):
                    filtered[key] = self.filter_pii(value)
                else:
                    filtered[key] = value
            return filtered
        elif isinstance(data, list):
            return [self.filter_pii(item) for item in data]
        return data

    def execute(self, state):
        # Filter PII before logging
        filtered_state = self.filter_pii(state.__dict__)
        self.logger.info("State (filtered)", extra=filtered_state)

        result = self.process(state)
        return result
```

---

## Structured Logging

### JSON Logging

**JSON formatter:**
```python
import json
import logging
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "@timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename",
                "funcName", "levelname", "levelno", "lineno",
                "module", "msecs", "message", "pathname",
                "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text",
                "stack_info"
            ]:
                log_obj[key] = value

        # Add exception
        if record.exc_info:
            log_obj["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }

        return json.dumps(log_obj)

# Configure
handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
```

**Usage:**
```python
logger.info(
    "User action",
    extra={
        "user_id": "user-123",
        "action": "query",
        "query": "weather",
        "duration_ms": 150
    }
)

# Output:
# {
#   "@timestamp": "2024-01-15T10:35:42.123Z",
#   "level": "INFO",
#   "logger": "my_cast.nodes.agent",
#   "message": "User action",
#   "user_id": "user-123",
#   "action": "query",
#   "query": "weather",
#   "duration_ms": 150
# }
```

### Context Managers

**Logging context:**
```python
from contextvars import ContextVar
import logging

# Context variable for request ID
request_id_var = ContextVar("request_id", default=None)

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

# Add filter
logger = logging.getLogger()
logger.addFilter(ContextFilter())

# Set context
def process_request(request_id, query):
    # Set request ID in context
    request_id_var.set(request_id)

    # All logs now include request_id
    logger.info("Processing query", extra={"query": query})

    result = graph.invoke({"query": query})

    logger.info("Completed")
    return result
```

### Request ID Tracking

**Request ID injection:**
```python
import uuid

class RequestIDNode(BaseNode):
    def execute(self, state, config):
        # Get or create request ID
        request_id = None
        if config and "metadata" in config:
            request_id = config["metadata"].get("request_id")

        if not request_id:
            request_id = str(uuid.uuid4())

        # Log with request ID
        self.logger.info(
            "Processing request",
            extra={"request_id": request_id}
        )

        # Add to state
        result = self.process(state)
        result["request_id"] = request_id

        return result
```

### Correlation IDs

**Cross-service correlation:**
```python
class CorrelatedLoggingNode(BaseNode):
    def execute(self, state, config):
        # Extract correlation IDs
        correlation_id = state.get("correlation_id")
        thread_id = None
        if config and "configurable" in config:
            thread_id = config["configurable"].get("thread_id")

        # Log with correlation context
        self.logger.info(
            "Node execution",
            extra={
                "correlation_id": correlation_id,
                "thread_id": thread_id,
                "node": self.name
            }
        )

        result = self.process(state)
        return result
```

---

## Log Configuration

### Configuration Files

**YAML configuration:**
```yaml
# logging.yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: '%(asctime)s %(name)s %(levelname)s %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: json
    filename: logs/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  {{ cookiecutter.python_package }}:
    level: DEBUG
    handlers: [console, file]
    propagate: false

root:
  level: WARNING
  handlers: [console]
```

**Load configuration:**
```python
import logging.config
import yaml

with open('logging.yaml', 'r') as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)
```

### Environment-Based Config

**Dynamic configuration:**
```python
import os
import logging

def configure_logging():
    """Configure logging based on environment."""
    env = os.getenv("ENV", "development")

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "handlers": ["console"],
        },
    }

    if env == "development":
        config["root"]["level"] = "DEBUG"
    elif env == "production":
        config["root"]["level"] = "WARNING"
        # Add CloudWatch handler
        config["handlers"]["cloudwatch"] = {
            "class": "watchtower.CloudWatchLogHandler",
            "log_group": "/aws/langgraph/{{ cookiecutter.act_slug }}",
        }
        config["root"]["handlers"].append("cloudwatch")

    logging.config.dictConfig(config)

# Call at startup
configure_logging()
```

### Dynamic Configuration

**Runtime log level changes:**
```python
import logging

def set_log_level(logger_name, level):
    """Change log level at runtime."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))

# Usage
set_log_level("{{ cookiecutter.python_package }}", "DEBUG")
```

### Log Rotation

**Rotating file handler:**
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger()
logger.addHandler(handler)
```

**Time-based rotation:**
```python
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    "logs/app.log",
    when="midnight",
    interval=1,
    backupCount=30  # Keep 30 days
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger()
logger.addHandler(handler)
```

---

## Advanced Techniques

### Custom Log Handlers

**Slack notification handler:**
```python
import logging
import requests

class SlackHandler(logging.Handler):
    def __init__(self, webhook_url, level=logging.ERROR):
        super().__init__(level)
        self.webhook_url = webhook_url

    def emit(self, record):
        try:
            msg = self.format(record)

            payload = {
                "text": f"*{record.levelname}*: {msg}",
                "username": "LangGraph Bot"
            }

            requests.post(self.webhook_url, json=payload)

        except Exception:
            self.handleError(record)

# Add to logger
slack_handler = SlackHandler("https://hooks.slack.com/services/...")
slack_handler.setLevel(logging.ERROR)
logger.addHandler(slack_handler)
```

### Log Filtering

**Custom filter:**
```python
class SensitiveDataFilter(logging.Filter):
    """Filter out logs containing sensitive data."""

    SENSITIVE_KEYWORDS = {"password", "api_key", "secret"}

    def filter(self, record):
        # Check if message contains sensitive keywords
        msg = record.getMessage().lower()
        return not any(keyword in msg for keyword in self.SENSITIVE_KEYWORDS)

# Add filter
logger = logging.getLogger()
logger.addFilter(SensitiveDataFilter())
```

### Performance Profiling

**Profiling decorator:**
```python
import cProfile
import pstats
import io

def profile_execution(func):
    """Profile function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.disable()

            # Print stats
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(10)  # Top 10

            logger = logging.getLogger(func.__module__)
            logger.debug(f"Profile for {func.__name__}:\n{s.getvalue()}")

    return wrapper
```

### Distributed Tracing

**OpenTelemetry integration:**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# Setup tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Add span processor
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

class TracedNode(BaseNode):
    def execute(self, state):
        with tracer.start_as_current_span("node_execution") as span:
            span.set_attribute("node.name", self.name)
            span.set_attribute("state.query", state.query)

            result = self.process(state)

            span.set_attribute("result.length", len(str(result)))

            return result
```

---

## Integration Patterns

### LangSmith + CloudWatch

**Dual logging:**
```python
import os
import logging
import watchtower

# LangSmith tracing (automatic)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."

# CloudWatch logging
logger = logging.getLogger()
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group="/aws/langgraph/{{ cookiecutter.act_slug }}"
))

# Now have both:
# - LangSmith traces for execution flow
# - CloudWatch logs for infrastructure monitoring
```

### LangSmith + Datadog

**Datadog integration:**
```python
from datadog import initialize, statsd
import logging

# Initialize Datadog
initialize(
    api_key=os.getenv("DATADOG_API_KEY"),
    app_key=os.getenv("DATADOG_APP_KEY")
)

class DatadogLoggingNode(BaseNode):
    def execute(self, state):
        # Send metrics to Datadog
        statsd.increment('node.execution', tags=[f"node:{self.name}"])

        start = time.time()

        try:
            result = self.process(state)

            duration = time.time() - start
            statsd.histogram('node.duration', duration, tags=[f"node:{self.name}"])
            statsd.increment('node.success', tags=[f"node:{self.name}"])

            return result

        except Exception as e:
            statsd.increment('node.error', tags=[f"node:{self.name}"])
            raise
```

### LangSmith + Sentry

**Combined error tracking:**
```python
import sentry_sdk
from sentry_sdk.integrations.langchain import LangchainIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[
        LangchainIntegration(),
    ],
    traces_sample_rate=0.1,
)

# Errors captured in both:
# - LangSmith: Execution trace with full context
# - Sentry: Error aggregation and alerting
```

### Custom Integrations

**Custom logging backend:**
```python
class CustomBackendHandler(logging.Handler):
    """Send logs to custom backend."""

    def __init__(self, api_endpoint, api_key):
        super().__init__()
        self.api_endpoint = api_endpoint
        self.api_key = api_key

    def emit(self, record):
        try:
            log_data = {
                "timestamp": record.created,
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
            }

            # Send to backend
            requests.post(
                self.api_endpoint,
                json=log_data,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

        except Exception:
            self.handleError(record)
```

---

## Troubleshooting

### No logs appearing

**Check configuration:**
```python
# Verify logger level
logger = logging.getLogger(__name__)
print(f"Logger level: {logger.level}")
print(f"Effective level: {logger.getEffectiveLevel()}")

# Check handlers
print(f"Handlers: {logger.handlers}")

# Test log
logger.info("Test message")
```

### LangSmith traces not showing

**Verify setup:**
```bash
# Check environment variables
echo $LANGCHAIN_TRACING_V2  # Should be "true"
echo $LANGCHAIN_API_KEY     # Should start with "ls__"
```

**Test connection:**
```python
from langsmith import Client

try:
    client = Client()
    print("LangSmith connected:", client.info)
except Exception as e:
    print(f"LangSmith error: {e}")
```

### Logs too verbose

**Adjust levels:**
```python
# Reduce verbosity
logging.getLogger("{{ cookiecutter.python_package }}").setLevel(logging.WARNING)

# Silence specific loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
```

### Missing context in logs

**Ensure extra fields:**
```python
# Always pass extra
logger.info(
    "Message",
    extra={
        "user_id": user_id,
        "request_id": request_id
    }
)
```

---

## Best Practices

1. **Use structured logging** - JSON format for production
2. **Set appropriate log levels** - DEBUG in dev, WARNING in prod
3. **Include context** - Add user_id, request_id, etc.
4. **Log errors with tracebacks** - Use `exc_info=True`
5. **Sanitize sensitive data** - Never log passwords, API keys
6. **Use LangSmith** - Automatic tracing for LangGraph
7. **Rotate logs** - Prevent disk space issues
8. **Aggregate logs** - Use CloudWatch, Datadog, etc.
9. **Monitor performance** - Track slow operations
10. **Test logging** - Verify logs work as expected

---

## References

**Official Documentation:**
- Python logging: https://docs.python.org/3/library/logging.html
- LangSmith: https://docs.smith.langchain.com/
- LangChain tracing: https://python.langchain.com/docs/guides/debugging

**Libraries:**
- python-json-logger: https://github.com/madzak/python-json-logger
- watchtower (CloudWatch): https://github.com/kislyuk/watchtower
- Sentry SDK: https://docs.sentry.io/platforms/python/

**Related Guides:**
- `studio_debugging.md`: Visual debugging with Studio
- `pytest_patterns.md`: Testing and test logging
- `config_runtime.md`: Runtime configuration
