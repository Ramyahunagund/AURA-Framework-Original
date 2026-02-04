from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.sign_in_helper import HPIDHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ink_web_enrollment_close_browser(stage_callback):
    framework_logger.info("=== C40644375 - Ink Web Enrollment - Close browser during enrollment flow started ===")
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

            # finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            # Close browser to simulate interruption
            page.close()
            framework_logger.info("Browser closed after enrollment completion")

        except Exception as e:
            framework_logger.error(f"An error occurred during enrollment phase: {e}\n{traceback.format_exc()}")
            raise e

    # Simulate reopening browser after close
    with PlaywrightManager() as page:
        try:
            # First access to dashboard after enrollment
            DashboardHelper.access(page, tenant_email)
            framework_logger.info("First access to dashboard completed successfully")

            framework_logger.info("=== C40644375 - Ink Web Enrollment - Close browser during enrollment flow finished ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during browser reopen phase: {e}\n{traceback.format_exc()}")
            raise e
