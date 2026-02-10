"""Base HTTP client with retry and error handling."""

from abc import ABC, abstractmethod
from typing import Any

import httpx
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from ..utils.errors import (
    APIError,
    AuthenticationError,
)
from ..utils.errors import (
    ConnectionError as LogseqConnectionError,
)


class BaseAPIClient(ABC):
    """Abstract base class for API clients."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 10, max_retries: int = 3):
        """Initialize the base client."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    async def _make_request(self, method: str, args: list[Any], timeout: int | None = None) -> Any:
        """Make HTTP POST request to API with retry logic."""
        payload = {"method": method, "args": args}
        timeout = timeout or self.timeout

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        ):
            with attempt:
                try:
                    response = await self._client.post("/api", json=payload, timeout=timeout)
                except httpx.TimeoutException as exc:
                    raise LogseqConnectionError(f"Request timeout after {timeout}s") from exc
                except httpx.NetworkError as exc:
                    raise LogseqConnectionError(f"Failed to connect to {self.base_url}") from exc

                if response.status_code in {401, 403}:
                    raise AuthenticationError(f"HTTP {response.status_code}")

                if response.status_code >= 400:
                    body = response.text[:500] if response.text else ""
                    raise APIError(f"HTTP {response.status_code}: {body}")

                try:
                    return response.json()
                except ValueError as exc:
                    raise APIError("Invalid JSON response from Logseq API") from exc

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if API is accessible."""
        pass

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
