import time
import traceback
from helper.landing_page_helper import LandingPageHelper
from pages.hpid_page import HPIDPage
import test_flows_common.test_flows_common as common
from test_flows import LandingPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
from helper.gemini_ra_helper import GeminiRAHelper
from pages.landing_page import LandingPage
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def sign_up_with_existing_account(stage_callback):
    framework_logger.info("=== C40644198 -Sign up with existing account started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        landing_page = LandingPage(page)

        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Landing Page
            LandingPageHelper.open(page)
            LandingPageHelper.access(page)

            # Click on Sign Up Now button
            landing_page.sign_up_header_button.click()
            framework_logger.info("Sign Up Now button clicked")

            # Create Account with existing account
            hpid_page = HPIDPage(page)
            hpid_page.wait.create_account_button_data(timeout=20000).click()
            page.fill("#firstName",common.DEFAULT_FIRSTNAME)
            page.fill("#lastName",common.DEFAULT_LASTNAME)
            page.fill("#email", tenant_email)
            page.fill("#password",common.DEFAULT_PASSWORD)
            page.locator("#sign-up-submit").click()
            framework_logger.info("Create Account with existing account attempted")

            # An error message on Create Account page is displayed
            time.sleep(10)
            assert "Already have an HP account?" in page.content()
            framework_logger.info("Error message is displayed on Create Account page")

            framework_logger.info("=== C40644198 -Sign up with existing account finished ===")
        except Exception as e:
                framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
                raise e