from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.ra_base_helper import RABaseHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from helper.overview_helper import OverviewHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.cancellation_plan_helper import CancellationPlanHelper
from core.playwright_manager import PlaywrightManager
from pages.overview_page import OverviewPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.notifications_page import NotificationsPage
from pages.print_history_page import PrintHistoryPage    
import test_flows_common.test_flows_common as common 
from core.settings import framework_logger
from playwright.sync_api import expect
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancel_with_payment_issue(stage_callback):
    framework_logger.info("=== C52792565 - Cancel with Payment issue flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:        
        side_menu = DashboardSideMenuPage(page)
        print_history = PrintHistoryPage(page)
        overview_page = OverviewPage(page)
        try:
            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info(f"Accessed Update Plan page")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            CancellationPlanHelper.select_cancellation_feedback_option(page)
            framework_logger.info("Subscription cancelled")
			
	        # Subscription shifted 31 days after cancelled
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            framework_logger.info(f"Subscription shifted 31 days after cancelled")

            # Executes the resque job: SubscriptionUnsubscriberJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionUnsubscriberJob"])
            framework_logger.info("SubscriptionUnsubscriberJob executed")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            expect(overview_page.plan_details_card).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Overview page")

            # Verify Unsubscribed status card is displayed
            OverviewHelper.verify_unsubscribed_status_card(page)
            framework_logger.info("Verified Unsubscribed status card is displayed on Overview page")

	        # Shift 32 and page tally 100
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            framework_logger.info(f"Shifted 32 days and page tally 100")

            # Update Pgs override response to payment problem
            GeminiRAHelper.update_to_payment_problem(page)			
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Updated Pgs override response to payment problem and Submited Charge")

            # Sees Payment state equals to problem on subscription page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            assert RABaseHelper.get_field_text_by_title(page, "Payment state") == "problem"
            framework_logger.info("Payment state verified as 'problem'")
			
            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            expect(overview_page.plan_details_card).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Overview page")
			
	        # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")
			
	        # Verify Payment Declined message is displayed on Notification page
            side_menu.click_notifications()
            DashboardHelper.see_notification_on_dashboard(page, "Cancellation request received")         
            framework_logger.info("Verified Billing update needed message is displayed on Notification page")

	        # Verify notification in Print History page
            side_menu.click_print_history()
            expect(print_history.payment_problem_banner).to_be_visible(timeout=60000)
            framework_logger.info("Verified notification message in Print History page")			
					
	        # Click link with text payment_issue in the Notification events on the Subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "cancellation", "Notification events")
            framework_logger.info("Accessed payment_issue from Notification events")

	        # Sees Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Payment state is complete")

            framework_logger.info("=== C52792565 - Cancel with Payment issue flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
