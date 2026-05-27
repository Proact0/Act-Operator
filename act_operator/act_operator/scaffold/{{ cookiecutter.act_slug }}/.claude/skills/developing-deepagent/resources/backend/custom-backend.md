# Custom Backend

Implement your own backend by following the `BackendProtocol`.

## Contents

- BackendProtocol Interface
- Example: S3 Backend
- Using a Custom Backend
- When to Use

## BackendProtocol Interface

```python
# casts.{cast_name}.modules.utils
from typing import Protocol

class BackendProtocol(Protocol):
    def ls(self, path: str) -> list[dict]:
        """List files in a directory with metadata (size, modified time)."""
        ...

    def read_file(self, path: str, offset: int = 0, limit: int | None = None) -> str:
        """Read file contents. Support offset/limit for large files."""
        ...

    def write_file(self, path: str, content: str) -> None:
        """Create or overwrite a file."""
        ...

    def edit_file(self, path: str, old_string: str, new_string: str, replace_all: bool = False) -> None:
        """Perform exact string replacement in a file."""
        ...

    def glob(self, pattern: str) -> list[str]:
        """Find files matching a glob pattern."""
        ...

    def grep(self, pattern: str, path: str | None = None, **kwargs) -> list[dict]:
        """Search file contents with regex."""
        ...
```

## Example: S3 Backend

```python
# casts.{cast_name}.modules.utils
import re
import fnmatch
import boto3
from datetime import datetime


class S3Backend:
    """Custom backend that stores agent files in S3."""

    def __init__(self, bucket: str, prefix: str = ""):
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.prefix = prefix

    def _full_key(self, path: str) -> str:
        return f"{self.prefix}{path.lstrip('/')}"

    def ls(self, path: str) -> list[dict]:
        prefix = self._full_key(path)
        if not prefix.endswith("/"):
            prefix += "/"
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix, Delimiter="/")
        return [
            {
                "name": obj["Key"].split("/")[-1],
                "size": obj["Size"],
                "modified": obj["LastModified"].isoformat(),
            }
            for obj in response.get("Contents", [])
        ]

    def read_file(self, path: str, offset: int = 0, limit: int | None = None) -> str:
        response = self.s3.get_object(Bucket=self.bucket, Key=self._full_key(path))
        content = response["Body"].read().decode("utf-8")
        lines = content.split("\n")
        if limit is not None:
            lines = lines[offset : offset + limit]
        elif offset > 0:
            lines = lines[offset:]
        return "\n".join(lines)

    def write_file(self, path: str, content: str) -> None:
        self.s3.put_object(
            Bucket=self.bucket,
            Key=self._full_key(path),
            Body=content.encode("utf-8"),
        )

    def edit_file(self, path: str, old_string: str, new_string: str, replace_all: bool = False) -> None:
        content = self.read_file(path)
        if replace_all:
            content = content.replace(old_string, new_string)
        else:
            content = content.replace(old_string, new_string, 1)
        self.write_file(path, content)

    def glob(self, pattern: str) -> list[str]:
        prefix = self._full_key("")
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        all_keys = [obj["Key"][len(prefix):] for obj in response.get("Contents", [])]
        return [f"/{k}" for k in all_keys if fnmatch.fnmatch(k, pattern.lstrip("/"))]

    def grep(self, pattern: str, path: str | None = None, **kwargs) -> list[dict]:
        files = self.glob(path or "**/*")
        results = []
        for f in files:
            content = self.read_file(f)
            for i, line in enumerate(content.split("\n"), 1):
                if re.search(pattern, line):
                    results.append({"file": f, "line": i, "content": line})
        return results
```

## Using a Custom Backend

### As Direct Instance

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .utils import S3Backend

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        backend=S3Backend(bucket="my-agent-bucket", prefix="agent-files/"),
    )
```

### As Factory (Legacy — Pre-v0.5 Runtime Injection)

The factory form `backend=lambda rt: MyBackend(rt)` is **deprecated** as of deepagents v0.5+. The harness now provides runtime access through protocol methods on the backend instance. Keep the factory form only for backwards compatibility with custom backends that require constructor-time runtime injection:

```python
# casts.{cast_name}.modules.utils — legacy factory pattern
class RuntimeAwareBackend:
    def __init__(self, runtime):
        self.runtime = runtime
    # ... implement protocol methods


def create_runtime_backend(runtime):
    return RuntimeAwareBackend(runtime=runtime)
```

```python
# casts.{cast_name}.modules.agents
from .utils import create_runtime_backend


def set_deep_agent():
    return create_deep_agent(
        backend=create_runtime_backend,  # deprecated; prefer direct instance
    )
```

For new custom backends, refactor runtime access into protocol methods (which receive the harness runtime as a parameter) and instantiate the backend directly.

### As CompositeBackend Route

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import CompositeBackend, StateBackend


def get_s3_composite_backend():
    return CompositeBackend(
        default=StateBackend(),
        routes={"/s3-data/": S3Backend(bucket="my-bucket")},
    )
```

## When to Use

- Need storage in S3, databases, or other external systems
- Existing infrastructure that backends should integrate with
- Custom access control or auditing requirements
