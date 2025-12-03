# State Schema Design Guide

## Schema Types

| Schema | Purpose | Visibility |
|--------|---------|------------|
| **InputState** | What caller must provide | External |
| **OutputState** | What caller receives back | External |
| **OverallState** | All fields for internal operation | Internal |

**Relationship:** OverallState ⊇ InputState ∪ OutputState

## Design Process

1. **Identify input fields** from user's stated input requirements
2. **Identify output fields** from user's stated output requirements
3. **Add internal fields** based on selected pattern (intermediate results, counters, etc.)
4. **Categorize** each field: Input / Output / Internal

## Output Format

```
InputState:
- field_name: type - description

OutputState:
- field_name: type - description

OverallState:
- field_name: type - description (Input)
- field_name: type - description (Output)
- field_name: type - description (Internal)
```

## Design Principles

**InputState:** Only required fields, minimal API.

**OutputState:** Only user-relevant results, hide internals.

**OverallState:** ALL fields needed by nodes.

## Common Patterns

| Use Case | Input | Output | Internal |
|----------|-------|--------|----------|
| Chat | `query: str` | `response: str` | `messages: list` |
| Document | `document: str` | `result: dict` | `parsed: dict` |
| Classification | `text: str` | `label: str` | `features: list` |

## Checklist

- [ ] InputState has only required fields
- [ ] OutputState has only user-relevant fields
- [ ] OverallState includes ALL fields
- [ ] Each field has type and description
