# Act-Operator CLI Commands Reference

Complete reference for act-operator CLI commands, workflows, and configuration.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [cast create Command](#cast-create-command)
4. [Common Workflows](#common-workflows)
5. [Configuration Options](#configuration-options)
6. [Environment Setup](#environment-setup)
7. [Troubleshooting](#troubleshooting)
8. [References](#references)

---

## Introduction

The act-operator CLI provides commands for creating and managing LangGraph Casts.

**Main command:**
```bash
act-operator cast create <name>
```

---

## Installation

```bash
# Install act-operator
pip install act-operator

# Or with UV
uv tool install act-operator

# Verify installation
act-operator --version
```

---

## cast create Command

### Basic Usage

```bash
# Create new Cast
act-operator cast create my-agent

# Creates directory structure:
# my-agent/
#   ├── .claude/
#   ├── my_agent/
#   │   ├── graph.py
#   │   ├── state.py
#   │   └── nodes/
#   ├── tests/
#   ├── pyproject.toml
#   └── ...
```

### With Options

```bash
# Specify description
act-operator cast create my-agent \
    --description "My custom agent"

# Interactive mode (prompts for options)
act-operator cast create my-agent --interactive
```

---

## Common Workflows

### Create and Run Cast

```bash
# 1. Create Cast
act-operator cast create my-agent

# 2. Navigate to directory
cd my-agent

# 3. Install dependencies
uv sync

# 4. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run dev server
uv run langgraph dev

# 6. Connect LangGraph Studio
# Open Studio, connect to http://localhost:8123
```

### Development Workflow

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Format code
uv run ruff format .

# Run dev server
uv run langgraph dev

# Build
uv build
```

---

## Configuration Options

### Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
```

### pyproject.toml

```toml
[project]
name = "my-agent"
version = "0.1.0"
dependencies = [
    "langgraph>=0.2.0",
    "langchain-anthropic>=0.1.0",
]

[dependency-groups]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
]
```

---

## Environment Setup

### API Keys

```bash
# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
export OPENAI_API_KEY=sk-...

# LangSmith (optional)
export LANGCHAIN_API_KEY=ls__...
export LANGCHAIN_TRACING_V2=true
```

### Development Tools

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install LangGraph CLI
uv tool install langgraph-cli

# Install LangGraph Studio (macOS only)
# Download from https://studio.langchain.com/
```

---

## Troubleshooting

### Command not found

```bash
# Ensure installed
pip install act-operator

# Or reinstall
pip install --force-reinstall act-operator

# Check PATH
which act-operator
```

### Import errors

```bash
# Sync dependencies
uv sync

# Or reinstall
uv sync --reinstall
```

### API key errors

```bash
# Verify environment
echo $ANTHROPIC_API_KEY

# Check .env loaded
cat .env
```

---

## References

- Act-Operator: https://github.com/yourusername/act-operator
- UV: https://docs.astral.sh/uv/
- LangGraph CLI: https://langchain-ai.github.io/langgraph/cloud/reference/cli/
