from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from playwright.sync_api import expect, sync_playwright
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancel_temp_cancellation_and_pause_pan_on_temporary_cancellation_subscriptions(stage_callback):
    framework_logger.info("=== C43471132 - Cancel temp cancellation and Pause Pan on temporary cancellation subscriptions flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info("Subscription moved to subscribed state and free months removed")

            # Charge a billing cycle
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "70")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 70 pages")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Pause plan for 2 months on Overview page
            DashboardHelper.pause_plan(page, 2)
            framework_logger.info(f"Paused plan for 2 months on Overview page")

            # Click and confirm Resume Plan
            DashboardHelper.click_resume_plan_banner(page)
            DashboardHelper.click_resume_plan(page)
            framework_logger.info(f"Clicked on Resume Plan button")

            # Verify rollover pages on Overview page: 0 of 30
            DashboardHelper.verify_pages_used(page, "rollover", 0, 30)
            framework_logger.info("Verified rollover pages as 0 of 30 on Overview page")

            # Verify rollover pages on current billing cycle
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.verify_rails_admin_info(page, "Initial rollover pages", "30")

            # Charge a billing cycle
            RABaseHelper.get_links_by_title(page, "Subscription").first.click()
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 100 pages")

            # Verify Billing Cycle Data
            page.reload()
            GeminiRAHelper.verify_rails_admin_info(page, "Initial rollover pages", "30")
            GeminiRAHelper.billing_cycle_data(page, "100", "100", "CPT-100", "true", "BillingCycle")
            framework_logger.info("Verified Billing Cycle Data")

            # Charge a billing cycle
            page.locator('//a[starts-with(text(), "Subscription #")]').click()
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "70")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 70 pages")

            # Verify Billing Cycle Data
            page.reload()
            GeminiRAHelper.verify_rails_admin_info(page, "Initial rollover pages", "30")
            GeminiRAHelper.billing_cycle_data(page, "100", "70", "CPT-100", "true", "BillingCycle")
            framework_logger.info("Verified Billing Cycle Data")

            framework_logger.info("=== C43471132 - Cancel temp cancellation and Pause Pan on temporary cancellation subscriptions flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
