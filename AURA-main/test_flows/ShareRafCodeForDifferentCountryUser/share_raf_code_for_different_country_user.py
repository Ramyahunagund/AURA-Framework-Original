import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def share_raf_code_for_different_country_user(stage_callback):
    framework_logger.info("=== C43905946 - Share RaF code for different country user started ===")
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

        # 2) Claim virtual printer and add address
        common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        try:
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

            price = None
            try:
                price = EnrollmentHelper.get_total_price_by_plan_card(page)
            except Exception:
                framework_logger.info(f"Failed to get price from plan card")

            # billing
            EnrollmentHelper.add_billing(page, plan_value=price)
            framework_logger.info(f"Billing added")

            benefits = EnrollmentHelper.get_redeemed_months_and_credits(page)
                      
            # validate RAF code        
            EnrollmentHelper.apply_and_validate_raf_code(page, "svgb68")
            benefits += 1
            EnrollmentHelper.validate_benefits_header(page, benefits)

            # billing
            EnrollmentHelper.add_billing(page, payment_method="credit_card_master", plan_value=price)
            framework_logger.info(f"Billing added")

            # finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            framework_logger.info("=== C43905946 - Share RaF code for different country user finished ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during browser reopen phase: {e}\n{traceback.format_exc()}")
            raise e