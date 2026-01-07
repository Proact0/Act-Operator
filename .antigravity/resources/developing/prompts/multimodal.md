# Multimodal Content

Multimodal inputs (images, audio, PDF, video) in prompts.

## Content Formats

| Format | Use Case |
|--------|----------|
| `url` | Remote file URL |
| `base64` | Encoded binary data |
| `file_id` | Provider-managed file |

## Image Input

```python
# casts.{cast_name}.modules.prompts
from langchain_core.messages import HumanMessage

def create_image_prompt(text: str, image_url: str) -> HumanMessage:
    """Create message with image from URL."""
    return HumanMessage(content=[
        {"type": "text", "text": text},
        {"type": "image", "url": image_url},
    ])

def create_image_base64_prompt(text: str, base64_data: str) -> HumanMessage:
    """Create message with base64 encoded image."""
    return HumanMessage(content=[
        {"type": "text", "text": text},
        {
            "type": "image",
            "base64": base64_data,
            "mime_type": "image/jpeg",
        },
    ])
```

## PDF Document Input

```python
# casts.{cast_name}.modules.prompts
from langchain_core.messages import HumanMessage

def create_pdf_prompt(text: str, pdf_url: str) -> HumanMessage:
    """Create message with PDF from URL."""
    return HumanMessage(content=[
        {"type": "text", "text": text},
        {"type": "file", "url": pdf_url},
    ])

def create_pdf_base64_prompt(text: str, base64_data: str) -> HumanMessage:
    """Create message with base64 encoded PDF."""
    return HumanMessage(content=[
        {"type": "text", "text": text},
        {
            "type": "file",
            "base64": base64_data,
            "mime_type": "application/pdf",
        },
    ])
```

## Audio Input

```python
# casts.{cast_name}.modules.prompts
from langchain_core.messages import HumanMessage

def create_audio_prompt(text: str, base64_data: str) -> HumanMessage:
    """Create message with audio."""
    return HumanMessage(content=[
        {"type": "text", "text": text},
        {
            "type": "audio",
            "base64": base64_data,
            "mime_type": "audio/wav",
        },
    ])
```

## Video Input

```python
# casts.{cast_name}.modules.prompts
from langchain_core.messages import HumanMessage

def create_video_prompt(text: str, base64_data: str) -> HumanMessage:
    """Create message with video."""
    return HumanMessage(content=[
        {"type": "text", "text": text},
        {
            "type": "video",
            "base64": base64_data,
            "mime_type": "video/mp4",
        },
    ])
```

## Usage in Nodes

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from .prompts import create_image_prompt
from .models import get_vision_model

class ImageAnalysisNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.model = get_vision_model()
    
    def execute(self, state):
        message = create_image_prompt(
            text="Describe this image in detail.",
            image_url=state["image_url"]
        )
        
        response = self.model.invoke([message])
        
        return {"analysis": response.content}
```

## Provider Support

Not all providers support all formats. Check provider documentation:
- **OpenAI**: Images, Audio, PDF
- **Anthropic**: Images, PDF
- **Google**: Images, Audio, Video

