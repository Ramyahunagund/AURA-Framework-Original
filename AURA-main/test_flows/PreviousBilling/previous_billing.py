# test_flows/PreviousBilling/previous_billing.py
from playwright.sync_api import sync_playwright, expect
from bs4 import BeautifulSoup
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from pages.sign_in_page import SignInPage
from pages.overview_page import OverviewPage
from helper.print_history_helper import PrintHistoryHelper
from pages.print_history_page import PrintHistoryPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def previous_billing(stage_callback):
    framework_logger.info("=== C38282388 - Previous Billing flow started ===")
    
    # Create subscription first
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            # Step 1: Identify user and move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)        
            GeminiRAHelper.subscription_to_subscribed(page)                
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info("Subscription moved to subscribed state and remove free months") 

            # A new billing cycle is charged for that subscription setting page used as 100
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page) 
            GeminiRAHelper.manual_retry_until_complete(page=page)  
            framework_logger.info(f"New billing cycle charged with 31 pages")  

            # Billing cycle is charged 37 for that subscription without page tally
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page) 
            GeminiRAHelper.event_shift(page, event_shift="37")
            GeminiRAHelper.access_second_billing_cycle(page) 
            GeminiRAHelper.calculate_page_tally(page)               
            GeminiRAHelper.submit_charge(page)   
            GeminiRAHelper.manual_retry_until_complete(page=page) 
            framework_logger.info(f"New billing cycle charged with 37 shifted pages without page tally")

            # Step 6: Shift subscription by 32 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page) 
            GeminiRAHelper.event_shift(page, event_shift="32")
            framework_logger.info("Subscription shifted by 32 days")
            
            # Step 3: Second billing cycle - charged for subscription with page used as 100
            GeminiRAHelper.access_third_billing_cycle(page)                
            GeminiRAHelper.define_page_tally(page, "150")
            framework_logger.info("Click calculate page tally and define page tally 150 for first billing cycle")

           # Step 3: First billing cycle - charged for subscription with page used as 100
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "120")
            GeminiRAHelper.submit_charge(page)
            GeminiRAHelper.manual_retry_until_complete(page=page)
            framework_logger.info("Second billing cycle charged")

            # Step 10: Open Instant Ink Dashboard
            DashboardHelper.first_access(page, tenant_email=tenant_email)
            framework_logger.info("Opened Instant Ink dashboard page and Skipped all preconditions")
            
            # Step 12: Click on Print History Menu
            side_menu = DashboardSideMenuPage(page)
            side_menu.click_print_history()
            framework_logger.info("Clicked on Print History Menu at UCDE")
                        
            PrintHistoryHelper.verify_all_billing_cycles_data(page, [
                {
                  "billing_cycle": "2",
                    "total_pages_printed": "120",
                    "pages": "100",
                    "rollover": "0",
                    "additional": "20",
                    "plan_price": "7.99",
                    "overage_price": "1.50",
                    "previous": "7.50",
                    "charges": "10.99",
                    "tax": "1.63",
                    "total": "20.12"
                },
                {
                   "billing_cycle": "3",
                    "total_pages_printed": "150",
                    "pages": "100",
                    "rollover": "0",
                    "additional": "50",
                    "plan_price": "7.99",
                    "overage_price": "1.50",
                    "previous": "0.00",
                    "charges": "7.99",
                    "tax": "0.70",
                    "total": "8.69" 
                }
            ])            
            framework_logger.info("Print History table validation completed successfully")
            framework_logger.info("=== Previous Billing flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the Previous Billing flow: {e}\n{traceback.format_exc()}")
            raise e
        
