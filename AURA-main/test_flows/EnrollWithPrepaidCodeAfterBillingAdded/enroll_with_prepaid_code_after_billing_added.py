import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState, framework_logger
from helper.dashboard_helper import DashboardHelper
from pages.confirmation_page import ConfirmationPage
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.hpid_helper import HPIDHelper
from pages.overview_page import OverviewPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
from playwright.sync_api import expect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#TC="C43769300"
def enroll_with_prepaid_code_after_billing_added(stage_callback):
    framework_logger.info("=== enroll_with_prepaid_code_after_billing_added started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # 1) HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer
        common.create_and_claim_virtual_printer()

    with PlaywrightManager() as page:
        try:
            # start enrollment
            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # sign in method
            HPIDHelper.complete_sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in")

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # choose HP checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing added successfully")

            # Add prepaid code
            prepaid_code = common.get_offer_code("prepaid")
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 30)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")

            # Verify that the message to add billing information is not displayed
            confirmation_page = ConfirmationPage(page)
            expect(confirmation_page.message_add_billing_info).not_to_be_visible()

            # Finish enrollment flow
            EnrollmentHelper.finish_enrollment_with_prepaid(page)
            framework_logger.info("Enrollment flow finished successfully")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_special_offer_value(page, 30)

            framework_logger.info("enroll_with_prepaid_code_after_billing_added completed successfully")

        except Exception as e:
            framework_logger.error(f"An error occurred during the enroll_with_prepaid_code_after_billing_added flow: {e}\n{traceback.format_exc()}")
            raise e
