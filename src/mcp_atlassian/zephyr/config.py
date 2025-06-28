"""Zephyr configuration management."""

import logging
import os
from dataclasses import dataclass
from typing import Optional

from mcp_atlassian.utils.logging import log_config_param

logger = logging.getLogger("mcp-atlassian.zephyr.config")


@dataclass(frozen=True)
class ZephyrConfig:
    """Configuration for Zephyr test management integration."""

    # Required settings
    api_token: str
    base_url: str
    
    # Optional settings
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Proxy settings
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    socks_proxy: Optional[str] = None
    no_proxy: Optional[str] = None
    
    # SSL verification
    ssl_verify: bool = True
    
    # Custom headers
    custom_headers: Optional[dict[str, str]] = None

    @classmethod
    def from_env(cls) -> "ZephyrConfig":
        """Create ZephyrConfig from environment variables."""
        
        # Required settings
        api_token = os.getenv("ZEPHYR_API_TOKEN")
        base_url = os.getenv("ZEPHYR_BASE_URL")
        
        if not api_token:
            raise ValueError(
                "Zephyr configuration requires ZEPHYR_API_TOKEN environment variable"
            )
            
        if not base_url:
            raise ValueError(
                "Zephyr configuration requires ZEPHYR_BASE_URL environment variable"
            )
        
        # Optional settings with defaults
        timeout = int(os.getenv("ZEPHYR_TIMEOUT", "30"))
        max_retries = int(os.getenv("ZEPHYR_MAX_RETRIES", "3"))
        retry_delay = float(os.getenv("ZEPHYR_RETRY_DELAY", "1.0"))
        
        # Proxy settings
        http_proxy = os.getenv("ZEPHYR_HTTP_PROXY")
        https_proxy = os.getenv("ZEPHYR_HTTPS_PROXY")
        socks_proxy = os.getenv("ZEPHYR_SOCKS_PROXY")
        no_proxy = os.getenv("ZEPHYR_NO_PROXY")
        
        # SSL verification
        ssl_verify = os.getenv("ZEPHYR_SSL_VERIFY", "true").lower() not in ("false", "0", "no", "off")
        
        # Custom headers
        custom_headers = None
        if os.getenv("ZEPHYR_CUSTOM_HEADERS"):
            try:
                import json
                custom_headers = json.loads(os.getenv("ZEPHYR_CUSTOM_HEADERS", "{}"))
            except (json.JSONDecodeError, TypeError):
                logger.warning("Invalid ZEPHYR_CUSTOM_HEADERS format, ignoring")
        
        config = cls(
            api_token=api_token,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            http_proxy=http_proxy,
            https_proxy=https_proxy,
            socks_proxy=socks_proxy,
            no_proxy=no_proxy,
            ssl_verify=ssl_verify,
            custom_headers=custom_headers,
        )
        
        # Log configuration (mask sensitive data)
        log_config_param(logger, "Zephyr", "BASE_URL", config.base_url)
        log_config_param(logger, "Zephyr", "API_TOKEN", config.api_token[:8] + "...", sensitive=True)
        log_config_param(logger, "Zephyr", "TIMEOUT", str(config.timeout))
        log_config_param(logger, "Zephyr", "SSL_VERIFY", str(config.ssl_verify))
        
        return config

    def is_auth_configured(self) -> bool:
        """Check if authentication is properly configured."""
        return bool(self.api_token and self.base_url)

    @property
    def is_configured(self) -> bool:
        """Check if Zephyr is properly configured."""
        return self.is_auth_configured() 