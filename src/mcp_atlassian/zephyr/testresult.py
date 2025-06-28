"""Zephyr Test Result operations mixin."""

import logging
from typing import Any

from mcp_atlassian.exceptions import MCPAtlassianError, MCPAtlassianNotFoundError
from mcp_atlassian.models.zephyr import ZephyrTestResult
from mcp_atlassian.zephyr.client import ZephyrClient
from mcp_atlassian.zephyr.protocols import ZephyrTestResultOperationsProto

logger = logging.getLogger("mcp-atlassian.zephyr.testresult")


class ZephyrTestResultMixin(
    ZephyrClient,
    ZephyrTestResultOperationsProto,
):
    """Mixin providing Zephyr test result operations."""

    def create_testresult(self, testresult_data: dict[str, Any]) -> int:
        """Create a new test result for a test case.
        
        Args:
            testresult_data: Test result data dictionary
            
        Returns:
            ID of the created test result
            
        Raises:
            MCPAtlassianError: If creation fails
        """
        try:
            response = self.request(
                method="POST",
                url="/testresult",
                json=testresult_data
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("id", 0)
            
        except Exception as e:
            logger.error(f"Failed to create test result: {e}")
            raise MCPAtlassianError(f"Failed to create test result: {e}") from e

    def get_testcase_latest_result(self, test_case_key: str) -> ZephyrTestResult | None:
        """Get the latest test result for a test case.
        
        Args:
            test_case_key: The test case key
            
        Returns:
            ZephyrTestResult object or None if no results found
            
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
                return None
                
            response.raise_for_status()
            result_data = response.json()
            return ZephyrTestResult.from_api_response(result_data)
            
        except Exception as e:
            if isinstance(e, MCPAtlassianError):
                raise
            logger.error(f"Failed to get latest result for test case {test_case_key}: {e}")
            raise MCPAtlassianError(f"Failed to get latest test result: {e}") from e

    def get_testrun_results(self, test_run_key: str) -> list[ZephyrTestResult]:
        """Get all test results for a test run.
        
        Args:
            test_run_key: The test run key
            
        Returns:
            List of ZephyrTestResult objects
            
        Raises:
            MCPAtlassianNotFoundError: If test run is not found
            MCPAtlassianError: If request fails
        """
        try:
            response = self.request(
                method="GET",
                url=f"/testrun/{test_run_key}/testresults"
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(f"Test run {test_run_key} not found")
                
            response.raise_for_status()
            result = response.json()
            
            test_results = []
            
            # Handle direct array response from Zephyr API
            if isinstance(result, list):
                result_data_list = result
            else:
                # Handle wrapped response (fallback)
                result_data_list = result.get("results", [])
            
            for result_data in result_data_list:
                try:
                    test_result = ZephyrTestResult.from_api_response(result_data)
                    test_results.append(test_result)
                except Exception as e:
                    logger.warning(f"Failed to parse test result data: {e}")
                    continue
                    
            return test_results
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to get test results for test run {test_run_key}: {e}")
            raise MCPAtlassianError(f"Failed to get test run results: {e}") from e

    def create_testrun_result(
        self,
        test_run_key: str,
        test_case_key: str,
        testresult_data: dict[str, Any],
        environment: str | None = None,
        user_key: str | None = None,
    ) -> int:
        """Create a test result within a test run.
        
        Args:
            test_run_key: The test run key
            test_case_key: The test case key
            testresult_data: Test result data
            environment: Optional environment filter
            user_key: Optional user key filter
            
        Returns:
            ID of the created test result
            
        Raises:
            MCPAtlassianError: If creation fails
        """
        try:
            params = {}
            if environment:
                params["environment"] = environment
            if user_key:
                params["userKey"] = user_key
                
            response = self.request(
                method="POST",
                url=f"/testrun/{test_run_key}/testcase/{test_case_key}/testresult",
                json=testresult_data,
                params=params
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("id", 0)
            
        except Exception as e:
            logger.error(f"Failed to create test result for {test_case_key} in {test_run_key}: {e}")
            raise MCPAtlassianError(f"Failed to create test result: {e}") from e

    def update_testrun_result(
        self,
        test_run_key: str,
        test_case_key: str,
        testresult_data: dict[str, Any],
        environment: str | None = None,
        user_key: str | None = None,
    ) -> int:
        """Update the latest test result within a test run.
        
        Args:
            test_run_key: The test run key
            test_case_key: The test case key
            testresult_data: Updated test result data
            environment: Optional environment filter
            user_key: Optional user key filter
            
        Returns:
            ID of the updated test result
            
        Raises:
            MCPAtlassianError: If update fails
        """
        try:
            params = {}
            if environment:
                params["environment"] = environment
            if user_key:
                params["userKey"] = user_key
                
            response = self.request(
                method="PUT",
                url=f"/testrun/{test_run_key}/testcase/{test_case_key}/testresult",
                json=testresult_data,
                params=params
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("id", 0)
            
        except Exception as e:
            logger.error(f"Failed to update test result for {test_case_key} in {test_run_key}: {e}")
            raise MCPAtlassianError(f"Failed to update test result: {e}") from e

    def create_bulk_testrun_results(
        self,
        test_run_key: str,
        testresults_data: list[dict[str, Any]],
        environment: str | None = None,
        user_key: str | None = None,
    ) -> list[int]:
        """Create multiple test results within a test run.
        
        Args:
            test_run_key: The test run key
            testresults_data: List of test result data dictionaries
            environment: Optional environment filter
            user_key: Optional user key filter
            
        Returns:
            List of IDs for the created test results
            
        Raises:
            MCPAtlassianError: If creation fails
        """
        try:
            params = {}
            if environment:
                params["environment"] = environment
            if user_key:
                params["userKey"] = user_key
                
            response = self.request(
                method="POST",
                url=f"/testrun/{test_run_key}/testresults",
                json=testresults_data,
                params=params
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("ids", [])
            
        except Exception as e:
            logger.error(f"Failed to create bulk test results for {test_run_key}: {e}")
            raise MCPAtlassianError(f"Failed to create bulk test results: {e}") from e 