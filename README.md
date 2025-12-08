<div align="center">
  <a href="https://www.proact0.org/">
    <picture>
      <source media="(prefers-color-scheme: light)" srcset=".github/images/light-theme.png">
      <source media="(prefers-color-scheme: dark)" srcset=".github/images/dark-theme.png">
      <img alt="Proact0 Logo" src=".github/images/light-theme.png" width="80%">
    </picture>
  </a>
</div>

<div align="center">
  <h2>Act Operator</h2>
</div>

<div align="center">
  <a href="https://www.apache.org/licenses/LICENSE-2.0" target="_blank"><img src="https://img.shields.io/pypi/l/act-operator" alt="PyPI - License"></a>
  <a href="https://pypistats.org/packages/act-operator" target="_blank"><img src="https://img.shields.io/pepy/dt/act-operator?color=deeppink" alt="PyPI - Downloads"></a>
  <a href="https://pypi.org/project/act-operator/#history" target="_blank"><img src="https://img.shields.io/pypi/v/act-operator" alt="Version"></a>
  <a href="https://www.linkedin.com/company/proact0" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-Proact0-blue?logo=linkedin" alt="LinkedIn">
  </a>
  <a href="https://www.proact0.org/" target="_blank">
    <img src="https://img.shields.io/badge/Homepage-Proact0.org-brightgreen?logo=internet-explorer" alt="Homepage">
  </a>
</div>

<br>

Act Operator is a production-ready CLI that scaffolds structured LangGraph projects with built-in AI collaboration capabilities. 

```bash
uvx --from act-operator act new
```

Generate clean, modular graph architectures with cookiecutter templates that include specialized Agent skills for architecture design, development, engineering, and testing—enabling you to build complex agentic workflows, business automations, or data pipelines with optimal maintainability and AI-assisted development.

## What is Act?

Act (AX Template) is a standardized project structure for LangGraph applications, designed to solve common challenges in building production-grade AI systems:

- **Modular by Design**: Each graph component (state, nodes, agents, tools, middlewares, ...) lives in its own module with clear responsibilities
- **Scalable Architecture**: Organize multiple graphs (casts) within a monorepo, each as an independent package
- **AI-Native Development**: Built-in Agent skills guide you through architecture decisions, implementation patterns, and testing strategies
- **Beginner-Friendly**: Comprehensive documentation and inline guides make LangGraph accessible to newcomers

**Use Cases**: Agentic AI systems, Business Workflow Automation, Multi-step data pipelines, conversational agents, document processing flows, or **any application requiring stateful graph/workflow orchestration.**

## Quick Start

Requires Python 3.11+. The CLI will prompt you for project details or you can pass them as options.

```bash
# Create a new Act project
uvx --from act-operator act new

# Follow interactive prompts:
# - Path & Act name: my_workflow
# - Cast name: chatbot
```

### Sync

After creating the project, install dependencies and sync the virtual environment:

```bash
uv sync
```

This command installs all dependencies defined in `pyproject.toml` and prepares the project for execution.


### Start Building with AI

If you're using Claude Code, you can leverage built-in agent skills to accelerate development:

```bash
claude
```

Reference the skills directory in your prompts: `.claude/skills`

**Available Skills**:
- `architecting-act`: Design graph architectures through interactive questioning
- `developing-cast`: Implement nodes, agents, tools with best practice patterns
- `engineering-act`: Manage casts & their dependencies, create new casts
- `testing-cast`: Write effective pytest tests with mocking strategies

### Working with Skills

Skills can be used individually or as a complete workflow:

**Individual Use**:
- Need to design your project architecture? → Use `architecting-act`
- Need to add a new cast? → Use `engineering-act`
- Need to implement a specific node? → Use `developing-cast`
- Need to write tests? → Use `testing-cast`

**Complete Workflow**:
```plaintext
1. Architecture → "Design a customer support chatbot"
   (architecting-act: guides requirements, suggests patterns, generates CLAUDE.md)

2. Project Setup → "Create a new cast called chatbot"
   (engineering-act: scaffolds cast structure, configures dependencies)

3. Implementation → "Implement the chatbot based on our project"
   (developing-cast: creates state, nodes, agents, tools, and graph)

4. Testing → "Write comprehensive tests for the chatbot"
   (testing-cast: generates pytest tests with LLM/API mocking)
```

## Project Structure

```
my_workflow/
├── .claude/
│   └── skills/                    # AI collaboration guides
│       ├── architecting-act/      # Architecture design
│       ├── developing-cast/       # Implementation patterns
│       ├── engineering-act/       # Project management
│       └── testing-cast/          # Testing strategies
├── casts/
│   ├── base_node.py              # Base node class
│   ├── base_graph.py             # Base graph utilities
│   └── chatbot/                  # Your cast (graph package)
│       ├── modules/
│       │   ├── state.py          # Graph state definition
│       │   ├── nodes.py          # Node implementations
│       │   ├── agents.py         # Agent configurations
│       │   ├── tools.py          # Tool definitions
│       │   ├── models.py         # LLM model configs
│       │   ├── conditions.py     # Routing conditions
│       │   ├── middlewares.py    # Custom middleware
│       │   └── prompts.py        # Prompt templates
│       ├── graph.py              # Graph assembly
│       └── pyproject.toml        # Cast dependencies
├── tests/
│   ├── cast_tests/               # Graph-level tests
│   └── node_tests/               # Unit tests
├── langgraph.json                # LangGraph configuration
├── pyproject.toml                # Monorepo dependencies
├── TEMPLATE_README.md            # Template Using Guideline
└── README.md
```

## Usage

### Create New Cast

Add another graph to your existing Act project:

```bash
uv run act cast
# Interactive prompts for cast name and configuration
```

### Add Dependencies

```bash
# Monorepo-level (shared across all casts)
uv add langchain-openai

# Cast-specific
uv add --package chatbot langchain-anthropic

# Development tools
uv add --dev pytest-mock
```

### Run Development Server

```bash
uv run langgraph dev
```

The LangGraph Studio will open at `http://localhost:8000` for visual graph debugging.

## Key Features

### 1. Structured Modularity

Each module has a single responsibility with clear guidelines:

- **state.py**: Define TypedDict schemas for graph state
- **nodes.py**: Implement business logic as node classes
- **agents.py**: Configure LLM agents with tools and memory
- **tools.py**: Create reusable tool functions
- **conditions.py**: Define routing logic between nodes
- **graph.py**: Assemble components into executable graph

### 2. AI-Assisted Development

Built-in Claude Code skills optimize your workflow:

- **Token-efficient**: Skills provide context-aware guidance without unnecessary code generation
- **Interactive**: Architecture skill uses a "20 questions" approach to understand requirements
- **Comprehensive**: 50+ implementation patterns for nodes, agents, tools, middleware, and testing
- **Official Documentation**: All patterns reference official LangChain/LangGraph docs

### 3. Production-Ready Patterns

Includes battle-tested patterns for:

- **Memory Management**: Short-term (conversation history) and long-term (Store API)
- **Reliability**: Retry logic, fallbacks, error handling
- **Safety**: Guardrails, rate limiting, human-in-the-loop
- **Observability**: LangSmith integration, structured logging
- **Testing**: Mocking strategies, fixtures, coverage guidelines

### 4. Beginner-Friendly

Perfect for LangChain/LangGraph newcomers:

- Step-by-step implementation guides
- Pattern decision matrices
- Interactive CLI with helpful prompts
- Comprehensive inline documentation
- Example patterns for common use cases

## CLI Commands

```bash
# Create new Act project
act new [OPTIONS]
  --act-name TEXT       Project name
  --cast-name TEXT      Initial cast name
  --path PATH           Target directory

# Add cast to existing project
act cast [OPTIONS]
  --cast-name TEXT      Cast name
  --path PATH           Act project directory
```

## Example Use Cases

### Agentic AI System

Build multi-agent systems with specialized roles (researcher, writer, reviewer) using the multi-agent pattern.

### Business Workflow Automation

Orchestrate complex business processes with conditional branching, human approval steps, and external API integrations.

### Data Processing Pipeline

Create sequential or parallel data transformation graphs with error handling and retry logic.

### Conversational AI

Develop context-aware chatbots with memory management, tool calling, and guardrails.

## Contributing

We welcome contributions from the community! Please read our contributing guide:

- [CONTRIBUTING.md](CONTRIBUTING.md) (English)

### Contributors

Thank you to all our contributors! Your contributions make Act Operator better.

<a href="https://github.com/Proact0/Act-Operator/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Proact0/Act-Operator" />
</a>

## License

Apache License 2.0 - see [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for details.

---

<div align="center">
  <p>Built with ❤️ by <a href="https://www.proact0.org/">Proact0</a></p>
  <p>A non-profit open-source hub dedicated to standardizing Act (AX Template) and boosting AI productivity</p>
</div>
