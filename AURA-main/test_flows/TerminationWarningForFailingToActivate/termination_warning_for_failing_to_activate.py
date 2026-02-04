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
from helper.email_helper import EmailHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC="C38430179"
def termination_warning_for_failing_to_activate(stage_callback):
    framework_logger.info("=== C38430179 - Termination warning for failing to activate flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
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

            # And the user sees the confirmation email with subject "Your account will be canceled on"
            EmailHelper.sees_email_with_subject(tenant_email, subject="Your account will be canceled on")
            framework_logger.info(f"Received email with subject 'Your account will be canceled on'")

            # Verify notification events on Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_link_by_text_on_rails_admin(page, "automated_cancellation", "Notification events")
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Verified notification events on Rails Admin")
           
            # Verify notification events on Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_link_by_text_on_rails_admin(page, "automated_cancellation", "Notification events")
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "cancel_enrolled_warning_35months-i_ink")
            framework_logger.info("Verified notification events on Rails Admin")

            framework_logger.info("=== C38430179 - Termination warning for failing to activate flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e