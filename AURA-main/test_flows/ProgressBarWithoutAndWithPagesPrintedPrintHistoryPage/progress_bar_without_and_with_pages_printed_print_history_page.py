from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.print_history_page import PrintHistoryPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def progress_bar_without_and_with_pages_printed_print_history_page(stage_callback):
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info("=== C42441384 - Progress bar without and with pages printed - Print and Payment History page ===")

    with PlaywrightManager() as page:
        try:
            print_history_page = PrintHistoryPage(page)
            side_menu = DashboardSideMenuPage(page)

            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")
            
            # Add free pages visible
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.add_free_pages_visible(page, "30")
            framework_logger.info(f"Added 30 free pages visible")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Print History Page
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan, rollover, credited pages on Print History Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Print History Page")

            # Verify credited pages tooltip
            DashboardHelper.verify_tooltip(page, "credited")
            framework_logger.info("Credited pages tooltip verified on Print History page")

            # Verify plan pages tooltip
            DashboardHelper.verify_tooltip(page, "plan")
            framework_logger.info("Plan pages tooltip verified on Print History page")

            # Verify trial pages tooltip
            DashboardHelper.verify_tooltip(page, "trial")
            framework_logger.info("Trial pages tooltip verified on Print History page")

            # Sees the rollover pages as 0 of 0 used on Print History page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info("Rollover pages verified as 0 of 0 used on Print History page")

            # Set printed pages to 10
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "10")
            framework_logger.info("Set printed pages to 10")

            # Access Print History Page
            DashboardHelper.access(page)
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan, rollover, credited pages on Print History Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Print History Page")

            # Sees the credited pages as 10 of 30 used on Print History page
            DashboardHelper.verify_pages_used(page, "credited", 10, 30)
            framework_logger.info("Credited pages verified as 10 of 30 used on Print History page")

            # Sees the plan pages as 0 of 100 used on Print History page
            DashboardHelper.verify_pages_used(page, "plan", 0, 100)
            framework_logger.info("Plan pages verified as 0 of 100 used on Print History page")

            # Sees the trial pages as 0 used on Print History page
            DashboardHelper.verify_trial_pages_used(page, 0)
            framework_logger.info("Trial pages verified as 0 used on Print History page")

            # Sees the rollover pages as 0 of 0 used on Print History page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info("Rollover pages verified as 0 of 0 used on Print History page")

            # Set printed pages to 35
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "35")
            framework_logger.info("Set printed pages to 35")

            # Access Print History Page
            DashboardHelper.access(page)
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan, rollover, credited pages on Print History Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Print History Page")

            # Sees the credited pages as 30 of 30 used on Print History page
            DashboardHelper.verify_pages_used(page, "credited", 30, 30)
            framework_logger.info("Credited pages verified as 30 of 30 used on Print History page")

            # Sees the plan pages as 5 of 100 used on Print History page
            DashboardHelper.verify_pages_used(page, "plan", 5, 100)
            framework_logger.info("Plan pages verified as 5 of 100 used on Print History page")

            # Sees the trial pages as 0 used on Print History page
            DashboardHelper.verify_trial_pages_used(page, 0)
            framework_logger.info("Trial pages verified as 0 used on Print History page")

            # Sees the rollover pages as 0 of 0 used on Print History page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info("Rollover pages verified as 0 of 0 used on Print History page")

            # Set printed pages to 135
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "135")
            framework_logger.info("Set printed pages to 135")

            # Access Print History Page
            DashboardHelper.access(page)
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan, rollover, credited pages on Print History Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Print History Page")

            # Sees the credited pages as 30 of 30 used on Print History page
            DashboardHelper.verify_pages_used(page, "credited", 30, 30)
            framework_logger.info("Credited pages verified as 30 of 30 used on Print History page")

            # Sees the plan pages as 100 of 100 used on Print History page
            DashboardHelper.verify_pages_used(page, "plan", 100, 100)
            framework_logger.info("Plan pages verified as 100 of 100 used on Print History page")

            # Sees the trial pages as 5 used on Print History page
            DashboardHelper.verify_trial_pages_used(page, 5)
            framework_logger.info("Trial pages verified as 5 used on Print History page")

            # Sees the rollover pages as 0 of 0 used on Print History page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info("Rollover pages verified as 0 of 0 used on Print History page")

            # Verify total printed pages
            DashboardHelper.verify_total_pages_printed(page, 135)
            framework_logger.info("Total printed pages verified as 135 on Print History page")
            framework_logger.info(f"=== C42441384 - Progress bar without and with pages printed - Print and Payment History page ===")
        except Exception as e:
            framework_logger.error(f"Error during flow execution: {e}")
            raise e
        finally:
            page.close()
