"""Configuration management using Pydantic Settings."""

from importlib.metadata import version as _pkg_version

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_version() -> str:
    try:
        return _pkg_version("logseq-mcp")
    except Exception:
        return "0.0.0"


class LogseqSettings(BaseSettings):
    """Logseq MCP Server settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="LOGSEQ_", extra="ignore"
    )

    # API Configuration
    api_token: str | None = Field(default=None, description="Logseq API authorization token")
    api_url: str = Field(default="http://localhost:12315", description="Logseq API base URL")
    api_timeout: int = Field(default=10, description="API request timeout in seconds")
    api_max_retries: int = Field(default=3, description="Maximum number of API retry attempts")

    # Server Configuration
    server_name: str = Field(default="logseq-mcp")
    server_version: str = Field(default_factory=_get_version)

    # Feature Flags
    enable_advanced_queries: bool = Field(default=True)
    enable_git_operations: bool = Field(default=False)
    enable_asset_management: bool = Field(default=False)


# Global settings instance
settings = LogseqSettings()
