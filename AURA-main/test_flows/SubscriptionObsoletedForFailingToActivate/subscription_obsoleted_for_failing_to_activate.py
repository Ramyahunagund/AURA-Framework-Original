from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def subscription_obsoleted_for_failing_to_activate(stage_callback):
    framework_logger.info("=== C38465559 - Subscription obsoleted for failing to activate (Printer is Online) flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        try:
            # Verify subscription state is subscribed_no_pens
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed_no_pens")

            # Event Shift 1095 days
            GeminiRAHelper.event_shift(page, event_shift="1095")
            framework_logger.info("Event shift updated")

            # Executes the resque job AutoCancellationNoticeNotifierJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["AutoCancellationNoticeNotifierJob"])
            framework_logger.info("Executed AutoCancellationNoticeNotifierJob")

            # Event Shift 31 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, event_shift="31")
            framework_logger.info("Event shift updated")

            # Executes the resque job ObsoleteAutoCancellationSubscriptionsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["ObsoleteAutoCancellationSubscriptionsJob"])
            framework_logger.info("Executed ObsoleteAutoCancellationSubscriptionsJob")

            # Access Dashboard for the first time
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Notifications page
            side_menu.my_account_menu_link.click()
            side_menu.notifications_submenu_link.click()
            framework_logger.info("Accessed Notifications page")

            # Verify cancellation confirmation notification is visible
            DashboardHelper.see_notification_on_dashboard(page, "Your cancellation confirmation")
            framework_logger.info("Verified cancellation confirmation notification is visible")

            # Verify notification events on Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_link_by_text_on_rails_admin(page, "automated_cancellation", "Notification events")
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "cancel_enrolled_36months-i_ink")
            framework_logger.info("Verified notification events on Rails Admin")
            framework_logger.info("=== C38465559 - Subscription obsoleted for failing to activate (Printer is Online) flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
