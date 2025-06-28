"""Constants for Zephyr API integration."""

# Zephyr API endpoints
ZEPHYR_API_BASE_URL = "https://jira.sberbank.ru"
ZEPHYR_API_VERSION = "1.0"
ZEPHYR_BASE_PATH = f"{ZEPHYR_API_BASE_URL}/rest/atm/{ZEPHYR_API_VERSION}"

# Test step status constants
TEST_STEP_STATUS_PASS = "PASS"
TEST_STEP_STATUS_FAIL = "FAIL"
TEST_STEP_STATUS_WIP = "WIP"
TEST_STEP_STATUS_BLOCKED = "BLOCKED"

# Default values
DEFAULT_ZEPHYR_TIMEOUT = 30
# JWT constants removed - now using Bearer token authentication
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0

# Zephyr test step field names
FIELD_ORDER_ID = "orderId"
FIELD_STEP = "step"
FIELD_DATA = "data"
FIELD_RESULT = "result"
FIELD_STEP_ID = "id"
FIELD_STEP_COLLECTION = "stepBeanCollection" 