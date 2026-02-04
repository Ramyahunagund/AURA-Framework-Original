from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def progress_bar_with_and_without_pages_printed_with_free_months_remaining(stage_callback):
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info("=== C42336966- Progress bar with and without pages printed on Overview page started ===")

    with PlaywrightManager() as page:
        try:
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

            # Verify the progress bars for plan, rollover, credited pages on Overview Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Overview Page")

            # Verify credited pages tooltip
            DashboardHelper.verify_tooltip(page, "credited")
            framework_logger.info("Credited pages tooltip verified on Overview page")
            
            # Sees the plan pages as 0 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 0, 100)
            framework_logger.info("Plan pages verified as 0 of 100 used on Overview page")

            # Verify plan pages tooltip
            DashboardHelper.verify_tooltip(page, "plan")
            framework_logger.info("Plan pages tooltip verified on Overview page")

            # Verify trial pages tooltip
            DashboardHelper.verify_tooltip(page, "trial")
            framework_logger.info("Trial pages tooltip verified on Overview page")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info("Rollover pages verified as 0 of 0 used on Overview page")

            # Set printed pages to 15
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "15")
            framework_logger.info("Set printed pages to 15")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify the progress bars for plan, rollover, credited pages on Overview Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Overview Page")

            # Sees the credited pages as 15 of 30 used on Overview page
            DashboardHelper.verify_pages_used(page, "credited", 15, 30)
            framework_logger.info("Credited pages verified as 15 of 30 used on Overview page")

            # Sees the plan pages as 0 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 0, 100)
            framework_logger.info("Plan pages verified as 0 of 100 used on Overview page")

            # Sees the trial pages used on Overview page
            DashboardHelper.verify_trial_pages_used(page, 0)
            framework_logger.info("Trial pages verified as 0 used on Overview page")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info("Rollover pages verified as 0 of 0 used on Overview page")

            # Set printed pages to 80
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "80")
            framework_logger.info("Set printed pages to 80")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify the progress bars for plan, rollover, credited pages on Overview Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Overview Page")

            # Sees the credited pages as 30 of 30 used on Overview page
            DashboardHelper.verify_pages_used(page, "credited", 30, 30)
            framework_logger.info("Credited pages verified as 30 of 30 used on Overview page")

            # Sees the plan pages as 50 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 50, 100)
            framework_logger.info("Plan pages verified as 50 of 100 used on Overview page")

            # Sees the trial pages used on Overview page
            DashboardHelper.verify_trial_pages_used(page, 0)
            framework_logger.info("Trial pages verified as 0 used on Overview page")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info("Rollover pages verified as 0 of 0 used on Overview page")

            # Set printed pages to 130
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "130")
            framework_logger.info("Set printed pages to 130")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify the progress bars for plan, rollover, credited pages on Overview Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover", "credited"])
            framework_logger.info(f"Verified progress bars for plan, rollover, credited pages on Overview Page")

            # Sees the credited pages as 30 of 30 used on Overview page
            DashboardHelper.verify_pages_used(page, "credited", 30, 30)
            framework_logger.info("Credited pages verified as 30 of 30 used on Overview page")

            # Sees the plan pages as 100 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 100, 100)
            framework_logger.info("Plan pages verified as 100 of 100 used on Overview page")

            # Sees the trial pages used on Overview page
            DashboardHelper.verify_trial_pages_used(page, 0)
            framework_logger.info("Trial pages verified as 0 used on Overview page")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info("Rollover pages verified as 0 of 0 used on Overview page")

            # Verify total printed pages
            DashboardHelper.verify_total_pages_printed(page, 130)
            framework_logger.info("Total printed pages verified as 130 on Overview page")
            framework_logger.info(f"=== C42336966 - Progress bar with and without pages printed on Print History page finished ===")
        except Exception as e:
            framework_logger.error(f"Error during flow execution: {e}")
            raise e
        finally:
            page.close()
