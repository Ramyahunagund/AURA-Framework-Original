from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.overview_page import OverviewPage
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def initiated_unsubscribed_enroll_or_replace_a_printer_after15_min(stage_callback):
    framework_logger.info("=== C49180767 - Initiated_unsubscribed Enroll or replace a printer after 15 min flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            CancellationPlanHelper.select_cancellation_feedback_option(page)
            framework_logger.info("Subscription cancellation initiated")

            # Wait more than 15 minutes
            framework_logger.info("Waiting for 15 minutes to let the session expire...")
            time.sleep(930)
            framework_logger.info("Waited for 15 minutes")

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            # Click cancel button in the session expired modal on the Smart Dashboard
            overview_page.expired_session_cancel.click()
            framework_logger.info("Clicked on cancel button in the session expired modal")

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click(timeout=90000)
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            # Click login button in the session expired modal on the Smart Dashboard
            DashboardHelper.login_on_security_session_expired(page, tenant_email)
            framework_logger.info("Logged in the session expired modal")

            # See the Overview page
            DashboardHelper.sees_status_card(page)
            framework_logger.info("Verified the Overview page")

            framework_logger.info("=== C49180767 - Initiated_unsubscribed Enroll or replace a printer after 15 min flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
