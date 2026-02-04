import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ink_web_change_plan_during_enrollment_flow(stage_callback):
    framework_logger.info("=== C40671269 - Ink Web - Change Plan during enrollment flow started ===")
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
            framework_logger.info(f"Signed in with email: {tenant_email}")

            # Printer selector
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # Accept automatic printer updates
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Select plan 50
            EnrollmentHelper.select_plan(page, 50)
            framework_logger.info(f"Plan selected: 50")

            # Select plan 300
            EnrollmentHelper.select_plan(page, 300)
            framework_logger.info(f"Plan selected: 300")

            # Verify selected plan on card is 300
            EnrollmentHelper.verify_selected_plan_on_card(page, 300)
            framework_logger.info(f"Verified selected plan on card: 300")

            # Select plan 100
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Verify selected plan on card is 100
            EnrollmentHelper.verify_selected_plan_on_card(page, 100)
            framework_logger.info(f"Verified selected plan on card: 100")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing added")

            # Finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Verify plan details card on Overview page shows plan 100
            DashboardHelper.verify_plan_pages_on_plan_details_card(page, "100", "Overview")
            framework_logger.info(f"Verified plan details card on Overview page shows plan 100")

            # Access Update Plan page
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.click_update_plan()

            # Verify plan details card on Update Plan page shows plan 100
            DashboardHelper.verify_plan_pages_on_plan_details_card(page, "100", "Update Plan")
            framework_logger.info(f"Verified plan details card on Update Plan page shows plan 100")

            # Access Print History page
            dashboard_side_menu_page.click_print_history()
            framework_logger.info(f"Opened Print History page")

            # Verify plan details card on Print History page shows plan 100
            DashboardHelper.verify_plan_pages_on_plan_details_card(page, "100", "Print History")
            framework_logger.info(f"Verified plan details card on Print History page shows plan 100")

            framework_logger.info("=== C40671269 - Ink Web - Change Plan during enrollment flow completed ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
