"""Zephyr Test Plan operations mixin."""

import logging
from typing import Any

from mcp_atlassian.exceptions import MCPAtlassianError, MCPAtlassianNotFoundError
from mcp_atlassian.models.zephyr import ZephyrTestPlan
from mcp_atlassian.zephyr.client import ZephyrClient
from mcp_atlassian.zephyr.protocols import ZephyrTestPlanOperationsProto

logger = logging.getLogger("mcp-atlassian.zephyr.testplan")


class ZephyrTestPlanMixin(
    ZephyrClient,
    ZephyrTestPlanOperationsProto,
):
    """Mixin providing Zephyr test plan operations."""

    def get_testplan(self, test_plan_key: str, fields: str | None = None) -> ZephyrTestPlan:
        """Get a test plan by key.
        
        Args:
            test_plan_key: The test plan key (e.g., 'JQA-P1234')
            fields: Optional comma-separated list of fields to include
            
        Returns:
            ZephyrTestPlan object
            
        Raises:
            MCPAtlassianNotFoundError: If test plan is not found
            MCPAtlassianError: If API request fails
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
                
            response = self.request(
                method="GET",
                url=f"/testplan/{test_plan_key}",
                params=params
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(f"Test plan {test_plan_key} not found")
                
            response.raise_for_status()
            return ZephyrTestPlan.from_api_response(response.json())
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to get test plan {test_plan_key}: {e}")
            raise MCPAtlassianError(f"Failed to get test plan: {e}") from e

    def create_testplan(self, testplan_data: dict[str, Any]) -> str:
        """Create a new test plan.
        
        Args:
            testplan_data: Test plan data dictionary
            
        Returns:
            The key of the created test plan
            
        Raises:
            MCPAtlassianError: If creation fails
        """
        try:
            response = self.request(
                method="POST",
                url="/testplan",
                json=testplan_data
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("key", "")
            
        except Exception as e:
            logger.error(f"Failed to create test plan: {e}")
            raise MCPAtlassianError(f"Failed to create test plan: {e}") from e

    def update_testplan(self, test_plan_key: str, testplan_data: dict[str, Any]) -> None:
        """Update a test plan.
        
        Args:
            test_plan_key: The test plan key to update
            testplan_data: Updated test plan data
            
        Raises:
            MCPAtlassianNotFoundError: If test plan is not found
            MCPAtlassianError: If update fails
        """
        try:
            response = self.request(
                method="PUT",
                url=f"/testplan/{test_plan_key}",
                json=testplan_data
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(f"Test plan {test_plan_key} not found")
                
            response.raise_for_status()
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to update test plan {test_plan_key}: {e}")
            raise MCPAtlassianError(f"Failed to update test plan: {e}") from e

    def delete_testplan(self, test_plan_key: str) -> None:
        """Delete a test plan.
        
        Args:
            test_plan_key: The test plan key to delete
            
        Raises:
            MCPAtlassianNotFoundError: If test plan is not found
            MCPAtlassianError: If deletion fails
        """
        try:
            response = self.request(
                method="DELETE",
                url=f"/testplan/{test_plan_key}"
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(f"Test plan {test_plan_key} not found")
                
            response.raise_for_status()
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to delete test plan {test_plan_key}: {e}")
            raise MCPAtlassianError(f"Failed to delete test plan: {e}") from e

    def search_testplans(
        self,
        query: str | None = None,
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 200,
    ) -> list[ZephyrTestPlan]:
        """Search for test plans.
        
        Args:
            query: TQL query string for filtering test plans
            fields: Optional comma-separated list of fields to include
            start_at: Offset for pagination
            max_results: Maximum number of results to return (default 200)
            
        Returns:
            List of ZephyrTestPlan objects
            
        Raises:
            MCPAtlassianError: If search fails
        """
        try:
            params = {}
            if query:
                params["query"] = query
            if fields:
                params["fields"] = fields
            if start_at > 0:
                params["startAt"] = start_at
            if max_results != 200:
                params["maxResults"] = max_results
                
            response = self.request(
                method="GET",
                url="/testplan/search",
                params=params
            )
            
            response.raise_for_status()
            result = response.json()
            
            test_plans = []
            
            # Handle direct array response from Zephyr API
            if isinstance(result, list):
                test_plan_data_list = result
            else:
                # Handle wrapped response (fallback)
                test_plan_data_list = result.get("results", [])
            
            for test_plan_data in test_plan_data_list:
                try:
                    test_plan = ZephyrTestPlan.from_api_response(test_plan_data)
                    test_plans.append(test_plan)
                except Exception as e:
                    logger.warning(f"Failed to parse test plan data: {e}")
                    continue
                    
            return test_plans
            
        except Exception as e:
            if isinstance(e, MCPAtlassianError):
                raise
            logger.error(f"Failed to search test plans: {e}")
            raise MCPAtlassianError(f"Failed to search test plans: {e}") from e 