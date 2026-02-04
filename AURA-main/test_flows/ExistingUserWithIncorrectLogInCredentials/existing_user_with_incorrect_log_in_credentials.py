import time
from pages.landing_page import LandingPage
from pages.sign_in_page import SignInPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
from helper.landing_page_helper import LandingPageHelper
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def existing_user_with_incorrect_log_in_credentials(stage_callback):
    framework_logger.info("=== C38992857 - Existing user with incorrect log in credentials started ===")
    tenant_email = create_ii_subscription(stage_callback)
    incorrect_email = "incorrect_" + tenant_email

    with PlaywrightManager() as page:
        try:
            sign_in_page = SignInPage(page)
            landing_page = LandingPage(page)

            # Access Landing Page
            LandingPageHelper.access(page)
            framework_logger.info("Landing page accessed successfully")

            # Click on Sign In button
            landing_page.sign_up_header_button.click()
            landing_page.sign_in_button.click()
            framework_logger.info("Sign in button clicked")

            # Fills email incorrect with existing account
            expect(sign_in_page.email_input).to_be_visible(timeout=90000)
            sign_in_page.email_input.fill(incorrect_email)
            sign_in_page.use_password_button.click()
            expect(page.locator('text=HP account not found')).to_be_visible(timeout=90000)
            framework_logger.info("Verified 'HP account not found' message for incorrect email")

            sign_in_page.email_input.fill(tenant_email)
            sign_in_page.use_password_button.click()
            
            expect(sign_in_page.password_input).to_be_visible(timeout=90000)
            sign_in_page.password_input.fill("incorrect_password")
            sign_in_page.sign_in_button.click()
            expect(page.locator('text=Invalid username or password')).to_be_visible(timeout=90000)
            framework_logger.info("Verified 'Invalid username or password' message for incorrect password")

            sign_in_page.password_input.fill(common.DEFAULT_PASSWORD)
            sign_in_page.sign_in_button.click()
            framework_logger.info("Logged in to Instant Ink account")

            framework_logger.info("=== C38992857 - Existing user with incorrect log in credentials finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
