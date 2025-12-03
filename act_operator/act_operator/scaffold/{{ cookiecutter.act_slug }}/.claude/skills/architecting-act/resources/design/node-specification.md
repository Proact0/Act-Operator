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

**Use VerbNoun:** `ParseInput`, `ValidateData`, `GenerateResponse`

**Avoid vague:** Bad: `Process`, `Handle` → Good: `ExtractEntities`, `ClassifyIntent`

## Checklist

- [ ] Each node has single responsibility
- [ ] Names are clear (VerbNoun format)
- [ ] Reads/Writes match state schema
- [ ] LLM calls are separated
