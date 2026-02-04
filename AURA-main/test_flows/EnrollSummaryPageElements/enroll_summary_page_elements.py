from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enroll_summary_page_elements(stage_callback):
    framework_logger.info("=== C44279920 - Enroll Summary Page elements started ===")
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
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            confirmation_page = ConfirmationPage(page)

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Choose hp checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Add Billing (Remove the billing step if not needed)
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            # Checks the Promo/Pin code link and apply 2freeinkusen code on confirmation page
            confirmation_page.enter_promo_or_pin_code_button.click()
            confirmation_page.close_modal_button.click()
            expect(confirmation_page.summary_benefits_header).to_be_visible(timeout=60000)
            confirmation_page.enter_promo_or_pin_code_button.click()
            confirmation_page.promotion_code_input.fill("2freeinkusen")
            confirmation_page.promotion_apply_button.click()
            confirmation_page.close_modal_button.click()
            framework_logger.info(f"Applied free months code on Confirmation page")

            # Validate redeemed months and credits
            EnrollmentHelper.validate_benefits_header(page, 3)
            framework_logger.info(f"Validated benefits header with 3 months")

            # Finish enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info(f"Finished enrollment with prepaid")

            framework_logger.info("=== C44279920 - Enroll Summary Page elements finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
