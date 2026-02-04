from datetime import datetime, timedelta
from helper.ra_base_helper import RABaseHelper
from pages import dashboard_side_menu_page
from pages.notifications_page import NotificationsPage
from pages.printers_page import PrintersPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.print_history_page import PrintHistoryPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC="C38330518"
def subscription_with_subscribed_no_pens_when_printer_is_online(stage_callback):
    framework_logger.info("=== C38330518 - View links for Subscription with subscribed status and free months flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        print_history = PrintHistoryPage(page)
        update_plan = UpdatePlanPage(page)
        try:
            # Shift subscription for 1095 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "1095")
            framework_logger.info("Shifted subscription for 1095 days")

            # Executes the resque job AutoCancellationNoticeNotifierJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["AutoCancellationNoticeNotifierJob"])
            framework_logger.info("Executed AutoCancellationNoticeNotifierJob")

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed_no_pens")


            links = RABaseHelper.get_links_by_title(page, "Auto cancellation notices")
            links.first.click()
            RABaseHelper.wait_page_to_load(page, "Auto cancellation notice")
            cancellation_date = RABaseHelper.get_field_text_by_title(page, "Cancellation date")
            cancellation_datetime = datetime.strptime(cancellation_date, "%Y/%m/%d %I:%M:%S %p")
            current_date = datetime.now()
            expected_cancellation_date = current_date + timedelta(days=31)

            # Compare cancellation date
            assert cancellation_datetime.date() == expected_cancellation_date.date(), (
                f"Cancellation date should be exactly 31 days from today. "
                f"Expected: {expected_cancellation_date.strftime('%Y/%m/%d')}, "
                f"but got: {cancellation_datetime.strftime('%Y/%m/%d')}"
            )
            framework_logger.info("Verified Auto cancellation notice and cancellation date")

            # Access Smart Dashboard and skip preconditions
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")
            
            # Verify printer is online
            side_menu.printers_menu_link.click()
            printers_page = PrintersPage(page)
            printers_page.wait.printer_online(timeout=60000)
            expect(printers_page.printer_online).to_be_visible(timeout=30000)
            framework_logger.info("Accessed Printers page and verified printer is online")
  
            # Verify cancellation notification
            side_menu.click_notifications()
            framework_logger.info("Clicked on Notifications in side menu")
            notifications_page = NotificationsPage(page)

            cancellation_notification = notifications_page.table_row.nth(1)
            notification_cancellation_date = common.extract_date_from_text(cancellation_notification.inner_text())
            cancellation_datetime = common.parse_flexible_date(cancellation_date)

            cancellation_rounded = cancellation_datetime.replace(second=0, microsecond=0)
            notification_rounded = notification_cancellation_date.replace(second=0, microsecond=0)
            assert cancellation_rounded == notification_rounded, (
                f"Expected cancellation date: {cancellation_rounded}, "
                f"but got: {notification_rounded}"
            )
            framework_logger.info("Verified cancellation notification date")

            # Shift 20 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "20")
            framework_logger.info("Shifted subscription back to 20 days")

            # Executes the resque job ObsoleteAutoCancellationSubscriptionsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["ObsoleteAutoCancellationSubscriptionsJob"])
            framework_logger.info("Executed ObsoleteAutoCancellationSubscriptionsJob")

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed_no_pens")
            GeminiRAHelper.event_shift(page, "12")
            framework_logger.info("Shifted subscription back to 12 days")

            # Executes the resque job ObsoleteAutoCancellationSubscriptionsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["ObsoleteAutoCancellationSubscriptionsJob"])
            framework_logger.info("Executed ObsoleteAutoCancellationSubscriptionsJob")

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "obsolete")
            framework_logger.info("Verified subscription state is obsolete")

            DashboardHelper.access(page, tenant_email)
            side_menu.click_overview()
            overview_page.wait.page_title(timeout=60000)
            expect(overview_page.no_active_plans).to_be_visible(timeout=30000)

            framework_logger.info("=== C38330518 - View links for Subscription with subscribed status and free months flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e