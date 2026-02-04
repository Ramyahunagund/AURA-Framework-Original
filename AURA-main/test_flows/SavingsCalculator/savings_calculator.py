from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def savings_calculator(stage_callback):
    framework_logger.info("=== C42199132 - Savings calculator ===")
    tenant_email = create_ii_subscription(stage_callback)
    
    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Charge a billing cycle
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "60")
            GeminiRAHelper.submit_charge(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            # click calculation retention
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_calculate_retention(page)

            # Click link with text Retention Calculation in the Retention calculation on the subscription page
            RABaseHelper.access_link_by_title(page, "Retention Calculation", "Retention calculation")
            framework_logger.info(f"Successfully recalculated retention and recommended plan for subscription")

            # Check the Average monthly savings in cents
            GeminiRAHelper.verify_rails_admin_info(page, "Average monthly savings in cents", "537")
            framework_logger.info("Average annual savings in cents equal to 537")

            # Check the Average annual savings in cents
            GeminiRAHelper.verify_rails_admin_info(page, "Average annual savings in cents", "6448")
            framework_logger.info("Average annual savings in cents equal to 6448")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Accessed Overview page")
           
           # Check the savings calculator card and the value on overview page
            data = {
                'annual_savings': '64.48',
                'printing_average': '60',
                'traditional_cartridge_cost': '160.36'
            }
            DashboardHelper.check_savings_calculator_on_overview(page, data)
            framework_logger.info("Saving calculator is checked on Overview page")

            framework_logger.info("=== C42199132 - Savings calculator ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        