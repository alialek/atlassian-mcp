"""Zephyr FastMCP server instance and tool definitions."""

import json
import logging
from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import Field

from mcp_atlassian.exceptions import MCPAtlassianAuthenticationError, MCPAtlassianNotFoundError
from mcp_atlassian.models.zephyr import TestStepRequest
from mcp_atlassian.servers.dependencies import get_zephyr_fetcher
from mcp_atlassian.utils.decorators import check_write_access

logger = logging.getLogger(__name__)

zephyr_mcp = FastMCP(
    name="Zephyr MCP Service",
    description="Provides tools for interacting with Zephyr test management.",
)


# ==================== TEST CASE TOOLS ====================

@zephyr_mcp.tool(tags={"zephyr", "testcase", "read"})
async def get_testcase(
    ctx: Context,
    test_case_key: Annotated[
        str,
        Field(description="The test case key (e.g., 'JQA-T1234')")
    ],
    fields: Annotated[
        str | None,
        Field(
            description=(
                "Optional comma-separated list of fields to include. "
                "Available fields: key, name, folder, status, priority, component, owner, "
                "estimatedTime, labels, customFields, issueLinks, testScript. "
                "If not specified, all fields will be returned."
            ),
            default=None
        )
    ] = None,
) -> str:
    """Get a test case by key.
    
    Args:
        ctx: The FastMCP context
        test_case_key: The test case key
        fields: Optional fields to include
        
    Returns:
        JSON string representing the test case data
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_case = zephyr.get_testcase(test_case_key, fields)
        response_data = {"success": True, "test_case": test_case.to_simplified_dict()}
    except MCPAtlassianNotFoundError as e:
        response_data = {"success": False, "error": f"Test case not found: {e}"}
    except Exception as e:
        logger.exception(f"Error getting test case {test_case_key}")
        response_data = {"success": False, "error": f"Failed to get test case: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testcase", "write"})
@check_write_access
async def create_testcase(
    ctx: Context,
    testcase_data: Annotated[
        str,
        Field(
            description=(
                "JSON string containing test case data. Required: name, projectKey. "
                "Optional fields: status, priority, component, folder, owner, estimatedTime, "
                "labels, customFields, issueLinks, testScript. "
                "Status values: 'Draft', 'Approved', 'Deprecated'. "
                "Test script types: 'PLAIN_TEXT', 'STEP_BY_STEP', 'BDD'. "
                "Example: {\"name\": \"Test login\", \"projectKey\": \"JQA\", \"status\": \"Draft\"}"
            )
        )
    ],
) -> str:
    """Create a new test case.
    
    Args:
        ctx: The FastMCP context
        testcase_data: JSON string with test case creation data
        
    Returns:
        JSON string with the created test case key
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        data = json.loads(testcase_data)
        test_case_key = zephyr.create_testcase(data)
        response_data = {"success": True, "test_case_key": test_case_key}
    except Exception as e:
        logger.exception("Error creating test case")
        response_data = {"success": False, "error": f"Failed to create test case: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testcase", "write"})
@check_write_access  
async def update_testcase(
    ctx: Context,
    test_case_key: Annotated[
        str,
        Field(description="The test case key to update (e.g., 'JQA-T1234')")
    ],
    testcase_data: Annotated[
        str,
        Field(
            description=(
                "JSON string containing updated test case data. "
                "Available fields: name, status, priority, component, folder, owner, "
                "estimatedTime, labels, customFields, issueLinks, testScript. "
                "Note: projectKey cannot be changed. Only fields present will be updated. "
                "Status values: 'Draft', 'Approved', 'Deprecated'. "
                "Test script types: 'PLAIN_TEXT', 'STEP_BY_STEP', 'BDD'. "
                "Example: {\"status\": \"Approved\", \"priority\": \"High\"}"
            )
        )
    ],
) -> str:
    """Update a test case.
    
    Args:
        ctx: The FastMCP context
        test_case_key: The test case key to update
        testcase_data: JSON string with updated test case data
        
    Returns:
        JSON string indicating success or failure
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        data = json.loads(testcase_data)
        zephyr.update_testcase(test_case_key, data)
        response_data = {"success": True, "message": f"Test case {test_case_key} updated"}
    except MCPAtlassianNotFoundError as e:
        response_data = {"success": False, "error": f"Test case not found: {e}"}
    except Exception as e:
        logger.exception(f"Error updating test case {test_case_key}")
        response_data = {"success": False, "error": f"Failed to update test case: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testcase", "write"})
@check_write_access
async def delete_testcase(
    ctx: Context,
    test_case_key: Annotated[
        str,
        Field(description="The test case key to delete (e.g., 'JQA-T1234')")
    ],
) -> str:
    """Delete a test case.
    
    Args:
        ctx: The FastMCP context
        test_case_key: The test case key to delete
        
    Returns:
        JSON string indicating success or failure
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        zephyr.delete_testcase(test_case_key)
        response_data = {"success": True, "message": f"Test case {test_case_key} deleted"}
    except MCPAtlassianNotFoundError as e:
        response_data = {"success": False, "error": f"Test case not found: {e}"}
    except Exception as e:
        logger.exception(f"Error deleting test case {test_case_key}")
        response_data = {"success": False, "error": f"Failed to delete test case: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testcase", "search"})
async def search_testcases(
    ctx: Context,
    query: Annotated[
        str | None,
        Field(
            description=(
                "TQL (Test Query Language) query string for filtering test cases. "
                "Available fields: projectKey, key, name, status, priority, component, folder, "
                "estimatedTime, labels, owner, issueKeys, and custom fields (quoted). "
                "Available operators: =, >, >=, <, <=, IN. Logical: AND. "
                "Examples: "
                "• 'projectKey = \"JQA\" AND status = \"Draft\"' "
                "• 'projectKey = \"JQA\" AND status IN (\"Draft\", \"Approved\")' "
                "• 'projectKey = \"JQA\" AND folder = \"/Test Folder\"' "
                "• 'key IN (\"JQA-T50\", \"JQA-T60\")' "
                "• 'projectKey = \"JQA\" AND \"Custom Field\" = \"Value\"'"
            ),
            default=None
        )
    ] = None,
    fields: Annotated[
        str | None,
        Field(
            description=(
                "Optional comma-separated list of fields to include. "
                "Available fields: key, name, folder, status, priority, component, owner, "
                "estimatedTime, labels, customFields, issueLinks, testScript. "
                "If not specified, all fields will be returned."
            ),
            default=None
        )
    ] = None,
    start_at: Annotated[
        int,
        Field(
            description="Offset for pagination (0-based). Use with max_results for pagination.",
            default=0,
            ge=0
        )
    ] = 0,
    max_results: Annotated[
        int,
        Field(
            description="Maximum number of results to return (1-200). Default: 200.",
            default=200,
            ge=1,
            le=200
        )
    ] = 200,
) -> str:
    """Search for test cases using TQL query.
    
    Args:
        ctx: The FastMCP context
        query: TQL query string for filtering
        fields: Optional fields to include in response
        start_at: Pagination offset (0-based)
        max_results: Maximum results (1-200)
        
    Returns:
        JSON string with search results including test cases array and count
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_cases = zephyr.search_testcases(query, fields, start_at, max_results)
        results = [tc.to_simplified_dict() for tc in test_cases]
        response_data = {"success": True, "test_cases": results, "count": len(results)}
    except Exception as e:
        logger.exception("Error searching test cases")
        response_data = {"success": False, "error": f"Failed to search test cases: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


# ==================== TEST PLAN TOOLS ====================

@zephyr_mcp.tool(tags={"zephyr", "testplan", "read"})
async def get_testplan(
    ctx: Context,
    test_plan_key: Annotated[
        str,
        Field(description="The test plan key (e.g., 'JQA-P1234')")
    ],
    fields: Annotated[
        str | None,
        Field(
            description=(
                "Optional comma-separated list of fields to include. "
                "Available fields: key, name, status, objective, testRuns, customFields, "
                "folder, labels, owner. If not specified, all fields will be returned."
            ),
            default=None
        )
    ] = None,
) -> str:
    """Get a test plan by key.
    
    Args:
        ctx: The FastMCP context
        test_plan_key: The test plan key
        fields: Optional fields to include
        
    Returns:
        JSON string representing the test plan data
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_plan = zephyr.get_testplan(test_plan_key, fields)
        response_data = {"success": True, "test_plan": test_plan.to_simplified_dict()}
    except MCPAtlassianNotFoundError as e:
        response_data = {"success": False, "error": f"Test plan not found: {e}"}
    except Exception as e:
        logger.exception(f"Error getting test plan {test_plan_key}")
        response_data = {"success": False, "error": f"Failed to get test plan: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testplan", "write"})
@check_write_access
async def create_testplan(
    ctx: Context,
    testplan_data: Annotated[
        str,
        Field(
            description=(
                "JSON string containing test plan data. Required: name, projectKey. "
                "Optional fields: status, objective, folder, labels, customFields. "
                "Example: {\"name\": \"Sprint 1 Test Plan\", \"projectKey\": \"JQA\", "
                "\"objective\": \"Test user authentication features\"}"
            )
        )
    ],
) -> str:
    """Create a new test plan.
    
    Args:
        ctx: The FastMCP context
        testplan_data: JSON string with test plan creation data
        
    Returns:
        JSON string with the created test plan key
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        data = json.loads(testplan_data)
        test_plan_key = zephyr.create_testplan(data)
        response_data = {"success": True, "test_plan_key": test_plan_key}
    except Exception as e:
        logger.exception("Error creating test plan")
        response_data = {"success": False, "error": f"Failed to create test plan: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testplan", "search"})
async def search_testplans(
    ctx: Context,
    query: Annotated[
        str | None,
        Field(
            description=(
                "TQL (Test Query Language) query string for filtering test plans. "
                "Available fields: projectKey, key, name, status, folder, labels, owner, "
                "issueKeys, and custom fields (quoted). "
                "Available operators: =, >, >=, <, <=, IN. Logical: AND. "
                "Examples: "
                "• 'projectKey = \"JQA\" AND status = \"Draft\"' "
                "• 'projectKey = \"JQA\" AND folder = \"/Test Plans\"' "
                "• 'projectKey = \"JQA\" AND labels IN (\"Functional\", \"UI\")'"
            ),
            default=None
        )
    ] = None,
    fields: Annotated[
        str | None,
        Field(
            description=(
                "Optional comma-separated list of fields to include. "
                "Available fields: key, name, status, objective, testRuns, customFields, "
                "folder, labels, owner. If not specified, all fields will be returned."
            ),
            default=None
        )
    ] = None,
    start_at: Annotated[
        int,
        Field(
            description="Offset for pagination (0-based). Use with max_results for pagination.",
            default=0,
            ge=0
        )
    ] = 0,
    max_results: Annotated[
        int,
        Field(
            description="Maximum number of results to return (1-200). Default: 200.",
            default=200,
            ge=1,
            le=200
        )
    ] = 200,
) -> str:
    """Search for test plans using TQL query.
    
    Args:
        ctx: The FastMCP context
        query: TQL query string
        fields: Optional fields to include
        start_at: Pagination offset
        max_results: Maximum results
        
    Returns:
        JSON string with search results
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_plans = zephyr.search_testplans(query, fields, start_at, max_results)
        results = [tp.to_simplified_dict() for tp in test_plans]
        response_data = {"success": True, "test_plans": results, "count": len(results)}
    except Exception as e:
        logger.exception("Error searching test plans")
        response_data = {"success": False, "error": f"Failed to search test plans: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


# ==================== TEST RUN TOOLS ====================

@zephyr_mcp.tool(tags={"zephyr", "testrun", "read"})
async def get_testrun(
    ctx: Context,
    test_run_key: Annotated[
        str,
        Field(description="The test run key (e.g., 'JQA-R1234')")
    ],
    fields: Annotated[
        str | None,
        Field(
            description=(
                "Optional comma-separated list of fields to include. "
                "Available fields: key, name, version, iteration, items, status, "
                "plannedStartDate, plannedEndDate, customFields. "
                "If not specified, all fields will be returned."
            ),
            default=None
        )
    ] = None,
) -> str:
    """Get a test run by key.
    
    Args:
        ctx: The FastMCP context
        test_run_key: The test run key
        fields: Optional fields to include
        
    Returns:
        JSON string representing the test run data
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_run = zephyr.get_testrun(test_run_key, fields)
        response_data = {"success": True, "test_run": test_run.to_simplified_dict()}
    except MCPAtlassianNotFoundError as e:
        response_data = {"success": False, "error": f"Test run not found: {e}"}
    except Exception as e:
        logger.exception(f"Error getting test run {test_run_key}")
        response_data = {"success": False, "error": f"Failed to get test run: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testrun", "write"})
@check_write_access
async def create_testrun(
    ctx: Context,
    testrun_data: Annotated[
        str,
        Field(
            description=(
                "JSON string containing test run data. Required: name, projectKey. "
                "Optional fields: plannedStartDate, plannedEndDate, testPlanKey, issueKey, "
                "version, iteration, items (test cases), customFields. "
                "Status values: 'Not Executed', 'In Progress', 'Done'. "
                "Example: {\"name\": \"Sprint 1 Test Run\", \"projectKey\": \"JQA\", "
                "\"testPlanKey\": \"JQA-P1234\"}"
            )
        )
    ],
) -> str:
    """Create a new test run.
    
    Args:
        ctx: The FastMCP context
        testrun_data: JSON string with test run creation data
        
    Returns:
        JSON string with the created test run key
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        data = json.loads(testrun_data)
        test_run_key = zephyr.create_testrun(data)
        response_data = {"success": True, "test_run_key": test_run_key}
    except Exception as e:
        logger.exception("Error creating test run")
        response_data = {"success": False, "error": f"Failed to create test run: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testrun", "search"})
async def search_testruns(
    ctx: Context,
    query: Annotated[
        str | None,
        Field(
            description=(
                "TQL (Test Query Language) query string for filtering test runs. "
                "Available fields: projectKey, folder. "
                "Available operators: =, IN. Logical: AND. "
                "Examples: "
                "• 'projectKey = \"JQA\"' "
                "• 'projectKey IN (\"JQA\", \"DEF\")' "
                "• 'projectKey = \"JQA\" AND folder = \"/Orbiter\"'"
            ),
            default=None
        )
    ] = None,
    fields: Annotated[
        str | None,
        Field(
            description=(
                "Optional comma-separated list of fields to include. "
                "Available fields: key, name, version, iteration, items, status, "
                "plannedStartDate, plannedEndDate, customFields. "
                "If not specified, all fields will be returned."
            ),
            default=None
        )
    ] = None,
    start_at: Annotated[
        int,
        Field(
            description="Offset for pagination (0-based). Use with max_results for pagination.",
            default=0,
            ge=0
        )
    ] = 0,
    max_results: Annotated[
        int,
        Field(
            description="Maximum number of results to return (1-200). Default: 200.",
            default=200,
            ge=1,
            le=200
        )
    ] = 200,
) -> str:
    """Search for test runs using TQL query.
    
    Args:
        ctx: The FastMCP context
        query: TQL query string
        fields: Optional fields to include
        start_at: Pagination offset
        max_results: Maximum results
        
    Returns:
        JSON string with search results
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_runs = zephyr.search_testruns(query, fields, start_at, max_results)
        results = [tr.to_simplified_dict() for tr in test_runs]
        response_data = {"success": True, "test_runs": results, "count": len(results)}
    except Exception as e:
        logger.exception("Error searching test runs")
        response_data = {"success": False, "error": f"Failed to search test runs: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


# ==================== TEST RESULT TOOLS ====================

@zephyr_mcp.tool(tags={"zephyr", "testresult", "write"})
@check_write_access
async def create_testresult(
    ctx: Context,
    testresult_data: Annotated[
        str,
        Field(
            description=(
                "JSON string containing test result data. Required: testCaseKey. "
                "Optional fields: status, actualStartDate, actualEndDate, comment, "
                "executedBy, environment, customFields. "
                "Status values: 'Not Executed', 'In Progress', 'Pass', 'Fail', 'Blocked'. "
                "Example: {\"testCaseKey\": \"JQA-T1234\", \"status\": \"Pass\", \"comment\": \"Test passed\"}"
            )
        )
    ],
) -> str:
    """Create a new test result for a test case.
    
    Args:
        ctx: The FastMCP context
        testresult_data: JSON string with test result creation data
        
    Returns:
        JSON string with the created test result ID
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        data = json.loads(testresult_data)
        test_result_id = zephyr.create_testresult(data)
        response_data = {"success": True, "test_result_id": test_result_id}
    except Exception as e:
        logger.exception("Error creating test result")
        response_data = {"success": False, "error": f"Failed to create test result: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testresult", "read"})
async def get_testcase_latest_result(
    ctx: Context,
    test_case_key: Annotated[
        str,
        Field(description="The test case key (e.g., 'JQA-T1234')")
    ],
) -> str:
    """Get the latest test result for a test case.
    
    Args:
        ctx: The FastMCP context
        test_case_key: The test case key
        
    Returns:
        JSON string with the latest test result data
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_result = zephyr.get_testcase_latest_result(test_case_key)
        if test_result:
            response_data = {"success": True, "test_result": test_result.to_simplified_dict()}
        else:
            response_data = {"success": True, "test_result": None, "message": "No results found"}
    except Exception as e:
        logger.exception(f"Error getting latest result for test case {test_case_key}")
        response_data = {"success": False, "error": f"Failed to get latest test result: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "testresult", "read"})
async def get_testrun_results(
    ctx: Context,
    test_run_key: Annotated[
        str,
        Field(description="The test run key (e.g., 'JQA-R1234')")
    ],
) -> str:
    """Get all test results for a test run.
    
    Args:
        ctx: The FastMCP context
        test_run_key: The test run key
        
    Returns:
        JSON string with all test results for the test run
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_results = zephyr.get_testrun_results(test_run_key)
        results = [tr.to_simplified_dict() for tr in test_results]
        response_data = {"success": True, "test_results": results, "count": len(results)}
    except MCPAtlassianNotFoundError as e:
        response_data = {"success": False, "error": f"Test run not found: {e}"}
    except Exception as e:
        logger.exception(f"Error getting test results for test run {test_run_key}")
        response_data = {"success": False, "error": f"Failed to get test run results: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


# ==================== ORIGINAL TEST STEP TOOLS ====================

@zephyr_mcp.tool(tags={"zephyr", "read"})
async def get_test_steps(
    ctx: Context,
    issue_id: Annotated[
        str,
        Field(
            description="JIRA issue ID for the test case (numeric ID, e.g., '12345')"
        ),
    ],
    project_id: Annotated[
        str,
        Field(
            description="JIRA project ID (numeric ID, e.g., '10000')"
        ),
    ],
) -> str:
    """Get test steps for a JIRA test case in Zephyr.

    Args:
        ctx: The FastMCP context.
        issue_id: JIRA issue ID (numeric)
        project_id: JIRA project ID (numeric)

    Returns:
        JSON string representing the test steps for the issue.

    Raises:
        ValueError: If the Zephyr client is not configured or available.
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_steps = await zephyr.get_test_steps(issue_id, project_id)
        result = test_steps.to_simplified_dict()
        response_data = {"success": True, "test_steps": result}
    except Exception as e:
        error_message = ""
        log_level = logging.ERROR
        
        if isinstance(e, ValueError) and "not found" in str(e).lower():
            log_level = logging.WARNING
            error_message = str(e)
        elif isinstance(e, MCPAtlassianAuthenticationError):
            error_message = f"Authentication/Permission Error: {str(e)}"
        else:
            error_message = (
                "An unexpected error occurred while fetching test steps."
            )
            logger.exception(
                f"Unexpected error in get_test_steps for issue '{issue_id}':"
            )
        
        error_result = {
            "success": False,
            "error": str(e),
            "issue_id": issue_id,
            "project_id": project_id,
        }
        logger.log(
            log_level,
            f"get_test_steps failed for issue '{issue_id}': {error_message}",
        )
        response_data = error_result
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "write"})
@check_write_access
async def add_test_step(
    ctx: Context,
    issue_id: Annotated[
        str,
        Field(
            description="JIRA issue ID for the test case (numeric ID, e.g., '12345')"
        ),
    ],
    project_id: Annotated[
        str,
        Field(
            description="JIRA project ID (numeric ID, e.g., '10000')"
        ),
    ],
    step: Annotated[
        str,
        Field(
            description="Description of the test step (what action to perform)"
        ),
    ],
    data: Annotated[
        str | None,
        Field(
            description="(Optional) Test data or input for this step",
            default=None,
        ),
    ] = None,
    result: Annotated[
        str | None,
        Field(
            description="(Optional) Expected result for this step",
            default=None,
        ),
    ] = None,
) -> str:
    """Add a single test step to a JIRA test case in Zephyr.

    Args:
        ctx: The FastMCP context.
        issue_id: JIRA issue ID (numeric)
        project_id: JIRA project ID (numeric)
        step: Description of the test step
        data: Optional test data or input
        result: Optional expected result

    Returns:
        JSON string representing the created test step.

    Raises:
        ValueError: If the Zephyr client is not configured or available.
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        
        step_request = TestStepRequest(
            step=step,
            data=data,
            result=result,
        )
        
        test_step = await zephyr.add_test_step(issue_id, project_id, step_request)
        result_data = test_step.to_simplified_dict()
        
        response_data = {
            "success": True,
            "test_step": result_data,
            "issue_id": issue_id,
            "project_id": project_id,
        }
    except Exception as e:
        error_message = ""
        log_level = logging.ERROR
        
        if isinstance(e, MCPAtlassianAuthenticationError):
            error_message = f"Authentication/Permission Error: {str(e)}"
        else:
            error_message = (
                "An unexpected error occurred while adding the test step."
            )
            logger.exception(
                f"Unexpected error in add_test_step for issue '{issue_id}':"
            )
        
        error_result = {
            "success": False,
            "error": str(e),
            "issue_id": issue_id,
            "project_id": project_id,
        }
        logger.log(
            log_level,
            f"add_test_step failed for issue '{issue_id}': {error_message}",
        )
        response_data = error_result
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "write"})
@check_write_access
async def add_multiple_test_steps(
    ctx: Context,
    issue_id: Annotated[
        str,
        Field(
            description="JIRA issue ID for the test case (numeric ID, e.g., '12345')"
        ),
    ],
    project_id: Annotated[
        str,
        Field(
            description="JIRA project ID (numeric ID, e.g., '10000')"
        ),
    ],
    steps: Annotated[
        str,
        Field(
            description=(
                "JSON array of test step objects. Each object should contain:\n"
                "- step (required): Description of the test step\n"
                "- data (optional): Test data or input for this step\n"
                "- result (optional): Expected result for this step\n"
                'Example: [{"step": "Login to system", "data": "username/password", "result": "User is logged in"}]'
            )
        ),
    ],
) -> str:
    """Add multiple test steps to a JIRA test case in Zephyr.

    Args:
        ctx: The FastMCP context.
        issue_id: JIRA issue ID (numeric)
        project_id: JIRA project ID (numeric)
        steps: JSON array of test step objects

    Returns:
        JSON string representing the results of adding multiple test steps.

    Raises:
        ValueError: If the Zephyr client is not configured or available.
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        
        # Parse the steps JSON
        try:
            steps_data = json.loads(steps)
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "error": f"Invalid JSON format for steps: {e}",
                "issue_id": issue_id,
                "project_id": project_id,
            }, indent=2, ensure_ascii=False)
        
        if not isinstance(steps_data, list):
            return json.dumps({
                "success": False,
                "error": "Steps must be a JSON array",
                "issue_id": issue_id,
                "project_id": project_id,
            }, indent=2, ensure_ascii=False)
        
        # Create TestStepRequest objects
        step_requests = []
        for i, step_data in enumerate(steps_data):
            try:
                step_request = TestStepRequest(
                    step=step_data.get("step", ""),
                    data=step_data.get("data"),
                    result=step_data.get("result"),
                )
                step_requests.append(step_request)
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid step data at index {i}: {e}",
                    "issue_id": issue_id,
                    "project_id": project_id,
                }, indent=2, ensure_ascii=False)
        
        # Add all test steps
        created_steps = await zephyr.add_multiple_test_steps(
            issue_id, project_id, step_requests
        )
        
        result_data = [step.to_simplified_dict() for step in created_steps]
        
        response_data = {
            "success": True,
            "test_steps": result_data,
            "total_requested": len(step_requests),
            "total_created": len(created_steps),
            "issue_id": issue_id,
            "project_id": project_id,
        }
    except Exception as e:
        error_message = ""
        log_level = logging.ERROR
        
        if isinstance(e, MCPAtlassianAuthenticationError):
            error_message = f"Authentication/Permission Error: {str(e)}"
        else:
            error_message = (
                "An unexpected error occurred while adding test steps."
            )
            logger.exception(
                f"Unexpected error in add_multiple_test_steps for issue '{issue_id}':"
            )
        
        error_result = {
            "success": False,
            "error": str(e),
            "issue_id": issue_id,
            "project_id": project_id,
        }
        logger.log(
            log_level,
            f"add_multiple_test_steps failed for issue '{issue_id}': {error_message}",
        )
        response_data = error_result
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


# ==================== ENVIRONMENT TOOLS ====================

@zephyr_mcp.tool(tags={"zephyr", "environment", "read"})
async def get_environments(
    ctx: Context,
    project_key: Annotated[
        str,
        Field(description="The project key to get environments for (e.g., 'JQA')")
    ],
) -> str:
    """Get all environments for a project.
    
    Args:
        ctx: The FastMCP context
        project_key: The project key
        
    Returns:
        JSON string with list of environments for the project
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        environments = zephyr.get_environments(project_key)
        response_data = {"success": True, "environments": environments, "count": len(environments)}
    except Exception as e:
        logger.exception(f"Error getting environments for project {project_key}")
        response_data = {"success": False, "error": f"Failed to get environments: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


@zephyr_mcp.tool(tags={"zephyr", "environment", "write"})
@check_write_access
async def create_environment(
    ctx: Context,
    environment_data: Annotated[
        str,
        Field(
            description=(
                "JSON string containing environment data. Required: name, projectKey. "
                "Optional fields: description. Environment name must be unique per project. "
                "Example: {\"name\": \"Production\", \"projectKey\": \"JQA\", \"description\": \"Production environment\"}"
            )
        )
    ],
) -> str:
    """Create a new environment for a project.
    
    Args:
        ctx: The FastMCP context
        environment_data: JSON string with environment creation data
        
    Returns:
        JSON string with the created environment ID
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        data = json.loads(environment_data)
        environment_id = zephyr.create_environment(data)
        response_data = {"success": True, "environment_id": environment_id}
    except Exception as e:
        logger.exception("Error creating environment")
        response_data = {"success": False, "error": f"Failed to create environment: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False)


# ==================== ISSUE LINK TOOLS ====================

@zephyr_mcp.tool(tags={"zephyr", "issuelink", "read"})
async def get_issue_testcases(
    ctx: Context,
    issue_key: Annotated[
        str,
        Field(description="The JIRA issue key to get linked test cases for (e.g., 'JQA-1234')")
    ],
    fields: Annotated[
        str | None,
        Field(
            description=(
                "Optional comma-separated list of fields to include. "
                "Available fields: key, name, folder, status, priority, component, owner, "
                "estimatedTime, labels, customFields, issueLinks. "
                "If not specified, all fields will be returned."
            ),
            default=None
        )
    ] = None,
) -> str:
    """Get all test cases linked to a JIRA issue.
    
    Args:
        ctx: The FastMCP context
        issue_key: The JIRA issue key
        fields: Optional fields to include
        
    Returns:
        JSON string with list of test cases linked to the issue
    """
    try:
        zephyr = await get_zephyr_fetcher(ctx)
        test_cases = zephyr.get_issue_testcases(issue_key, fields)
        results = [tc.to_simplified_dict() for tc in test_cases] if test_cases else []
        response_data = {"success": True, "test_cases": results, "count": len(results)}
    except Exception as e:
        logger.exception(f"Error getting test cases for issue {issue_key}")
        response_data = {"success": False, "error": f"Failed to get test cases for issue: {e}"}
    
    return json.dumps(response_data, indent=2, ensure_ascii=False) 