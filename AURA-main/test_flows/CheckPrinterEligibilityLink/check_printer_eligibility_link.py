import traceback
from playwright.sync_api import expect
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.landing_page_helper import LandingPageHelper
from pages.landing_page import LandingPage
from pages.privacy_banner_page import PrivacyBannerPage
from pages.hpid_page import HPIDPage
import test_flows_common.test_flows_common as common
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_printer_eligibility_link(stage_callback):
    framework_logger.info("=== C38574376 - Check Printer Eligibility Link flow started ===")
    common.setup()
    timeout_ms = 1200000

    with PlaywrightManager() as page:
        landing_page = LandingPage(page)
        hpid_page = HPIDPage(page)

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

            # Verify the "Check to see if your HP printer works with Instant Ink" link is displayed
            expect(landing_page.check_printer_eligibility_link).to_be_visible(timeout=timeout_ms)
            framework_logger.info("'Check to see if your HP printer works with Instant Ink' link is visible")

            # Click the "Check to see if your HP printer works with Instant Ink" link
            landing_page.check_printer_eligibility_link.click()
            framework_logger.info("Clicked on 'Check to see if your HP printer works with Instant Ink' link")

            # Verify the eligibility search modal pops up
            expect(landing_page.eligibility_search_modal).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Eligibility search modal is visible")

            framework_logger.info("=== C38574376 - Check Printer Eligibility Link flow ended successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Sign Up Now Button test: {e}\n{traceback.format_exc()}")
            raise e
