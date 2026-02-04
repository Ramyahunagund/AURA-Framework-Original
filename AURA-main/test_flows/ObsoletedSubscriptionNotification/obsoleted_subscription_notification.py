from datetime import datetime, timedelta
import re
from helper.ra_base_helper import RABaseHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.cancellation_timeline_page import CancellationTimelinePage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.print_history_page import PrintHistoryPage
from pages.update_plan_page import UpdatePlanPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from pages.shipping_billing_page import ShippingBillingPage
from pages.printer_selection_page import PrinterSelectionPage
from test_flows.EnrollmentOOBE.enrollment_oobe import enrollment_oobe
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obsoleted_subscription_notification(stage_callback):
    framework_logger.info("=== C57236542 - Obsoleted subscription notification flow started ===")
    
    # Pre-condition 1: Enroll the printer to dashboard page
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        print_history_page = PrintHistoryPage(page)
        update_plan_page = UpdatePlanPage(page)
        shipment_tracking_page = ShipmentTrackingPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        printer_selection_page = PrinterSelectionPage(page)
        
        try:
            # Pre-condition 2: Make sure the subscription is "obsolete" status
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info(f"Subscription cancellation")
            
            # Verifies the First and Third steps section on Cancellation Timeline Page
            cancellation_timeline_page = CancellationTimelinePage(page)
            today = datetime.today()
            # Time definition
            text = cancellation_timeline_page.cancellation_step(1).text_content()
            last_day = re.search(r'([A-Za-z]{3} \d{2}, \d{4})', text).group(1)
            last_day_date = datetime.strptime(last_day, '%b %d, %Y')
            cancel_initiate_date = (today - timedelta(days=72)).strftime('%b %d, %Y')
            final_bill_first = (last_day_date - timedelta(days=71)).strftime('%b %d, %Y')
            framework_logger.info(f"Cancellation date: {cancel_initiate_date} and Final bill date: {final_bill_first}")


            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Charged a new billing cycle with 100 pages")

            GeminiRAHelper.complete_jobs(page, ["SubscriptionUnsubscriberJob"])

            # Charge a new billing cycle with 100 pages
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "40")
            framework_logger.info("Shifted event by 40 days")
            GeminiRAHelper.complete_jobs(page, ["SubscriptionObsoleteJob"])

            DashboardHelper.access(page, tenant_email)
            side_menu = DashboardSideMenuPage(page)
            # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")
            side_menu.wait.notifications_submenu_link()
            side_menu.notifications_submenu_link.click(timeout=60000)
            framework_logger.info("Accessed Notifications page")

            # Verify cancellation confirmation notification is visible
            DashboardHelper.see_notification_on_dashboard(page, "Your cancellation confirmation")
            framework_logger.info("Verified cancellation confirmation notification is visible")

            # Access Print History
            side_menu.click_print_history()
            framework_logger.info(f"Opened Print History page")

            # Sees "HP Instant Ink Service Obsolete" message on Print and Payment History page
            print_history_page.print_history_table_button.click()
            print_history_page.wait.print_history_table_description(timeout=60000)
            assert "HP Instant Ink Service Obsolete" in print_history_page.print_history_table.text_content(timeout=5000)
            framework_logger.info(f"Verified obsolete message on Print and Payment History page")

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)

            common.retry_operation(
                lambda: RABaseHelper.access_link_by_title(page, "cancellation", "Notification events"),
                "cancellation",
                12,
                10
            )

            status = RABaseHelper.get_field_text_by_title(page, "Status")
            assert status == "complete" or status == "sent", f"Expected status to be 'complete' or 'sent', but got '{status}'"
            framework_logger.info("Verified notification events on Rails Admin")

            RABaseHelper.access_menu_of_page(page, "Template Data")

            RABaseHelper.validate_template_data(page, cancel_initiate_date, final_bill_first)
            framework_logger.info("Validated Template Data final charge and cancel initiate date")

            framework_logger.info("=== C57236542 - Obsoleted subscription notificationd flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the obsolete re-enroll simplified flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
