from pages.landing_page import LandingPage
from core.settings import framework_logger
from core.playwright_manager import PlaywrightManager  
from pages.privacy_banner_page import PrivacyBannerPage
import test_flows_common.test_flows_common as common
import time
import traceback

def instant_ink_for_business(stage_callback):
    framework_logger.info("=== C38471735 -Instant Ink for Business validation flow started ===")
    common.setup()

    timeout_ms = 120000

    try:
        with PlaywrightManager() as page:
            page.set_default_timeout(timeout_ms)

            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)
            
            # Navigate to consumer landing page
            page.goto(common._instantink_url, timeout=timeout_ms)
            framework_logger.info(f"Navigated to consumer landing page: {common._instantink_url}")

            # Accept privacy banner if present
            privacy_banner_page.accept_privacy_banner()

            # Scroll down
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            framework_logger.info("Scrolled to bottom of page")
            time.sleep(2)

            # Verify business section
            business_section = landing_page.instant_ink_for_business_section
            is_visible = business_section.is_visible()
            
            if is_visible:
                framework_logger.error("FAILURE: 'Instant Ink for Business' section is visible on consumer landing page")
                raise AssertionError("'Instant Ink for Business' section should NOT be displayed on consumer landing page")
            else:
                framework_logger.info("SUCCESS: 'Instant Ink for Business' section is not displayed on consumer landing page")

            framework_logger.info("=== C38471735 -Instant Ink for Business validation flow ended successfully ===")
    except Exception as e:
        framework_logger.error(f"An error occurred during the Instant Ink for Business test: {e}\n{traceback.format_exc()}")
        raise e
    