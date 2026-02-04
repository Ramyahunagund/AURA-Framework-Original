from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.update_plan_helper import UpdatePlanHelper
from pages.update_plan_page import UpdatePlanPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.gemini_ra_helper import GeminiRAHelper
from playwright.sync_api import expect
import time
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def welcome_back_notification(stage_callback): 
    framework_logger.info("=== C57490042 - Welcome back notification flow started ===")

    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"Created initial subscription for tenant: {tenant_email}")
    
    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)
            update_plan_page = UpdatePlanPage(page)

            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard and skip preconditions
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard and skipped preconditions")

            # Navigate to Change Plan and Cancel Subscription
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Change Plan page")

            # Cancel subscription - this will navigate to cancellation page
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("Initiated subscription cancellation")

            # Navigate to Plan Overview
            side_menu.click_overview()
            framework_logger.info("Navigated to Plan Overview page")

            # Wait 30 seconds as specified in scenario
            time.sleep(30)
            framework_logger.info("Waited 30 seconds")

            # Click on Keep Enrollment (Welcome back scenario)
            DashboardHelper.keep_subscription(page)
            framework_logger.info("Clicked Keep Enrollment - Welcome back scenario")
            
            # Access Notifications page
            side_menu.expand_my_account_menu()
            side_menu.click_notifications()
            framework_logger.info("Accessed Smart Dashboard Notifications page")
            
            # Verify "Welcome back to HP Instant Ink" notification
            DashboardHelper.see_notification_on_dashboard(page, "Welcome back to HP Instant Ink")
            framework_logger.info("Verified 'Welcome back to HP Instant Ink' notification")

            # Verify Rails Admin notification event
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_link_by_text_on_rails_admin(page, "accountsetup_returnback", "Notification events")
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "sent")
            framework_logger.info("Verified accountsetup_returnback notification event in Rails Admin")

            framework_logger.info("=== C57490042 - Welcome back notification flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the welcome back notification flow: {e}\n{traceback.format_exc()}")
            raise e
        