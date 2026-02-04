import traceback
from playwright.sync_api import sync_playwright, expect
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState, framework_logger
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage
import test_flows_common.test_flows_common as common

def privacy_banner(stage_callback):
    framework_logger.info("=== C38569195 - Privacy Banner flow started ===")
    common.setup()

    timeout_ms = 30000

    with PlaywrightManager() as page:
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)

            # Step 1: Launch the Consumer Landing page
            framework_logger.info("Step 1: Navigating to Consumer Landing page")
            page.goto(common._instantink_url, timeout=timeout_ms)

            # Step 2: Verify that privacy banner is displayed well
            framework_logger.info("Step 2: Verifying privacy banner is visible")
            expect(privacy_banner_page.accept_button).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Privacy banner is visible as expected")

            # Step 3: Click "I ACCEPT" button
            framework_logger.info("Step 3: Clicking 'I ACCEPT' button")
            privacy_banner_page.accept_button.click()
            framework_logger.info("'I ACCEPT' button clicked successfully")

            # Step 4: Verify the privacy banner does not display anymore
            framework_logger.info("Step 4: Verifying privacy banner is no longer visible")
            expect(privacy_banner_page.accept_button).not_to_be_visible(timeout=timeout_ms)
            framework_logger.info("Privacy banner has disappeared as expected")

            # Additional verification: Ensure landing page elements are visible after banner is dismissed
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Landing page is accessible after dismissing privacy banner")

            framework_logger.info("=== C38569195 - Privacy Banner flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Privacy Banner test: {e}\n{traceback.format_exc()}")
            raise e
 