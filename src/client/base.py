"""Base HTTP client with retry and error handling."""

from abc import ABC, abstractmethod
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


class BaseAPIClient(ABC):
    """Abstract base class for API clients."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 10, max_retries: int = 3):
        """Initialize the base client."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _make_request(self, method: str, args: list[Any], timeout: int | None = None) -> Any:
        """Make HTTP POST request to API with retry logic."""
        payload = {"method": method, "args": args}
        timeout = timeout or self.timeout

        try:
            response = self.session.post(f"{self.base_url}/api", json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise ConnectionError(f"Request timeout after {timeout}s")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Failed to connect to {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    @abstractmethod
    def health_check(self) -> bool:
        """Check if API is accessible."""
        pass
