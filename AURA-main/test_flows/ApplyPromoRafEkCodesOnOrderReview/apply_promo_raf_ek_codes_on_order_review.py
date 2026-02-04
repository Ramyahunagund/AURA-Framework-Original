import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from pages.confirmation_page import ConfirmationPage
from pages.overview_page import OverviewPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC="C41351106"
def apply_promo_raf_ek_codes_on_order_review(stage_callback):
    framework_logger.info("=== apply_promo_raf_ek_codes_on_order_review started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")
    with PlaywrightManager() as page:
        page = common.create_hpid(page)
        stage_callback("landing_page", page)
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer and add address
        common.create_and_claim_virtual_printer_and_add_address()
    with PlaywrightManager() as page:
        try:
            # start enrollment 
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")    

            benefits = EnrollmentHelper.get_redeemed_months_and_credits(page)

            prepaid = common.get_offer(GlobalState.country_code, "prepaid")
            identifier = prepaid.get("identifier")
            if not identifier:
                raise ValueError(f"No identifier found for region: {GlobalState.country_code}")
            prepaid_code = common.offer_request(identifier)
            
            prepaid_value = int(prepaid.get("amountCents"))/ 100
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, prepaid_value)

            # change plans
            EnrollmentHelper.select_plan(page, 300)
            framework_logger.info(f"Plan selected: 300")
            
            # validate again
            confirmation_page = ConfirmationPage(page)
            confirmation_page.enter_promo_or_pin_code_button.click()
            
            EnrollmentHelper.validate_promotion(page, confirmation_page.elements.prepaid_value, prepaid_value)
            confirmation_page.close_modal_button.click()

            offer = common.get_offer(GlobalState.country_code)
            identifier = offer.get("identifier")
            if not identifier:
                raise ValueError(f"No identifier found for region: {GlobalState.country_code}")

            ek_code = common.offer_request(identifier)
            EnrollmentHelper.apply_and_validate_ek_code(page, ek_code)
            benefits += int(offer.get("months"))

            EnrollmentHelper.validate_benefits_header(page, benefits)

            EnrollmentHelper.apply_and_validate_promo_code(page, "freeinkautonew2025")
            benefits += 1
            EnrollmentHelper.validate_benefits_header(page, benefits)

            EnrollmentHelper.apply_and_validate_raf_code(page, "2nbdy7")
            benefits += 1            
            EnrollmentHelper.validate_benefits_header(page, benefits)

            # Finish enrollment flow
            EnrollmentHelper.finish_enrollment_with_prepaid(page)
            framework_logger.info("Enrollment flow finished successfully")

            DashboardHelper.first_access(page, tenant_email)

            DashboardHelper.verify_free_months_value(page, benefits)

            DashboardHelper.verify_special_offer_value(page, prepaid_value)

            framework_logger.info("apply_promo_raf_ek_codes_on_order_review completed successfully")

        except Exception as e:
            framework_logger.error(f"An error occurred during the ii_flow_with_prepaid flow: {e}\n{traceback.format_exc()}")
            raise e
        except Exception as e:
            framework_logger.error(f"An error occurred during the ii_flow_with_prepaid: {e}\n{traceback.format_exc()}")
