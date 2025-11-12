# {{ cookiecutter.act_name }} Project Setup Checklist

Use this checklist to ensure your Act-Operator project is properly set up and ready for development.

## Initial Setup

- [ ] **Project Created**
  - [ ] Ran `act-operator new {{ cookiecutter.act_name }}`
  - [ ] Project directory exists at `{{ cookiecutter.act_slug }}/`
  - [ ] All scaffold files generated successfully

- [ ] **Environment Setup**
  - [ ] Python virtual environment created (`python -m venv venv`)
  - [ ] Virtual environment activated
  - [ ] Dependencies installed (`pip install -r requirements.txt`)
  - [ ] Development dependencies installed (`pip install -r requirements-dev.txt`)

- [ ] **API Keys Configured**
  - [ ] Created `.env` file from `.env.example`
  - [ ] Added required API keys (OpenAI, Anthropic, etc.)
  - [ ] Verified `.env` is in `.gitignore`

## Cast Development

- [ ] **Cast Structure**
  - [ ] Reviewed `casts/{{ cookiecutter.cast_snake }}/` directory
  - [ ] Understood state definition in `modules/state.py`
  - [ ] Reviewed sample nodes in `modules/nodes.py`
  - [ ] Examined graph structure in `graph.py`

- [ ] **State Schema**
  - [ ] Defined `InputState` with required input fields
  - [ ] Defined `OutputState` with required output fields
  - [ ] Defined `State` with all intermediate fields
  - [ ] Added type annotations and Annotated reducers where needed
  - [ ] Documented state fields in docstrings

- [ ] **Node Implementation**
  - [ ] Implemented required nodes (at least 1 custom node)
  - [ ] All nodes inherit from `BaseNode` or `AsyncBaseNode`
  - [ ] All nodes implement `execute()` method
  - [ ] Nodes return dict with state updates
  - [ ] Added verbose logging where helpful

- [ ] **Graph Composition**
  - [ ] Defined graph in `graph.py`
  - [ ] Added all nodes to the graph
  - [ ] Connected nodes with edges
  - [ ] Added conditional edges if needed
  - [ ] Set entry point (START) and exit point (END)
  - [ ] Graph compiles without errors

## Testing

- [ ] **Unit Tests**
  - [ ] Created test files in `tests/unit_tests/`
  - [ ] Tested each node in isolation
  - [ ] Verified node outputs are correct
  - [ ] Tested error cases
  - [ ] All unit tests pass (`pytest tests/unit_tests/`)

- [ ] **Integration Tests**
  - [ ] Created test files in `tests/integration_tests/`
  - [ ] Tested complete graph execution
  - [ ] Tested different input scenarios
  - [ ] Verified end-to-end behavior
  - [ ] All integration tests pass (`pytest tests/integration_tests/`)

- [ ] **Test Coverage**
  - [ ] Ran coverage report (`pytest --cov=casts`)
  - [ ] Coverage is above 80% (recommended)
  - [ ] Critical paths are covered
  - [ ] Edge cases are tested

## CLI Integration

- [ ] **Development Server**
  - [ ] Successfully ran `act-operator dev {{ cookiecutter.cast_snake }}`
  - [ ] Tested graph with sample inputs
  - [ ] Verified outputs are correct
  - [ ] No runtime errors

- [ ] **Production Build**
  - [ ] Successfully ran `act-operator run {{ cookiecutter.cast_snake }}`
  - [ ] Tested with production-like inputs
  - [ ] Performance is acceptable
  - [ ] Resource usage is reasonable

## Code Quality

- [ ] **Code Style**
  - [ ] Code follows PEP 8 style guide
  - [ ] Ran linter (`ruff check .` or `pylint casts/`)
  - [ ] No linting errors
  - [ ] Fixed all warnings (or justified exceptions)

- [ ] **Type Hints**
  - [ ] Added type hints to all functions
  - [ ] Ran type checker (`mypy casts/`)
  - [ ] No type errors
  - [ ] Type hints are accurate

- [ ] **Documentation**
  - [ ] All modules have docstrings
  - [ ] All classes have docstrings
  - [ ] All public functions have docstrings
  - [ ] Docstrings follow Google or NumPy style
  - [ ] README.md is updated with project-specific info

## Advanced Features (Optional)

- [ ] **Tools Integration**
  - [ ] Defined tools in `modules/tools.py`
  - [ ] Tools have proper docstrings
  - [ ] Tools are tested
  - [ ] Tools are integrated into agent nodes

- [ ] **Agent Integration**
  - [ ] Created agent nodes in `modules/agents.py`
  - [ ] Agents use appropriate tools
  - [ ] Agent behavior is tested
  - [ ] Agent prompts are optimized

- [ ] **Streaming**
  - [ ] Implemented streaming where appropriate
  - [ ] Tested streaming behavior
  - [ ] Stream chunks are properly formatted

- [ ] **Persistence**
  - [ ] Configured checkpointer if needed
  - [ ] Tested state persistence
  - [ ] Recovery from failures works

- [ ] **Custom Modules**
  - [ ] Implemented custom conditions in `modules/conditions.py`
  - [ ] Implemented custom prompts in `modules/prompts.py`
  - [ ] Implemented utilities in `modules/utils.py`
  - [ ] All custom modules are tested

## Deployment Preparation

- [ ] **Configuration**
  - [ ] Environment-specific configs are ready
  - [ ] Secrets management is configured
  - [ ] Logging is properly configured
  - [ ] Error handling is robust

- [ ] **Performance**
  - [ ] Load tested with expected traffic
  - [ ] Identified and optimized bottlenecks
  - [ ] Memory usage is acceptable
  - [ ] Response times meet requirements

- [ ] **Monitoring**
  - [ ] Added appropriate logging statements
  - [ ] Configured error tracking
  - [ ] Set up performance monitoring
  - [ ] Created alerts for critical failures

## Documentation

- [ ] **Project Documentation**
  - [ ] Updated README.md with project overview
  - [ ] Documented setup instructions
  - [ ] Documented usage examples
  - [ ] Added troubleshooting guide

- [ ] **API Documentation**
  - [ ] Documented input schema
  - [ ] Documented output schema
  - [ ] Documented error responses
  - [ ] Added usage examples

- [ ] **Developer Documentation**
  - [ ] Documented architecture decisions
  - [ ] Created contribution guidelines
  - [ ] Documented development workflow
  - [ ] Added code examples

## Pre-launch Checklist

- [ ] **Final Review**
  - [ ] All tests passing
  - [ ] No linting errors
  - [ ] No type errors
  - [ ] Documentation is complete
  - [ ] Security review completed
  - [ ] Performance requirements met

- [ ] **Version Control**
  - [ ] All changes committed
  - [ ] Meaningful commit messages
  - [ ] No sensitive data in repository
  - [ ] Tagged release version

- [ ] **Ready for Deployment**
  - [ ] Deployment plan created
  - [ ] Rollback plan prepared
  - [ ] Monitoring is active
  - [ ] Team is trained

---

## Notes

Use this space to track project-specific notes, issues, or decisions:

```
[Add your notes here]
```

---

## Validation Commands

Run these commands to validate your setup:

```bash
# Validate cast structure
python .claude/skills/cast-development/scripts/validate_cast.py {{ cookiecutter.cast_snake }}

# Run tests with coverage
python .claude/skills/testing-debugging/scripts/run_tests.py --coverage

# Visualize graph
python .claude/skills/graph-composition/scripts/visualize_graph.py {{ cookiecutter.cast_snake }}

# Run development server
act-operator dev {{ cookiecutter.cast_snake }}
```

---

**Last Updated:** [Date]  
**Completed By:** [Name]  
**Project Status:** [In Development / Ready for Testing / Production Ready]
