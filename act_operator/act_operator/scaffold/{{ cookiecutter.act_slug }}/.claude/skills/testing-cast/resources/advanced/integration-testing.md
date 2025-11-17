# Integration Testing

## When to Use This Resource
Read this for testing complete workflows, multi-node interactions, and end-to-end scenarios.

## Complete Workflow Testing

```python
# tests/integration/test_workflow.py
import pytest
from langgraph.checkpoint.sqlite import SqliteSaver

class TestCompleteWorkflow:
    @pytest.fixture
    def integrated_graph(self):
        """Graph with all dependencies."""
        from casts.my_cast.graph import MyCastGraph
        checkpointer = SqliteSaver.from_conn_string(":memory:")
        return MyCastGraph().build(checkpointer=checkpointer)

    def test_end_to_end_flow(self, integrated_graph):
        """Test complete user journey."""
        config = {"configurable": {"thread_id": "integration-test"}}

        # Step 1: Initial query
        result1 = integrated_graph.invoke(
            {"input": "Start workflow"},
            config=config
        )
        assert result1["status"] == "in_progress"

        # Step 2: Follow-up
        result2 = integrated_graph.invoke(
            {"input": "Continue"},
            config=config
        )
        assert result2["status"] == "completed"
```

## Multi-Node Integration

```python
class TestMultiNodeIntegration:
    def test_nodes_work_together(self, graph):
        """Nodes should pass data correctly."""
        result = graph.invoke({"input": "test data"})

        # Verify data flowed through nodes
        assert "processed_by_node1" in result
        assert "processed_by_node2" in result
        assert result["final_output"] is not None
```

## Testing with Real Dependencies (Optional)

```python
@pytest.mark.integration
@pytest.mark.slow
class TestWithRealServices:
    """Tests using real external services."""

    @pytest.mark.skipif(not has_api_key(), reason="API key not configured")
    def test_real_llm_call(self, graph):
        """Test with actual LLM (requires API key)."""
        result = graph.invoke({"input": "Real query"})

        assert result["response"] is not None
        # More assertions on real behavior
```

## Testing Error Recovery

```python
class TestErrorRecovery:
    def test_recovers_from_node_failure(self, graph):
        """Graph should handle node failures gracefully."""
        # Inject error condition
        result = graph.invoke({"input": "trigger_error", "retry": True})

        # Should have attempted recovery
        assert result.get("retries", 0) > 0
        # Should have final result despite error
        assert "result" in result or "error" in result
```

## Testing Subgraph Integration

```python
class TestSubgraphIntegration:
    def test_parent_child_communication(self, parent_graph):
        """Parent and subgraph should communicate correctly."""
        result = parent_graph.invoke({"input": "test"})

        # Verify subgraph executed
        assert "subgraph_output" in result
        # Verify parent processed subgraph result
        assert result["final"] is not None
```

## Testing Concurrent Execution

```python
import asyncio

class TestConcurrentExecution:
    @pytest.mark.asyncio
    async def test_parallel_requests(self, graph):
        """Multiple concurrent requests should work."""
        configs = [
            {"configurable": {"thread_id": f"user-{i}"}}
            for i in range(5)
        ]

        results = await asyncio.gather(*[
            graph.ainvoke({"input": f"query {i}"}, config=configs[i])
            for i in range(5)
        ])

        assert len(results) == 5
        # Each should have unique result
        assert len(set(r.get("thread_id") for r in results)) == 5
```

## Testing Long-Running Workflows

```python
class TestLongWorkflows:
    @pytest.mark.slow
    def test_multi_step_workflow(self, graph_with_memory):
        """Test workflow with many steps."""
        config = {"configurable": {"thread_id": "long-workflow"}}

        steps = [
            "Initialize",
            "Gather data",
            "Process",
            "Analyze",
            "Generate report"
        ]

        for step in steps:
            result = graph_with_memory.invoke(
                {"input": step},
                config=config
            )
            assert result["status"] != "error"

        # Final state should be complete
        final_state = graph_with_memory.get_state(config)
        assert "report" in final_state.values
```

## Snapshot Testing for Integration

```python
class TestIntegrationSnapshots:
    def test_output_matches_snapshot(self, graph, snapshot):
        """Compare complete workflow output to snapshot."""
        result = graph.invoke({"input": "standard test case"})

        # Remove non-deterministic fields
        result.pop("timestamp", None)
        result.pop("duration", None)

        assert result == snapshot
```

## Performance Testing

```python
import time

class TestPerformance:
    @pytest.mark.slow
    def test_executes_within_time_limit(self, graph):
        """Workflow should complete in reasonable time."""
        start = time.time()

        result = graph.invoke({"input": "performance test"})

        duration = time.time() - start

        assert duration < 10.0  # Should complete in < 10s
        assert result is not None
```

## References
- Related: `testing-graphs.md` (graph-level testing)
- Related: `async-testing.md` (async integration tests)
- Related: `coverage-best-practices.md` (coverage goals)
