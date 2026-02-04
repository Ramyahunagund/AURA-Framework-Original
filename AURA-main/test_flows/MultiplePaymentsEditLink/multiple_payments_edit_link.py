import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from playwright.sync_api import expect
from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def multiple_payments_edit_link(stage_callback):
    framework_logger.info("=== Multiple Payments - Edit link flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # Claim virtual printer and add address
        common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        try:
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            framework_logger.info(f"Enrollment started and signed in with email: {tenant_email}")

            # Printer selector
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # Accept automatic printer updates
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Select Plan
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing added")

            # Edit Billing and add another payment method - Paypal
            EnrollmentHelper.edit_billing_for_paypal(page)
            framework_logger.info(f"Billing updated to PayPal")

            # Finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            framework_logger.info("=== C40233835 - Multiple Payments - Edit link completed ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()