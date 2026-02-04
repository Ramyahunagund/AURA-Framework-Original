from test_flows.BillingCycle.billing_cycle import billing_cycle
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
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def monthly_summary_progress_bar_overview(stage_callback):
    framework_logger.info("=== C41929005 - Monthly Summary Progress Bar Overview page flow started ===")
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

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            # Does not see free months in Overview page
            DashboardHelper.doesnt_see_free_months(page)
            framework_logger.info(f"Verified free months are not displayed in Overview page")

            #Access subscription by tenant
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)

            # Access Billing Summary
            GeminiRAHelper.access_first_billing_cycle(page)
            framework_logger.info("Access Billing Summary page")

            #Get billing cycle start and end dates
            start_time, end_time = GeminiRAHelper.get_billing_cycle_times(page)

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            # Verify the monthly section on status card
            DashboardHelper.verify_monthly_section_on_status_card(page, '7.99', start_time, end_time)

            # Verify the progress bars for plan, rollover pages on Overview Page
            DashboardHelper.verify_progress_bars_visible(page, ["plan", "rollover"])
            framework_logger.info(f"Verified progress bars for plan, rollover pages on Overview Page")

            # Sees the plan pages as 0 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 0, 100)
            framework_logger.info(f"Verified plan pages as 0 of 100 used on Overview page")

            # Sees the plan pages tooltip
            DashboardHelper.verify_pages_on_tooltip(page, "plan", total_pages=100 )
            framework_logger.info(f"Verified plan pages tooltip")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 0)
            framework_logger.info(f"Verified rollover pages as 0 of 0 used on Overview page")

            # Sees the plan pages tooltip
            DashboardHelper.verify_pages_on_tooltip(page, "rollover", total_pages=300)
            framework_logger.info(f"Verified plan pages tooltip")

            # Set printed pages to 50
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "50")
            framework_logger.info("Set printed pages to 50")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            # Sees the plan pages as 50 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 50, 100)
            framework_logger.info(f"Verified plan pages as 50 of 100 used on Overview page")

            # Set printed pages to 105
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "105")
            framework_logger.info("Set printed pages to 105")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

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
            DashboardHelper.verify_pages_on_tooltip(page, "additional", total_pages=10)
            framework_logger.info(f"Verified additional pages tooltip")

            # Verify message to set addicional info
            overview_page = OverviewPage(page)
            expect(overview_page.set_pages_addicional).to_have_text("You have purchased 1 set of additional pages (10 pages/set).")

            # Sees the 105 total pages printed on Overview page
            DashboardHelper.verify_total_pages_printed(page, 105)
            framework_logger.info(f"Verified total pages printed as 105 Overview page")

            framework_logger.info("=== C41929005 - Monthly Summary Progress Bar Overview page flow started flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e