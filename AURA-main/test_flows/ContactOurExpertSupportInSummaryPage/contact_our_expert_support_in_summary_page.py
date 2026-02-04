from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from core.playwright_manager import PlaywrightManager
from pages.overview_page import OverviewPage
from core.settings import framework_logger
from playwright.sync_api import expect
import urllib3
import traceback
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pages.cancellation_page import CancellationPage

def contact_our_expert_support_in_summary_page(stage_callback):
    framework_logger.info("=== C40797066 - Contact our expert support flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click on Cancel Instant Ink on Overview page
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            #new tab is opened and the page for standard printer replacement flow is displayed.
            CancellationPlanHelper.validate_transfer_subscription_contact_support_link(page,section_title="Contact Support")
            framework_logger.info("Validated Contact Support link on Cancellation Summary Page")

            framework_logger.info("=== C40797066 - Contact our expert support flow completed ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e