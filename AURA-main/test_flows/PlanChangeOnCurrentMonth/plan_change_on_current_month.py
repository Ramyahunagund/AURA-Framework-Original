from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.ra_base_helper import RABaseHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def plan_change_on_current_month(stage_callback):
    framework_logger.info("=== C52050947 - Plan Change on current month flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        update_plan = UpdatePlanPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status changed to 'subscribed'")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")

            # Click to change plan to the fifth plan on Update Plan page
            UpdatePlanHelper.select_plan_by_position(page, 5)
            framework_logger.info("Selected the fifth plan")

            # Select to upgrade to the next month on upgrade modal
            update_plan.upgrade_current_month.first.click()
            framework_logger.info("Selected Upgrade Next Month option on Upgrade Modal")
        
            # Click change plan button on upgrade modal
            update_plan.change_plan_button.click()
            expect(update_plan.upgrade_plan_confirmation).not_to_be_visible(timeout=30000)
            framework_logger.info("Clicked Change Plan button on Upgrade Modal")
            
            # Access Notifications Menu
            side_menu.my_account_menu_link.click()
            side_menu.click_notifications()
            framework_logger.info("Accessed Notifications page")

            # See "This change is effective" on Notification page
            DashboardHelper.see_notification_on_dashboard(page, "This change is effective")
            framework_logger.info("Verified notification 'This change is effective' is present")

            # Access Print History link
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # See "Plan change requested: HP Instant Ink service" notification on Print History card
            PrintHistoryHelper.see_notification_on_print_history(page, "Plan changed:")
            framework_logger.info("Verified notification 'Plan change requested: HP Instant Ink service' is present")

            # Access Subscription page in Rails Admin
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info("Accessed Subscription page in Rails Admin")

            # Click link with text plan_change in the Notification events
            RABaseHelper.access_link_by_title(page, "plan_change", "Notification events")
            framework_logger.info("Accessed plan_change page from Notification events")

            # See Status equals to complete on Plan Change page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")

            framework_logger.info("=== C52050947 - Plan Change on current month flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
