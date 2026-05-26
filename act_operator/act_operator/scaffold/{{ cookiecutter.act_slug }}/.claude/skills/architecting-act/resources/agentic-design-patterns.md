# Agentic Design Patterns

Guide for Step 1a: Determine if AI Agent is needed, and select appropriate Agentic Pattern.

## When to Consider Agentic Patterns

**First, assess if the workflow requires AI agent capabilities:**

| Indicator | Example | → Agentic Pattern |
|-----------|---------|-------------------|
| Autonomous decision-making | Route queries to appropriate handler | Coordinator |
| Tool/API access | Query databases, call external APIs | Single-Agent |
| Iterative reasoning | Refine output until quality threshold | Iterative Refinement |
| Self-correction | Detect and fix errors autonomously | ReAct, Loop |
| Human oversight needed | High-stakes decisions, compliance | Human-in-the-Loop |
| Multiple specialized roles | Generator + Critic, Researcher + Writer | Multi-Agent |

**Skip Agentic Patterns when:**
- Simple data transformation (CSV→JSON)
- Fixed, deterministic workflows
- No external interactions needed
- All logic expressible as explicit rules

---

## Pattern Catalog

### 1. Single-Agent System

**Structure:** One AI model + tools + system prompt

```mermaid
graph LR
    START([START]) --> A["AgentNode(tools=[tool1, tool2, ...])"]
    A --> END([END])
```

**Use when:**
- Moderate complexity tasks
- Early-stage development
- Tool count < 10

**Trade-offs:**
- ✅ Simple to implement and debug
- ❌ Performance degrades with many tools
- ❌ Complex tasks may need decomposition

**Example:** Customer support agent with order lookup, FAQ retrieval tools

---

### 2. Multi-Agent Systems

#### 2a. Sequential Pattern

**Structure:** Agent1 → Agent2 → Agent3 → END

```mermaid
graph LR
    START([START]) --> A[DataCollectorNode]
    A --> B[AnalyzerNode]
    B --> C[ReportWriterNode]
    C --> END([END])
```

**Use when:**
- Rigid, ordered pipeline
- Each step depends on previous output
- No dynamic routing needed

**Trade-offs:**
- ✅ Predictable, low orchestration cost
- ❌ Inflexible, cannot skip steps
- ❌ Poor for dynamic conditions

---

#### 2b. Parallel Pattern

**Structure:** [Agent1, Agent2, Agent3] execute simultaneously → Synthesize

```mermaid
graph LR
    START([START]) --> A[SentimentNode] & B[KeywordNode] & C[CategoryNode]
    A & B & C --> D[SynthesizerNode]
    D --> END([END])
```

**Use when:**
- Independent tasks executable concurrently
- Gathering diverse perspectives
- Reducing overall latency

**Trade-offs:**
- ✅ Reduced latency through concurrency
- ❌ Higher resource/cost utilization
- ❌ Complex synthesis for conflicting results

---

#### 2c. Loop Pattern

**Structure:** Process → Evaluate → (Refine ↺ | Complete)

```mermaid
graph LR
    START([START]) --> A[GeneratorNode]
    A --> B[EvaluatorNode]
    B -->|needs_refinement| A
    B -->|complete| END([END])
```

**Use when:**
- Iterative refinement tasks
- Quality threshold must be met
- Self-correction workflows

**Design notes:**
- Set max iterations (3-10)
- Define clear exit conditions
- Track progress per iteration

**Trade-offs:**
- ✅ Enables iterative improvement
- ❌ Risk of infinite loops
- ❌ Unpredictable latency

---

#### 2d. Review and Critique Pattern

**Structure:** Generator → Critic → (Revise ↺ | Approve)

```mermaid
graph LR
    START([START]) --> A[GeneratorNode]
    A --> B[CriticNode]
    B -->|rejected| A
    B -->|approved| END([END])
```

**Use when:**
- High accuracy requirements
- Strict formatting/constraint compliance
- Code generation with security review
- Sensitive document validation

**Trade-offs:**
- ✅ Improved output quality
- ✅ Dedicated verification step
- ❌ Additional latency from review
- ❌ Revision loops accumulate costs

---

#### 2e. Iterative Refinement Pattern

**Structure:** Cycle with session state across multiple iterations

```mermaid
graph LR
    START([START]) --> A[GeneratorNode]
    A --> B[CriticNode]
    B --> C{MeetsThreshold}
    C -->|no| D[RefineWithFeedbackNode]
    D --> A
    C -->|yes| END([END])
```

**Use when:**
- Complex generation difficult in single step
- Code writing and debugging
- Multi-part planning
- Long-form document drafting

**Key difference from Loop:** Maintains rich session state across cycles, stores improvement history

**Trade-offs:**
- ✅ Produces highly polished outputs
- ❌ Direct cost/latency increase per cycle
- ❌ Requires sophisticated exit conditions

---

#### 2f. Coordinator Pattern

**Structure:** Central AI analyzes → dispatches to specialists

```mermaid
graph LR
    START([START]) --> A[CoordinatorNode]
    A -->|order_query| B[OrderAgentNode]
    B --> A
    A -->|returns| C[ReturnsAgentNode]
    C --> A
    A -->|faq| D[FAQAgentNode]
    D --> A
    A --> END([END])
```

**Use when:**
- Varied input types needing flexible routing
- Structured business process automation
- Adaptive routing requirements

**Trade-offs:**
- ✅ Flexible, handles diverse inputs
- ✅ Runtime adaptation capability
- ❌ Multiple model calls increase costs
- ❌ Higher latency than direct routing

---

#### 2g. Hierarchical Task Decomposition Pattern

**Structure:** Root agent decomposes → delegates to sub-agents

```mermaid
graph LR
    START([START]) --> A[RootAgentNode]
    A --> B[SubAgentsNode]
    B --> C[SubSubAgentsNode]
    C --> D[SynthesizerNode]
    D --> END([END])
```

**Use when:**
- Complex, ambiguous, open-ended problems
- Multi-step research and planning
- Problems requiring extensive decomposition
- Quality more important than speed

**Trade-offs:**
- ✅ Handles highly complex problems
- ✅ Comprehensive, high-quality results
- ❌ High architectural complexity
- ❌ Difficult to debug and maintain
- ❌ Significantly increased latency/costs

---

#### 2h. Swarm Pattern

**Structure:** All-to-all collaboration, iterative debate

```mermaid
graph LR
    subgraph Swarm["Collaborative Debate"]
        A[Agent1Node] <--> B[Agent2Node]
        B <--> C[Agent3Node]
        C <--> A
    end
```

**Use when:**
- Highly complex, ambiguous problems
- Solutions benefit from debate/refinement
- Consensus-building requirements
- Creative problem-solving

**Trade-offs:**
- ✅ Simulates collaborative expert team
- ✅ Exceptionally creative solutions
- ❌ Most complex and costly pattern
- ❌ Risk of unproductive loops
- ❌ May fail to converge

---

### 3. ReAct (Reason and Act) Pattern

**Structure:** Thought → Action → Observation loop

```mermaid
graph LR
    START([START]) --> A[ReasonNode]
    A --> B[SelectActionNode]
    B --> C[ExecuteActionNode]
    C --> D{IsFinalAnswer}
    D -->|no| A
    D -->|yes| END([END])
```

**Use when:**
- Complex, dynamic tasks requiring continuous planning
- Adaptive approach based on new observations
- Robotics, pathfinding, navigation
- Real-time environmental constraints

**Trade-offs:**
- ✅ Transparent reasoning (aids debugging)
- ✅ Dynamic adaptation to new information
- ❌ Higher latency from multi-step iteration
- ❌ Effectiveness depends on model quality
- ❌ Errors propagate through observations

---

### 4. Human-in-the-Loop Pattern

**Structure:** Agent workflow with predefined human checkpoints

```mermaid
graph LR
    START([START]) --> A[AutoProcessNode]
    A --> B{HumanCheckpoint}
    B -->|approved| C[ContinueProcessNode]
    C --> END([END])
    B -->|rejected| A
    B -.- D[HumanReviewerNode]
```

**Use when:**
- High-stakes decisions
- Safety-critical operations
- Subjective judgment requirements
- Compliance and validation needs
- Escalation after agent failure

**Implementation:**
- Define clear checkpoint criteria
- Build approval/rejection UI
- Handle timeout scenarios
- Log human decisions

**Trade-offs:**
- ✅ Improves safety and reliability
- ✅ Adds human judgment at critical points
- ❌ Requires external interaction system
- ❌ Adds latency from human waiting
- ❌ Scaling challenges with multiple approvals

---

### 5. Custom Logic Pattern

**Structure:** Code-based orchestration with complex branching

```mermaid
graph LR
    START([START]) --> A{ConditionA}
    A -->|yes| B[AgentANode]
    B --> C{ConfidenceCheck}
    C -->|high| D[HandleResultNode]
    C -->|low| E[AgentBNode]
    E --> F[MergeResultsNode]
    A -->|no:fallback| G[FallbackAgentNode]
    D --> END([END])
    F --> END([END])
    G --> END([END])
```

**Use when:**
- Complex branching beyond linear sequences
- Mixing predefined rules with model reasoning
- Fine-grained process control
- Workflows not fitting standard templates

**Trade-offs:**
- ✅ Maximum control over execution
- ✅ Accommodates unique business logic
- ❌ Increases development complexity
- ❌ More error-prone than patterns
- ❌ Requires extensive testing

---

## Subgraph Composition with `create_agent` / `create_deep_agent`

LangGraph's `create_agent()` (from `langchain.agents`) returns a `CompiledGraph` — a self-contained agent subgraph with its own internal node/edge structure. This subgraph can be composed into a parent graph in multiple ways.

> **Note:** `create_react_agent` is deprecated since LangGraph v1. Always use `create_agent`.

### Agent Type Selection

| Criterion | `create_agent` | `create_deep_agent` |
|-----------|----------------|---------------------|
| Complexity | Standard ReAct agent | Multi-step agent harness |
| Tool usage | Direct tool binding | Tools + subagent delegation |
| Memory | External (checkpointer) | Built-in long-term memory |
| Sandbox | No | Yes (virtual filesystems) |
| Human-in-the-Loop | Via interrupt nodes | Built-in HITL |
| Subagent spawning | Manual composition | Native subagent support |
| Best for | Tool-calling agents, reasoning loops | Complex multi-step tasks, coding agents |

**Rule:** Use `create_agent` for focused tool-calling agents. Use `create_deep_agent` when the agent needs subagent delegation, sandboxed execution, or long-term memory.

---

### Composition Strategy A: Subgraph AS a Node

The compiled agent is directly added as a node. The parent graph treats it as an opaque unit.

```mermaid
graph LR
    START([START]) --> A[PreprocessNode]
    A --> B

    subgraph B["ResearchAgent (create_agent subgraph)"]
        direction LR
        B1([entry]) --> B2[ReasonNode]
        B2 --> B3[ToolCallNode]
        B3 --> B4{ShouldContinue}
        B4 -->|yes| B2
        B4 -->|no| B5([exit])
    end

    B --> C[PostprocessNode]
    C --> END([END])
```

**Use when:**
- The agent has a well-defined, reusable responsibility
- Internal agent logic should be encapsulated (black-box)
- State mapping between parent ↔ subgraph is straightforward

---

### Composition Strategy B: Subgraph INSIDE a Node

A regular node function internally invokes one or more agent subgraphs, handling state transformation and orchestration logic.

```mermaid
graph LR
    START([START]) --> A[RouterNode]
    A -->|type_a| B[OrchestratorNodeA]
    A -->|type_b| C[OrchestratorNodeB]

    B -.->|internally invokes| D["AgentAlpha (subgraph)"]
    B -.->|internally invokes| E["AgentBeta (subgraph)"]

    C -.->|internally invokes| F["AgentGamma (subgraph)"]

    B --> G[SynthesizeNode]
    C --> G
    G --> END([END])
```

**Use when:**
- Custom pre/post-processing around the agent is needed
- Multiple agents are orchestrated within a single step
- State transformation between parent and agent requires logic
- The node needs to decide which agent(s) to invoke dynamically

---

### Composition Strategy C: Multi-Agent Subgraph Network

Multiple agent subgraphs are composed as separate nodes in the parent graph, connected via edges.

```mermaid
graph LR
    START([START]) --> A

    subgraph A["PlannerAgent (create_agent subgraph)"]
        direction LR
        A1([entry]) --> A2[PlanNode] --> A3([exit])
    end

    A --> B

    subgraph B["ExecutorAgent (create_agent subgraph)"]
        direction LR
        B1([entry]) --> B2[ExecuteNode] --> B3[ToolNode] --> B4{Done}
        B4 -->|no| B2
        B4 -->|yes| B5([exit])
    end

    B --> C{QualityCheck}
    C -->|pass| END([END])
    C -->|fail| A
```

**Use when:**
- Each agent has distinct specialty and tools
- Agents need to hand off work to each other
- The overall flow between agents has conditional logic
- Each agent's internal complexity warrants its own subgraph

---

### Composition Strategy D: DeepAgent with Subagents

`create_deep_agent` as a top-level or nested agent with subagent delegation.

```mermaid
graph LR
    START([START]) --> A

    subgraph A["OrchestratorAgent (create_deep_agent)"]
        direction LR
        A1([entry]) --> A2[PlanNode]
        A2 --> A3{DelegateTask}
        A3 -->|code_task| A4["CoderSubAgent"]
        A3 -->|research_task| A5["ResearchSubAgent"]
        A4 --> A6[ReviewNode]
        A5 --> A6
        A6 --> A7{NeedMore}
        A7 -->|yes| A2
        A7 -->|no| A8([exit])
    end

    A --> B[FinalizeNode]
    B --> END([END])
```

**Use when:**
- Complex multi-step tasks requiring planning + delegation
- Subagents need sandboxed execution environments
- Long-running tasks requiring persistent memory across sessions
- Native human-in-the-loop approval workflows

---

### Node Type Decision

| Criterion | Custom Node | ToolNode | `create_agent` | `create_deep_agent` |
|-----------|-------------|----------|----------------|---------------------|
| Has its own tool set | No | Yes (executes calls) | Yes (binds tools) | Yes + subagent delegation |
| Internal reasoning loop | No | No | Yes (ReAct) | Yes + planning |
| Reusable across casts | Unlikely | Yes | Yes | Yes |
| Internal complexity | Low (single function) | Low (stateless dispatch) | Medium (tool-calling loop) | High (multi-step + subagents) |
| State isolation needed | No | No | Yes | Yes |
| Sandbox execution | No | No | No | Yes |
| Long-term memory | No | No | No | Yes |

**Rule of thumb:**
- Single deterministic operation → **Custom Node** (BaseNode/AsyncBaseNode)
- Model outputs tool_calls, needs stateless execution → **ToolNode**
- Needs tools + autonomous reasoning loop → **`create_agent` subgraph**
- Needs subagent delegation, sandbox, or long-term memory → **`create_deep_agent`**

---

## Resilience & Long-Run Patterns (langgraph v1.2+)

Architecture decisions sometimes require resilience capabilities that shape graph topology. These are not standalone patterns — they overlay any pattern above.

### Saga / Compensation

When a step has side effects (payment, external write) that must be unwound on failure, design the cast with an explicit compensation branch. The failing node has an `error_handler` that updates state and routes to the compensation node after retries are exhausted.

```mermaid
graph LR
    START([START]) --> A[ValidateNode]
    A --> B[ChargePaymentNode]
    B --> C[FulfillOrderNode]
    C --> END([END])
    B -.->|error_handler after retries| D[CompensationNode]
    D --> E[FinalizeNode]
    E --> END
```

**Design signal:** Node has irreversible external effects + must always reach a consistent terminal state.

### Long-Running Thread (DeltaChannel)

When a channel grows unbounded across many turns (chat history, audit log, accumulated documents), design the state so the channel can use `DeltaChannel` storage. Architecturally this means:

- The channel must have an **associative, pure-function** bulk reducer.
- Identity / stable IDs must be assigned **upstream** of the channel, not inside the reducer.
- Pair with `snapshot_frequency=K` for bounded read latency.

**Design signal:** Conversation length or accumulation grows linearly across turns and checkpoint size is becoming a problem.

### Graceful Drain Checkpoints

When a node performs expensive work (LLM call, long DB query) and the cast may need to terminate cooperatively (SIGTERM, infra reclaim), design nodes to **read drain state** and skip work at safe boundaries.

```mermaid
graph LR
    START([START]) --> A[InspectDrainNode]
    A -->|drain_requested| B[CheckpointAndExitNode]
    A -->|continue| C[ExpensiveWorkNode]
    C --> END([END])
    B --> END
```

Pair with a checkpointer so the drained run is resumable from the saved checkpoint.

**Design signal:** Cast is long-running, deploys in containers, or holds external locks/resources that must release on shutdown.

### Node Timeout Boundaries

For nodes that call external services with unpredictable latency (web scrape, LLM, network DB), set node timeouts at the architecture level — they shape the retry/fallback topology around the node. Async nodes only.

| Topology cue | Implementation |
|--------------|----------------|
| Wall-clock guarantee per call | `timeout=` (seconds or `TimeoutPolicy(run_timeout=...)`) |
| Progress-aware streaming work | `TimeoutPolicy(idle_timeout=...)` + `runtime.heartbeat()` calls in the node |
| Retry on timeout | `retry_policy=RetryPolicy(retry_on=TimeoutError)` paired with `timeout=` |
| Compensation on persistent timeout | `error_handler=` returning `Command(goto=...)` to a fallback branch |

---

## Combining Patterns

**Common pattern combinations:**

| Primary Pattern | + Secondary Pattern | Use Case |
|-----------------|---------------------|----------|
| Coordinator | + Human-in-the-Loop | Routing with escalation checkpoints |
| Iterative Refinement | + Human-in-the-Loop | Quality cycles with human fallback |
| Sequential | + Human-in-the-Loop | Pipeline with approval gates |
| Coordinator | + Review & Critique | Routing with output validation |

**Design approach for combinations:**
1. Identify primary workflow pattern
2. Overlay secondary pattern at specific checkpoints
3. Define clear transition criteria between patterns

---

## Single-Agent vs Multi-Agent Decision

| Criterion | Single-Agent | Multi-Agent |
|-----------|--------------|-------------|
| Tool count | < 10 tools | > 10 tools or specialized domains |
| Task complexity | One domain, moderate complexity | Multiple domains, high complexity |
| Routing needs | Static, predictable | Dynamic, input-dependent |
| Development stage | Early/prototyping | Production, proven requirements |

**Start with Single-Agent** unless clear indicators for Multi-Agent exist.

---

## Pattern Selection Decision Matrix

### By Workload Characteristics

| Workload Type | Primary Pattern | Alternative |
|---------------|-----------------|-------------|
| Deterministic pipeline | Sequential | - |
| Classification + routing | Coordinator | Branching |
| Quality-critical generation | Review & Critique | Iterative Refinement |
| Time-sensitive | Single-Agent | Parallel |
| Cost-constrained | Single-Agent | Sequential |
| High-stakes decisions | Human-in-the-Loop | - |
| Complex branching | Custom Logic | Coordinator |
| Creative/ambiguous problems | Swarm | Hierarchical |
| Continuous reasoning | ReAct | Loop |

### By Performance Requirements

| Priority | Recommended | Avoid |
|----------|-------------|-------|
| Low Latency | Sequential, Parallel, Single-Agent | Hierarchical, Swarm |
| Low Cost | Single-Agent, Sequential | Swarm, Hierarchical |
| High Quality | Review & Critique, Iterative Refinement | Single-pass patterns |
| High Flexibility | Coordinator, Custom Logic | Sequential |
| Easy Debugging | Single-Agent, ReAct | Swarm |

---

## Quick Reference: Pattern Selection Flowchart

```mermaid
flowchart TD
    A{IsAIAgentNeeded}
    A -->|YES| B{HowManyAgents}
    A -->|NO| C[BasicPatternsNode<br/>(Sequential/Branching/<br/>Cyclic/Multi-agent)]

    B -->|ONE| D[SingleAgentNode]
    B -->|2-3| E{WhichCollaboration}
    B -->|4+| F{ComplexOrchestration}

    E --> G[SequentialNode]
    E --> H[ParallelNode]

    F --> I[HierarchicalNode]
    F --> J[SwarmNode]

    C --> K{NeedHumanOversight}
    D --> K
    G --> K
    H --> K
    I --> K
    J --> K

    K -->|YES| L[HumanInTheLoopNode]
    K -->|NO| M[ContinuePatternNode]
```