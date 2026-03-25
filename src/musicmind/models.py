"""Pydantic models for Apple Music API responses and internal data."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """Response model for the health check tool."""

    status: str = Field(description="Server status")
    version: str = Field(description="Server version")
    has_developer_token: bool = Field(description="Whether a developer token can be generated")
    has_user_token: bool = Field(description="Whether a Music User Token is configured")
    storefront: str = Field(description="Configured storefront country code")
