from test_flows.CancellationTimelinePage.cancellation_timeline_page import cancellation_timeline_page
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from datetime import datetime, timedelta
from helper.ra_base_helper import RABaseHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.update_plan_helper import UpdatePlanHelper
from core.playwright_manager import PlaywrightManager
from pages.overview_page import OverviewPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage  
from pages.cancellation_timeline_page import CancellationTimelinePage 
from core.settings import framework_logger
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common 
import urllib3
import traceback
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def unsubscribed_notification_cancellation_confirmation(stage_callback):
    framework_logger.info("=== C27590133 - Unsubscribed Notification Cancellation Confirmation flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:  
        cancellation_timeline_page = CancellationTimelinePage(page)      
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription moved to subscribed state")

            # Make sure the subscription without free months
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info("Removed free months from subscription")

            # Open Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened Instant Ink Dashboard")

            # Cancel the subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("Subscription cancelled")

            # Get cancellation dates from timeline page for later validation
            text = cancellation_timeline_page.cancellation_step(1).text_content()
            last_day = re.search(r'([A-Za-z]{3} \d{2}, \d{4})', text).group(1)
            last_day_date = datetime.strptime(last_day, '%b %d, %Y')

            # Subtract 32 days to account for the event shift
            adjusted_current_date = (datetime.today() - timedelta(days=32)).strftime('%b %d, %Y')
            adjusted_final_bill_date = (last_day_date + timedelta(days=1) - timedelta(days=32)).strftime('%b %d, %Y')

            framework_logger.info(f"Cancellation initiated on {adjusted_current_date}, final bill date will be {adjusted_final_bill_date}")

            # Check subscription state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "initiated_unsubscribe")
            framework_logger.info("Verified subscription state is initiated_unsubscribe")

            # Shift 32 days and trigger a billing cycle
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Shifted 32 days and triggered billing cycle with page tally 100")

            # Run SubscriptionUnsubscriberJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionUnsubscriberJob"])
            framework_logger.info("Executed SubscriptionUnsubscriberJob")

            # Wait the subscription state change to unsubscribed
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "unsubscribed")
            framework_logger.info("Verified subscription state is unsubscribed")

            # Access Notifications
            DashboardHelper.access(page)
            side_menu.expand_my_account_menu()
            side_menu.click_notifications()
            framework_logger.info("Accessed Notifications page")

            # Verify "Your cancellation confirmation" notification
            DashboardHelper.see_notification_on_dashboard(page, "Your cancellation confirmation")         
            framework_logger.info("Verified 'Your cancellation confirmation' notification is displayed on Notification page")

            # Access Print and Payment History
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Verify "HP Instant Ink Service Cancelled" notification
            PrintHistoryHelper.see_notification_on_print_history(page, "HP Instant Ink Service Cancelled")
            framework_logger.info("Verified 'HP Instant Ink Service Cancelled' notification is visible on Print History page")

            # Verify the notification events "cancellation" was triggered 
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "cancellation", "Notification events")
            framework_logger.info("Accessed cancellation from Notification events")

            # Verify Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Verified notification status is complete")

            # Access "Template Data"
            RABaseHelper.access_menu_of_page(page, "Template Data")
            framework_logger.info("Accessed Template Data menu on Rails Admin")

            # Validate final_charge_date and cancel_initiate_date
            RABaseHelper.validate_template_data(page, adjusted_current_date, adjusted_final_bill_date)
            framework_logger.info("Validated Template Data: final_charge_date and cancel_initiate_date match dashboard timeline")

            framework_logger.info("=== C27590133 - Unsubscribed Notification Cancellation Confirmation flow finished successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e