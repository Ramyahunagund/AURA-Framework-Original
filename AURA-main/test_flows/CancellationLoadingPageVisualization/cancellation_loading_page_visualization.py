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


def cancellation_loading_page_visualization(stage_callback):
    framework_logger.info("=== C40797082 - Cancellation loading page visualization flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)
        dashboard_page = UpdatePlanPage(page)

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

            # Go to Cancellation Timeline page
            dashboard_page.cancel_instant_ink.wait_for(state="visible", timeout=90000)
            dashboard_page.cancel_instant_ink.click()
            cancellation_page.confirm_cancellation_button.wait_for(state="visible", timeout=120000)
            cancellation_page.confirm_cancellation_button.click()
            try:
                expect(cancellation_page.cancellation_loading_page_title).to_be_visible(timeout=30000)
            except Exception:
                cancellation_page.confirm_cancellation_button.click()


            #Verify the user stays on the loading page for at least 4s
            CancellationPlanHelper.verify_user_stays_on_loading_page_for_at_least_4s(page)
            framework_logger.info("Verified the user stays on the loading page for at least 4s")

            framework_logger.info("=== C40797082 - Cancellation loading page visualization flow finished successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the Cancellation Loading Page flow: {e}\n{traceback.format_exc()}")
            raise e