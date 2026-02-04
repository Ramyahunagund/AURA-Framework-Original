from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.print_history_page import PrintHistoryPage
from playwright.sync_api import expect
import urllib3
import test_flows_common.test_flows_common as common
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC = "C43727713"
def pause_plan_banner_on_status_card_with_paused_plan_on_overview_page(stage_callback):
    framework_logger.info("=== C43727713 - Rollover Pages progress bar with free months flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        print_history_page = PrintHistoryPage(page)
        side_menu = DashboardSideMenuPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Free months removed from tenant")
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status updated to 'subscribed'")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Pause plan for 2 months on Overview page
            DashboardHelper.pause_plan(page, 2)
            framework_logger.info(f"Paused plan for 2 months on Overview page")

            # Shift subscription for 32 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            framework_logger.info("Shifted subscription for 32 days")

            # Access Dashboard
            DashboardHelper.access(page)
            side_menu.click_overview()
            overview_page = OverviewPage(page)
            overview_page.wait.page_title(timeout=60000)

            DashboardHelper.verify_pages_used(page, "complimentary", 0, 10)
            DashboardHelper.verify_pages_on_tooltip(page, "complimentary", 0, 10)
            framework_logger.info("Complimentary pages verified as 0 of 10 used on Overview page")


            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            framework_logger.info(f"access_billing_summary_page")
            GeminiRAHelper.calculate_and_define_page_tally(page, "13")
            framework_logger.info("Calculated and defined page tally as 13")

            # Access Dashboard
            DashboardHelper.access(page)
            side_menu.click_overview()
            overview_page = OverviewPage(page)
            overview_page.wait.overview_page_title()

            DashboardHelper.verify_pages_used(page, "complimentary", 10, 10)
            DashboardHelper.verify_pages_on_tooltip(page, "complimentary", 10, 10)
            DashboardHelper.verify_pages_used(page, "additional", 3, 10)
            framework_logger.info("Complimentary pages verified as 10 of 10 used and additional pages as 3 of 10 used on Overview page")

            framework_logger.info("=== C43727713 - Flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow C43727713: {e}\n{traceback.format_exc()}")
            raise e
