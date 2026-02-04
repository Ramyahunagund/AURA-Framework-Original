import traceback
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState, framework_logger
import test_flows_common.test_flows_common as common


def launch_with_basic_url(stage_callback):
    framework_logger.info("=== C38421788 - Launch with basic URL flow started ===")
    common.setup()

    with PlaywrightManager() as page:
        try:
            # Navigate to base URL
            framework_logger.info(f"Navigating to base URL: {common._instantink_url}")
            page.goto(common._instantink_url, wait_until="load")
            
            # Verify locale redirect
            expected_locale_path = f"/{GlobalState.country_code.lower()}/{GlobalState.language.lower()}"
            current_url = page.url
            
            assert expected_locale_path in current_url.lower(), \
                f"Expected '{expected_locale_path}' in '{current_url}'"
            
            framework_logger.info(f"Browser redirected correctly to: {current_url}")
            framework_logger.info("=== C38421788 - Launch with basic URL flow completed successfully ===")
            
        except Exception as e:
            framework_logger.error(f"Test failed: {e}\n{traceback.format_exc()}")
            raise e