"""Zephyr test result models."""

from typing import Any

from mcp_atlassian.models.base import ApiModel, TimestampMixin
from mcp_atlassian.models.constants import EMPTY_STRING


class ZephyrTestResult(ApiModel, TimestampMixin):
    """Model representing a Zephyr test result."""

    id: int | None = None
    test_case_key: str = EMPTY_STRING
    project_key: str = EMPTY_STRING
    status: str = EMPTY_STRING
    environment: str | None = None
    executed_by: str | None = None
    actual_start_date: str | None = None
    actual_end_date: str | None = None
    comment: str | None = None
    test_run_key: str | None = None
    custom_fields: dict[str, Any] = {}
    steps: list[dict[str, Any]] = []
    attachments: list[dict[str, Any]] = []
    created_on: str = EMPTY_STRING
    last_modified_on: str = EMPTY_STRING

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "ZephyrTestResult":
        """Create ZephyrTestResult from Zephyr API response.
        
        Args:
            data: API response data
            **kwargs: Additional context parameters
            
        Returns:
            ZephyrTestResult instance
        """
        return cls(
            id=data.get("id"),
            test_case_key=data.get("testCaseKey", EMPTY_STRING),
            project_key=data.get("projectKey", EMPTY_STRING),
            status=data.get("status", EMPTY_STRING),
            environment=data.get("environment"),
            executed_by=data.get("executedBy"),
            actual_start_date=data.get("actualStartDate"),
            actual_end_date=data.get("actualEndDate"),
            comment=data.get("comment"),
            test_run_key=data.get("testRunKey"),
            custom_fields=data.get("customFields", {}),
            steps=data.get("steps", []),
            attachments=data.get("attachments", []),
            created_on=data.get("createdOn", EMPTY_STRING),
            last_modified_on=data.get("lastModifiedOn", EMPTY_STRING),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API responses.
        
        Returns:
            Dictionary with essential test result fields
        """
        result = {
            "test_case_key": self.test_case_key,
            "project_key": self.project_key,
            "status": self.status,
            "executed_by": self.executed_by,
            "steps_count": len(self.steps),
            "attachments_count": len(self.attachments),
            "created_on": self.format_timestamp(self.created_on),
            "last_modified_on": self.format_timestamp(self.last_modified_on),
        }
        
        # Add optional fields if present
        if self.id is not None:
            result["id"] = self.id
        if self.environment:
            result["environment"] = self.environment
        if self.actual_start_date:
            result["actual_start_date"] = self.format_timestamp(self.actual_start_date)
        if self.actual_end_date:
            result["actual_end_date"] = self.format_timestamp(self.actual_end_date)
        if self.comment:
            result["comment"] = self.comment
        if self.test_run_key:
            result["test_run_key"] = self.test_run_key
        if self.custom_fields:
            result["custom_fields"] = self.custom_fields
        if self.steps:
            result["steps"] = self.steps
        if self.attachments:
            result["attachments"] = self.attachments
            
        return result 