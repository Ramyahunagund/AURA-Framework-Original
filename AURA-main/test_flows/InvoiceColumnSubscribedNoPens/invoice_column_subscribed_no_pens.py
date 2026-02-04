from helper.print_history_helper import PrintHistoryHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.print_history_page import PrintHistoryPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def invoice_column_subscribed_no_pens(stage_callback):
    framework_logger.info("=== C29890908 - Invoice column subscribed no pens flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)
            print_history_page = PrintHistoryPage(page)
            
            # Verify subscription state is subscribed_no_pens
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed_no_pens")
            framework_logger.info(f"Verified subscription state is subscribed_no_pens")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")
            
            # Click on Print and Payment History and validate the no pens page 
            side_menu.click_print_history()
            PrintHistoryHelper.validate_no_pens_print_history_page(page)
            framework_logger.info("Validated no pens Print History page")
           
            # Check elements are not visible
            expect(print_history_page.download_all_invoices_button).not_to_be_visible(timeout=30000)
            expect(print_history_page.table_invoice).not_to_be_visible(timeout=30000)

            framework_logger.info("=== C29890908 - Invoice column subscribed no pens flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
            