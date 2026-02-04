from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState, framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.confirmation_page import ConfirmationPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect, sync_playwright
from core.settings import GlobalState
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enroll_with_prepaid_code_and_change_plan_paypal(stage_callback):
    framework_logger.info("=== C41519357 - Enroll with Prepaid code and Change plan PayPal flow started ===")
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
        confirmation_page = ConfirmationPage(page)
        overview_page = OverviewPage(page)
        try:
            # Start enrollment
            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # Sign in method
            HPIDHelper.complete_sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in")

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Choose hp checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Apply prepaid code
            prepaid_code = common.get_offer_code("prepaid")
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 30)
            framework_logger.info(f"Prepaid code applied")

            # Validate redeemed months and credits
            EnrollmentHelper.validate_benefits_header(page, 3)
            framework_logger.info(f"Redeemed months and credits validated with 3 months")

            # Sees Optional billing information
            expect(confirmation_page.message_add_billing_info).to_have_text("Optional: Add your billing information to avoid service interruptions")
            framework_logger.info(f"Optional billing information message is visible")

            # Continue button is enabled
            expect(confirmation_page.continue_enrollment_button).to_be_enabled()
            framework_logger.info(f"Continue button is enabled")

            # Change plan
            EnrollmentHelper.select_plan(page, 300)
            framework_logger.info(f"Plan selected: 300")

            # Validate redeemed months and credits
            EnrollmentHelper.validate_benefits_header(page, 3)
            framework_logger.info(f"Redeemed months and credits validated with 3 months")

            # Change plan to the most expensive plan
            EnrollmentHelper.select_plan(page, 700)
            framework_logger.info(f"Plan selected: 700")

            # Continue button is disabled
            expect(confirmation_page.continue_enrollment_button).to_be_disabled()
            framework_logger.info(f"Continue button is disabled after changing plan")

            # Add paypal billing method
            EnrollmentHelper.add_paypal_billing(page)
            framework_logger.info(f"PayPal billing method added successfully")

            # Finish enrollment
            EnrollmentHelper.finish_enrollment_with_prepaid(page)
            framework_logger.info(f"Finished enrollment with prepaid")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page for tenant: {tenant_email}")

            # Verify prepaid value in Overview page
            DashboardHelper.verify_special_offer_value(page, 30)
            framework_logger.info(f"Prepaid value verified in Overview page")

            # Verify paypal information in Overview page
            expect(overview_page.paypal_info).to_be_visible()
            framework_logger.info(f"PayPal information is visible in Overview page")

            framework_logger.info(" C41519357 - Enroll with Prepaid code and Change plan PayPal flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the C41519357 flow: {e}\n{traceback.format_exc()}")
            raise e