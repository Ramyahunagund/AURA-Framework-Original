
import time
import traceback
from playwright.sync_api import expect
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.landing_page_helper import LandingPageHelper
from pages.landing_page import LandingPage
from pages.hpid_page import HPIDPage
from pages.privacy_banner_page import PrivacyBannerPage
import test_flows_common.test_flows_common as common
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def sign_up_now_button(stage_callback):
    framework_logger.info("=== C38574375 - Sign Up Now Button test started ===")
    common.setup()

    with PlaywrightManager() as page:
        landing_page = LandingPage(page)
        hpid_page = HPIDPage(page)

        try:
            # Open Landing Page
            LandingPageHelper.open(page)

            # Accept privacy banner
            privacy_banner_page = PrivacyBannerPage(page)
            privacy_banner_page.accept_privacy_banner()

            # Scroll to the plans section
            page.evaluate("document.querySelector('[data-testid=\"landing-page-plans-container\"]').scrollIntoView()")
            framework_logger.info("Scrolled to Plans section")

            # Wait for the plans container to be visible
            expect(page.locator("[class^='planSection-module_planCardContainer']")).to_be_visible(timeout=30000)

            # Get all plan cards and verify each has a "Sign Up Now" button
            plan_cards = page.locator("[data-testid='landing-page-plans-container'] [data-testid^='lp-plans-plan-card-']").all()
            framework_logger.info(f"Found {len(plan_cards)} plan cards")

            if len(plan_cards) == 0:
                raise Exception("No plan cards found on the Landing Page")

            # Verify the first plan card has a "Sign Up Now" button
            plan_sign_up_now = landing_page.plan_sign_up_now_button
            expect(plan_sign_up_now).to_be_visible(timeout=30000)

            # Get the button text to verify it says "Sign Up Now"
            button_text = plan_sign_up_now.inner_text()
            framework_logger.info(f"Button text: '{button_text}'")

            # Verify button text contains "Sign Up" (exact text may vary by locale)
            assert "sign" in button_text.lower() and "up" in button_text.lower(), \
                f"Expected button text to contain 'Sign Up', but got: '{button_text}'"
            framework_logger.info("Verified 'Sign Up Now' button is visible on plan card")

            # Click the button and expect a new page/tab to open
            plan_sign_up_now.click()
            framework_logger.info("'Sign Up Now' button clicked")
            
            # Wait for HPID value prop page to load
            expect(hpid_page.sign_in_option).to_be_visible(timeout=60000)
            framework_logger.info("Successfully navigated to HPID value prop page")

            framework_logger.info("=== C38574375 - Sign Up Now Button test completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Sign Up Now Button test: {e}\n{traceback.format_exc()}")
            raise e