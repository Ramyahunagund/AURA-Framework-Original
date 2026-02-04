from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from helper.print_history_helper import PrintHistoryHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def welcome_notification_event(stage_callback):
    framework_logger.info("=== C35466773 / C27590132 - Welcome notification event flow started ===")

    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"Created subscription for tenant: {tenant_email}")

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        try:
            # Access the subscription
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info("Accessed subscription")

            # Click on the accountsetup notification event to check its status
            GeminiRAHelper.click_link_by_text_on_rails_admin(page, "account_setup", "Notification events")
            framework_logger.info("Clicked on accountsetup notification event")

            # Verify the status is "complete"
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Verified notification event status is 'complete'")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Verify Welcome to HP Instant Ink message is displayed well in Bell Notifications section
            DashboardHelper.see_notification_on_bell_icon(page, "Welcome to HP Instant Ink")
            framework_logger.info("Verified 'Welcome to HP Instant Ink' notification in bell icon")

            # Access Notifications
            side_menu.expand_my_account_menu()
            side_menu.click_notifications()
            framework_logger.info("Accessed Smart Dashboard Notifications page")

            # Verify Welcome to HP Instant Ink message is shown in notifications section
            DashboardHelper.see_notification_on_dashboard(page, "Welcome to HP Instant Ink")
            framework_logger.info("Verified 'Welcome to HP Instant Ink' notification on Notifications page")

            # Access Print and Payment History
            side_menu.click_print_history()
            framework_logger.info("Accessed Print and Payment History page")

            # Verify the activity detail is displayed in Print and Payment History section
            PrintHistoryHelper.see_notification_on_print_history(page, "HP Instant Ink Service Started")
            framework_logger.info("Verified activity detail in Print and Payment History section")

            framework_logger.info("=== C35466773 / C27590132 - Welcome notification event flow finished successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e