from pages.cancellation_page import CancellationPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from playwright.sync_api import expect
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def cancellation_timeline_page_section3(stage_callback):
    framework_logger.info("=== C40797085 - Cancellation Timeline page visualization flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        cancellation_page = CancellationPage(page)

        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")


            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Go to Cancellation Timeline page
            UpdatePlanHelper.cancellation_subscription(page,callback=stage_callback)
            framework_logger.info("Navigated to Cancellation Timeline page")
            stage_callback("cancellation_timelinepage", page, screenshot_only=True)



            # restore icon printer replacement icons are displayed well
            #stage_callback("context_name", page, screenshot_only=True)
            # stage_callback("context_name", page)


            # Verify 'Change your mind' section
            CancellationPlanHelper.verify_change_your_mind_section(page)
            framework_logger.info("Verified the 'Change your mind' section on Cancellation Timeline page")


            framework_logger.info("=== C40797085 - Cancellation Timeline page visualization flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")