import traceback
from core.playwright_manager import PlaywrightManager
from helper.landing_page_helper import LandingPageHelper
from pages.privacy_banner_page import PrivacyBannerPage
import test_flows_common.test_flows_common as common
from core.settings import framework_logger
from playwright.sync_api import expect

TC="C39365496"
def one_trust_cookie_banner(stage_callback):
    framework_logger.info("=== C39365496 One Trust Cookie Banner flow started ===")
    common.setup()
    try:
        with PlaywrightManager() as page:
                LandingPageHelper.open(page)
                privacy_banner_page = PrivacyBannerPage(page)
                privacy_banner_page.wait.accept_button(timeout=30000)
                expect(privacy_banner_page.accept_button).to_be_visible()

        with PlaywrightManager() as page:
                page.goto(common._instantink_url + "/enroll/start_v2_web", timeout=120000)
                privacy_banner_page = PrivacyBannerPage(page)
                privacy_banner_page.wait.accept_button(timeout=30000)
                expect(privacy_banner_page.accept_button).to_be_visible()

        framework_logger.info("=== One Trust Cookie Banner flow completed successfully ===")
    except Exception as e:
        framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
        raise e
