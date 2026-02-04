from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.print_history_page import PrintHistoryPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import time
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def remaining_free_trial_and_progress_bar_on_print_history(stage_callback):
    framework_logger.info("=== C42157252 - Remaining free trial and Progress Bar on Print history flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        print_history = PrintHistoryPage(page)
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
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Charged a billing cycle with 100 pages")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            # Access Print History
            side_menu.click_print_history()
            expect(print_history.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Print History page")

            # Does not see free months on Print History Page
            expect(print_history.free_months).not_to_be_visible()
            framework_logger.info(f"Verified free months are not displayed on Print History page")

            # Verify the progress bars for plan and rollover on Print History Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover"])
            framework_logger.info(f"Verified progress bars for plan and rollover pages on Overview Page")

            # Sees the plan pages tooltip
            DashboardHelper.verify_tooltip(page, "plan")
            framework_logger.info(f"Verified plan pages tooltip")

            # Sees the plan pages as 0 of 100 used on Print History Page
            DashboardHelper.verify_pages_used(page, "plan", 0, 100)
            framework_logger.info(f"Verified plan pages as 0 of 100 used on Print History Page")

            # Sees the rollover pages tooltip
            DashboardHelper.verify_tooltip(page, "rollover")
            framework_logger.info(f"Verified rollover pages tooltip")

            # Sees the rollover pages as 0 of 0 used on Print History Page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info(f"Verified rollover pages as 0 of 0 used on Print History Page")

            # Set printed pages to 50
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_billing_summary_page(page)
            GeminiRAHelper.set_printed_pages(page, "50")
            framework_logger.info("Set printed pages to 50")

            # Access Print History
            DashboardHelper.access(page)
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Sees the plan pages as 50 of 100 used on Print History Page
            DashboardHelper.verify_pages_used(page, "plan", 50, 100)
            framework_logger.info(f"Verified plan pages as 50 of 100 used on Print History Page")

            # Set printed pages to 105
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_billing_summary_page(page)
            GeminiRAHelper.set_printed_pages(page, "105")
            framework_logger.info("Set printed pages to 105")

            # Access Print History
            DashboardHelper.access(page)
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Verify the progress bars for plan and rollover on Print History Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover"])
            framework_logger.info(f"Verified progress bars for plan and rollover pages on Overview Page")

            # Sees the additional pages as 5 of 10 used on Print History Page
            DashboardHelper.verify_pages_used(page, "additional", 5, 10)
            framework_logger.info(f"Verified additional pages as 5 of 10 used on Print History Page")

            # Sees the additional pages message on Print History Page
            expect(print_history.additional_pages_message).to_be_visible(timeout=90000)
            expect(print_history.additional_pages_message).to_contain_text("additional pages (10 pages/set)")
            framework_logger.info(f"Verified additional pages message on Print History Page")

            # Sees the additional pages tooltip
            DashboardHelper.verify_tooltip(page, "additional")
            framework_logger.info(f"Verified additional pages message and tooltip on Print History Page")

            # Sees the plan pages as 100 of 100 used on Print History Page
            DashboardHelper.verify_pages_used(page, "plan", 100, 100)
            framework_logger.info(f"Verified plan pages as 100 of 100 used on Print History Page")

            # Sees the rollover pages as 0 of 0 used on Print History Page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info(f"Verified rollover pages as 0 of 0 used on Print History Page")

            # Sees the 105 total pages printed on Print History Page
            DashboardHelper.verify_total_pages_printed(page, 105)
            framework_logger.info(f"Verified total pages printed as 105 on Print History Page")

            framework_logger.info("=== C42157252 - Remaining free trial and Progress Bar on Print history flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e