"""Zephyr test case models."""

from typing import Any

from mcp_atlassian.models.base import ApiModel, TimestampMixin
from mcp_atlassian.models.constants import EMPTY_STRING


class ZephyrTestCase(ApiModel, TimestampMixin):
    """Model representing a Zephyr test case."""

    key: str = EMPTY_STRING
    name: str = EMPTY_STRING
    project_key: str = EMPTY_STRING
    status: str = EMPTY_STRING
    priority: str = EMPTY_STRING
    component: str | None = None
    owner: str | None = None
    estimated_time: int | None = None
    folder: str | None = None
    labels: list[str] = []
    objective: str | None = None
    precondition: str | None = None
    test_script: dict[str, Any] | None = None
    parameters: dict[str, Any] | None = None
    custom_fields: dict[str, Any] = {}
    issue_links: list[str] = []
    created_on: str = EMPTY_STRING
    last_modified_on: str = EMPTY_STRING
    created_by: str | None = None
    last_modified_by: str | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "ZephyrTestCase":
        """Create ZephyrTestCase from Zephyr API response.
        
        Args:
            data: API response data
            **kwargs: Additional context parameters
            
        Returns:
            ZephyrTestCase instance
        """
        return cls(
            key=data.get("key", EMPTY_STRING),
            name=data.get("name", EMPTY_STRING),
            project_key=data.get("projectKey", EMPTY_STRING),
            status=data.get("status", EMPTY_STRING),
            priority=data.get("priority", EMPTY_STRING),
            component=data.get("component"),
            owner=data.get("owner"),
            estimated_time=data.get("estimatedTime"),
            folder=data.get("folder"),
            labels=data.get("labels", []),
            objective=data.get("objective"),
            precondition=data.get("precondition"),
            test_script=data.get("testScript"),
            parameters=data.get("parameters"),
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
            Dictionary with essential test case fields
        """
        result = {
            "key": self.key,
            "name": self.name,
            "project_key": self.project_key,
            "status": self.status,
            "priority": self.priority,
            "folder": self.folder,
            "labels": self.labels,
            "created_on": self.format_timestamp(self.created_on),
            "last_modified_on": self.format_timestamp(self.last_modified_on),
        }
        
        # Add optional fields if present
        if self.component:
            result["component"] = self.component
        if self.owner:
            result["owner"] = self.owner
        if self.estimated_time is not None:
            result["estimated_time"] = self.estimated_time
        if self.objective:
            result["objective"] = self.objective
        if self.precondition:
            result["precondition"] = self.precondition
        if self.test_script:
            result["test_script"] = self.test_script
        if self.parameters:
            result["parameters"] = self.parameters
        if self.custom_fields:
            result["custom_fields"] = self.custom_fields
        if self.issue_links:
            result["issue_links"] = self.issue_links
        if self.created_by:
            result["created_by"] = self.created_by
        if self.last_modified_by:
            result["last_modified_by"] = self.last_modified_by
            
        return result 