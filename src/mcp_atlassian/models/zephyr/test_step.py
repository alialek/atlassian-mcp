"""Zephyr test step models."""

from typing import Any

from mcp_atlassian.models.base import ApiModel


class TestStep(ApiModel):
    """Represents a test step in Zephyr."""

    order_id: int
    step: str
    data: str = ""
    result: str = ""
    step_id: int | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "TestStep":
        """Create TestStep from Zephyr API response.
        
        Args:
            data: API response data
            **kwargs: Additional context parameters
            
        Returns:
            TestStep instance
        """
        return cls(
            order_id=data.get("orderId", 0),
            step=data.get("step", ""),
            data=data.get("data", ""),
            result=data.get("result", ""),
            step_id=data.get("id"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API responses.
        
        Returns:
            Dictionary with essential test step fields
        """
        result = {
            "order_id": self.order_id,
            "step": self.step,
            "data": self.data,
            "result": self.result,
        }
        
        if self.step_id is not None:
            result["step_id"] = self.step_id
            
        return result


class TestStepRequest(ApiModel):
    """Request model for creating test steps."""

    step: str
    data: str | None = None
    result: str | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "TestStepRequest":
        """Create TestStepRequest from API response.
        
        Args:
            data: API response data
            **kwargs: Additional context parameters
            
        Returns:
            TestStepRequest instance
        """
        return cls(
            step=data.get("step", ""),
            data=data.get("data"),
            result=data.get("result"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API requests.
        
        Returns:
            Dictionary with test step request fields
        """
        result = {"step": self.step}
        
        if self.data is not None:
            result["data"] = self.data
            
        if self.result is not None:
            result["result"] = self.result
            
        return result


class ZephyrTestSteps(ApiModel):
    """Collection of test steps for a test case."""

    issue_id: str
    project_id: str
    steps: list[TestStep]

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "ZephyrTestSteps":
        """Create ZephyrTestSteps from Zephyr API response.
        
        Args:
            data: API response data containing stepBeanCollection
            **kwargs: Additional context parameters (issue_id, project_id)
            
        Returns:
            ZephyrTestSteps instance
        """
        issue_id = kwargs.get("issue_id", "")
        project_id = kwargs.get("project_id", "")
        
        # Extract steps from stepBeanCollection
        step_data = data.get("stepBeanCollection", [])
        steps = []
        
        for step_info in step_data:
            try:
                step = TestStep.from_api_response(step_info)
                steps.append(step)
            except Exception:
                # Skip invalid steps
                continue
        
        return cls(
            issue_id=issue_id,
            project_id=project_id,
            steps=steps,
        )

    @classmethod
    def from_zephyr_response(cls, data: dict[str, Any], issue_id: str, project_id: str) -> "ZephyrTestSteps":
        """Create ZephyrTestSteps from Zephyr API response.
        
        Args:
            data: API response data containing stepBeanCollection
            issue_id: JIRA issue ID
            project_id: JIRA project ID
            
        Returns:
            ZephyrTestSteps instance
        """
        return cls.from_api_response(data, issue_id=issue_id, project_id=project_id)

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API responses.
        
        Returns:
            Dictionary with test steps collection
        """
        return {
            "issue_id": self.issue_id,
            "project_id": self.project_id,
            "total_steps": len(self.steps),
            "steps": [step.to_simplified_dict() for step in self.steps],
        } 