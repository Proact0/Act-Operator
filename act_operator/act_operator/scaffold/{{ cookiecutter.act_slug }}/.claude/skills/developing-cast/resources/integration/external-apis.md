# External APIs Integration

## When to Use This Resource
Read this when integrating REST APIs, GraphQL, webhooks, or any external services not using MCP.

## Integration Approaches

### Approach 1: Tools (Recommended for LLM Access)

**When:** LLM should be able to call the API.

```python
# modules/tools/api_tools.py
from langchain_core.tools import tool
import requests

@tool
def search_products(query: str, limit: int = 10) -> list[dict]:
    """Search products in the catalog.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of product dictionaries
    """
    response = requests.get(
        "https://api.example.com/products/search",
        params={"q": query, "limit": limit},
        headers={"Authorization": f"Bearer {os.getenv('API_KEY')}"}
    )
    response.raise_for_status()
    return response.json()["products"]
```

**Pros:**
- ✅ LLM can discover and use
- ✅ Reusable across graphs
- ✅ Self-documenting (docstring)

### Approach 2: Nodes (For Complex Logic)

**When:** API call requires state context or complex pre/post-processing.

```python
# casts/my_cast/nodes.py
from casts.base_node import BaseNode
import requests

class FetchUserDataNode(BaseNode):
    """Fetches user data from external API."""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.base_url = "https://api.example.com"

    def execute(self, state: dict) -> dict:
        user_id = state.get("user_id")

        if not user_id:
            return {"error": "Missing user_id"}

        try:
            response = requests.get(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()

            user_data = response.json()

            return {
                "user_data": user_data,
                "user_name": user_data.get("name"),
                "user_email": user_data.get("email")
            }

        except requests.Timeout:
            return {"error": "API timeout"}
        except requests.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            self.log(f"Unexpected error: {e}")
            return {"error": "API call failed"}
```

**Pros:**
- ✅ Full control over request/response
- ✅ State-aware processing
- ✅ Complex error handling

### Approach 3: Async Nodes (For Performance)

**When:** Multiple API calls or I/O-bound operations.

```python
from casts.base_node import AsyncBaseNode
import httpx  # Async HTTP client

class AsyncAPINode(AsyncBaseNode):
    """Async API calls for better performance."""

    async def execute(self, state: dict) -> dict:
        async with httpx.AsyncClient() as client:
            # Parallel requests
            tasks = [
                client.get(f"https://api.example.com/item/{id}")
                for id in state.get("item_ids", [])
            ]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            results = []
            errors = []

            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    errors.append({"item_id": state["item_ids"][i], "error": str(response)})
                else:
                    results.append(response.json())

            return {"results": results, "errors": errors if errors else None}
```

## API Client Patterns

### Pattern 1: Reusable API Client Class

```python
# modules/clients/example_api.py
import requests
from typing import Optional

class ExampleAPIClient:
    """Client for Example API."""

    def __init__(self, api_key: str, base_url: str = "https://api.example.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def get_user(self, user_id: str) -> dict:
        response = self.session.get(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()

    def search(self, query: str, filters: Optional[dict] = None) -> list[dict]:
        params = {"q": query}
        if filters:
            params.update(filters)

        response = self.session.get(f"{self.base_url}/search", params=params)
        response.raise_for_status()
        return response.json()["results"]

    def create_item(self, data: dict) -> dict:
        response = self.session.post(f"{self.base_url}/items", json=data)
        response.raise_for_status()
        return response.json()

# Use in nodes or tools
from modules.clients.example_api import ExampleAPIClient

class APINode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = ExampleAPIClient(api_key=os.getenv("EXAMPLE_API_KEY"))

    def execute(self, state: dict) -> dict:
        results = self.client.search(state["query"])
        return {"search_results": results}
```

### Pattern 2: GraphQL APIs

```python
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

class GraphQLNode(BaseNode):
    def __init__(self, endpoint: str, **kwargs):
        super().__init__(**kwargs)

        transport = RequestsHTTPTransport(
            url=endpoint,
            headers={"Authorization": f"Bearer {os.getenv('API_KEY')}"}
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def execute(self, state: dict) -> dict:
        query = gql('''
            query GetUser($userId: ID!) {
                user(id: $userId) {
                    name
                    email
                    posts {
                        title
                    }
                }
            }
        ''')

        result = self.client.execute(query, variable_values={"userId": state["user_id"]})
        return {"user_data": result}
```

### Pattern 3: Rate Limiting

```python
from time import sleep, time
from collections import deque

class RateLimitedAPIClient:
    """API client with rate limiting."""

    def __init__(self, api_key: str, max_requests: int = 10, time_window: int = 60):
        self.api_key = api_key
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_times = deque()

    def _wait_if_needed(self):
        """Implements sliding window rate limiting."""
        now = time()

        # Remove requests outside time window
        while self.request_times and self.request_times[0] < now - self.time_window:
            self.request_times.popleft()

        # Wait if at limit
        if len(self.request_times) >= self.max_requests:
            sleep_time = self.time_window - (now - self.request_times[0])
            if sleep_time > 0:
                sleep(sleep_time)

        self.request_times.append(time())

    def call_api(self, endpoint: str, **kwargs) -> dict:
        self._wait_if_needed()
        response = requests.get(f"https://api.example.com{endpoint}", **kwargs)
        response.raise_for_status()
        return response.json()
```

## Webhook Integration

### Pattern: Webhook Receiver Node

```python
class WebhookProcessorNode(BaseNode):
    """Processes incoming webhook data."""

    def execute(self, state: dict) -> dict:
        webhook_data = state.get("webhook_payload")

        # Validate webhook signature
        if not self.verify_signature(webhook_data, state.get("signature")):
            return {"error": "Invalid webhook signature"}

        # Process webhook event
        event_type = webhook_data.get("type")

        if event_type == "user.created":
            return self.handle_user_created(webhook_data)
        elif event_type == "order.completed":
            return self.handle_order_completed(webhook_data)
        else:
            return {"error": f"Unknown event type: {event_type}"}

    def verify_signature(self, payload: dict, signature: str) -> bool:
        """Verify HMAC signature."""
        import hmac
        import hashlib

        secret = os.getenv("WEBHOOK_SECRET")
        computed = hmac.new(
            secret.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed, signature)
```

## Error Handling & Retries

```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class RobustAPINode(BaseNode):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError))
    )
    def call_api_with_retry(self, url: str, **kwargs) -> dict:
        """API call with automatic retry."""
        response = requests.get(url, timeout=10, **kwargs)
        response.raise_for_status()
        return response.json()

    def execute(self, state: dict) -> dict:
        try:
            result = self.call_api_with_retry(
                "https://api.example.com/data",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return {"api_result": result}

        except requests.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                return {"error": "rate_limit", "retry_after": e.response.headers.get("Retry-After")}
            elif e.response.status_code >= 500:
                return {"error": "server_error", "status_code": e.response.status_code}
            else:
                return {"error": "client_error", "details": e.response.text}

        except requests.Timeout:
            return {"error": "timeout"}

        except Exception as e:
            self.log(f"Unexpected error: {e}")
            return {"error": "unexpected", "details": str(e)}
```

## Authentication Patterns

### Pattern 1: API Key
```python
headers = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}
```

### Pattern 2: OAuth2
```python
from requests_oauthlib import OAuth2Session

class OAuth2APINode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.oauth = OAuth2Session(
            client_id=os.getenv("OAUTH_CLIENT_ID"),
            token=self.get_token()
        )

    def get_token(self) -> dict:
        # Implement token refresh logic
        pass

    def execute(self, state: dict) -> dict:
        response = self.oauth.get("https://api.example.com/data")
        return {"data": response.json()}
```

### Pattern 3: JWT
```python
import jwt
from datetime import datetime, timedelta

def create_jwt_token(secret: str, user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, secret, algorithm="HS256")
```

## Common Mistakes

❌ **Hardcoded API keys**
```python
# ❌ Never do this
api_key = "sk-1234567890"

# ✅ Use environment variables
api_key = os.getenv("API_KEY")
```

❌ **No timeout**
```python
# ❌ Can hang forever
requests.get(url)

# ✅ Always set timeout
requests.get(url, timeout=10)
```

❌ **Not handling rate limits**
```python
# ❌ Will fail on 429 responses
# ✅ Implement rate limiting or exponential backoff
```

❌ **Synchronous in async context**
```python
# ❌ Blocks async execution
class AsyncNode(AsyncBaseNode):
    async def execute(self, state):
        result = requests.get(url)  # Blocking!

# ✅ Use async HTTP client
async def execute(self, state):
    async with httpx.AsyncClient() as client:
        result = await client.get(url)
```

## References
- Related: `../core/tools-integration.md` (creating tools for APIs)
- Related: `../advanced/error-handling-retry.md` (robust API error handling)
- Related: `mcp-adapter.md` (MCP-based API integration)
