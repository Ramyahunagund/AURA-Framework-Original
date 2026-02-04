import traceback
from playwright.sync_api import expect
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.landing_page_helper import LandingPageHelper
from pages.landing_page import LandingPage
from pages.privacy_banner_page import PrivacyBannerPage
import test_flows_common.test_flows_common as common
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def need_more_plan_info_link(stage_callback):
    framework_logger.info("=== C38569225 - Need more plans info? link flow started ===")
    common.setup()
    timeout_ms = 1200000

    with PlaywrightManager() as page:
        landing_page = LandingPage(page)

        try:         
            # Open Landing Page
            LandingPageHelper.open(page)

            # Accept privacy banner
            privacy_banner_page = PrivacyBannerPage(page)
            privacy_banner_page.accept_privacy_banner()

            # Verify Plans section is visible
            expect(landing_page.ink_plans_tab).to_be_visible(timeout=timeout_ms)
            landing_page.ink_plans_tab.scroll_into_view_if_needed()
            framework_logger.info("Plans section is visible")

            # Click the link and verify modal opens
            landing_page.need_more_plan_info.click()
            expect(landing_page.plans_info_modal).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Modal opened successfully after clicking link")

            # The actual values may vary by locale and configuration
            modal_content = landing_page.plans_info_modal.text_content()
            assert modal_content is not None and len(modal_content) > 0, "Modal content should not be empty"
            assert "Additional pages are available in sets of 10-15 pages, depending on your plan, for only $1.50 per set." in modal_content, \
                "Expected additional pages info not found in modal content"

            # Open sign in link in new tab
            with page.context.expect_page() as new_page_info:
                landing_page.plans_info_modal_signin_link.click()
            new_tab = new_page_info.value
            new_tab.bring_to_front()

            # Verify HPID sign in page is displayed in the new tab
            new_tab.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            assert "hpid" in new_tab.url.lower() or "signin" in new_tab.url.lower() or "login" in new_tab.url.lower(), \
                f"Expected HPID sign in page, but got URL: {new_tab.url}"
            framework_logger.info(f"HPID sign in page opened in new tab")

            # Close the new tab and verify modal is still displayed
            new_tab.close()
            page.bring_to_front()

            # Verify we're back to the original page with modal still visible
            expect(landing_page.plans_info_modal).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Modal is still visible after closing the new tab")

            # Click the X button on the modal and verify modal closes
            expect(landing_page.modal_close).to_be_visible(timeout=timeout_ms)
            landing_page.modal_close.click()

            # Verify modal is closed
            expect(landing_page.plans_info_modal).not_to_be_visible(timeout=timeout_ms)
            framework_logger.info("Modal closed successfully after clicking X button")

            framework_logger.info("=== C38569225 - Need more plans info? link flow ended successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Sign Up Now Button test: {e}\n{traceback.format_exc()}")
            raise e