from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.privacy_banner_page import PrivacyBannerPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
import urllib3
import traceback
from playwright.sync_api import sync_playwright
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
import test_flows_common.test_flows_common as common
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def skip_tour_with_switch_with_multiple_subscriptions(stage_callback):
    framework_logger.info("=== C51985957 - Skip tour with Switch with Multiple subscriptions ===")
    tenant_email = create_ii_subscription(stage_callback)
    common.create_and_claim_virtual_printer()
    if not tenant_email:
        raise ValueError("Error creating the first subscription")
    with PlaywrightManager() as page:
        try:
             # start enrollment 
            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # sign in method
            HPIDHelper.complete_sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in")

            # accept TOS
            EnrollmentHelper.accept_terms_of_service(page)
            framework_logger.info(f"Terms of Services accepted")  

            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            # Access Dashboard for the first time
            DashboardHelper.access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            DashboardHelper.accept_banner_and_access_overview_page(page)
            framework_logger.info("Accessed Overview page")

            # Skip all but tour precondition
            DashboardHelper.skips_all_but_tour_precondition(page)
            framework_logger.info("Skipped all but tour modal")

            # Skip Tour modal on Overview page
            DashboardHelper.skip_tour_modal(page)
            framework_logger.info("Skipped tour modal")

            overview_page = OverviewPage(page)
            overview_page.printer_selector.click()
            overview_page.printer_selector_printers.nth(1).click()

            # Verify Tour modal is not visible
            DashboardHelper.verify_tour_modal_not_appears(page)
            framework_logger.info("Verified Tour modal is not visible on Overview page")
            framework_logger.info("=== C51985957 - Skip tour with Switch with Multiple subscriptions ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()