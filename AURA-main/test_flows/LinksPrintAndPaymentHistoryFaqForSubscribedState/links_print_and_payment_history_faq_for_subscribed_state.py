from helper.print_history_helper import PrintHistoryHelper
from helper.update_plan_helper import UpdatePlanHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.update_plan_page import UpdatePlanPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC="C44016157"
def links_print_and_payment_history_faq_for_subscribed_state(stage_callback):
    framework_logger.info("=== C44016157 - Print and Payment History FAQ for no-pens/ Update plan flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)
            update_plan = UpdatePlanPage(page)

            # Move subscription to subscribed
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Print History page
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Validate the FAQ on Smart Dashboard > Print and Payment History page
            PrintHistoryHelper.validate_faq_on_print_and_payment_history(page)
            framework_logger.info("Validated FAQ on Print and Payment History page")
            framework_logger.info("=== C44016157 - Print and Payment History FAQ for subscribed subscription ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
