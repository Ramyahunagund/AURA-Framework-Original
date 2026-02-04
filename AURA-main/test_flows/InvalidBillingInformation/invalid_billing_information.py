from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import urllib3
import test_flows_common.test_flows_common as common
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def invalid_billing_information(stage_callback):
    framework_logger.info("=== C38238374 - Invalid Billing Information flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        side_menu = DashboardSideMenuPage(page)
        try:
            # Open instant ink dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page")

            # Access Shipping Billing Page
            side_menu.click_shipping_billing()
            framework_logger.info(f"Clicked on Shipping & Billing in side menu")
            
            # Set invalid credit card on Billing modal
            DashboardHelper.set_invalid_billing_address(page, "address with special characters")
            framework_logger.info("Set address with special characters on Billing modal")

            # Set invalid credit card on Billing modal
            DashboardHelper.set_invalid_billing_address(page, "address with incomplete information")
            framework_logger.info("Set address with incomplete information on Billing modal")

            # Set invalid credit card on Billing modal
            DashboardHelper.set_invalid_billing_address(page, "credit card invalid")
            framework_logger.info("Set invalid credit card on Billing modal")   

            framework_logger.info("=== C38238374 - Invalid Billing Information flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow C38238374: {e}\n{traceback.format_exc()}")
            raise e
