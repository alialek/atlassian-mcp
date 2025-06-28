"""Protocol interfaces for Zephyr operations."""

from typing import Any, Protocol

from mcp_atlassian.models.zephyr import (
    ZephyrTestCase,
    ZephyrTestPlan,
    ZephyrTestResult,
    ZephyrTestRun,
)


class ZephyrTestCaseOperationsProto(Protocol):
    """Protocol for Zephyr test case operations."""

    def get_testcase(self, test_case_key: str, fields: str | None = None) -> ZephyrTestCase:
        """Get a test case by key."""
        ...

    def create_testcase(self, testcase_data: dict[str, Any]) -> str:
        """Create a new test case."""
        ...

    def update_testcase(self, test_case_key: str, testcase_data: dict[str, Any]) -> None:
        """Update a test case."""
        ...

    def delete_testcase(self, test_case_key: str) -> None:
        """Delete a test case."""
        ...

    def search_testcases(
        self,
        query: str | None = None,
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 200,
    ) -> list[ZephyrTestCase]:
        """Search for test cases."""
        ...


class ZephyrTestPlanOperationsProto(Protocol):
    """Protocol for Zephyr test plan operations."""

    def get_testplan(self, test_plan_key: str, fields: str | None = None) -> ZephyrTestPlan:
        """Get a test plan by key."""
        ...

    def create_testplan(self, testplan_data: dict[str, Any]) -> str:
        """Create a new test plan."""
        ...

    def update_testplan(self, test_plan_key: str, testplan_data: dict[str, Any]) -> None:
        """Update a test plan."""
        ...

    def delete_testplan(self, test_plan_key: str) -> None:
        """Delete a test plan."""
        ...

    def search_testplans(
        self,
        query: str | None = None,
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 200,
    ) -> list[ZephyrTestPlan]:
        """Search for test plans."""
        ...


class ZephyrTestRunOperationsProto(Protocol):
    """Protocol for Zephyr test run operations."""

    def get_testrun(self, test_run_key: str, fields: str | None = None) -> ZephyrTestRun:
        """Get a test run by key."""
        ...

    def create_testrun(self, testrun_data: dict[str, Any]) -> str:
        """Create a new test run."""
        ...

    def delete_testrun(self, test_run_key: str) -> None:
        """Delete a test run."""
        ...

    def search_testruns(
        self,
        query: str | None = None,
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 200,
    ) -> list[ZephyrTestRun]:
        """Search for test runs."""
        ...


class ZephyrTestResultOperationsProto(Protocol):
    """Protocol for Zephyr test result operations."""

    def create_testresult(self, testresult_data: dict[str, Any]) -> int:
        """Create a new test result."""
        ...

    def get_testcase_latest_result(self, test_case_key: str) -> ZephyrTestResult | None:
        """Get the latest test result for a test case."""
        ...

    def get_testrun_results(self, test_run_key: str) -> list[ZephyrTestResult]:
        """Get all test results for a test run."""
        ...

    def create_testrun_result(
        self,
        test_run_key: str,
        test_case_key: str,
        testresult_data: dict[str, Any],
        environment: str | None = None,
        user_key: str | None = None,
    ) -> int:
        """Create a test result within a test run."""
        ...

    def update_testrun_result(
        self,
        test_run_key: str,
        test_case_key: str,
        testresult_data: dict[str, Any],
        environment: str | None = None,
        user_key: str | None = None,
    ) -> int:
        """Update the latest test result within a test run."""
        ...

    def create_bulk_testrun_results(
        self,
        test_run_key: str,
        testresults_data: list[dict[str, Any]],
        environment: str | None = None,
        user_key: str | None = None,
    ) -> list[int]:
        """Create multiple test results within a test run."""
        ... 