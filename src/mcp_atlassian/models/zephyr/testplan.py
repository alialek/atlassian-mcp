"""Zephyr test plan models."""

from typing import Any

from mcp_atlassian.models.base import ApiModel, TimestampMixin
from mcp_atlassian.models.constants import EMPTY_STRING


class ZephyrTestPlan(ApiModel, TimestampMixin):
    """Model representing a Zephyr test plan."""

    key: str = EMPTY_STRING
    name: str = EMPTY_STRING
    project_key: str = EMPTY_STRING
    status: str = EMPTY_STRING
    folder: str | None = None
    owner: str | None = None
    labels: list[str] = []
    objective: str | None = None
    test_runs: list[dict[str, Any]] = []
    custom_fields: dict[str, Any] = {}
    issue_links: list[str] = []
    created_on: str = EMPTY_STRING
    last_modified_on: str = EMPTY_STRING
    created_by: str | None = None
    last_modified_by: str | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "ZephyrTestPlan":
        """Create ZephyrTestPlan from Zephyr API response.
        
        Args:
            data: API response data
            **kwargs: Additional context parameters
            
        Returns:
            ZephyrTestPlan instance
        """
        return cls(
            key=data.get("key", EMPTY_STRING),
            name=data.get("name", EMPTY_STRING),
            project_key=data.get("projectKey", EMPTY_STRING),
            status=data.get("status", EMPTY_STRING),
            folder=data.get("folder"),
            owner=data.get("owner"),
            labels=data.get("labels", []),
            objective=data.get("objective"),
            test_runs=data.get("testRuns", []),
            custom_fields=data.get("customFields", {}),
            issue_links=data.get("issueLinks", []),
            created_on=data.get("createdOn", EMPTY_STRING),
            last_modified_on=data.get("lastModifiedOn", EMPTY_STRING),
            created_by=data.get("createdBy"),
            last_modified_by=data.get("lastModifiedBy"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API responses.
        
        Returns:
            Dictionary with essential test plan fields
        """
        result = {
            "key": self.key,
            "name": self.name,
            "project_key": self.project_key,
            "status": self.status,
            "folder": self.folder,
            "labels": self.labels,
            "test_runs_count": len(self.test_runs),
            "created_on": self.format_timestamp(self.created_on),
            "last_modified_on": self.format_timestamp(self.last_modified_on),
        }
        
        # Add optional fields if present
        if self.owner:
            result["owner"] = self.owner
        if self.objective:
            result["objective"] = self.objective
        if self.test_runs:
            result["test_runs"] = self.test_runs
        if self.custom_fields:
            result["custom_fields"] = self.custom_fields
        if self.issue_links:
            result["issue_links"] = self.issue_links
        if self.created_by:
            result["created_by"] = self.created_by
        if self.last_modified_by:
            result["last_modified_by"] = self.last_modified_by
            
        return result 