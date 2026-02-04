from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.hpid_helper import HPIDHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def skip_tour_modal_login_for_second_time(stage_callback):
    framework_logger.info("=== C41227587 - Tour Modal Behavior After Sign Out flow started ===")  
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"Created II subscription for tenant: {tenant_email}")

    # First access - complete/skip tour
    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)
            overview_page = OverviewPage(page)

            # Login with a valid account and go to dashboard page for the first time
            DashboardHelper.access(page, tenant_email)
            framework_logger.info("Logged in with valid account and accessed dashboard page (first time)")
          
            
        except Exception as e:
            framework_logger.error(f"An error occurred during first access: {e}\n{traceback.format_exc()}")
            raise e

    # Second access - verify tour modal doesn't appear
    with PlaywrightManager() as page2:
        try:
            side_menu = DashboardSideMenuPage(page2)
            overview_page = OverviewPage(page2)
            
            # 3. Login with the same account and go to Overview page for the second time
            DashboardHelper.access(page2, tenant_email)
            framework_logger.info("Step 3: Logged in again with same account and accessed Overview page (second time)")

              # Go to Overview page and complete or skip the tour
            DashboardHelper.skips_all_but_tour_precondition(page2)            
            expect(overview_page.skip_tour).to_be_visible(timeout=30000)            
            DashboardHelper.skip_tour_modal(page2)
            framework_logger.info("Navigated to Overview page and verified Tour modal is displayed")
            
            # Sign out
            DashboardHelper.sign_out(page2)
            framework_logger.info("Signed out from account")

            DashboardHelper.access(page2, tenant_email)
            framework_logger.info("Logged in again with same account and accessed Overview page (second time)")
            
            # Verify the Tour modal is not shown again
            DashboardHelper.skips_all_but_tour_precondition(page2)
            DashboardHelper.verify_tour_modal_not_appears(page2)
            framework_logger.info("Tour modal is NOT displayed after completing/skipping tour")

            framework_logger.info("=== C41227587 - Tour Modal Behavior After Sign Out flow completed successfully ===")
            return tenant_email
            
        except Exception as e:
            framework_logger.error(f"An error occurred during second access: {e}\n{traceback.format_exc()}")
            raise e
