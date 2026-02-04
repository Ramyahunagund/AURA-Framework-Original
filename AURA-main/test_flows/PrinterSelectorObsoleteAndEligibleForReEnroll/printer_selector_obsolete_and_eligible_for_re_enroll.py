from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.cancellation_page import CancellationPage
from helper.ra_base_helper import RABaseHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common 
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def printer_selector_obsolete_and_eligible_for_re_enroll(stage_callback):
    framework_logger.info("=== C42896598 - Printer Selector (obsolete and eligible for re-enroll) flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        side_menu = DashboardSideMenuPage(page)
        cancellation_page = CancellationPage(page)
        try:
            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Cancel the subscription
            UpdatePlanHelper.cancellation_subscription(page)
            cancellation_page.continue_button.click()
            framework_logger.info("User cancelled subscription")

	        # New Billing Cycle
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "5")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New Billing Cycle charged")
           
	        # Executes the resque job: SubscriptionUnsubscriberJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionUnsubscriberJob"])
            framework_logger.info("SubscriptionUnsubscriberJob executed")

            # New Event Shift - 40 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "40")
            framework_logger.info(f"Shifted 40 days")

            # Executes the resque job: SubscriptionObsoleteJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionObsoleteJob"])
            framework_logger.info("SubscriptionObsoleteJob executed")

            # Verify subscription state is obsolete
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            time.sleep(120)
            page.reload()
            GeminiRAHelper.verify_rails_admin_info(page, "State", "obsolete")
            framework_logger.info("Verified subscription state is obsolete")

            # Access Dashboard
            DashboardHelper.access(page)
            framework_logger.info(f"Accessed Dashboard")

            # Verify cancelled printer on printer selector - Overview page
            side_menu.click_overview()
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")
            framework_logger.info("Cancelled printer is displayed on printer selector - Overview page")

            # Verify cancelled printer on printer selector - Print History page
            side_menu.click_print_history()
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")
            framework_logger.info("Cancelled printer is displayed on printer selector - Print History page")

            framework_logger.info("=== C42896598 - Printer Selector (obsolete and eligible for re-enroll) flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
