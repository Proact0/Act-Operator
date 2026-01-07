# Tool with Complex Inputs

Define complex inputs using Pydantic models.

## Pydantic Schema

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Literal

class WeatherInput(BaseModel):
    """Input for weather queries."""
    location: str = Field(description="City name or coordinates")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )
    include_forecast: bool = Field(
        default=False,
        description="Include 5-day forecast"
    )

@tool(args_schema=WeatherInput)
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Get current weather and optional forecast."""
    temp = 22 if units == "celsius" else 72
    result = f"Current weather in {location}: {temp}°{units[0].upper()}"
    if include_forecast:
        result += "\nNext 5 days: Sunny"
    return result
```

## JSON Schema (Alternative)

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool

weather_schema = {
    "type": "object",
    "properties": {
        "location": {"type": "string"},
        "units": {"type": "string"},
        "include_forecast": {"type": "boolean"}
    },
    "required": ["location"]
}

@tool(args_schema=weather_schema)
def get_weather_json(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Get current weather."""
    return f"Weather in {location}: 22°C"
```

---

## Agent Usage

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .models import get_model
from .tools import get_weather

def set_weather_agent():
    return create_agent(
        model=get_model(),
        tools=[get_weather],
    )
```

## Model(Standalone) Usage

```python
# casts.{cast_name}.modules.models
from langchain_openai import ChatOpenAI
from .tools import get_weather

def get_tool_model():
    model = ChatOpenAI(model="gpt-4o")
    model.bind_tools([get_weather])
    return model
```