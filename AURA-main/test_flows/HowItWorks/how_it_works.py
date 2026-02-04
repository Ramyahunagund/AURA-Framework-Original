from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.landing_page_helper import LandingPageHelper
from pages.landing_page import LandingPage
from pages.privacy_banner_page import PrivacyBannerPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def how_it_works(stage_callback):
    framework_logger.info("=== C38471744 - How it works section validation flow started ===")
    common.setup()

    with PlaywrightManager() as page:
        try:
            landing_page = LandingPage(page)
            privacy_banner_page = PrivacyBannerPage(page)

            # Launch the Consumer Landing page
            framework_logger.info("Launching Consumer Landing page")
            LandingPageHelper.open(page)
            privacy_banner_page.accept_privacy_banner()
            framework_logger.info("Consumer Landing page loaded successfully")

            # Close any banners that might be present
            try:
                # Using a generic banner close button selector
                banner_close = page.locator("[class*='close'], [aria-label*='close' i], [data-testid*='close']")
                if banner_close.first.is_visible(timeout=3000):
                    banner_close.first.click()
                    framework_logger.info("Closed banner")
            except Exception as e:
                framework_logger.info(f"No banner to close or banner not found: {e}")

            # Scroll to the "How it works" section
            how_it_works_section = landing_page.how_it_works
            how_it_works_section.scroll_into_view_if_needed(timeout = 30000)
            page.wait_for_timeout(1000)
            framework_logger.info("Scrolled to 'How it works' section")

            # Step 3: Verify the "How it works" section is displayed
            assert(how_it_works_section.is_visible()), "'How it works' section is not visible"
            framework_logger.info("'How it works' section is visible")

            # Verify Never run out of ink section
            how_it_works_never_run_out = page.locator(landing_page.elements.how_it_works_never_run_out)
            expect(how_it_works_never_run_out).to_be_visible(timeout=30000)
            framework_logger.info("'Never run out of ink' section is visible")

            # Verify "Save time and money" element
            how_it_works_save = page.locator(landing_page.elements.how_it_works_save)
            expect(how_it_works_save).to_be_visible(timeout=30000)
            framework_logger.info("'Save time and money' element is visible")

            # Verifying including typography, colors, layout, and images
            framework_logger.info("Capturing 'How it works' section for validation")
            stage_callback("how_it_works_section", page, animations=True)
            framework_logger.info("'How it works' section captured successfully")

            framework_logger.info("=== C38471744 - How it works section validation flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the How it works validation flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()