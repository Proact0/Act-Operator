# LangGraph Studio Debugging Guide

Complete guide to debugging LangGraph applications using LangGraph Studio with step-through debugging, state inspection, and graph visualization.

## Table of Contents

1. [Introduction](#introduction)
2. [Studio Overview](#studio-overview)
   - [What is LangGraph Studio](#what-is-langgraph-studio)
   - [Key Features](#key-features)
   - [When to Use Studio](#when-to-use-studio)
3. [Installation and Setup](#installation-and-setup)
   - [System Requirements](#system-requirements)
   - [Installing LangGraph Studio](#installing-langgraph-studio)
   - [Installing LangGraph CLI](#installing-langgraph-cli)
   - [Verifying Installation](#verifying-installation)
4. [Connecting to Dev Server](#connecting-to-dev-server)
   - [Starting langgraph dev](#starting-langgraph-dev)
   - [Connecting Studio](#connecting-studio)
   - [Configuration Files](#configuration-files)
   - [Environment Variables](#environment-variables)
5. [Studio Interface](#studio-interface)
   - [Graph Visualization](#graph-visualization)
   - [Thread Panel](#thread-panel)
   - [State Inspector](#state-inspector)
   - [Message History](#message-history)
6. [Step-Through Debugging Workflow](#step-through-debugging-workflow)
   - [Starting a Debug Session](#starting-a-debug-session)
   - [Stepping Through Nodes](#stepping-through-nodes)
   - [Inspecting State at Each Step](#inspecting-state-at-each-step)
   - [Breakpoints and Interrupts](#breakpoints-and-interrupts)
7. [State Inspection](#state-inspection)
   - [Viewing Current State](#viewing-current-state)
   - [State History](#state-history)
   - [State Diffs](#state-diffs)
   - [Nested State Objects](#nested-state-objects)
8. [Graph Visualization](#graph-visualization-1)
   - [Node Layout](#node-layout)
   - [Edge Types](#edge-types)
   - [Conditional Routing](#conditional-routing)
   - [Execution Path Highlighting](#execution-path-highlighting)
9. [Advanced Debugging Techniques](#advanced-debugging-techniques)
   - [Time Travel Debugging](#time-travel-debugging)
   - [Checkpoint Inspection](#checkpoint-inspection)
   - [Streaming Mode](#streaming-mode)
   - [Multi-Thread Debugging](#multi-thread-debugging)
10. [Debugging Common Issues](#debugging-common-issues)
    - [Infinite Loops](#infinite-loops)
    - [Incorrect State Updates](#incorrect-state-updates)
    - [Routing Problems](#routing-problems)
    - [Performance Issues](#performance-issues)
11. [Troubleshooting](#troubleshooting)
    - [Connection Issues](#connection-issues)
    - [Studio Not Loading](#studio-not-loading)
    - [Graph Not Appearing](#graph-not-appearing)
    - [State Not Updating](#state-not-updating)
12. [Best Practices](#best-practices)
13. [Integration with Act-Operator](#integration-with-act-operator)
14. [References](#references)

---

## Introduction

LangGraph Studio is a visual debugging tool for LangGraph applications. It provides real-time graph visualization, step-through debugging, and comprehensive state inspection capabilities that make debugging complex agent workflows significantly easier.

**What you'll learn:**
- Installing and configuring LangGraph Studio
- Connecting to your development server
- Step-through debugging of graph execution
- Inspecting state at each node
- Visualizing graph structure and execution flow
- Troubleshooting common debugging issues

**Prerequisites:**
- LangGraph application (Act-Operator Cast)
- Python 3.11 or higher
- macOS (Studio is currently macOS only)
- LangGraph CLI installed

---

## Studio Overview

### What is LangGraph Studio

LangGraph Studio is a desktop application for macOS that provides:
- **Visual graph editor**: See your graph structure visually
- **Step debugger**: Step through node execution one at a time
- **State inspector**: Examine state at each step
- **Time travel**: Rewind and replay execution
- **Multi-thread support**: Debug multiple conversation threads

**Architecture:**
```
┌─────────────────────┐
│  LangGraph Studio   │ (macOS Desktop App)
│   (Port 3000)       │
└──────────┬──────────┘
           │ HTTP/WebSocket
           ↓
┌─────────────────────┐
│  langgraph dev      │ (CLI Dev Server)
│   (Port 8123)       │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Your Cast Graph    │ (Python Code)
└─────────────────────┘
```

### Key Features

1. **Real-time Graph Visualization**
   - Automatic layout of nodes and edges
   - Color-coded node types
   - Edge routing visualization
   - Current execution highlighting

2. **Interactive Debugging**
   - Step through execution
   - Set breakpoints (interrupts)
   - Pause/resume execution
   - Manual state editing

3. **State Inspection**
   - View complete state at each step
   - Diff between states
   - State history timeline
   - Nested object exploration

4. **Thread Management**
   - Multiple conversation threads
   - Thread history
   - Thread switching
   - Thread state isolation

### When to Use Studio

**Use Studio when:**
- Developing new graph logic
- Debugging complex routing
- Understanding execution flow
- Investigating state issues
- Learning LangGraph concepts
- Demonstrating graph behavior

**Don't need Studio for:**
- Simple unit tests
- CI/CD pipelines
- Production deployment
- Non-visual debugging
- Linux/Windows development (not supported)

---

## Installation and Setup

### System Requirements

**Operating System:**
- macOS 11 (Big Sur) or later
- Apple Silicon (M1/M2/M3) or Intel

**Software:**
- Python 3.11 or higher
- Node.js 16+ (for CLI)
- Git

**Hardware:**
- 8GB RAM minimum (16GB recommended)
- 2GB free disk space

### Installing LangGraph Studio

**Method 1: Direct Download**
```bash
# Visit LangGraph Studio download page
# https://studio.langchain.com/

# Download the .dmg file
# Double-click to mount
# Drag LangGraph Studio to Applications folder
```

**Method 2: Homebrew (if available)**
```bash
# Check if available via Homebrew
brew install --cask langgraph-studio
```

**Verify Installation:**
```bash
# Open Applications folder
# Look for "LangGraph Studio"
# Double-click to launch
# Grant necessary permissions
```

### Installing LangGraph CLI

The CLI provides the `langgraph dev` command:

```bash
# Install with pip
pip install langgraph-cli

# Or with pipx (recommended)
pipx install langgraph-cli

# Verify installation
langgraph --version
# Should show: langgraph 0.1.x or higher
```

**Install in Cast project:**
```bash
# Navigate to your Cast directory
cd /path/to/your-cast

# Install CLI in project environment
uv pip install langgraph-cli

# Verify
uv run langgraph --version
```

### Verifying Installation

```bash
# Check Studio
# Open LangGraph Studio app
# Should show connection screen

# Check CLI
langgraph --help
# Should show commands including 'dev'

# Check Python packages
python -c "import langgraph; print(langgraph.__version__)"
# Should show 0.2.x or higher
```

---

## Connecting to Dev Server

### Starting langgraph dev

**Basic usage:**
```bash
# Navigate to Cast directory
cd /path/to/{{ cookiecutter.act_slug }}

# Start dev server
langgraph dev

# Output:
# Starting LangGraph API server...
# Server running at http://localhost:8123
# LangGraph Studio: http://localhost:8123/studio
```

**With custom port:**
```bash
# Use different port
langgraph dev --port 8124

# With specific host
langgraph dev --host 0.0.0.0 --port 8123
```

**With environment file:**
```bash
# Load .env file
langgraph dev --env-file .env

# Multiple env files
langgraph dev --env-file .env --env-file .env.local
```

**Configuration file:**
```bash
# Use langgraph.json config
langgraph dev --config langgraph.json

# Example langgraph.json:
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./your_cast/graph.py:graph"
  },
  "env": ".env"
}
```

### Connecting Studio

**Step 1: Start dev server**
```bash
# In terminal
cd {{ cookiecutter.act_slug }}
langgraph dev

# Wait for: "Server running at http://localhost:8123"
```

**Step 2: Open Studio**
```bash
# Launch LangGraph Studio app
# or click: http://localhost:8123/studio (if available)
```

**Step 3: Connect**
```
In Studio:
1. Enter server URL: http://localhost:8123
2. Click "Connect"
3. Studio will discover available graphs
4. Select your graph from dropdown
5. Graph visualization appears
```

**Connection status:**
```
🟢 Connected - Green indicator, graph visible
🟡 Connecting - Yellow indicator, loading
🔴 Disconnected - Red indicator, check server
```

### Configuration Files

**langgraph.json:**
```json
{
  "dependencies": ["."],
  "graphs": {
    "my_cast": "./{{ cookiecutter.python_package }}/graph.py:graph"
  },
  "env": ".env",
  "python_version": "3.11"
}
```

**Required fields:**
- `dependencies`: Python package paths
- `graphs`: Named graph entry points
- `env`: Environment file (optional)

**Example for Act-Operator Cast:**
```json
{
  "dependencies": ["."],
  "graphs": {
    "{{ cookiecutter.act_slug }}": "./{{ cookiecutter.python_package }}/graph.py:graph"
  },
  "env": ".env",
  "python_version": "3.11"
}
```

### Environment Variables

**Required variables:**
```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
```

**Loading in dev server:**
```bash
# Auto-loads .env
langgraph dev

# Explicit env file
langgraph dev --env-file .env.production

# Environment variable
ANTHROPIC_API_KEY=sk-ant-... langgraph dev
```

**Checking variables:**
```python
# In your Cast code
import os
print("API Key loaded:", bool(os.getenv("ANTHROPIC_API_KEY")))
```

---

## Studio Interface

### Graph Visualization

**Graph canvas:**
```
┌─────────────────────────────────────────┐
│         [Start] ──────> [Agent]         │
│                           │             │
│                           ├─> [Tools]   │
│                           │      │      │
│                           │      ↓      │
│                           ├─> [End]     │
│                           │             │
│                           └─> [Human]   │
└─────────────────────────────────────────┘
```

**Elements:**
- **Nodes**: Rectangles with node names
- **Edges**: Arrows showing flow
- **Conditional edges**: Dashed arrows
- **Current node**: Highlighted in blue
- **Executed nodes**: Green checkmark
- **Start/End**: Special styling

**Controls:**
- Zoom: Scroll or pinch
- Pan: Click and drag
- Reset view: Double-click canvas
- Auto-layout: Refresh button

### Thread Panel

**Thread list:**
```
Threads:
┌─────────────────────────────┐
│ + New Thread                │
├─────────────────────────────┤
│ ▶ Thread 1 (2 messages)     │
│ ▶ Thread 2 (5 messages)     │
│ ▶ Thread 3 (1 message)      │
└─────────────────────────────┘
```

**Thread actions:**
- New thread: Create fresh conversation
- Select thread: View history and state
- Delete thread: Remove thread and checkpoints
- Rename thread: Change display name

**Thread details:**
```
Thread: Thread 1
Messages: 2
Created: 2024-01-15 10:30
Last updated: 2024-01-15 10:35
Checkpoints: 5
```

### State Inspector

**State view:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi there!"
    }
  ],
  "query": "Hello",
  "count": 1,
  "iteration": 0
}
```

**Features:**
- JSON tree view
- Expandable/collapsible
- Search in state
- Copy state to clipboard
- Type indicators (string, number, array, object)

**State navigation:**
```
State at Step 3:
├─ messages (Array[2])
│  ├─ [0] (Object)
│  │  ├─ role: "user"
│  │  └─ content: "Hello"
│  └─ [1] (Object)
│     ├─ role: "assistant"
│     └─ content: "Hi there!"
├─ query: "Hello"
├─ count: 1
└─ iteration: 0
```

### Message History

**Message timeline:**
```
Timeline:
┌─────────────────────────────┐
│ 1. User: Hello              │
│    State: {query: "Hello"}  │
├─────────────────────────────┤
│ 2. Agent: Processing...     │
│    State: {query: "Hello",  │
│            count: 1}        │
├─────────────────────────────┤
│ 3. Assistant: Hi there!     │
│    State: {messages: [...]} │
└─────────────────────────────┘
```

**Timeline features:**
- Chronological order
- Node that produced message
- State snapshot at that step
- Click to jump to step
- Expand for details

---

## Step-Through Debugging Workflow

### Starting a Debug Session

**Step 1: Create new thread**
```
In Studio:
1. Click "+ New Thread"
2. Thread panel shows new thread
3. Input box appears at bottom
```

**Step 2: Send input**
```
1. Type message: "Hello, what's the weather?"
2. Click Send or press Enter
3. Graph begins execution
```

**Step 3: Execution starts**
```
Graph highlights:
- START node: ✓ Completed
- Agent node: ⚡ Executing
- Other nodes: ⏸ Waiting
```

### Stepping Through Nodes

**Automatic execution:**
```
Graph executes:
START → Agent → Tools → Agent → END
Each node:
1. Highlights in blue (executing)
2. Shows state updates
3. Marks complete (green)
4. Moves to next node
```

**Manual stepping:**
```
If graph has interrupts:
1. Execution pauses at interrupt
2. "Resume" button appears
3. Inspect state
4. Click "Resume" to continue
5. Or click "Cancel" to stop
```

**Step controls:**
```
Controls:
┌──────────────────────┐
│ ▶ Resume             │
│ ⏸ Pause (if running) │
│ ■ Stop               │
│ ↻ Restart            │
└──────────────────────┘
```

### Inspecting State at Each Step

**View state at any point:**
```
Timeline shows:
Step 1: Agent (Initial)
  State: {query: "weather", location: null}

Step 2: Tools (After tool call)
  State: {query: "weather", location: "San Francisco"}

Step 3: Agent (After processing)
  State: {query: "weather", location: "SF", temp: 72}
```

**State diff view:**
```
State changes from Step 1 → Step 2:
{
  "query": "weather",          // Unchanged
  "location": null → "San Francisco",  // Added
+ "tool_calls": [...]          // Added
}
```

**Detailed inspection:**
```
Click on any state field:
- Expand nested objects
- View full message content
- Copy values to clipboard
- Search within field
```

### Breakpoints and Interrupts

**LangGraph interrupts:**
```python
# In your Cast graph
from langgraph.graph import StateGraph

builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

# Add interrupt before node
builder.add_edge("agent", "tools", interrupt="before")
# Execution pauses before tools node

# Or interrupt after
builder.add_edge("tools", "agent", interrupt="after")
# Execution pauses after tools node
```

**Using interrupts in Studio:**
```
When graph hits interrupt:
1. Execution pauses
2. Current state shown
3. Resume button enabled
4. Can inspect/modify state
5. Click Resume to continue
```

**Conditional interrupts:**
```python
# Interrupt based on state
def should_interrupt(state):
    return state.get("requires_human")

builder.add_conditional_edges(
    "agent",
    should_interrupt,
    {
        True: "human_input",
        False: "continue"
    }
)
```

---

## State Inspection

### Viewing Current State

**State panel:**
```
Current State (Step 3 of 5):
┌─────────────────────────────┐
│ messages: Array[3]          │
│   [0]: {role: "user", ...}  │
│   [1]: {role: "assistant"...│
│   [2]: {role: "user", ...}  │
│                             │
│ query: "weather in SF"      │
│ location: "San Francisco"   │
│ temperature: 72             │
│ iteration: 2                │
└─────────────────────────────┘
```

**Interaction:**
- Click field to expand
- Hover for type info
- Right-click to copy
- Search bar at top

**State metadata:**
```
Checkpoint ID: 8a7f9d2c-...
Node: tools
Timestamp: 2024-01-15 10:35:42
Parent: 7b6e8c1b-...
```

### State History

**Timeline view:**
```
State History:
┌─────────────────────────────┐
│ Step 5: END                 │
│   ✓ Complete                │
├─────────────────────────────┤
│ Step 4: Agent               │
│   ✓ Processed response      │
├─────────────────────────────┤
│ Step 3: Tools               │
│   ✓ Called weather API      │
├─────────────────────────────┤
│ Step 2: Agent               │
│   ✓ Planned tool call       │
├─────────────────────────────┤
│ Step 1: START               │
│   ✓ Initialized             │
└─────────────────────────────┘
```

**Navigate history:**
- Click any step to view state
- Use keyboard: ←/→ to move between steps
- Timeline scrubber to jump
- "Current" button to return to latest

### State Diffs

**Diff between steps:**
```
Changes from Step 2 → Step 3:
┌─────────────────────────────┐
│ Added:                      │
│ + temperature: 72           │
│ + conditions: "sunny"       │
│                             │
│ Modified:                   │
│ ~ location: null → "SF"     │
│ ~ iteration: 1 → 2          │
│                             │
│ Removed:                    │
│ - pending_query             │
└─────────────────────────────┘
```

**Diff modes:**
- Side-by-side: Before | After
- Inline: Highlighted changes
- Tree: Nested structure changes
- Raw: JSON diff

### Nested State Objects

**Expanding complex state:**
```
messages: Array[3]
├─ [0]: Object
│  ├─ role: "user"
│  ├─ content: "Hello"
│  └─ additional_kwargs: Object
│     ├─ timestamp: "2024-01-15..."
│     └─ metadata: Object
│        ├─ source: "web"
│        └─ user_id: "123"
├─ [1]: Object
│  ├─ role: "assistant"
│  └─ content: "Hi! How can I help?"
└─ [2]: Object
   └─ ...
```

**Navigation:**
- Click ▶ to expand
- Click ▼ to collapse
- Double-click to expand all children
- Right-click for context menu:
  - Copy value
  - Copy path
  - Copy as JSON
  - View in new window

---

## Graph Visualization

### Node Layout

**Automatic layout:**
```
        ┌──────────┐
        │  START   │
        └────┬─────┘
             │
        ┌────▼─────┐
        │  Agent   │
        └────┬─────┘
             │
     ┌───────┴───────┐
     ▼               ▼
┌─────────┐     ┌─────────┐
│  Tools  │     │  Human  │
└────┬────┘     └────┬────┘
     │               │
     └───────┬───────┘
             ▼
        ┌─────────┐
        │   END   │
        └─────────┘
```

**Layout options:**
- Automatic (default): Algorithm-based
- Hierarchical: Top-to-bottom flow
- Radial: Circular layout
- Manual: Drag to position

**Customizing layout:**
```
Layout Settings:
- Direction: Top→Bottom, Left→Right
- Spacing: Compact, Normal, Spacious
- Alignment: Center, Start, End
- Auto-arrange: On/Off
```

### Edge Types

**Normal edges:**
```python
# Solid arrow
builder.add_edge("agent", "tools")
```
```
Agent ──────> Tools
```

**Conditional edges:**
```python
# Dashed arrows
builder.add_conditional_edges(
    "agent",
    router,
    {"continue": "tools", "end": END}
)
```
```
Agent ┈┈┈┈┈> Tools
  │
  └┈┈┈┈┈> END
```

**Edge labels:**
```
      "continue"
Agent ┈┈┈┈┈┈┈┈┈> Tools
  │
  │ "end"
  └┈┈┈┈┈┈┈┈┈> END
```

### Conditional Routing

**Visual representation:**
```
        ┌────────┐
        │ Router │
        └───┬────┘
            │
    ┌───────┼───────┐
    │       │       │
  "A"      "B"     "C"
    │       │       │
    ▼       ▼       ▼
  ┌───┐   ┌───┐   ┌───┐
  │ A │   │ B │   │ C │
  └───┘   └───┘   └───┘
```

**Active path highlighting:**
```
When "B" path taken:
        ┌────────┐
        │ Router │ ✓
        └───┬────┘
            │
    ┌───────┼───────┐
    │       │       │
  "A"   🔵"B"     "C"
    │       │       │
    ▼       ▼       ▼
  ┌───┐   ┌───┐   ┌───┐
  │ A │   │ B │✓  │ C │
  └───┘   └───┘   └───┘
```

### Execution Path Highlighting

**During execution:**
```
Timeline:
1. START ✓ (green)
2. Agent ⚡ (blue, executing)
3. Tools ⏸ (gray, waiting)
4. END ⏸ (gray, waiting)
```

**After execution:**
```
Completed path:
START ✓ → Agent ✓ → Tools ✓ → Agent ✓ → END ✓
All nodes show green checkmark
Edges show execution order
```

**Path replay:**
```
Use timeline scrubber:
- Drag to any step
- Graph highlights path taken
- Shows state at that point
- Can compare different paths
```

---

## Advanced Debugging Techniques

### Time Travel Debugging

**Go back to any state:**
```
Timeline:
Step 5 ← Current
Step 4
Step 3 ← Click to go back
Step 2
Step 1

After clicking Step 3:
- State reverts to Step 3
- Graph shows position at Step 3
- Can resume from here
- Creates new branch
```

**Branching execution:**
```
Original:
Step 1 → Step 2 → Step 3 → Step 4 → Step 5

Go back to Step 3, make different choice:
Step 1 → Step 2 → Step 3 → Step 4 → Step 5
                           ↓
                         Step 3' → Step 4' → Step 5'
```

**Use cases:**
- Test different routing decisions
- Replay with modified state
- Understand alternate paths
- Debug specific scenarios

### Checkpoint Inspection

**View checkpoints:**
```
Checkpoints for Thread:
┌─────────────────────────────┐
│ 5. END (Latest)             │
│    ID: 9c8d7e6f...          │
│    Time: 10:35:50           │
├─────────────────────────────┤
│ 4. Agent                    │
│    ID: 8b7c6d5e...          │
│    Time: 10:35:48           │
├─────────────────────────────┤
│ 3. Tools                    │
│    ID: 7a6b5c4d...          │
│    Time: 10:35:45           │
└─────────────────────────────┘
```

**Checkpoint details:**
```
Checkpoint: 8b7c6d5e...
Node: agent
Timestamp: 2024-01-15 10:35:48
Parent: 7a6b5c4d...
Channel values:
  - messages: [...]
  - query: "weather"
  - iteration: 2
Metadata:
  - source: "user_input"
  - langgraph_node: "agent"
```

**Navigate checkpoints:**
- Click to load state
- Compare checkpoints
- Export checkpoint
- Restore from checkpoint

### Streaming Mode

**Enable streaming:**
```python
# In graph compilation
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human"],
    stream_mode="values"  # or "updates", "messages"
)
```

**Stream visualization:**
```
Real-time updates:
Agent: Thinking... 🔄
Agent: Generated response... ✓
Tools: Calling weather API... 🔄
Tools: Received data... ✓
```

**Stream modes:**
- `values`: Full state at each step
- `updates`: Only changed fields
- `messages`: Message stream
- `debug`: Detailed execution info

### Multi-Thread Debugging

**Managing threads:**
```
Threads Panel:
┌─────────────────────────────┐
│ ▶ User A (3 active)         │
│   Thread 1: Shopping cart   │
│   Thread 2: Support         │
│   Thread 3: Browse          │
├─────────────────────────────┤
│ ▶ User B (1 active)         │
│   Thread 1: Checkout        │
└─────────────────────────────┘
```

**Comparing threads:**
```
Thread 1 State:
{
  "user_id": "A",
  "cart": ["item1", "item2"],
  "step": "checkout"
}

Thread 2 State:
{
  "user_id": "A",
  "question": "How do I return?",
  "step": "support"
}
```

**Thread isolation:**
- Each thread has own state
- Separate checkpoint history
- Independent execution
- No cross-contamination

---

## Debugging Common Issues

### Infinite Loops

**Detecting loops:**
```
Studio shows:
Agent → Tools → Agent → Tools → Agent → ...
(Repeating pattern)

Warning: "Execution exceeded 100 steps"
```

**Finding the cause:**
```
1. Check state at loop iteration
2. Look for unchanging condition
3. Inspect routing logic
4. Verify termination condition
```

**Example issue:**
```python
# Bug: Never sets should_continue to False
def router(state):
    if state.get("result"):
        return "end"
    return "continue"  # Always returns this if no result

# Fix: Add iteration limit
def router(state):
    if state.get("result") or state["iteration"] > 5:
        return "end"
    return "continue"
```

**Studio features:**
- Loop detection warning
- Step count display
- State comparison between iterations
- Cancel long-running execution

### Incorrect State Updates

**Symptom:**
```
Expected state:
{
  "count": 3,
  "total": 10
}

Actual state:
{
  "count": 1,
  "total": undefined
}
```

**Debugging steps:**
```
1. Check state at previous step
2. Inspect node return value
3. Verify reducer function
4. Check annotations
```

**Example issue:**
```python
# Bug: Not returning state update
class MyNode(BaseNode):
    def execute(self, state):
        count = state.count + 1
        # Forgot to return!

# Fix: Return update dict
class MyNode(BaseNode):
    def execute(self, state):
        count = state.count + 1
        return {"count": count}
```

**Studio debugging:**
- View state diff between steps
- Check node return value in logs
- Inspect reducer behavior
- Validate state schema

### Routing Problems

**Symptom:**
```
Expected path: Agent → Tools → END
Actual path: Agent → END (skipped Tools)
```

**Debugging:**
```
1. View conditional edge logic
2. Check state at routing point
3. Inspect router function return
4. Verify edge mapping
```

**Example issue:**
```python
# Bug: Wrong condition
def route_agent(state):
    if state.get("tool_calls"):  # Empty list is falsy!
        return "tools"
    return "end"

# Fix: Check length
def route_agent(state):
    if len(state.get("tool_calls", [])) > 0:
        return "tools"
    return "end"
```

**Studio features:**
- Highlights chosen edge
- Shows router return value
- Displays edge mapping
- Can test different conditions

### Performance Issues

**Symptom:**
```
Node "agent" taking 30+ seconds
Graph execution very slow
```

**Debugging:**
```
Studio shows:
Agent: 🔄 Executing... (25s)
Tools: ⏸ Waiting
```

**Finding bottlenecks:**
```
1. Check timestamp between steps
2. Identify slow nodes
3. Inspect LLM calls
4. Review tool execution time
```

**Profiling in Studio:**
```
Execution Times:
┌─────────────────────────────┐
│ Agent: 28.5s                │
│   LLM call: 25.2s ⚠️         │
│   Processing: 3.3s          │
├─────────────────────────────┤
│ Tools: 2.1s                 │
│   API call: 1.8s            │
│   Parse: 0.3s               │
└─────────────────────────────┘
```

---

## Troubleshooting

### Connection Issues

**Problem: Studio won't connect**

```
Error: "Failed to connect to http://localhost:8123"
```

**Solutions:**

1. **Check server is running:**
```bash
# In terminal
langgraph dev
# Should show: "Server running at http://localhost:8123"
```

2. **Verify port:**
```bash
# Check if port is in use
lsof -i :8123

# If port blocked, use different port
langgraph dev --port 8124
```

3. **Check firewall:**
```bash
# macOS: System Settings > Network > Firewall
# Allow incoming connections for langgraph
```

4. **Try localhost vs 127.0.0.1:**
```
In Studio:
Try: http://127.0.0.1:8123
Instead of: http://localhost:8123
```

### Studio Not Loading

**Problem: Studio opens but shows blank screen**

**Solutions:**

1. **Check Studio version:**
```bash
# Update to latest
# Download from: https://studio.langchain.com/
```

2. **Clear Studio cache:**
```bash
# Close Studio
# Delete cache:
rm -rf ~/Library/Application\ Support/LangGraph\ Studio/Cache
# Reopen Studio
```

3. **Check console for errors:**
```
In Studio:
View > Developer > Developer Tools
Check Console tab for errors
```

### Graph Not Appearing

**Problem: Connected but no graph shown**

**Solutions:**

1. **Check langgraph.json:**
```json
{
  "dependencies": ["."],
  "graphs": {
    "my_graph": "./path/to/graph.py:graph"
  }
}
```

2. **Verify graph export:**
```python
# In graph.py
from langgraph.graph import StateGraph

# Build graph
graph = builder.compile()

# Must be module-level variable named in langgraph.json
```

3. **Check server logs:**
```bash
# Terminal running langgraph dev
# Look for errors like:
# "Failed to import graph"
# "Module not found"
```

4. **Restart server:**
```bash
# Ctrl+C to stop
langgraph dev
```

### State Not Updating

**Problem: State not changing in Studio**

**Solutions:**

1. **Verify node returns dict:**
```python
# ✅ Correct
def execute(self, state):
    return {"field": "value"}

# ❌ Wrong
def execute(self, state):
    state.field = "value"  # Doesn't work
    return state
```

2. **Check state annotations:**
```python
from typing_extensions import Annotated

@dataclass
class State:
    # If using custom reducer, verify it works
    items: Annotated[list, lambda old, new: old + new]
```

3. **Refresh Studio:**
```
In Studio:
- Click refresh button
- Or restart thread
```

4. **Check checkpointer:**
```python
# Ensure checkpointer configured
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

---

## Best Practices

### 1. Use descriptive node names

```python
# ✅ Good
builder.add_node("extract_user_intent", intent_node)
builder.add_node("call_weather_api", weather_node)

# ❌ Bad
builder.add_node("node1", intent_node)
builder.add_node("n2", weather_node)
```

### 2. Add interrupts strategically

```python
# Add interrupts at decision points
builder.add_edge("agent", "human_review", interrupt="before")

# Or after critical operations
builder.add_edge("execute_action", "verify", interrupt="after")
```

### 3. Keep state inspectable

```python
# ✅ Good - flat, readable state
@dataclass
class State:
    query: str
    step: str
    result: dict

# ❌ Bad - deeply nested
@dataclass
class State:
    data: dict  # Contains everything nested
```

### 4. Use meaningful thread IDs

```python
# In production
config = {
    "configurable": {
        "thread_id": f"user-{user_id}-session-{session_id}"
    }
}

# Easy to identify in Studio
```

### 5. Enable LangSmith tracing

```bash
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...

# See execution in LangSmith alongside Studio
```

### 6. Test with Studio, deploy without

```python
# Development
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human"]  # For Studio debugging
)

# Production
graph = builder.compile(
    checkpointer=checkpointer
    # No interrupts unless needed
)
```

### 7. Document routing logic

```python
def route_agent(state):
    """Route based on agent decision.

    Returns:
        "tools": If tool calls present
        "end": If final answer ready
        "human": If needs human input
    """
    if state.get("tool_calls"):
        return "tools"
    elif state.get("requires_human"):
        return "human"
    return "end"
```

---

## Integration with Act-Operator

### Cast-specific setup

**langgraph.json for Cast:**
```json
{
  "dependencies": ["."],
  "graphs": {
    "{{ cookiecutter.act_slug }}": "./{{ cookiecutter.python_package }}/graph.py:graph"
  },
  "env": ".env"
}
```

**Starting dev server for Cast:**
```bash
# Navigate to Cast directory
cd {{ cookiecutter.act_slug }}

# Ensure dependencies installed
uv sync

# Start dev server
uv run langgraph dev

# Or if langgraph-cli installed in project
langgraph dev
```

**Debugging Cast nodes:**
```python
# Your Cast nodes work with Studio automatically
from act_operator_lib.base_node import BaseNode

class MyCastNode(BaseNode):
    def execute(self, state):
        # Visible in Studio
        return {"result": "value"}
```

### Cast graph visualization

```
Your Cast in Studio:
┌──────────┐
│  START   │
└────┬─────┘
     │
     ▼
┌──────────┐
│  Input   │
│  Parser  │
└────┬─────┘
     │
     ▼
┌──────────┐
│  Agent   │
└────┬─────┘
     │
     ├─────> Tools
     │
     └─────> END
```

---

## References

**Official Documentation:**
- LangGraph Studio: https://langchain-ai.github.io/langgraph/cloud/reference/studio/
- LangGraph CLI: https://langchain-ai.github.io/langgraph/cloud/reference/cli/
- LangGraph Debugging: https://langchain-ai.github.io/langgraph/how-tos/debugging/

**Downloads:**
- Studio Download: https://studio.langchain.com/
- LangGraph Docs: https://langchain-ai.github.io/langgraph/

**Related Guides:**
- `pytest_patterns.md`: Unit testing Casts
- `logging_guide.md`: Production logging
- `config_runtime.md`: Runtime configuration

**Support:**
- LangChain Discord: https://discord.gg/langchain
- GitHub Issues: https://github.com/langchain-ai/langgraph

---

## Summary

**Key Takeaways:**
- Studio provides visual debugging for LangGraph
- `langgraph dev` starts development server
- Connect Studio to inspect graph execution
- Step through nodes and inspect state
- Time travel debugging to replay execution
- Use interrupts for breakpoints
- Helpful for development, not needed for production

**Workflow:**
1. Install Studio and CLI
2. Create/navigate to Cast directory
3. Run `langgraph dev`
4. Connect Studio
5. Create thread and send input
6. Step through execution
7. Inspect state at each node
8. Fix issues and restart

**Next Steps:**
- Practice with sample Cast
- Add interrupts for debugging
- Explore time travel debugging
- Check LangSmith for detailed traces
- See `logging_guide.md` for production debugging
