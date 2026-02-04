import traceback
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from helper.landing_page_helper import LandingPageHelper
from pages.overview_page import OverviewPage
import test_flows_common.test_flows_common as common
from test_flows import LandingPage
from pages.hpid_page import HPIDPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
from pages.landing_page import LandingPage
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def username_password_recovery(stage_callback):
    framework_logger.info("=== C40978443 -Username/password recovery started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        landing_page = LandingPage(page)
        overview_page = OverviewPage(page)

        try:
            # Access Landing Page
            LandingPageHelper.open(page)
            LandingPageHelper.access(page)
            framework_logger.info("Landing page accessed successfully")

            # Click on Sign In button
            landing_page.sign_in_button.click()
            framework_logger.info("Sign Up Now button clicked")

            # Add the email and click forgot password link
            page.fill("#username", tenant_email)
            page.locator("#user-name-form-submit").click()
            page.locator("#forgot-password").click()
            framework_logger.info("Create Account with existing account attempted")

            # Sees recover password and check current email on username field
            page.wait_for_selector("#recoveryInput")
            email_value = page.locator("#recoveryInput").input_value()
            if email_value == tenant_email:
                framework_logger.info("Recover password email is pre-filled with the correct email.")
            else:
                framework_logger.warning("Recover password email is NOT pre-filled with the correct email.")

            # Clicks next button on recover password page
            page.locator("#password-recovery").click()
            framework_logger.info("Next button clicked on recover password page")

            # Confirms the account for recovery process using the verification code received via email
            hpid_page = HPIDPage(page)
            verification_code = common.fetch_verification_code(tenant_email)
            hpid_page.code.fill(verification_code)
            framework_logger.info("Account confirmed for recovery process")

            # Fills new password field and SignIn
            new_password = "NewPass321@"
            page.fill("#password", new_password)
            page.fill("#confirmPassword-label", new_password)
            page.locator('button[type=submit]').click()
            framework_logger.info("New password set and reset password button clicked")

            # Fills email and new password to sign in on HPID page 
            new_password = "NewPass321@"
            HPIDHelper.sign_in(page, tenant_email, new_password)
            framework_logger.info("Sign in attempted with new password")

            # Access the Dashboard page and sign out
            EnrollmentHelper.accept_terms_of_service(page)
            DashboardHelper.skips_all_but_tour_precondition(page)
            DashboardHelper.skip_tour_modal(page)
            overview_page.avatar_menu.click()
            overview_page.sign_out_button.click()
            framework_logger.info("Signed out successfully")

            # Click forgot username link
            LandingPageHelper.open(page)
            page.locator("#forgot-cred").click()
            framework_logger.info("Sign In button clicked and forgot username link clicked")

            # Fills email field and sees recover username page
            page.fill("#recoveryInput", tenant_email)
            page.locator("#username-recovery").click()
            assert('Recover username') in page.content()
            framework_logger.info("Email filled and Next button clicked on recover username page")

            framework_logger.info("=== C40978443 -Username/password recovery finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e