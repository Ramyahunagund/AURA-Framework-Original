from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from pages.thank_you_page import ThankYouPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enrollment_flow_is_longer_than15_minutes(stage_callback):
    framework_logger.info("=== C44812141 - Enrollment flow is longer than 15 minutes flow started ===")
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
        thank_you_page = ThankYouPage(page)
        try:
            # Start enrollment and sign in
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            framework_logger.info(f"Enrollment started and signed in with email: {tenant_email}")

            # Wait 180 seconds
            framework_logger.info("Waiting for 180 seconds to simulate a long enrollment process...")
            time.sleep(180)
            framework_logger.info("Waited 180 seconds")

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Wait 180 seconds
            framework_logger.info("Waiting for 180 seconds to simulate a long enrollment process...")
            time.sleep(180)
            framework_logger.info("Waited 180 seconds")
            
            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Wait 180 seconds
            framework_logger.info("Waiting for 180 seconds to simulate a long enrollment process...")
            time.sleep(180)
            framework_logger.info("Waited 180 seconds")

            # Choose hp checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Wait 180 seconds
            framework_logger.info("Waiting for 180 seconds to simulate a long enrollment process...")
            time.sleep(180)
            framework_logger.info("Waited 180 seconds")

            # Add billing method
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing method added successfully")

            # Click on continue enrollment on confirmation page
            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            framework_logger.info(f"Clicked on Continue Enrollment button")

            # Wait 190 seconds
            framework_logger.info("Waiting for 190 seconds to simulate a long enrollment process...")
            time.sleep(190)
            framework_logger.info("Waited 190 seconds")

            # Accept terms and confirm enroll
            confirmation_page.terms_agreement_checkbox.wait_for(state="visible", timeout=60000)
            confirmation_page.terms_agreement_checkbox.check(force=True)
            confirmation_page.enroll_button.click()
            thank_you_page.continue_button.wait_for(state="visible", timeout=60000)
            framework_logger.info(f"Enrollment confirmed and Thank You page displayed")

            framework_logger.info("=== C44812141 - Enrollment flow is longer than 15 minutes flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e