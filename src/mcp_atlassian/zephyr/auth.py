"""Bearer token authentication for Zephyr API."""

import logging
from typing import Optional

from mcp_atlassian.exceptions import MCPAtlassianAuthenticationError

from .config import ZephyrConfig

logger = logging.getLogger("mcp-atlassian.zephyr.auth")


class ZephyrAuth:
    """Bearer token authentication handler for Zephyr API."""

    def __init__(self, config: ZephyrConfig) -> None:
        """Initialize Zephyr authentication.
        
        Args:
            config: Zephyr configuration containing API token
        """
        self.config = config

    def get_auth_headers(self, method: str, url: str) -> dict[str, str]:
        """Get authentication headers for Zephyr API request.
        
        Args:
            method: HTTP method (GET, POST, etc.) - not used for Bearer auth but kept for compatibility
            url: API endpoint URL - not used for Bearer auth but kept for compatibility
            
        Returns:
            Dictionary of headers including Authorization
            
        Raises:
            MCPAtlassianAuthenticationError: If API token is not configured
        """
        if not self.config.api_token:
            raise MCPAtlassianAuthenticationError(
                "Zephyr API token is required for authentication"
            )
        
        return {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json",
        }

    def validate_token_format(self) -> bool:
        """Validate that the API token has a reasonable format.
        
        Returns:
            True if token appears to be valid format, False otherwise
        """
        if not self.config.api_token:
            return False
        
        # Basic validation - token should be a non-empty string
        # Add more specific validation based on your Zephyr token format if needed
        token = self.config.api_token.strip()
        if len(token) < 10:  # Arbitrary minimum length
            logger.warning("Zephyr API token appears too short")
            return False
        
        return True 