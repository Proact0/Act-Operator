# Routing Patterns in LangGraph

Comprehensive guide to routing functions and conditional logic patterns in LangGraph.

## Table of Contents

1. [Introduction](#introduction)
2. [Routing Function Fundamentals](#routing-function-fundamentals)
   - [Basic Structure](#basic-structure)
   - [Return Values](#return-values)
   - [State Access](#state-access)
   - [Pure Functions](#pure-functions)
3. [Simple Routing Patterns](#simple-routing-patterns)
   - [Boolean Routing](#boolean-routing)
   - [Enum-Based Routing](#enum-based-routing)
   - [Status-Based Routing](#status-based-routing)
   - [Type-Based Routing](#type-based-routing)
4. [Conditional Logic Patterns](#conditional-logic-patterns)
   - [If-Elif-Else Chains](#if-elif-else-chains)
   - [Early Return Pattern](#early-return-pattern)
   - [Guard Clauses](#guard-clauses)
   - [Nested Conditions](#nested-conditions)
5. [Multi-Path Routing](#multi-path-routing)
   - [Three-Way Routing](#three-way-routing)
   - [Multi-Criteria Routing](#multi-criteria-routing)
   - [Score-Based Routing](#score-based-routing)
   - [Priority-Based Routing](#priority-based-routing)
6. [Complex Routing Patterns](#complex-routing-patterns)
   - [State Machine Routing](#state-machine-routing)
   - [Decision Tree Routing](#decision-tree-routing)
   - [Rule-Based Routing](#rule-based-routing)
   - [Matrix Routing](#matrix-routing)
7. [Dynamic Routing](#dynamic-routing)
   - [Runtime Configuration](#runtime-configuration)
   - [Feature Flags](#feature-flags)
   - [A/B Testing](#ab-testing)
   - [Load-Based Routing](#load-based-routing)
8. [Message-Based Routing](#message-based-routing)
   - [Agent Tool Routing](#agent-tool-routing)
   - [Message Type Routing](#message-type-routing)
   - [Content-Based Routing](#content-based-routing)
9. [Error and Retry Routing](#error-and-retry-routing)
   - [Error Detection](#error-detection)
   - [Retry Logic](#retry-logic)
   - [Fallback Routing](#fallback-routing)
   - [Circuit Breaker](#circuit-breaker)
10. [Best Practices](#best-practices)
11. [Testing Routing Functions](#testing-routing-functions)
12. [Common Pitfalls](#common-pitfalls)
13. [Troubleshooting](#troubleshooting)
14. [Examples](#examples)

---

## Introduction

Routing functions are the decision-making heart of LangGraph conditional edges. They determine the flow of execution based on state.

**Purpose:**
- Determine next node in execution
- Branch based on conditions
- Enable dynamic graph behavior
- Implement complex logic flow

**Key principles:**
- Pure functions (no side effects)
- Deterministic output
- Return string route keys
- Access full state

---

## Routing Function Fundamentals

### Basic Structure

```python
def route_function(state):
    """
    Basic routing function structure.

    Args:
        state: Graph state object

    Returns:
        str: Route key matching path mapping
    """
    # Inspect state
    # Make decision
    # Return route key
    return "route_key"
```

**Example:**
```python
from dataclasses import dataclass

@dataclass(kw_only=True)
class State:
    status: str
    count: int = 0

def simple_route(state):
    """Simple routing based on status."""
    if state.status == "success":
        return "success"
    else:
        return "error"

# Usage in graph
builder.add_conditional_edges(
    "process",
    simple_route,
    {
        "success": "success_handler",
        "error": "error_handler"
    }
)
```

### Return Values

Routing functions must return strings:

```python
# ✅ Correct - returns string
def route(state):
    return "path_a"

# ✅ Correct - conditional string return
def route(state):
    return "success" if state.valid else "error"

# ❌ Wrong - returns boolean
def route(state):
    return True  # TypeError!

# ❌ Wrong - returns None
def route(state):
    if state.valid:
        return "success"
    # Implicitly returns None - ERROR!

# ✅ Correct - all paths return string
def route(state):
    if state.valid:
        return "success"
    return "error"  # Default return
```

### State Access

Access any state field:

```python
@dataclass(kw_only=True)
class State:
    query: str
    result: str = None
    error: str = None
    retry_count: int = 0
    metadata: dict = None

def route_with_state_access(state):
    """Access various state fields."""
    # String fields
    if state.error:
        return "error"

    # Numeric fields
    if state.retry_count > 3:
        return "max_retries"

    # Dict fields
    if state.metadata and state.metadata.get("priority") == "high":
        return "priority"

    # Check None
    if state.result is None:
        return "pending"

    return "complete"
```

### Pure Functions

Routing functions should be pure:

```python
# ✅ Correct - pure function
def pure_route(state):
    """No side effects, deterministic."""
    score = calculate_score(state.input)
    return "high" if score > 0.8 else "low"

# ❌ Wrong - side effects
def impure_route(state):
    """Has side effects - avoid!"""
    import logging
    logging.info("Routing...")  # Side effect

    # Mutating state (doesn't work anyway)
    state.routed = True  # Bad!

    # Non-deterministic
    import random
    if random.random() > 0.5:  # Non-deterministic!
        return "a"
    return "b"

# ❌ Wrong - external state
counter = 0
def stateful_route(state):
    """Uses external state - avoid!"""
    global counter
    counter += 1
    return "a" if counter % 2 == 0 else "b"
```

---

## Simple Routing Patterns

### Boolean Routing

Simple yes/no decisions:

```python
def boolean_route(state):
    """Binary decision."""
    return "yes" if state.condition else "no"

# Examples
def is_valid_route(state):
    """Validation routing."""
    return "valid" if state.validated else "invalid"

def is_ready_route(state):
    """Readiness check."""
    return "ready" if state.ready else "wait"

def has_error_route(state):
    """Error check."""
    return "error" if state.error else "success"
```

### Enum-Based Routing

Route based on enumerated values:

```python
from enum import Enum

class QueryType(Enum):
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"

@dataclass(kw_only=True)
class State:
    query_type: QueryType

def enum_route(state):
    """Route based on enum value."""
    if state.query_type == QueryType.FACTUAL:
        return "factual_handler"
    elif state.query_type == QueryType.ANALYTICAL:
        return "analytical_handler"
    elif state.query_type == QueryType.CREATIVE:
        return "creative_handler"
    else:
        return "default"

# Alternative: Direct enum value
def enum_route_simple(state):
    """Use enum value directly."""
    return state.query_type.value  # Returns string
```

### Status-Based Routing

Route based on status field:

```python
def status_route(state):
    """Route based on processing status."""
    status = state.status

    if status == "pending":
        return "process"
    elif status == "processing":
        return "wait"
    elif status == "complete":
        return "finalize"
    elif status == "error":
        return "error_handler"
    else:
        return "unknown"
```

### Type-Based Routing

Route based on data type:

```python
def type_route(state):
    """Route based on data type."""
    data_type = state.data_type

    if data_type == "text":
        return "text_processor"
    elif data_type == "image":
        return "image_processor"
    elif data_type == "audio":
        return "audio_processor"
    elif data_type == "video":
        return "video_processor"
    else:
        return "unsupported"
```

---

## Conditional Logic Patterns

### If-Elif-Else Chains

Standard conditional chains:

```python
def chain_route(state):
    """Conditional chain pattern."""
    score = state.score

    if score >= 90:
        return "excellent"
    elif score >= 80:
        return "good"
    elif score >= 70:
        return "satisfactory"
    elif score >= 60:
        return "passing"
    else:
        return "failing"
```

### Early Return Pattern

Return as soon as condition is met:

```python
def early_return_route(state):
    """Early return pattern - cleaner than nested ifs."""
    # Check critical conditions first
    if state.critical_error:
        return "critical"

    if state.error:
        return "error"

    if not state.validated:
        return "validate"

    if state.retry_count > 3:
        return "max_retries"

    # Default path
    return "process"
```

### Guard Clauses

Check preconditions first:

```python
def guard_clause_route(state):
    """Use guard clauses for preconditions."""
    # Guard: Check required fields
    if not state.input:
        return "missing_input"

    if not state.user_id:
        return "missing_user"

    # Guard: Validate state
    if state.invalid:
        return "invalid_state"

    # Guard: Check permissions
    if not state.authorized:
        return "unauthorized"

    # Main logic - all guards passed
    if state.priority == "high":
        return "expedited"

    return "standard"
```

### Nested Conditions

Hierarchical decision logic:

```python
def nested_route(state):
    """Nested conditions - use sparingly."""
    if state.category == "A":
        if state.priority == "high":
            if state.urgent:
                return "a_urgent_high"
            else:
                return "a_high"
        else:
            return "a_normal"
    elif state.category == "B":
        if state.complexity == "simple":
            return "b_simple"
        else:
            return "b_complex"
    else:
        return "default"

# Better: Flatten with multiple conditions
def flat_route(state):
    """Flattened version - easier to read."""
    # Category A paths
    if state.category == "A" and state.priority == "high" and state.urgent:
        return "a_urgent_high"

    if state.category == "A" and state.priority == "high":
        return "a_high"

    if state.category == "A":
        return "a_normal"

    # Category B paths
    if state.category == "B" and state.complexity == "simple":
        return "b_simple"

    if state.category == "B":
        return "b_complex"

    return "default"
```

---

## Multi-Path Routing

### Three-Way Routing

Three distinct paths:

```python
def three_way_route(state):
    """Three-way routing decision."""
    quality = state.quality_score

    if quality > 0.8:
        return "high_quality"
    elif quality > 0.5:
        return "medium_quality"
    else:
        return "low_quality"
```

### Multi-Criteria Routing

Consider multiple factors:

```python
def multi_criteria_route(state):
    """Route based on multiple criteria."""
    score = state.score
    priority = state.priority
    user_tier = state.user_tier

    # High priority always goes to fast lane
    if priority == "critical":
        return "critical_lane"

    # Premium users get expedited processing
    if user_tier == "premium":
        if score > 0.7:
            return "premium_fast"
        else:
            return "premium_review"

    # Regular users by score
    if score > 0.9:
        return "auto_approve"
    elif score > 0.7:
        return "standard_process"
    elif score > 0.5:
        return "review_required"
    else:
        return "reject"
```

### Score-Based Routing

Route based on calculated scores:

```python
def score_route(state):
    """Route based on calculated score."""
    # Calculate composite score
    quality = state.quality_score * 0.4
    relevance = state.relevance_score * 0.3
    confidence = state.confidence_score * 0.3

    total_score = quality + relevance + confidence

    # Route by score thresholds
    if total_score > 0.9:
        return "tier_1"
    elif total_score > 0.75:
        return "tier_2"
    elif total_score > 0.6:
        return "tier_3"
    else:
        return "manual_review"
```

### Priority-Based Routing

Route by priority levels:

```python
def priority_route(state):
    """Priority-based routing with overflow handling."""
    priority = state.priority
    queue_size = state.queue_size

    # Critical - always immediate
    if priority == 0:
        return "immediate"

    # High priority
    if priority == 1:
        # Check capacity
        if queue_size < 10:
            return "expedited"
        else:
            return "expedited_queued"

    # Normal priority
    if priority == 2:
        if queue_size < 50:
            return "standard"
        else:
            return "standard_queued"

    # Low priority - batch
    return "batch"
```

---

## Complex Routing Patterns

### State Machine Routing

Implement state machine logic:

```python
def state_machine_route(state):
    """State machine routing pattern."""
    current_state = state.machine_state
    event = state.event

    # State transitions
    if current_state == "idle":
        if event == "start":
            return "initialize"
        return "idle"

    elif current_state == "initializing":
        if event == "ready":
            return "process"
        elif event == "error":
            return "error"
        return "initializing"

    elif current_state == "processing":
        if event == "complete":
            return "finalize"
        elif event == "pause":
            return "paused"
        elif event == "error":
            return "error"
        return "processing"

    elif current_state == "paused":
        if event == "resume":
            return "process"
        elif event == "cancel":
            return "cancelled"
        return "paused"

    elif current_state == "finalizing":
        if event == "done":
            return "complete"
        return "finalizing"

    else:
        return "unknown_state"
```

### Decision Tree Routing

Hierarchical decision tree:

```python
def decision_tree_route(state):
    """Decision tree routing."""
    # Level 1: Type
    if state.type == "query":
        # Level 2: Complexity
        if state.complexity == "simple":
            # Level 3: Cached?
            if state.cached:
                return "query_simple_cached"
            else:
                return "query_simple_fresh"
        else:
            # Complex query
            if state.requires_tools:
                return "query_complex_tools"
            else:
                return "query_complex_llm"

    elif state.type == "command":
        # Level 2: Permission
        if state.authorized:
            return "command_execute"
        else:
            return "command_denied"

    elif state.type == "data":
        # Level 2: Size
        if state.size > 1000000:
            return "data_large_batch"
        else:
            return "data_small_sync"

    else:
        return "unknown_type"
```

### Rule-Based Routing

Business rule evaluation:

```python
def rule_based_route(state):
    """Route based on business rules."""
    # Rule 1: Fraud detection
    if state.fraud_score > 0.8:
        return "fraud_review"

    # Rule 2: Compliance
    if state.amount > 10000 and not state.kyc_verified:
        return "compliance_review"

    # Rule 3: Risk assessment
    if state.risk_level == "high":
        if state.manual_review_required:
            return "manual_review"
        else:
            return "automated_review"

    # Rule 4: VIP handling
    if state.customer_tier == "VIP":
        return "vip_processing"

    # Rule 5: Volume check
    if state.transaction_count_today > 100:
        return "volume_review"

    # All rules passed
    return "auto_approve"
```

### Matrix Routing

Two-dimensional decision matrix:

```python
def matrix_route(state):
    """Route using decision matrix."""
    urgency = state.urgency  # low, medium, high
    complexity = state.complexity  # simple, moderate, complex

    # Decision matrix
    routing_matrix = {
        ("low", "simple"): "batch_simple",
        ("low", "moderate"): "batch_moderate",
        ("low", "complex"): "scheduled_complex",
        ("medium", "simple"): "standard_simple",
        ("medium", "moderate"): "standard_moderate",
        ("medium", "complex"): "standard_complex",
        ("high", "simple"): "expedited_simple",
        ("high", "moderate"): "expedited_moderate",
        ("high", "complex"): "critical_complex",
    }

    key = (urgency, complexity)
    return routing_matrix.get(key, "default")
```

---

## Dynamic Routing

### Runtime Configuration

Route based on runtime config:

```python
def config_based_route(state):
    """Route based on runtime configuration."""
    # Check feature flags in state
    features = state.get("features", {})

    if features.get("new_algorithm_enabled"):
        return "new_algorithm"

    if features.get("experimental_enabled"):
        return "experimental"

    return "stable"
```

### Feature Flags

Route based on feature flags:

```python
def feature_flag_route(state):
    """Route based on feature flags."""
    flags = state.feature_flags

    # Percentage rollout
    if flags.get("beta_feature"):
        # Check user ID hash for consistent routing
        user_hash = hash(state.user_id) % 100
        if user_hash < flags.get("beta_percentage", 0):
            return "beta_handler"

    # Boolean flags
    if flags.get("use_cache"):
        return "cached_handler"

    # Multi-variant flags
    variant = flags.get("algorithm_variant", "A")
    if variant == "B":
        return "algorithm_b"

    return "algorithm_a"
```

### A/B Testing

Route for A/B testing:

```python
def ab_test_route(state):
    """Route for A/B testing."""
    # Get user ID
    user_id = state.user_id

    # Consistent hashing for stable assignment
    import hashlib
    hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    bucket = hash_value % 100

    # 50/50 split
    if bucket < 50:
        return "variant_a"
    else:
        return "variant_b"

# Multi-variant testing
def multivariate_route(state):
    """Multi-variant testing."""
    user_id = state.user_id
    hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    bucket = hash_value % 100

    # 40% A, 40% B, 20% C
    if bucket < 40:
        return "variant_a"
    elif bucket < 80:
        return "variant_b"
    else:
        return "variant_c"
```

### Load-Based Routing

Route based on system load:

```python
def load_based_route(state):
    """Route based on current system load."""
    # Get current load from state
    current_load = state.get("system_load", 0)
    queue_length = state.get("queue_length", 0)

    # High load - queue or throttle
    if current_load > 0.9:
        return "throttled"

    if current_load > 0.7:
        if queue_length < 100:
            return "queued"
        else:
            return "rejected"

    # Normal load
    if state.priority == "high":
        return "expedited"

    return "standard"
```

---

## Message-Based Routing

### Agent Tool Routing

Route based on tool calls:

```python
def agent_tool_route(state):
    """Route based on agent's tool usage."""
    messages = state.messages
    last_message = messages[-1]

    # Check if last message has tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # No more tools needed
    return "end"

# Usage
builder.add_conditional_edges(
    "agent",
    agent_tool_route,
    {
        "tools": "tool_node",
        "end": END
    }
)
builder.add_edge("tool_node", "agent")  # Loop back
```

### Message Type Routing

Route based on message type:

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def message_type_route(state):
    """Route based on message type."""
    messages = state.messages
    last_message = messages[-1]

    if isinstance(last_message, HumanMessage):
        return "process_human"
    elif isinstance(last_message, AIMessage):
        return "process_ai"
    elif isinstance(last_message, SystemMessage):
        return "process_system"
    else:
        return "unknown"
```

### Content-Based Routing

Route based on message content:

```python
def content_based_route(state):
    """Route based on message content."""
    messages = state.messages
    last_message = messages[-1]
    content = last_message.content.lower()

    # Keyword detection
    if "help" in content or "how do i" in content:
        return "help_handler"

    if "error" in content or "problem" in content:
        return "error_handler"

    if "thank" in content or "thanks" in content:
        return "acknowledgment"

    # Intent classification
    if any(word in content for word in ["calculate", "compute", "solve"]):
        return "calculator"

    if any(word in content for word in ["search", "find", "lookup"]):
        return "search"

    return "general"
```

---

## Error and Retry Routing

### Error Detection

Route based on error state:

```python
def error_detection_route(state):
    """Detect and route errors."""
    # Check for error field
    if state.error:
        # Classify error type
        error = state.error.lower()

        if "timeout" in error:
            return "timeout_handler"

        if "connection" in error:
            return "connection_handler"

        if "validation" in error:
            return "validation_handler"

        return "general_error"

    return "success"
```

### Retry Logic

Implement retry routing:

```python
def retry_route(state):
    """Route with retry logic."""
    # Check if error exists
    if not state.error:
        return "success"

    # Check retry count
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)

    if retry_count >= max_retries:
        return "max_retries_exceeded"

    # Determine if should retry
    error_type = state.error_type

    # Retryable errors
    if error_type in ["timeout", "connection", "rate_limit"]:
        return "retry"

    # Non-retryable errors
    if error_type in ["validation", "authentication", "not_found"]:
        return "permanent_failure"

    # Unknown error - retry once
    if retry_count < 1:
        return "retry"

    return "unknown_error"
```

### Fallback Routing

Route with fallback chain:

```python
def fallback_route(state):
    """Route with fallback chain."""
    # Try primary
    if state.primary_available and not state.primary_failed:
        return "primary"

    # Try secondary
    if state.secondary_available and not state.secondary_failed:
        return "secondary"

    # Try tertiary
    if state.tertiary_available and not state.tertiary_failed:
        return "tertiary"

    # All failed - use cache or default
    if state.cached_result:
        return "use_cache"

    return "default_response"
```

### Circuit Breaker

Implement circuit breaker pattern:

```python
def circuit_breaker_route(state):
    """Circuit breaker pattern routing."""
    failure_count = state.get("failure_count", 0)
    last_success_time = state.get("last_success_time", 0)
    circuit_state = state.get("circuit_state", "closed")

    import time
    current_time = time.time()

    # Circuit states: closed, open, half_open
    if circuit_state == "closed":
        # Normal operation
        if failure_count >= 5:
            # Open circuit
            return "circuit_open"
        return "process"

    elif circuit_state == "open":
        # Check timeout (30 seconds)
        if current_time - last_success_time > 30:
            # Try half-open
            return "circuit_half_open"
        # Still open
        return "circuit_open"

    elif circuit_state == "half_open":
        # Test request
        return "circuit_test"

    return "unknown_state"
```

---

## Best Practices

### 1. Keep routing functions simple

```python
# ✅ Good - clear and simple
def simple_route(state):
    if state.type == "A":
        return "handler_a"
    if state.type == "B":
        return "handler_b"
    return "default"

# ❌ Bad - too complex
def complex_route(state):
    return ("handler_a" if state.type == "A" and state.valid and
            not state.error and state.score > 0.5 else
            "handler_b" if state.type == "B" else "default")
```

### 2. Document routing logic

```python
def documented_route(state):
    """
    Route queries based on type and priority.

    Routing logic:
    - Critical priority → immediate handler
    - Type A + high priority → expedited_a
    - Type A → standard_a
    - Type B + high priority → expedited_b
    - Type B → standard_b
    - Default → general handler

    Args:
        state: Must have 'type' and 'priority' fields

    Returns:
        Route key for handler
    """
    if state.priority == "critical":
        return "immediate"

    if state.type == "A":
        return "expedited_a" if state.priority == "high" else "standard_a"

    if state.type == "B":
        return "expedited_b" if state.priority == "high" else "standard_b"

    return "general"
```

### 3. Use early returns

```python
# ✅ Good - early returns
def early_return(state):
    if state.critical:
        return "critical"

    if state.error:
        return "error"

    if not state.valid:
        return "invalid"

    return "process"

# ❌ Bad - nested ifs
def nested(state):
    if not state.critical:
        if not state.error:
            if state.valid:
                return "process"
            else:
                return "invalid"
        else:
            return "error"
    else:
        return "critical"
```

### 4. Handle all cases

```python
# ✅ Good - all cases handled
def complete_route(state):
    status = state.status

    if status == "pending":
        return "process"
    elif status == "processing":
        return "wait"
    elif status == "complete":
        return "finalize"
    else:
        # Always have a default
        return "unknown"

# ❌ Bad - missing default
def incomplete_route(state):
    if state.status == "pending":
        return "process"
    elif state.status == "processing":
        return "wait"
    # What if status is something else?
```

### 5. Test routing independently

```python
def test_routing():
    """Test routing function."""
    from dataclasses import dataclass

    @dataclass
    class State:
        status: str

    # Test all paths
    assert simple_route(State(status="success")) == "success"
    assert simple_route(State(status="error")) == "error"
    assert simple_route(State(status="unknown")) == "default"
```

### 6. Use constants for route keys

```python
# ✅ Good - constants
class Routes:
    SUCCESS = "success"
    ERROR = "error"
    RETRY = "retry"

def route_with_constants(state):
    if state.error:
        return Routes.ERROR
    return Routes.SUCCESS

# ❌ Bad - magic strings
def route_with_strings(state):
    if state.error:
        return "eror"  # Typo! Runtime error
    return "success"
```

### 7. Avoid side effects

```python
# ✅ Good - pure function
def pure_route(state):
    score = calculate_score(state.data)
    return "high" if score > 0.8 else "low"

# ❌ Bad - side effects
def impure_route(state):
    logging.info("Routing...")  # Side effect
    global counter
    counter += 1  # Side effect
    return "route"
```

---

## Testing Routing Functions

### Unit testing

```python
import pytest
from dataclasses import dataclass

@dataclass
class State:
    status: str
    count: int = 0

def route_to_test(state):
    if state.status == "success":
        return "success"
    if state.count > 3:
        return "retry_exceeded"
    return "retry"

def test_success_route():
    """Test success path."""
    state = State(status="success", count=0)
    assert route_to_test(state) == "success"

def test_retry_exceeded():
    """Test retry exceeded."""
    state = State(status="error", count=4)
    assert route_to_test(state) == "retry_exceeded"

def test_retry():
    """Test retry path."""
    state = State(status="error", count=2)
    assert route_to_test(state) == "retry"

def test_all_paths():
    """Test all routing paths."""
    test_cases = [
        (State(status="success", count=0), "success"),
        (State(status="error", count=4), "retry_exceeded"),
        (State(status="error", count=2), "retry"),
        (State(status="error", count=0), "retry"),
    ]

    for state, expected in test_cases:
        assert route_to_test(state) == expected
```

### Property-based testing

```python
from hypothesis import given
from hypothesis import strategies as st

@given(st.integers(min_value=0, max_value=10))
def test_count_based_routing(count):
    """Property: count > 3 should always route to retry_exceeded."""
    state = State(status="error", count=count)
    result = route_to_test(state)

    if count > 3:
        assert result == "retry_exceeded"
    else:
        assert result == "retry"
```

---

## Common Pitfalls

### 1. Forgetting default case

```python
# ❌ Wrong - no default
def bad_route(state):
    if state.type == "A":
        return "handler_a"
    elif state.type == "B":
        return "handler_b"
    # What if type is "C"? Returns None!

# ✅ Correct
def good_route(state):
    if state.type == "A":
        return "handler_a"
    elif state.type == "B":
        return "handler_b"
    return "default"  # Always have default
```

### 2. Non-deterministic routing

```python
# ❌ Wrong - non-deterministic
import random

def bad_route(state):
    if random.random() > 0.5:  # Different each time!
        return "a"
    return "b"

# ✅ Correct - deterministic
def good_route(state):
    # Use state for consistent routing
    hash_value = hash(state.user_id)
    if hash_value % 2 == 0:
        return "a"
    return "b"
```

### 3. Side effects

```python
# ❌ Wrong - logging side effect
def bad_route(state):
    print("Routing...")  # Side effect
    return "route"

# ✅ Correct - no side effects
def good_route(state):
    # Routing logic only
    return "route"
```

### 4. Typos in route keys

```python
# ❌ Wrong - typo
def bad_route(state):
    return "succes"  # Typo! Runtime error

# ✅ Correct - use constants
class Routes:
    SUCCESS = "success"

def good_route(state):
    return Routes.SUCCESS  # Type-safe
```

---

## Troubleshooting

### Issue: "KeyError: route_key"

**Cause:** Routing function returns unmapped key

**Fix:**
```python
# Add mapping for all possible returns
builder.add_conditional_edges(
    "node",
    route_function,
    {
        "success": "success_handler",
        "error": "error_handler",
        "unknown": "default_handler"  # Add missing mapping
    }
)
```

### Issue: Routing function returns None

**Cause:** Missing return statement

**Fix:**
```python
# ❌ Wrong
def route(state):
    if state.valid:
        return "valid"
    # Missing else - returns None!

# ✅ Correct
def route(state):
    if state.valid:
        return "valid"
    return "invalid"  # Always return something
```

### Issue: Inconsistent routing

**Cause:** Non-deterministic logic

**Fix:**
```python
# Use state fields, not external state
def route(state):
    # Base on state, not time/random
    return "a" if state.user_id % 2 == 0 else "b"
```

---

## Examples

### Complete Example: Query Router

```python
from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass

@dataclass(kw_only=True)
class State:
    query: str
    query_type: str = None
    priority: str = "normal"
    authenticated: bool = False

def classify_and_route(state):
    """
    Classify query and route appropriately.

    Routing logic:
    1. Unauthenticated → auth required
    2. High priority → expedited
    3. Query type:
       - search → search handler
       - calculation → calculator
       - general → LLM handler
    """
    # Guard: Check authentication
    if not state.authenticated:
        return "auth_required"

    # Priority routing
    if state.priority == "high":
        return "expedited"

    # Type-based routing
    query_type = state.query_type

    if query_type == "search":
        return "search"
    elif query_type == "calculation":
        return "calculator"
    elif query_type == "general":
        return "llm"
    else:
        return "unknown"

def build_router():
    """Build query router graph."""
    builder = StateGraph(State)

    # Add nodes
    builder.add_node("classify", ClassifyNode())
    builder.add_node("auth_required", AuthNode())
    builder.add_node("expedited", ExpeditedNode())
    builder.add_node("search", SearchNode())
    builder.add_node("calculator", CalculatorNode())
    builder.add_node("llm", LLMNode())
    builder.add_node("unknown", UnknownNode())

    builder.add_edge(START, "classify")

    # Conditional routing
    builder.add_conditional_edges(
        "classify",
        classify_and_route,
        {
            "auth_required": "auth_required",
            "expedited": "expedited",
            "search": "search",
            "calculator": "calculator",
            "llm": "llm",
            "unknown": "unknown"
        }
    )

    # All routes to END
    for node in ["auth_required", "expedited", "search",
                  "calculator", "llm", "unknown"]:
        builder.add_edge(node, END)

    return builder.compile()
```

---

## Summary

**Key principles:**
- Pure functions (no side effects)
- Deterministic output
- Return strings (route keys)
- Handle all cases
- Document logic

**Common patterns:**
- Boolean routing (yes/no)
- Multi-way routing (many paths)
- Priority-based routing
- Error and retry routing
- Message-based routing

**Best practices:**
- Keep functions simple
- Use early returns
- Document logic
- Test independently
- Use constants for keys
- Handle edge cases

**References:**
- LangGraph Conditional Edges: https://langchain-ai.github.io/langgraph/how-tos/branching/
- State Management: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
