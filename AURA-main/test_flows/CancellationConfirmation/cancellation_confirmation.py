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

def cancellation_confirmation(stage_callback):
    framework_logger.info("=== C57522252 - Cancellation Confirmation flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:  
        cancellation_timeline_page = CancellationTimelinePage(page)      
        side_menu = DashboardSideMenuPage(page)
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
            framework_logger.info("Subscription cancelled")

            # Verifies the First and Third steps section on Cancellation Timeline Page
            today = datetime.today()
            
            # Time definition
            text = cancellation_timeline_page.cancellation_step(1).text_content()
            last_day = re.search(r'([A-Za-z]{3} \d{2}, \d{4})', text).group(1)
            last_day_date = datetime.strptime(last_day, '%b %d, %Y')
            current_date = today.strftime('%b %d, %Y')
            final_bill_first = last_day_date + timedelta(days=1)
            final_bill_date = final_bill_first.strftime('%b %d, %Y')

            expect(cancellation_timeline_page.first_step_icon).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step(0)).to_be_visible()

            expect(cancellation_timeline_page.third_step_icon(2)).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step(2)).to_be_visible()
            framework_logger.info("Verified the First and Third steps section on Cancellation Timeline Page")
			
	        # Shift 32 and page tally 5
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "5")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Shifted 32 days and page tally 5")

            # Executes the resque job: SubscriptionUnsubscriberJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionUnsubscriberJob"])
            framework_logger.info("SubscriptionUnsubscriberJob executed")

            # Verify the subscription state in Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "unsubscribed")
			
            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            expect(overview_page.plan_details_card).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Overview page")
			
	        # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")
			
	        # Verify Your cancellation confirmation message is displayed on Notification page
            side_menu.click_notifications()
            DashboardHelper.see_notification_on_dashboard(page, "Your cancellation confirmation")         
            framework_logger.info("Verified Your cancellation confirmation message is displayed on Notification page")

	        # Access Print History page
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # And the user sees "HP Instant Ink Service Cancelled" notification on Print History card
            PrintHistoryHelper.see_notification_on_print_history(page, "HP Instant Ink Service Cancelled")
            framework_logger.info(f"'HP Instant Ink Service Cancelled' notification is visible on Print History page")			
					
	        # Click link with text payment_issue in the Notification events on the Subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "cancellation", "Notification events")
            framework_logger.info("Accessed payment_issue from Notification events")

	        # Sees Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Payment state is complete")

            # Clicks on Template Data menu
            RABaseHelper.access_menu_of_page(page, "Template Data")
            framework_logger.info("Accessed Template Data menu on Rails Admin")

            # Validates final charge and cancel initiate date in notifications events is equal to the cancellation timeline page with 0 days to add
            RABaseHelper.validate_template_data(page, current_date, final_bill_date)
            framework_logger.info("Validated Template Data final charge and cancel initiate date")

            framework_logger.info("=== C57522252 - Cancellation Confirmation flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
