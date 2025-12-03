# Guardrails

Implement safety checks and content filtering at key execution points.

## Contents

- Built-in: PII Detection
- Custom: Before Agent Guardrail
- Custom: After Agent Guardrail
- Combining Guardrails

## Built-in: PII Detection

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import PIIMiddleware

def get_pii_middlewares():
    return [
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",  # Custom regex
            strategy="block",
            apply_to_input=True,
        ),
    ]
```

**Strategies:** `redact` → `[REDACTED_TYPE]`, `mask` → `****1234`, `hash` → deterministic hash, `block` → raise error

**Built-in PII types:** `email`, `credit_card`, `ip`, `mac_address`, `url`

**Parameters:** `apply_to_input` (True), `apply_to_output` (False), `apply_to_tool_results` (False)

## Custom: Before Agent Guardrail

Block requests containing banned keywords before processing.

```python
# casts.{cast_name}.modules.middlewares
from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime

class ContentFilterMiddleware(AgentMiddleware):
    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]

    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if not state["messages"]:
            return None
        
        first_message = state["messages"][0]
        if first_message.type != "human":
            return None
        
        content = first_message.content.lower()
        for keyword in self.banned_keywords:
            if keyword in content:
                return {
                    "messages": [{"role": "assistant", "content": "Cannot process this request."}],
                    "jump_to": "end"
                }
        return None
```

## Custom: After Agent Guardrail

Validate final outputs using LLM-based safety check.

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.messages import AIMessage
from langchain.chat_models import init_chat_model

class SafetyGuardrailMiddleware(AgentMiddleware):
    def __init__(self):
        super().__init__()
        self.safety_model = init_chat_model("gpt-4o-mini")

    @hook_config(can_jump_to=["end"])
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if not state["messages"]:
            return None
        
        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None
        
        safety_prompt = f"Evaluate if safe. Respond 'SAFE' or 'UNSAFE'.\n\nResponse: {last_message.content}"
        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])
        
        if "UNSAFE" in result.content:
            last_message.content = "I cannot provide that response."
        return None
```

## Combining Guardrails

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware, HumanInTheLoopMiddleware
from .middlewares import ContentFilterMiddleware, SafetyGuardrailMiddleware

def set_guarded_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[
            ContentFilterMiddleware(banned_keywords=["hack", "exploit"]),
            PIIMiddleware("email", strategy="redact", apply_to_input=True),
            HumanInTheLoopMiddleware(interrupt_on={"send_email": True}),
            SafetyGuardrailMiddleware(),
        ],
    )
```
