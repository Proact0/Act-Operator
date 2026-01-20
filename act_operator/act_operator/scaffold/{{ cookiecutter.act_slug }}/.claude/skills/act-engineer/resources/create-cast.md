# Create Cast

## Before Creating

**Check CLAUDE.md files if they exist:**
- **Root `/CLAUDE.md`**: Review existing Casts in "Casts" table
- **Cast `/casts/{cast_slug}/CLAUDE.md`**: Check if design already exists for this cast
- Understand how new Cast relates to existing ones

## Command

```bash
uv run act cast -c "My Cast Name"
```

Interactive mode:
```bash
uv run act cast
```

## After Creation

1. Define state in `modules/state.py`
2. Implement nodes in `modules/nodes.py`
3. Build graph in `graph.py`
4. Add cast dependencies if needed:
   ```bash
   uv add --package {cast_name} langchain-openai
   ```

