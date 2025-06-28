"""Zephyr test run models."""

from typing import Any

from mcp_atlassian.models.base import ApiModel, TimestampMixin
from mcp_atlassian.models.constants import EMPTY_STRING


class ZephyrTestRun(ApiModel, TimestampMixin):
    """Model representing a Zephyr test run."""

    key: str = EMPTY_STRING
    name: str = EMPTY_STRING
    project_key: str = EMPTY_STRING
    status: str = EMPTY_STRING
    folder: str | None = None
    owner: str | None = None
    version: str | None = None
    iteration: str | None = None
    environment: str | None = None
    planned_start_date: str | None = None
    planned_end_date: str | None = None
    actual_start_date: str | None = None
    actual_end_date: str | None = None
    test_plan_key: str | None = None
    issue_key: str | None = None
    items: list[dict[str, Any]] = []
    custom_fields: dict[str, Any] = {}
    issue_links: list[str] = []
    created_on: str = EMPTY_STRING
    last_modified_on: str = EMPTY_STRING
    created_by: str | None = None
    last_modified_by: str | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "ZephyrTestRun":
        """Create ZephyrTestRun from Zephyr API response.
        
        Args:
            data: API response data
            **kwargs: Additional context parameters
            
        Returns:
            ZephyrTestRun instance
        """
        return cls(
            key=data.get("key", EMPTY_STRING),
            name=data.get("name", EMPTY_STRING),
            project_key=data.get("projectKey", EMPTY_STRING),
            status=data.get("status", EMPTY_STRING),
            folder=data.get("folder"),
            owner=data.get("owner"),
            version=data.get("version"),
            iteration=data.get("iteration"),
            environment=data.get("environment"),
            planned_start_date=data.get("plannedStartDate"),
            planned_end_date=data.get("plannedEndDate"),
            actual_start_date=data.get("actualStartDate"),
            actual_end_date=data.get("actualEndDate"),
            test_plan_key=data.get("testPlanKey"),
            issue_key=data.get("issueKey"),
            items=data.get("items", []),
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
            Dictionary with essential test run fields
        """
        result = {
            "key": self.key,
            "name": self.name,
            "project_key": self.project_key,
            "status": self.status,
            "folder": self.folder,
            "items_count": len(self.items),
            "created_on": self.format_timestamp(self.created_on),
            "last_modified_on": self.format_timestamp(self.last_modified_on),
        }
        
        # Add optional fields if present
        if self.owner:
            result["owner"] = self.owner
        if self.version:
            result["version"] = self.version
        if self.iteration:
            result["iteration"] = self.iteration
        if self.environment:
            result["environment"] = self.environment
        if self.planned_start_date:
            result["planned_start_date"] = self.format_timestamp(self.planned_start_date)
        if self.planned_end_date:
            result["planned_end_date"] = self.format_timestamp(self.planned_end_date)
        if self.actual_start_date:
            result["actual_start_date"] = self.format_timestamp(self.actual_start_date)
        if self.actual_end_date:
            result["actual_end_date"] = self.format_timestamp(self.actual_end_date)
        if self.test_plan_key:
            result["test_plan_key"] = self.test_plan_key
        if self.issue_key:
            result["issue_key"] = self.issue_key
        if self.items:
            result["items"] = self.items
        if self.custom_fields:
            result["custom_fields"] = self.custom_fields
        if self.issue_links:
            result["issue_links"] = self.issue_links
        if self.created_by:
            result["created_by"] = self.created_by
        if self.last_modified_by:
            result["last_modified_by"] = self.last_modified_by
            
        return result 