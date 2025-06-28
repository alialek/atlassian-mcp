class MCPAtlassianAuthenticationError(Exception):
    """Raised when Atlassian API authentication fails (401/403)."""

    pass


class MCPAtlassianError(Exception):
    """Base exception for MCP Atlassian errors."""

    pass


class MCPAtlassianNotFoundError(MCPAtlassianError):
    """Raised when a requested resource is not found (404)."""

    pass
