from helper.print_history_helper import PrintHistoryHelper
from helper.update_plan_helper import UpdatePlanHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.update_plan_page import UpdatePlanPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_and_payment_history_faq_for_no_pens(stage_callback):
    framework_logger.info("=== C44812164 - Print and Payment History FAQ for no-pens/ Update plan flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)
            update_plan = UpdatePlanPage(page)

            # Verify subscription state is subscribed_no_pens
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed_no_pens")
            framework_logger.info(f"Verified subscription state is subscribed_no_pens")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Print History page
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Validate the FAQ on Smart Dashboard > Print and Payment History page
            PrintHistoryHelper.validate_faq_on_print_and_payment_history(page)
            framework_logger.info("Validated FAQ on Print and Payment History page")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info(f"Accessed Update Plan page")

            # Click on Print and Payment History and validate the no pens page 
            update_plan.print_history_link.click()
            PrintHistoryHelper.validate_no_pens_print_history_page(page)
            framework_logger.info("Validated no pens Print History page")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info(f"Accessed Update Plan page")
            
            # Verify the Terms of Service link at Update Plan section
            UpdatePlanHelper.validate_terms_of_service_page(page)
            framework_logger.info("Validated Terms of Service link at Update Plan section")
            framework_logger.info("=== Ca - Print and Payment History FAQ for no-pens/ Update plan flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
            