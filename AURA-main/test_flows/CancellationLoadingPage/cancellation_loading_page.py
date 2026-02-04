from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.cancellation_page import CancellationPage
from pages.update_plan_page import UpdatePlanPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancellation_loading_page(stage_callback):
    framework_logger.info("=== C43163814 - Cancellation loading page flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)
        
        try:
            # Move to subscribed state and remove free months if needed
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Access HP Smart Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"User signs into HP Smart and opens Smart Dashboard page")

            # Navigate to Update Plan page first
            side_menu.click_update_plan()
            framework_logger.info("Navigated to Update Plan page")

            # Click cancel subscription button
            update_plan_page = UpdatePlanPage(page)
            update_plan_page.cancel_instant_ink.click()
            framework_logger.info("Clicked Cancel Instant Ink button")

            # Click confirm cancellation button
            expect(cancellation_page.confirm_cancellation_button).to_be_visible()
            cancellation_page.confirm_cancellation_button.click()
            framework_logger.info("Clicked Confirm Cancellation button")

            # verify the title on Cancellation Loading Page
            expect(cancellation_page.cancellation_card).to_be_visible(timeout=5000)
            framework_logger.info("Verified the title Cancellation Loading Page")

            # Verify the printer information on Cancellation Loading Page
            expect(cancellation_page.printer_img).to_be_visible(timeout=3000)
            expect(cancellation_page.printer_info_name).to_be_visible(timeout=3000)
            expect(cancellation_page.printer_info_serial).to_be_visible(timeout=3000)
            framework_logger.info("Verified printer information on Cancellation Loading Page")

            # Verify the cancellation animation on Cancellation Loading Page
            expect(cancellation_page.cancellation_animation).to_be_visible(timeout=3000)
            framework_logger.info("Verified the cancellation animation on Cancellation Loading Page")
          
            # Redirected to the Cancellation Timeline page
            expect(cancellation_page.whats_happens_next).to_be_visible(timeout=60000)
            framework_logger.info("User is redirected to the Cancellation Timeline page")

            framework_logger.info("=== C43163814 - Cancellation loading page flow finished successfully ===")
            
        except Exception as e:
            framework_logger.error(f"An error occurred during the Cancellation Loading Page flow: {e}\n{traceback.format_exc()}")
            raise e
     
