from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.overview_page import OverviewPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.notifications_page import NotificationsPage
from pages.print_history_page import PrintHistoryPage    
import test_flows_common.test_flows_common as common 
from playwright.sync_api import expect
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def payment_declined(stage_callback):
    framework_logger.info("=== C51829435 - Payment Declined flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:        
        try:
            overview_page = OverviewPage(page)
            side_menu = DashboardSideMenuPage(page)
            notifications_page = NotificationsPage(page)
            print_history = PrintHistoryPage(page)

            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")
			
	        # Shift 32 and page tally 100
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            framework_logger.info(f"Shifted 32 days and page tally 100")
            
            # Update Pgs override response to payment problem
            GeminiRAHelper.update_to_payment_problem(page)			
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Updated Pgs override response to payment problem and Submited Charge")
			
	        # Shift 37 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "37")
            framework_logger.info(f"Shifted 37 days")
           
	        # Executes the resque job: SubscriptionBillingJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionBillingJob"])
            framework_logger.info("SubscriptionBillingJob executed")

            # Sees Payment state equals to problem 
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "problem")
            framework_logger.info("Status is problem")

            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "1")
            framework_logger.info(f"Shifted 1 day")

            # Executes the resque job: SubscriptionBillingJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["RetryBillingParallelJob"])
            framework_logger.info("RetryBillingParallelJob executed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")
			
	        # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")
			
	        # Verify Payment Declined message is displayed on Notification page
            side_menu.click_notifications()
            DashboardHelper.see_notification_on_dashboard(page, "Billing update needed")         
            framework_logger.info("Verified Billing update needed message is displayed on Notification page")

	        # Verify notification in Print History page
            side_menu.click_print_history()
            expect(print_history.payment_problem_banner).to_be_visible(timeout=60000)
            framework_logger.info("Verified notification message in Print History page")			
					
	        # click link with text payment_issue in the Notification events on the Subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "payment_issue", "Notification events")
            framework_logger.info("Accessed payment_issue from Notification events")
            
	        # Sees Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Payment state is complete")

            framework_logger.info("=== C51829435 - Payment Declined flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        
