from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def notifications_extended_prepaid_warning(stage_callback):
    framework_logger.info("=== C49558973 - Notifications extended - Prepaid warning started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription status updated to 'subscribed'")

            # First billing cycle (shift 31 and page tally 100)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"First billing cycle completed")

            # Open instant ink dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page")

            # Expand My Account Menu and click on Notifications
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.expand_my_account_menu()
            dashboard_side_menu_page.click_notifications()
            framework_logger.info("Accessed Smart Dashboard Notifications page")

            # Prepaid credit Insufficient warning is displayed
            assert "Prepaid credit Insufficient in two months" in page.content()
            framework_logger.info("Suspended text is visible")

            # Click on the prepaidcard_insufficient link in the Notification events
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "prepaidcard_insufficient", "Notification events")
            framework_logger.info("Accessed payment_issue from Notification events")

            # Sees Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Payment state is complete")

            # Third billing cycle (shift 31 and page tally 100)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Third billing cycle completed")

            # Open instant ink dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page")

            # Expand My Account Menu and click on Notifications
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.expand_my_account_menu()
            dashboard_side_menu_page.click_notifications()
            framework_logger.info("Accessed Smart Dashboard Notifications page")

            # Prepaid credit Insufficient in next month is displayed
            assert "Prepaid credit Insufficient next month" in page.content()
            framework_logger.info("Suspended text is visible")

            # Click on the prepaidcard_insufficient link in the Notification events
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "prepaidcard_insufficient", "Notification events")
            framework_logger.info("Accessed payment_issue from Notification events")

            # Sees Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Payment state is complete")

            # Fourth billing cycle (shift 31 and page tally 100)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Fourth billing cycle completed")

            # Open instant ink dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page")

            # Expand My Account Menu and click on Notifications
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.expand_my_account_menu()
            dashboard_side_menu_page.click_notifications()
            framework_logger.info("Accessed Smart Dashboard Notifications page")

            # Prepaid credit Insufficient in next month is displayed
            assert "Prepaid credit insufficient" in page.content()
            framework_logger.info("Suspended text is visible")

            # Click on the prepaidcard_insufficient link in the Notification events
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "prepaidcard_insufficient", "Notification events")
            framework_logger.info("Accessed payment_issue from Notification events")

            # Sees Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Payment state is complete")

            
            framework_logger.info("=== C49558973 - Notifications extended - Prepaid warning finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow C42407561: {e}\n{traceback.format_exc()}")
            raise e
