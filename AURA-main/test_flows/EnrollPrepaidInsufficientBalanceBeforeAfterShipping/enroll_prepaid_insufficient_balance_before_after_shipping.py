import time
from playwright.sync_api import sync_playwright
from tenacity import sleep
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState, framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.hpid_helper import HPIDHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from pages.confirmation_page import ConfirmationPage
from pages.overview_page import OverviewPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
from playwright.sync_api import expect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC="C38970869" 
def enroll_prepaid_insufficient_balance_before_after_shipping(stage_callback):
    framework_logger.info("=== Test started ===")
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

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 700)
            framework_logger.info(f"Plan selected: 700")

            EnrollmentHelper.choose_hp_checkout(page)
            
            # Add Billing button is disabled
            confirmation_page = ConfirmationPage(page)
            expect(confirmation_page.add_billing_button).to_be_disabled(timeout=30000)

            # Add prepaid code
            prepaid = common.get_offer(GlobalState.country_code, "prepaid", amount_less=1500)
            prepaid_code = common.offer_request(prepaid["identifier"])
            framework_logger.info(f"Prepaid code fetched: {prepaid_code}")
            amount = prepaid["amountCents"] / 100
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, amount, billing_message=True)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")

            # Validate redeemed months and credits
            benefits = 3
            EnrollmentHelper.validate_benefits_header(page, benefits)

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Add Billing button is enabled
            expect(confirmation_page.add_billing_button).to_be_enabled(timeout=30000)

            # billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing added successfully")

            # Add prepaid code
            prepaid = common.get_offer(GlobalState.country_code, "prepaid", amount_less=1500)
            prepaid_code = common.offer_request(prepaid["identifier"])
            framework_logger.info(f"Prepaid code fetched: {prepaid_code}")
            amount += (prepaid["amountCents"] / 100)
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, prepaid["amountCents"] / 100, billing_message=False)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")

            EnrollmentHelper.validate_benefits_header(page, benefits)

            # Finish enrollment flow
            EnrollmentHelper.finish_enrollment_with_prepaid(page)
            framework_logger.info("Enrollment flow finished successfully")

            DashboardHelper.first_access(page, tenant_email)

            DashboardHelper.verify_free_months_value(page, benefits)

            DashboardHelper.verify_special_offer_value(page, amount)
        
            framework_logger.info("=== enroll_with_sufficient_prepaid_code_before_and_after_shipping completed successfully ===") 
        
        except Exception as e:
            framework_logger.error(f"An error occurred during the printer_replacement_with_sufficient_prepaidd flow: {e}\n{traceback.format_exc()}")
            raise e
    