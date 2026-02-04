from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.print_history_page import PrintHistoryPage
from playwright.sync_api import expect
import urllib3
import test_flows_common.test_flows_common as common
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC = "C42614796"
def rollover_pages_overview_print_and_payment_history_without_free_months(stage_callback):
    framework_logger.info("=== C42614796 - Rollover Pages progress bar with free months flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        print_history_page = PrintHistoryPage(page)
        side_menu = DashboardSideMenuPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Free months removed from tenant")
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status updated to 'subscribed'")
   
            # Charge a new billing cycle with 160 pages
            GeminiRAHelper.event_shift(page, "33")
            framework_logger.info(f"event_shift 33 days")
            GeminiRAHelper.access_second_billing_cycle(page)
            framework_logger.info(f"access_billing_summary_page")

            GeminiRAHelper.calculate_and_define_page_tally(page, "60")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 60 pages")

            # Add free pages visible as 15
            RABaseHelper.get_links_by_title(page, "Subscription").first.click(timeout=60000)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.add_free_pages_visible(page, "15")
            framework_logger.info("Added 15 free pages visible")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            # Verify the progress bars for plan, trial, rollover, credits pages on Overview page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info("Progress bars verified on Overview page")

            # Sees the rollover pages as 0 of 40 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 40)
            framework_logger.info("Rollover pages verified as 0 of 40 used on Overview page")

            # Access Print History Page
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan, trial, rollover, credits pages on Print History page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info("Progress bars verified on Print History page")

            # Sees the rollover pages as 0 of 40 used on Print History page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 40)
            framework_logger.info("Rollover pages verified as 0 of 40 used on Print History page")

            # Set printed pages to 655
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "105")
            framework_logger.info("Set printed pages to 105")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify the progress bars for plan, trial, rollover, credits pages on Overview page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info("Progress bars verified on Overview page")

            # Sees the rollover pages as 0 of 40 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 40)
            framework_logger.info("Rollover pages verified as 0 of 40 used on Overview page")

            # Access Print History Page
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan, trial, rollover, credits pages on Print History page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info("Progress bars verified on Print History page")

            # Sees the rollover pages as 0 of 40 used on Print History page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 40)
            framework_logger.info("Rollover pages verified as 0 of 40 used on Print History page")

            # Set printed pages to 720
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "125")
            framework_logger.info("Set printed pages to 125")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify the progress bars for plan, trial, rollover, credits pages on Overview page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info("Progress bars verified on Overview page")

            # Sees the rollover pages as 0 of 40 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 10, 40)
            framework_logger.info("Rollover pages verified as 0 of 40 used on Overview page")

            # Access Print History Page
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan, trial, rollover, credits pages on Print History page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info("Progress bars verified on Print History page")

            # Sees the rollover pages as 0 of 40 used on Print History page
            DashboardHelper.verify_pages_used(page, "rollover", 10, 40)
            framework_logger.info("Rollover pages verified as 0 of 40 used on Print History page")

            # Set printed pages to 745
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "170")
            framework_logger.info("Set printed pages to 170")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify the progress bars for plan, trial, rollover, credits pages on Overview page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info("Progress bars verified on Overview page")

            # Sees the rollover pages as 0 of 40 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 40, 40)
            framework_logger.info("Rollover pages verified as 0 of 40 used on Overview page")

            # Sees the credits pages as 15 of 15 used on Overview page
            DashboardHelper.verify_pages_used(page, "credited", 15, 15)
            framework_logger.info("Credits pages verified as 15 of 15 used on Overview page")

            # Sees the plan pages as 100 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 100, 100)
            framework_logger.info("Plan pages verified as 100 of 100 used on Overview page")

            # Access Print History Page
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan, trial, rollover, credits pages on Print History page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info("Progress bars verified on Print History page")

            # Sees the rollover pages as 0 of 40 used on Print History page
            DashboardHelper.verify_pages_used(page, "rollover", 40, 40)
            framework_logger.info("Rollover pages verified as 0 of 40 used on Print History page")

            # Sees the credits pages as 15 of 15 used on Overview page
            DashboardHelper.verify_pages_used(page, "credited", 15, 15)
            framework_logger.info("Credits pages verified as 15 of 15 used on Print History page")

            # Sees the plan pages as 100 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 100, 100)
            framework_logger.info("Plan pages verified as 100 of 100 used on Print History page")

            # Shift subscription for 33 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "33")
            framework_logger.info("Shifted subscription for 33 days")

            # Executes the resque job FetchMissingTalliesForBillingJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["FetchMissingTalliesForBillingJob"])
            framework_logger.info("Executed FetchMissingTalliesForBillingJob")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Sees status card
            DashboardHelper.sees_status_card(page)
            framework_logger.info("Status card is visible on Overview page")

            # Verify the progress bars for plan and rollover pages on Overview page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover"])
            framework_logger.info("Verified progress bars for plan and rollover pages on Overview page")

            # Access Print History Page
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan and rollover pages on Print History page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover"])
            
            framework_logger.info("Verified progress bars for plan and rollover pages on Print History page")

            framework_logger.info("=== C42614796 - Flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow C42614796: {e}\n{traceback.format_exc()}")
            raise e
