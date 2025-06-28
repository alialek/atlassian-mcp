"""Zephyr Test Case operations mixin."""

import logging
from typing import Any

from mcp_atlassian.exceptions import MCPAtlassianError, MCPAtlassianNotFoundError
from mcp_atlassian.models.zephyr import ZephyrTestCase
from mcp_atlassian.zephyr.client import ZephyrClient
from mcp_atlassian.zephyr.protocols import ZephyrTestCaseOperationsProto

logger = logging.getLogger("mcp-atlassian.zephyr.testcase")


class ZephyrTestCaseMixin(
    ZephyrClient,
    ZephyrTestCaseOperationsProto,
):
    """Mixin providing Zephyr test case operations."""

    def get_testcase(self, test_case_key: str, fields: str | None = None) -> ZephyrTestCase:
        """Get a test case by key.
        
        Args:
            test_case_key: The test case key (e.g., 'JQA-T1234')
            fields: Optional comma-separated list of fields to include
            
        Returns:
            ZephyrTestCase object
            
        Raises:
            MCPAtlassianNotFoundError: If test case is not found
            MCPAtlassianError: If API request fails
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
                
            response = self.request(
                method="GET",
                url=f"/testcase/{test_case_key}",
                params=params
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(f"Test case {test_case_key} not found")
                
            response.raise_for_status()
            return ZephyrTestCase.from_api_response(response.json())
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to get test case {test_case_key}: {e}")
            raise MCPAtlassianError(f"Failed to get test case: {e}") from e

    def create_testcase(self, testcase_data: dict[str, Any]) -> str:
        """Create a new test case.
        
        Args:
            testcase_data: Test case data dictionary
            
        Returns:
            The key of the created test case
            
        Raises:
            MCPAtlassianError: If creation fails
        """
        try:
            response = self.request(
                method="POST",
                url="/testcase",
                json=testcase_data
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("key", "")
            
        except Exception as e:
            logger.error(f"Failed to create test case: {e}")
            raise MCPAtlassianError(f"Failed to create test case: {e}") from e

    def update_testcase(self, test_case_key: str, testcase_data: dict[str, Any]) -> None:
        """Update a test case.
        
        Args:
            test_case_key: The test case key to update
            testcase_data: Updated test case data
            
        Raises:
            MCPAtlassianNotFoundError: If test case is not found
            MCPAtlassianError: If update fails
        """
        try:
            response = self.request(
                method="PUT",
                url=f"/testcase/{test_case_key}",
                json=testcase_data
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(f"Test case {test_case_key} not found")
                
            response.raise_for_status()
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to update test case {test_case_key}: {e}")
            raise MCPAtlassianError(f"Failed to update test case: {e}") from e

    def delete_testcase(self, test_case_key: str) -> None:
        """Delete a test case.
        
        Args:
            test_case_key: The test case key to delete
            
        Raises:
            MCPAtlassianNotFoundError: If test case is not found
            MCPAtlassianError: If deletion fails
        """
        try:
            response = self.request(
                method="DELETE",
                url=f"/testcase/{test_case_key}"
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(f"Test case {test_case_key} not found")
                
            response.raise_for_status()
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to delete test case {test_case_key}: {e}")
            raise MCPAtlassianError(f"Failed to delete test case: {e}") from e

    def search_testcases(
        self,
        query: str | None = None,
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 200,
    ) -> list[ZephyrTestCase]:
        """Search for test cases.
        
        Args:
            query: TQL query string for filtering test cases
            fields: Optional comma-separated list of fields to include
            start_at: Offset for pagination
            max_results: Maximum number of results to return (default 200)
            
        Returns:
            List of ZephyrTestCase objects
            
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
                url="/testcase/search",
                params=params
            )
            
            response.raise_for_status()
            result = response.json()
            
            test_cases = []
            
            # Handle direct array response from Zephyr API
            if isinstance(result, list):
                test_case_data_list = result
            else:
                # Handle wrapped response (fallback)
                test_case_data_list = result.get("results", [])
            
            for test_case_data in test_case_data_list:
                try:
                    test_case = ZephyrTestCase.from_api_response(test_case_data)
                    test_cases.append(test_case)
                except Exception as e:
                    logger.warning(f"Failed to parse test case data: {e}")
                    continue
                    
            return test_cases
            
        except Exception as e:
            if isinstance(e, MCPAtlassianError):
                raise
            logger.error(f"Failed to search test cases: {e}")
            raise MCPAtlassianError(f"Failed to search test cases: {e}") from e

    def get_testcase_latest_result(self, test_case_key: str) -> dict[str, Any] | None:
        """Get the latest test result for a test case.
        
        Args:
            test_case_key: The test case key
            
        Returns:
            Latest test result data or None if no results found
            
        Raises:
            MCPAtlassianNotFoundError: If test case is not found
            MCPAtlassianError: If request fails
        """
        try:
            response = self.request(
                method="GET",
                url=f"/testcase/{test_case_key}/testresult/latest"
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(
                    f"Test case {test_case_key} not found or has no results"
                )
                
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to get latest result for test case {test_case_key}: {e}")
            raise MCPAtlassianError(f"Failed to get latest test result: {e}") from e 