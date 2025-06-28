"""Zephyr Test Run operations mixin."""

import logging
from typing import Any

from mcp_atlassian.exceptions import MCPAtlassianError, MCPAtlassianNotFoundError
from mcp_atlassian.models.zephyr import ZephyrTestResult, ZephyrTestRun
from mcp_atlassian.zephyr.client import ZephyrClient
from mcp_atlassian.zephyr.protocols import ZephyrTestResultOperationsProto, ZephyrTestRunOperationsProto

logger = logging.getLogger("mcp-atlassian.zephyr.testrun")


class ZephyrTestRunMixin(
    ZephyrClient,
    ZephyrTestRunOperationsProto,
    ZephyrTestResultOperationsProto,
):
    """Mixin providing Zephyr test run operations."""

    def get_testrun(self, test_run_key: str, fields: str | None = None) -> ZephyrTestRun:
        """Get a test run by key.
        
        Args:
            test_run_key: The test run key (e.g., 'JQA-R1234')
            fields: Optional comma-separated list of fields to include
            
        Returns:
            ZephyrTestRun object
            
        Raises:
            MCPAtlassianNotFoundError: If test run is not found
            MCPAtlassianError: If API request fails
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
                
            response = self.request(
                method="GET",
                url=f"/testrun/{test_run_key}",
                params=params
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(f"Test run {test_run_key} not found")
                
            response.raise_for_status()
            return ZephyrTestRun.from_api_response(response.json())
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to get test run {test_run_key}: {e}")
            raise MCPAtlassianError(f"Failed to get test run: {e}") from e

    def create_testrun(self, testrun_data: dict[str, Any]) -> str:
        """Create a new test run.
        
        Args:
            testrun_data: Test run data dictionary
            
        Returns:
            The key of the created test run
            
        Raises:
            MCPAtlassianError: If creation fails
        """
        try:
            response = self.request(
                method="POST",
                url="/testrun",
                json=testrun_data
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("key", "")
            
        except Exception as e:
            logger.error(f"Failed to create test run: {e}")
            raise MCPAtlassianError(f"Failed to create test run: {e}") from e

    def delete_testrun(self, test_run_key: str) -> None:
        """Delete a test run.
        
        Args:
            test_run_key: The test run key to delete
            
        Raises:
            MCPAtlassianNotFoundError: If test run is not found
            MCPAtlassianError: If deletion fails
        """
        try:
            response = self.request(
                method="DELETE",
                url=f"/testrun/{test_run_key}"
            )
            
            if response.status_code == 404:
                raise MCPAtlassianNotFoundError(f"Test run {test_run_key} not found")
                
            response.raise_for_status()
            
        except Exception as e:
            if isinstance(e, (MCPAtlassianNotFoundError, MCPAtlassianError)):
                raise
            logger.error(f"Failed to delete test run {test_run_key}: {e}")
            raise MCPAtlassianError(f"Failed to delete test run: {e}") from e

    def search_testruns(
        self,
        query: str | None = None,
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 200,
    ) -> list[ZephyrTestRun]:
        """Search for test runs.
        
        Args:
            query: TQL query string for filtering test runs
            fields: Optional comma-separated list of fields to include
            start_at: Offset for pagination
            max_results: Maximum number of results to return (default 200)
            
        Returns:
            List of ZephyrTestRun objects
            
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
                url="/testrun/search",
                params=params
            )
            
            response.raise_for_status()
            result = response.json()
            
            test_runs = []
            
            # Handle direct array response from Zephyr API
            if isinstance(result, list):
                test_run_data_list = result
            else:
                # Handle wrapped response (fallback)
                test_run_data_list = result.get("results", [])
            
            for test_run_data in test_run_data_list:
                try:
                    test_run = ZephyrTestRun.from_api_response(test_run_data)
                    test_runs.append(test_run)
                except Exception as e:
                    logger.warning(f"Failed to parse test run data: {e}")
                    continue
                    
            return test_runs
            
        except Exception as e:
            if isinstance(e, MCPAtlassianError):
                raise
            logger.error(f"Failed to search test runs: {e}")
            raise MCPAtlassianError(f"Failed to search test runs: {e}") from e

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