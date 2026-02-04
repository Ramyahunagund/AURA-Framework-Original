from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def emergency_banner(stage_callback):
    framework_logger.info("=== C38215347 - Emergency banner flow started ===")
    common.setup()
    tenant_email = "IIQA.automation+stage1_NO_20240906_151510_9783@outlook.com"

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            # Verify each color banner
            colors = ["blue", "orange", "red"]
            for color in colors:
                framework_logger.info(f"Verifying {color} banner")

                # Check banner exists
                banner_selector = getattr(overview_page, f"{color}_banner")
                expect(banner_selector).to_be_visible()
                                
                # Find banner elements
                banner_container = banner_selector.locator("xpath=../../../..")
                header = banner_container.locator(overview_page.banner_header).first
                content = banner_container.locator(overview_page.banner_content)
                arrow = banner_container.locator(overview_page.banner_arrow)
                dismiss = banner_container.locator(overview_page.banner_dismiss)
                
                # Verify header and content are visible
                expect(header).to_be_visible()
                expect(content).to_be_visible()
                
                # Click arrow
                arrow.click()
                time.sleep(3)
                
                # Click dismiss
                dismiss.click()
                
                framework_logger.info(f"Verified {color} banner successfully")
            
            # Verify black banner is not displayed
            expect(page.locator("text=US black banner Title")).not_to_be_visible()
            framework_logger.info("Verified banner text is no longer visible")

            framework_logger.info("=== C38215347 - Emergency banner flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
