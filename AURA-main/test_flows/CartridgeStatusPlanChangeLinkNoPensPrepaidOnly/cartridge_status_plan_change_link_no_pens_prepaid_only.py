import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


TC="C42481707"
def cartridge_status_plan_change_link_no_pens_prepaid_only(stage_callback):
    framework_logger.info("=== cartridge_status_plan_change_link_no_pens_prepaid_only started ===")
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

        # 2) Claim virtual printer and add address
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

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            benefits = EnrollmentHelper.get_redeemed_months_and_credits(page)

            prepaid = common.get_offer(GlobalState.country_code, "prepaid")
            identifier = prepaid.get("identifier")
            if not identifier:
                raise ValueError(f"No identifier found for region: {GlobalState.country_code}")
            prepaid_code = common.offer_request(identifier)
            
            prepaid_value = int(prepaid.get("amountCents"))/ 100
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, prepaid_value)

            # Add Billing (Remove the billing step if not needed)
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            # Finish enrollment flow
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment  finished successfully")

            DashboardHelper.first_access(page, tenant_email)

            DashboardHelper.verify_free_months_value(page, benefits)

            DashboardHelper.verify_special_offer_value(page, prepaid_value)
           
            DashboardHelper.verify_plan_value(page, 100)
            
            overview_page = OverviewPage(page)
            assert overview_page.redeem_code_link.is_visible(), "Redeem code link is not visible"
            assert overview_page.cancel_instant_ink.is_visible(), "Cancel link is not visible"

            overview_page.change_plan_link.click()

            update_plan_page = UpdatePlanPage(page)
            update_plan_page.wait.page_title(timeout=60000)
            
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.click_overview()

            no_pens = overview_page.wait.no_pens_status(timeout=60000)
            assert no_pens.is_visible(), "No Pens status is not visible"

            framework_logger.info("Test completed successfully: verified Cartridge status, Plan, Change plan link and no_pens card in a prepaid-only subscription")

        except Exception as e:
            framework_logger.error(f"Test with Error: {e}\n{traceback.format_exc()}")
            raise e
