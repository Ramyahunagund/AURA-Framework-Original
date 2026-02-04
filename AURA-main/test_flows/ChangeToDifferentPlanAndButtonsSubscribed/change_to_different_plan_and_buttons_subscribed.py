from pages.cancellation_page import CancellationPage
from pages.overview_page import OverviewPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def change_to_different_plan_and_buttons_subscribed(stage_callback):
    framework_logger.info("=== C42774978 - Change to different plan + buttons (subscribed) flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)
            cancellation_page = CancellationPage(page)

            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Verify the Change Plan modal and close it
            DashboardHelper.verify_and_close_change_plan_modal(page)
            framework_logger.info(f"Change Plan modal verified and closed")

             # Click to keep the subscription on Cancellation Summary Page
            cancellation_page.keep_enrollment_button.click()
            framework_logger.info("Clicked to keep the subscription on Cancellation Summary Page")

            # Click on Cancel Instant Ink on Overview page
            overview_page.plan_details_card.wait_for(timeout=90000)
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            # Click to confirm the cancellation on Cancellation Summary Page
            cancellation_page.confirm_cancellation_button.click()
            framework_logger.info("Clicked to confirm the cancellation on Cancellation Summary Page")
            framework_logger.info("=== C42774978 - Change to different plan + buttons (subscribed) flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
