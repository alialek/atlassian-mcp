"""Base client module for Zephyr API interactions."""

import logging
import os
from typing import Any

import httpx

from mcp_atlassian.exceptions import MCPAtlassianAuthenticationError
from mcp_atlassian.models.zephyr import TestStep, TestStepRequest, ZephyrTestSteps
from mcp_atlassian.utils.logging import get_masked_session_headers, log_config_param

from .auth import ZephyrAuth
from .config import ZephyrConfig

# Configure logging
logger = logging.getLogger("mcp-atlassian.zephyr")


class ZephyrClient:
    """Base client for Zephyr API interactions."""

    def __init__(self, config: ZephyrConfig | None = None) -> None:
        """Initialize the Zephyr client with configuration options.

        Args:
            config: Optional configuration object (will use env vars if not provided)

        Raises:
            ValueError: If configuration is invalid or required credentials are missing
            MCPAtlassianAuthenticationError: If authentication fails
        """
        # Load configuration from environment variables if not provided
        self.config = config or ZephyrConfig.from_env()

        # Initialize authentication
        self.auth = ZephyrAuth(self.config)
        self._http_client: httpx.Client | None = None

        # Initialize HTTP client
        self._initialize_http_client()

        # Test authentication during initialization (in debug mode only)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Debug mode enabled, authentication validation will occur on first request")

    def _initialize_http_client(self) -> None:
        """Initialize the HTTP client."""
        # Create HTTP client with SSL configuration
        self._http_client = httpx.Client(
            base_url=self.config.base_url,
            timeout=httpx.Timeout(self.config.timeout),
            limits=httpx.Limits(max_connections=5, max_keepalive_connections=2),
            verify=self.config.ssl_verify,
        )

        # Log SSL configuration
        if not self.config.ssl_verify:
            logger.warning(
                "Zephyr SSL verification disabled. This is insecure and should only be used in testing environments."
            )
        else:
            logger.debug("Zephyr SSL verification enabled")

        # Proxy configuration
        proxies = {}
        if self.config.http_proxy:
            proxies["http://"] = self.config.http_proxy
        if self.config.https_proxy:
            proxies["https://"] = self.config.https_proxy
        if self.config.socks_proxy:
            proxies["socks://"] = self.config.socks_proxy
        if proxies:
            # Update the client with proxy configuration
            self._http_client.proxies = proxies
            for k, v in proxies.items():
                log_config_param(
                    logger, "Zephyr", f"{k.upper()}_PROXY", v, sensitive=True
                )
        if self.config.no_proxy and isinstance(self.config.no_proxy, str):
            os.environ["NO_PROXY"] = self.config.no_proxy
            log_config_param(logger, "Zephyr", "NO_PROXY", self.config.no_proxy)

        # Apply custom headers if configured
        if self.config.custom_headers:
            self._apply_custom_headers()

        logger.info(f"Zephyr client initialized with base URL: {self.config.base_url}")

    def _apply_custom_headers(self) -> None:
        """Apply custom headers to the Zephyr session."""
        if not self.config.custom_headers or not self._http_client:
            return

        logger.debug(
            f"Applying {len(self.config.custom_headers)} custom headers to Zephyr session"
        )
        for header_name, header_value in self.config.custom_headers.items():
            self._http_client.headers[header_name] = header_value
            logger.debug(f"Applied custom header: {header_name}")

    def _validate_authentication(self) -> None:
        """Validate Zephyr connection and authentication."""
        try:
            logger.debug("Testing Zephyr authentication...")
            
            # Test basic connectivity with a simple request to environments endpoint
            url = "/rest/atm/1.0/environments"
            params = {"projectKey": "TEST"}  # Use a test project key
            
            response = self.request("GET", url, params=params)
            response.raise_for_status()
            
            logger.info("Zephyr authentication successful")
            
        except httpx.HTTPStatusError as e:
            error_msg = f"Zephyr authentication validation failed: {e.response.status_code}"
            if e.response.status_code == 401:
                error_msg = "Zephyr authentication failed - check Bearer token"
            logger.error(error_msg)
            raise MCPAtlassianAuthenticationError(error_msg)
        except Exception as e:
            error_msg = f"Zephyr connection validation failed: {e}"
            logger.error(error_msg)
            raise MCPAtlassianAuthenticationError(error_msg)

    def close(self) -> None:
        """Close client connections."""
        if self._http_client:
            self._http_client.close()
            self._http_client = None
        logger.info("Zephyr client connections closed")

    def request(
        self, 
        method: str, 
        url: str, 
        **kwargs: Any
    ) -> httpx.Response:
        """Make HTTP request with authentication.
        
        Args:
            method: HTTP method
            url: Request URL (relative to base URL)
            **kwargs: Additional request parameters
            
        Returns:
            HTTP response
            
        Raises:
            MCPAtlassianAuthenticationError: If request fails
        """
        if not self._http_client:
            raise MCPAtlassianAuthenticationError("HTTP client not initialized")
        
        # Add authentication headers
        headers = self.auth.get_auth_headers(method, url)
        if "headers" in kwargs:
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers
        
        try:
            response = self._http_client.request(method, url, **kwargs)
            
            # Log request details in debug mode
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Zephyr API {method} {url} -> {response.status_code}")
                
            return response
            
        except Exception as e:
            logger.error(f"Zephyr API request failed: {method} {url} - {e}")
            raise MCPAtlassianAuthenticationError(f"Request failed: {e}")

    def get_test_steps(self, issue_id: str, project_id: str) -> ZephyrTestSteps:
        """Get test steps for a test case using Zephyr Scale (Server) API.
        
        Note: This method attempts to retrieve test steps from a test case.
        Since Zephyr Scale Server API doesn't have a direct test steps endpoint,
        we'll try to get the test case details which should include test script steps.
        
        Args:
            issue_id: JIRA issue ID (test case key like 'JQA-T123')
            project_id: JIRA project ID (not used in this implementation)
            
        Returns:
            ZephyrTestSteps object containing all test steps
            
        Raises:
            MCPAtlassianAuthenticationError: If API request fails
        """
        logger.info(f"Getting test steps for test case {issue_id}")
        
        try:
            # Use the test case endpoint to get test case details including test script
            url = f"/rest/atm/1.0/testcase/{issue_id}"
            params = {"fields": "key,name,testScript"}
            
            response = self.request("GET", url, params=params)
            
            if response.status_code == 404:
                logger.warning(f"Test case {issue_id} not found")
                # Return empty test steps
                return ZephyrTestSteps(
                    issue_id=issue_id,
                    project_id=project_id,
                    steps=[]
                )
                
            response.raise_for_status()
            data = response.json()
            
            # Extract steps from test script
            steps = []
            test_script = data.get("testScript", {})
            
            if test_script and test_script.get("type") == "STEP_BY_STEP":
                script_steps = test_script.get("steps", [])
                for i, step_data in enumerate(script_steps):
                    step = TestStep(
                        order_id=i + 1,
                        step=step_data.get("description", ""),
                        data=step_data.get("testData", ""),
                        result=step_data.get("expectedResult", ""),
                        step_id=step_data.get("id")
                    )
                    steps.append(step)
            elif test_script and test_script.get("type") == "PLAIN_TEXT":
                # For plain text scripts, create a single step
                text_content = test_script.get("text", "")
                if text_content:
                    step = TestStep(
                        order_id=1,
                        step=text_content,
                        data="",
                        result="",
                        step_id=None
                    )
                    steps.append(step)
            
            test_steps = ZephyrTestSteps(
                issue_id=issue_id,
                project_id=project_id,
                steps=steps
            )
            
            logger.info(f"Retrieved {len(test_steps.steps)} test steps for test case {issue_id}")
            return test_steps
            
        except Exception as e:
            logger.error(f"Failed to get test steps for test case {issue_id}: {e}")
            if "authentication" in str(e).lower() or "401" in str(e):
                raise MCPAtlassianAuthenticationError(f"Authentication failed: {e}")
            raise MCPAtlassianAuthenticationError(f"Failed to get test steps: {e}")

    def add_test_step(
        self, 
        issue_id: str, 
        project_id: str, 
        step_request: TestStepRequest
    ) -> TestStep:
        """Add a test step to a test case by updating its test script.
        
        Note: This method updates the test case's test script to add a new step.
        For Zephyr Scale Server, we need to update the entire test script.
        
        Args:
            issue_id: JIRA issue ID (test case key like 'JQA-T123') 
            project_id: JIRA project ID (not used in this implementation)
            step_request: Test step details
            
        Returns:
            Created TestStep object
            
        Raises:
            MCPAtlassianAuthenticationError: If API request fails
        """
        logger.info(f"Adding test step to test case {issue_id}: {step_request.step}")
        
        try:
            # First, get the current test case to retrieve existing test script
            current_case = self.get_test_steps(issue_id, project_id)
            
            # Determine the next order ID
            next_order = len(current_case.steps) + 1
            
            # Create the new test step
            new_step = TestStep(
                order_id=next_order,
                step=step_request.step,
                data=step_request.data or "",
                result=step_request.result or "",
                step_id=None  # Will be assigned by Zephyr
            )
            
            # Prepare the updated test script
            all_steps = current_case.steps + [new_step]
            
            # Build the test script steps data
            script_steps = []
            for step in all_steps:
                script_steps.append({
                    "description": step.step,
                    "testData": step.data,
                    "expectedResult": step.result
                })
            
            # Prepare the update payload
            payload = {
                "testScript": {
                    "type": "STEP_BY_STEP",
                    "steps": script_steps
                }
            }
            
            # Update the test case
            url = f"/rest/atm/1.0/testcase/{issue_id}"
            response = self.request("PUT", url, json=payload)
            
            if response.status_code == 404:
                raise MCPAtlassianAuthenticationError(f"Test case {issue_id} not found")
                
            response.raise_for_status()
            
            logger.info(f"Successfully added test step to test case {issue_id}")
            return new_step
            
        except Exception as e:
            logger.error(f"Failed to add test step to test case {issue_id}: {e}")
            if "authentication" in str(e).lower() or "401" in str(e):
                raise MCPAtlassianAuthenticationError(f"Authentication failed: {e}")
            raise MCPAtlassianAuthenticationError(f"Failed to add test step: {e}")

    def add_multiple_test_steps(
        self,
        issue_id: str,
        project_id: str,
        step_requests: list[TestStepRequest]
    ) -> list[TestStep]:
        """Add multiple test steps to a test case by updating its test script.
        
        Args:
            issue_id: JIRA issue ID (test case key)
            project_id: JIRA project ID (not used in this implementation)
            step_requests: List of test step requests
            
        Returns:
            List of created TestStep objects
        """
        logger.info(f"Adding {len(step_requests)} test steps to test case {issue_id}")
        
        try:
            # Get current test case
            current_case = self.get_test_steps(issue_id, project_id)
            
            # Create new test steps
            new_steps = []
            next_order = len(current_case.steps) + 1
            
            for i, step_request in enumerate(step_requests):
                step = TestStep(
                    order_id=next_order + i,
                    step=step_request.step,
                    data=step_request.data or "",
                    result=step_request.result or "",
                    step_id=None
                )
                new_steps.append(step)
            
            # Combine all steps
            all_steps = current_case.steps + new_steps
            
            # Build the test script steps data
            script_steps = []
            for step in all_steps:
                script_steps.append({
                    "description": step.step,
                    "testData": step.data,
                    "expectedResult": step.result
                })
            
            # Prepare the update payload
            payload = {
                "testScript": {
                    "type": "STEP_BY_STEP",
                    "steps": script_steps
                }
            }
            
            # Update the test case
            url = f"/rest/atm/1.0/testcase/{issue_id}"
            response = self.request("PUT", url, json=payload)
            
            if response.status_code == 404:
                raise MCPAtlassianAuthenticationError(f"Test case {issue_id} not found")
                
            response.raise_for_status()
            
            logger.info(f"Successfully added {len(new_steps)} test steps to test case {issue_id}")
            return new_steps
            
        except Exception as e:
            logger.error(f"Failed to add multiple test steps to test case {issue_id}: {e}")
            if "authentication" in str(e).lower() or "401" in str(e):
                raise MCPAtlassianAuthenticationError(f"Authentication failed: {e}")
            raise MCPAtlassianAuthenticationError(f"Failed to add test steps: {e}")

    def _safe_get_json(self, response: httpx.Response) -> dict[str, Any]:
        """Safely extract JSON from response.
        
        Args:
            response: HTTP response
            
        Returns:
            JSON data or empty dict if parsing fails
        """
        try:
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return {} 