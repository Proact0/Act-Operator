# CLAUDE.md Output Template

## Template Structure

### 1. Overview

    # {Project Name} Architecture
    
    ## Overview
    
    **Purpose:** {One sentence}
    **Pattern:** {Sequential | Branching | Cyclic | Multi-agent}
    **Latency:** {Low | Medium | High}

### 2. Architecture Diagram

    ## Architecture Diagram
    
    ```mermaid
    graph TD
        START((START)) --> Node1[Node Name]
        Node1 --> END((END))
    ```

### 3. State Schema

    ## State Schema
    
    ### InputState
    | Field | Type | Description |
    |-------|------|-------------|
    
    ### OutputState
    | Field | Type | Description |
    |-------|------|-------------|
    
    ### OverallState
    | Field | Type | Category | Description |
    |-------|------|----------|-------------|

### 4. Node Specifications

    ## Node Specifications
    
    ### NodeName
    | Attribute | Value |
    |-----------|-------|
    | Type | Input/Process/Decision/Output/Tool |
    | Responsibility | Single sentence |
    | Reads | fields |
    | Writes | fields |

### 5. Edge Definitions

    ## Edge Definitions
    
    ### Normal Edges
    | Source | Target |
    |--------|--------|
    
    ### Conditional Edges (if any)
    | Source | Condition | Target |
    |--------|-----------|--------|

### 6. Technology Stack

> Note: `langgraph`, `langchain` are already in template. List only **additional** dependencies.

    ## Technology Stack
    
    ### Additional Dependencies
    | Package | Purpose |
    |---------|---------|
    
    ### Environment Variables
    | Variable | Required | Description |
    |----------|----------|-------------|

## Checklist

- [ ] Diagram matches node/edge specs
- [ ] All nodes documented
- [ ] All edges defined with defaults
- [ ] State schema complete
- [ ] Dependencies listed
