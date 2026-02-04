from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.overview_page import OverviewPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


TC="C41949162"
def waiver_pages(stage_callback):
    framework_logger.info("=== C41949162 waiver_pages started ===")
    common.setup()
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"Generated tenant_email={tenant_email}")
    with PlaywrightManager() as page:
        try:
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)

            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Dashboard first access completed successfully")
            overview_page = OverviewPage(page)
            body_text = overview_page.status_card_body.inner_text()
            assert "700" not in body_text, f"Text '700' found in body: {body_text}"
            framework_logger.info("Test completed successfully")
        except Exception as e:
            framework_logger.error(f"Test with Error: {e}\n{traceback.format_exc()}")
            raise e
