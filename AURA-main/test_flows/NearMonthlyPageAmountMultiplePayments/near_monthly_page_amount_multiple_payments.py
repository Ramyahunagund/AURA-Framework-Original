from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.notifications_page import NotificationsPage
from playwright.sync_api import expect
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def near_monthly_page_amount_multiple_payments(stage_callback):
    framework_logger.info("=== C51821170 - Near Monthly Page Amount Multiple Payments flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        notifications_page = NotificationsPage(page)
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Print 98 additional pages by RTP
            GeminiRAHelper.add_pages_by_rtp(page, "98")
            framework_logger.info(f"Added 98 pages by RTP")

            # Access subscription
            links = RABaseHelper.get_links_by_title(page, "Current subscription")
            links.first.click()
            framework_logger.info(f"Accessed current subscription")

            # Click link with text near_availablepages in the Notification events
            RABaseHelper.access_link_by_title(page, "near_availablepages", "Notification events")
            framework_logger.info(f"Accessed near_availablepages")

            # Sees Status equals to complete on near_availablepages page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click notification icon
            notifications_page.notifications_icon.click()
            framework_logger.info(f"Clicked on notifications icon")

            # See notification on Smart Dashboard
            expect(notifications_page.notifications_box).to_be_visible()
            framework_logger.info(f"Notifications box is visible")

            framework_logger.info("=== C51821170 - Near Monthly Page Amount Multiple Payments flow successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
