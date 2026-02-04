from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.print_history_page import PrintHistoryPage
from playwright.sync_api import expect
import urllib3
import traceback
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# TC = C38571168
def rollover_pages_limit_ink(stage_callback):
    framework_logger.info("=== Rollover pages limit (Ink) flow started ===")
    tenant_email = enrollment_ink_web(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        print_history_page = PrintHistoryPage(page)
        
        try:
            # Remove free months of subscription if needed
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info("Removed free months and moved subscription to subscribed state")
            
            # Add free pages visible as 15
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.add_free_pages_visible(page, "15")
            framework_logger.info("Added 15 free pages visible")
          
            # First billing cycle - charge 32 days, 5 pages used
            RABaseHelper.get_links_by_title(page, "Subscription").first.click()
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "5")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("First billing cycle charged: 32 days, 5 pages used")

            # Access Smart Dashboard and verify rollover pages: 0 of 110
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Accessed Smart Dashboard")

            # Verify rollover pages on Overview page: 0 of 110
            DashboardHelper.verify_pages_used(page, "rollover", 0, 110)
            framework_logger.info("Verified rollover pages as 0 of 110 on Overview page")

            # Click on Print History Menu and verify rollover pages
            side_menu.click_print_history()
            DashboardHelper.verify_pages_used(page, "rollover", 0, 110)
            framework_logger.info("Verified rollover pages as 0 of 110 on Print and Payment History page")

            # Second billing cycle - charge 32 days, 15 pages used
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "15")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Second billing cycle charged: 32 days, 15 pages used")

            # Access instant ink dashboard and verify rollover pages: 0 of 195
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 195)
            framework_logger.info("Verified rollover pages as 0 of 195 on Overview page")

            # Click on Print History Menu and verify rollover pages
            side_menu.click_print_history()
            DashboardHelper.verify_pages_used(page, "rollover", 0, 195)
            framework_logger.info("Verified rollover pages as 0 of 195 on Print and Payment History page")

            # Third billing cycle - charge 32 days, 5 pages used
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "5")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Third billing cycle charged: 32 days, 5 pages used")

            # Access instant ink dashboard and verify rollover pages: 0 of 290
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 290)
            framework_logger.info("Verified rollover pages as 0 of 290 on Overview page")

            # Click on Print History Menu and verify rollover pages
            side_menu.click_print_history()
            DashboardHelper.verify_pages_used(page, "rollover", 0, 290)
            framework_logger.info("Verified rollover pages as 0 of 290 on Print and Payment History page")

            # Fourth billing cycle - charge 32 days, 10 pages used
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "10")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Fourth billing cycle charged: 32 days, 10 pages used")

            # Final verification - access instant ink dashboard: 0 of 300
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 300)
            framework_logger.info("Verified rollover pages as 0 of 300 on Overview page")

            # Final Print History verification
            side_menu.click_print_history()
            DashboardHelper.verify_pages_used(page, "rollover", 0, 300)
            framework_logger.info("Verified rollover pages as 0 of 300 on Print and Payment History page")

            framework_logger.info("=== Rollover pages limit (Ink) flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the rollover pages limit (Ink) flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
