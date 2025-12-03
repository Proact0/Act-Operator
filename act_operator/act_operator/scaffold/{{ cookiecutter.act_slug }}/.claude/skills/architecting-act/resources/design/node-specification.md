# Node Specification Guide

## Core Principle

**Single Responsibility:** Each node does ONE thing.

**Test:** If you use "and" to describe it, split it.

## Design Process

1. Break workflow into discrete operations
2. Each LLM/API/DB call = separate node
3. Apply granularity check

**Too coarse (split):** Does multiple operations, hard to describe in one sentence.

**Too fine (merge):** Always runs together, trivial operation.

## Output Format

**IMPORTANT: Describe node structure only. Do NOT write other modules(tool, middleware etc.) or implementation code (def functions, classes etc.).**

```
Nodes:
- NodeName - Single responsibility description
  - Reads: [state fields]
  - Writes: [state fields]
  - Type: [Input/Process/Decision/Output/Tool]
```

## Node Types

| Type | Purpose | Example |
|------|---------|---------|
| **Input** | Parse/validate | `ParseQuery` |
| **Process** | Transform/compute | `ExtractEntities` |
| **Decision** | Determine routing | `ClassifyIntent` |
| **Output** | Format response | `FormatResult` |
| **Tool** | External action | `CallAPI` |

## Naming Convention

**REQUIRED: CamelCase format** (not lowercase or snake_case)
- ✅ Good: `InspectorAgent`, `ResponseGenerater`
- ❌ Bad: `inspect_agent`, `generate_response`

## Checklist

- [ ] Each node has single responsibility
- [ ] Names are clear (VerbNoun format)
- [ ] Reads/Writes match state schema
- [ ] LLM calls are separated
