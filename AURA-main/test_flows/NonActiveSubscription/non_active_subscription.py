from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.print_history_helper import PrintHistoryHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.print_history_page import PrintHistoryPage
from pages.update_plan_page import UpdatePlanPage
from pages.cancellation_page import CancellationPage
from playwright.sync_api import expect
import urllib3
import traceback
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web
import test_flows_common.test_flows_common as common
from helper.update_plan_helper import UpdatePlanHelper
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def non_active_subscription(stage_callback):
    framework_logger.info("=== C38333186  Non-Active subscription flow started ===")
    tenant_email = enrollment_ink_web(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        update_plan_page = UpdatePlanPage(page)
              
        try:                
            # Access Gemini Rails Admin to work with subscription
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)

            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")
         
           # Charge a billing cycle
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)    
            framework_logger.info(f"New billing cycle charged with 31 pages")    
            
            # Access Smart Dashboard and skip preconditions
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")
            
            # # Click on Change Plan Menu (Update Plan)
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Clicked on Change Plan Menu")

            # # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info(f"Subscription cancellation")
      
            # Charge a billing cycle 32 days after cancelled
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)    
            framework_logger.info(f"New billing cycle charged with 32 pages")  

            # # Execute SubscriptionUnsubscriberJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionUnsubscriberJob"])
            framework_logger.info("Executed SubscriptionUnsubscriberJob")

            # Verify subscription state is unsubscribed
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            page.reload()
            page.wait_for_load_state("networkidle")
            GeminiRAHelper.verify_rails_admin_info(page, "State", "unsubscribed")
                     
            # Open instant ink dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page")

            # Verify previous billing cycle period on Print History page
            side_menu.click_print_history()                    
            PrintHistoryHelper.verify_previous_billing_cycle_period(page)
            framework_logger.info("Verified previous billing cycle period on Print History page")

            # Shift subscription by 40 days after cancelled
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "40")
            framework_logger.info("Shifted subscription by 40 days after cancellation") 
            
            # Execute SubscriptionObsoleteJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionObsoleteJob"])
            framework_logger.info("Executed SubscriptionObsoleteJob")

            # Verify subscription state is obsolete
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            page.reload()
            page.wait_for_load_state("networkidle")
            GeminiRAHelper.verify_rails_admin_info(page, "State", "obsolete")
            
            # Open instant ink dashboard page again
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page again")

           # Verify previous billing cycle period on Print History page again
            side_menu.click_print_history()   
            PrintHistoryHelper.verify_previous_billing_cycle_period(page)
            framework_logger.info("Verified previous billing cycle period on Print History page again")

            framework_logger.info("=== Non-Active subscription C38333186 flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the non-active subscription flow: {e}\n{traceback.format_exc()}")
            raise e
