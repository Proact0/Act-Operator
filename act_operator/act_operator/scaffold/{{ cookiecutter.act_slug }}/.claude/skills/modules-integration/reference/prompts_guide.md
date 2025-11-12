# Prompts Guide for LangGraph Applications

Comprehensive guide to prompt engineering, templates, and best practices for LangGraph applications.

## Table of Contents

1. [Introduction](#introduction)
2. [Prompt Fundamentals](#prompt-fundamentals)
3. [ChatPromptTemplate](#chatprompttemplate)
4. [PromptTemplate](#prompttemplate)
5. [Few-Shot Prompting](#few-shot-prompting)
6. [Dynamic Prompt Construction](#dynamic-prompt-construction)
7. [Prompt Composition](#prompt-composition)
8. [Best Practices](#best-practices)
9. [References](#references)

---

## Introduction

Effective prompting is crucial for LLM performance. This guide covers prompt templates, patterns, and best practices for LangGraph applications.

**Key concepts:**
- **ChatPromptTemplate**: For chat models
- **PromptTemplate**: For text completion
- **Few-shot**: Examples in prompts
- **Dynamic**: Runtime prompt construction

---

## Prompt Fundamentals

**Basic prompt:**
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{query}")
])

# Format
messages = prompt.format_messages(query="Hello!")
```

---

## ChatPromptTemplate

**Usage:**
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

# Create template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}."),
    ("user", "{question}")
])

# Chain with LLM
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
chain = prompt | llm

# Invoke
result = chain.invoke({
    "domain": "physics",
    "question": "What is gravity?"
})
```

**With message history:**
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder("history"),
    ("user", "{query}")
])

messages = prompt.format_messages(
    history=[
        ("user", "Hi"),
        ("assistant", "Hello!")
    ],
    query="How are you?"
)
```

---

## PromptTemplate

**Basic template:**
```python
from langchain_core.prompts import PromptTemplate

template = """Answer the following question:

Question: {question}
Context: {context}

Answer:"""

prompt = PromptTemplate.from_template(template)
formatted = prompt.format(
    question="What is LangGraph?",
    context="LangGraph is a framework..."
)
```

**With custom variables:**
```python
template = PromptTemplate(
    input_variables=["topic", "style"],
    template="Write a {style} article about {topic}"
)

result = template.format(
    topic="AI",
    style="technical"
)
```

---

## Few-Shot Prompting

**With examples:**
```python
examples = [
    {
        "input": "Happy",
        "output": "Sad"
    },
    {
        "input": "Tall",
        "output": "Short"
    }
]

example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="Input: {input}\nOutput: {output}"
)

from langchain_core.prompts import FewShotPromptTemplate

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Input: {input}\nOutput:",
    input_variables=["input"]
)

result = prompt.format(input="Big")
# Output includes examples + "Input: Big\nOutput:"
```

---

## Dynamic Prompt Construction

**Runtime prompt building:**
```python
class DynamicPromptNode(BaseNode):
    def execute(self, state):
        # Build prompt based on state
        messages = [
            ("system", "You are a helpful assistant.")
        ]
        
        # Add context if available
        if state.get("context"):
            messages.append(
                ("system", f"Context: {state.context}")
            )
        
        # Add history
        if state.get("history"):
            messages.extend(state.history)
        
        # Add user query
        messages.append(("user", state.query))
        
        prompt = ChatPromptTemplate.from_messages(messages)
        response = self.llm.invoke(prompt.format_messages())
        
        return {"response": response.content}
```

---

## Prompt Composition

**Combining prompts:**
```python
from langchain_core.prompts import ChatPromptTemplate

base_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant.")
])

specialized_prompt = ChatPromptTemplate.from_messages([
    ("system", "You specialize in {domain}.")
])

# Compose
final_prompt = base_prompt + specialized_prompt + ChatPromptTemplate.from_messages([
    ("user", "{query}")
])
```

---

## Best Practices

1. **Be specific** - Clear instructions
2. **Use examples** - Show desired format
3. **Set context** - Provide relevant information
4. **Test variations** - Iterate on prompts
5. **Use system messages** - Set behavior
6. **Keep concise** - Avoid unnecessary text
7. **Use templates** - Reusable prompts
8. **Version prompts** - Track changes

---

## References

- LangChain Prompts: https://python.langchain.com/docs/modules/model_io/prompts
- Prompt Engineering Guide: https://www.promptingguide.ai/
