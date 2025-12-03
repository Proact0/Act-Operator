## Message content

### Contents

- Content formats (String, Provider-native, Standard content blocks)
- Multimodal inputs (Image, PDF document, Audio, Video)

You can think of a message's content as the payload of data that gets sent to the model. Messages have a `content` attribute that is loosely-typed, supporting strings and lists of untyped objects (e.g., dictionaries). This allows support for provider-native structures directly in LangChain chat models, such as [multimodal](#multimodal) content and other data.

Separately, LangChain provides dedicated content types for text, reasoning, citations, multi-modal data, server-side tool calls, and other message content. See [content blocks](#standard-content-blocks) below.

LangChain chat models accept message content in the `content` attribute.

This may contain either:

1. A string
2. A list of content blocks in a provider-native format
3. A list of [LangChain's standard content blocks](#standard-content-blocks)

See below for an example using [multimodal](#multimodal) inputs:

```python  theme={null}
from langchain.messages import HumanMessage

# String content
human_message = HumanMessage("Hello, how are you?")

# Provider-native format (e.g., OpenAI)
human_message = HumanMessage(content=[
    {"type": "text", "text": "Hello, how are you?"},
    {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
])

# List of standard content blocks
human_message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Hello, how are you?"},
    {"type": "image", "url": "https://example.com/image.jpg"},
])
```

<Tip>
  Specifying `content_blocks` when initializing a message will still populate message
  `content`, but provides a type-safe interface for doing so.
</Tip>

### Multimodal

**Multimodality** refers to the ability to work with data that comes in different
forms, such as text, audio, images, and video. LangChain includes standard types
for these data that can be used across providers.

[Chat models](/oss/python/langchain/models) can accept multimodal data as input and generate
it as output. Below we show short examples of input messages featuring multimodal data.

<Note>
  Extra keys can be included top-level in the content block or nested in `"extras": {"key": value}`.

  [OpenAI](/oss/python/integrations/chat/openai#pdfs) and [AWS Bedrock Converse](/oss/python/integrations/chat/bedrock),
  for example, require a filename for PDFs. See the [provider page](/oss/python/integrations/providers/overview)
  for your chosen model for specifics.
</Note>

<CodeGroup>
  ```python Image input theme={null}
  # From URL
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this image."},
          {"type": "image", "url": "https://example.com/path/to/image.jpg"},
      ]
  }

  # From base64 data
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this image."},
          {
              "type": "image",
              "base64": "AAAAIGZ0eXBtcDQyAAAAAGlzb21tcDQyAAACAGlzb2...",
              "mime_type": "image/jpeg",
          },
      ]
  }

  # From provider-managed File ID
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this image."},
          {"type": "image", "file_id": "file-abc123"},
      ]
  }
  ```

  ```python PDF document input theme={null}
  # From URL
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this document."},
          {"type": "file", "url": "https://example.com/path/to/document.pdf"},
      ]
  }

  # From base64 data
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this document."},
          {
              "type": "file",
              "base64": "AAAAIGZ0eXBtcDQyAAAAAGlzb21tcDQyAAACAGlzb2...",
              "mime_type": "application/pdf",
          },
      ]
  }

  # From provider-managed File ID
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this document."},
          {"type": "file", "file_id": "file-abc123"},
      ]
  }
  ```

  ```python Audio input theme={null}
  # From base64 data
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this audio."},
          {
              "type": "audio",
              "base64": "AAAAIGZ0eXBtcDQyAAAAAGlzb21tcDQyAAACAGlzb2...",
              "mime_type": "audio/wav",
          },
      ]
  }

  # From provider-managed File ID
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this audio."},
          {"type": "audio", "file_id": "file-abc123"},
      ]
  }
  ```

  ```python Video input theme={null}
  # From base64 data
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this video."},
          {
              "type": "video",
              "base64": "AAAAIGZ0eXBtcDQyAAAAAGlzb21tcDQyAAACAGlzb2...",
              "mime_type": "video/mp4",
          },
      ]
  }

  # From provider-managed File ID
  message = {
      "role": "user",
      "content": [
          {"type": "text", "text": "Describe the content of this video."},
          {"type": "video", "file_id": "file-abc123"},
      ]
  }
  ```
</CodeGroup>

<Warning>
  Not all models support all file types. Check the model provider's [reference](https://reference.langchain.com/python/integrations/) for supported formats and size limits.
</Warning>
