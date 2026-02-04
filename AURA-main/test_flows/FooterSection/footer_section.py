from helper.print_history_helper import PrintHistoryHelper
from pages.overview_page import OverviewPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def footer_section(stage_callback):
    framework_logger.info("=== C41827589 - Footer section flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Verify Footer section on Overview page
            DashboardHelper.verify_footer_section(page)
            framework_logger.info(f"Verified Footer section on Overview page")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info(f"Accessed Update Plan page")

            # Verify Footer section on Update Plan page
            DashboardHelper.verify_footer_section(page)
            framework_logger.info(f"Verified Footer section on Update Plan page")

            # Access Print History page
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Verify Footer section on Print History page
            DashboardHelper.verify_footer_section(page)
            framework_logger.info(f"Verified Footer section on Print History page")

            # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            framework_logger.info("Dashboard Shipment Tracking page accessed successfully")

            # Verify Footer section on Shipment Tracking page
            DashboardHelper.verify_footer_section(page)
            framework_logger.info(f"Verified Footer section on Shipment Tracking page")

            # Access Shipping & Billing page
            side_menu.my_account_menu_link.click()
            side_menu.shipping_billing_submenu_link.click()
            framework_logger.info("Accessed Shipping & Billing page")

            # Verify Footer section on Shipping & Billing page
            DashboardHelper.verify_footer_section(page)
            framework_logger.info(f"Verified Footer section on Shipping & Billing page")
            framework_logger.info("=== C41827589 - Footer section flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()