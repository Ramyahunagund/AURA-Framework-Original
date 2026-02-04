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

def progress_bar_with_and_without_pages_printed_on_overview_page_without_free_months(stage_callback):
    framework_logger.info("=== C42536266 - Progress bar with and without pages printed on Overview Page without free months flow started ===")
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
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)

            # Add free pages visible
            RABaseHelper.get_links_by_title(page, "Subscription").first.click()
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.add_free_pages_visible(page, "15")
            framework_logger.info(f"Added 15 free pages visible")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            # Does not see free months in Overview page
            DashboardHelper.doesnt_see_free_months(page)
            framework_logger.info(f"Verified free months are not displayed in Overview page")

            # Verify the progress bars for plan, rollover, credited pages on Overview Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Overview Page")
            
            # Verify the credited pages tooltip
            DashboardHelper.verify_tooltip(page, "credited")
            framework_logger.info(f"Verified credited pages tooltip")

            # Sees the credited pages as 0 of 15 used on Overview page
            DashboardHelper.verify_pages_used(page, "credited", 0, 15)
            framework_logger.info(f"Verified credited pages as 0 of 15 used on Overview page")

            # Sees the plan pages as 0 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 0, 100)
            framework_logger.info(f"Verified plan pages as 0 of 100 used on Overview page")

            # Sees the plan pages tooltip
            DashboardHelper.verify_tooltip(page, "plan")
            framework_logger.info(f"Verified plan pages tooltip")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info(f"Verified rollover pages as 0 of 0 used on Overview page")

            # Set printed pages to 10
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "10")
            framework_logger.info("Set printed pages to 10")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify the progress bars for plan, rollover, credited pages on Overview Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Overview Page")

            # Sees the credited pages as 10 of 15 used on Overview page
            DashboardHelper.verify_pages_used(page, "credited", 10, 15)
            framework_logger.info(f"Verified credited pages as 10 of 15 used on Overview page")

            # Sees the plan pages as 0 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 0, 100)
            framework_logger.info(f"Verified plan pages as 0 of 100 used on Overview page")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info(f"Verified rollover pages as 0 of 0 used on Overview page")

            # Set printed pages to 65
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "65")
            framework_logger.info("Set printed pages to 65")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify the progress bars for plan, rollover, credited pages on Overview Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Overview Page")

            # Sees the credited pages as 15 of 15 used on Overview page
            DashboardHelper.verify_pages_used(page, "credited", 15, 15)
            framework_logger.info(f"Verified credited pages as 15 of 15 used on Overview page")

            # Sees the plan pages as 50 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 50, 100)
            framework_logger.info(f"Verified plan pages as 50 of 100 used on Overview page")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info(f"Verified rollover pages as 0 of 0 used on Overview page")

            # Set printed pages to 120
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "120")
            framework_logger.info("Set printed pages to 120")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify the progress bars for plan, rollover, credited pages on Overview Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Overview Page")

            # Sees the credited pages as 15 of 15 used on Overview page
            DashboardHelper.verify_pages_used(page, "credited", 15, 15)
            framework_logger.info(f"Verified credited pages as 15 of 15 used on Overview page")

            # Sees the plan pages as 100 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 100, 100)
            framework_logger.info(f"Verified plan pages as 100 of 100 used on Overview page")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info(f"Verified rollover pages as 0 of 0 used on Overview page")

            # Sees the additional pages as 5 of 10 used on Overview page
            DashboardHelper.verify_pages_used(page, "additional", 5, 10)
            framework_logger.info(f"Verified additional pages as 5 of 10 used on Overview page")

            # Sees the additional pages tooltip
            DashboardHelper.verify_tooltip(page, "additional")
            framework_logger.info(f"Verified additional pages tooltip")

            # Sees the 120 total pages printed on Overview page
            DashboardHelper.verify_total_pages_printed(page, 120)
            framework_logger.info(f"Verified total pages printed as 120 on Overview page")

            framework_logger.info("=== C42536266 - Progress bar with and without pages printed on Overview Page without free months flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e