from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from helper.ra_base_helper import RABaseHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.print_history_page import PrintHistoryPage
from core.settings import framework_logger 
from playwright.sync_api import expect   
import test_flows_common.test_flows_common as common 
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def payment_problem_and_suspended_notifications_prepaid_only(stage_callback):
    framework_logger.info("=== C50353932 - Payment problem and Suspended notifications - Prepaid only flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:        
        try:
            side_menu = DashboardSideMenuPage(page)
            print_history = PrintHistoryPage(page)

            # Move subscription to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")
			
	        # First billing cycle (shift 31 and page tally 100)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"First billing cycle completed")

            # Second billing cycle (shift 31 and page tally 100)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Second billing cycle completed")

            # Third billing cycle (shift 31 and page tally 100)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Third billing cycle completed")

            # Fourth billing cycle (shift 31 and page tally 100)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Fourth billing cycle completed")

            # Fifth billing cycle (shift 31 and page tally 100)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Fifth billing cycle completed")

	        # Click on the prepaidcard_insufficient link in the Notification events
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "prepaidcard_insufficient", "Notification events")
            framework_logger.info("Accessed payment_issue from Notification events")

            # Sees Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Payment state is complete")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

	        # Expand My Account Menu
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")
			
	        # Verify "Prepaid credit insufficient" message displayed on Notification page
            side_menu.click_notifications()
            DashboardHelper.see_notification_on_dashboard(page, "Prepaid credit insufficient")         
            framework_logger.info("Verified Billing update needed message is displayed on Notification page")

            # Sees Payment state equals to problem 
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "problem")
            framework_logger.info("Payment state is 'problem'")		

            # Shift 14 days 
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "14")
            framework_logger.info(f"Shifted 14 days")

	        # Run the resque job: SubscriptionSuspenderJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionSuspenderJob"])
            framework_logger.info("SubscriptionSuspenderJob executed")

            # Access Dashboard
            DashboardHelper.access(page)
            framework_logger.info(f"Accessed Dashboard")
			
	        # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")
			
	        # Verify "Account suspended" message displayed on Notification page
            side_menu.click_notifications()
            DashboardHelper.see_notification_on_dashboard(page, "Account suspended")         
            framework_logger.info("Verified Account suspended message is displayed on Notification page")

	        # Verify notification in Print History page
            side_menu.click_print_history()
            expect(print_history.account_suspended_banner).to_be_visible(timeout=60000)
            framework_logger.info("Verified notification message in Print History page")			
					
	        # Click on the prepaidcard_insufficient link in the Notification events
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "prepaidcard_insufficient", "Notification events")
            framework_logger.info("Accessed payment_issue from Notification events")
            
	        # Sees Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Payment state is complete")

            framework_logger.info("=== C50353932 - Payment problem and Suspended notifications - Prepaid only flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close
        