# test_flows/LandingPageFAQLinks/landing_page_faq_links.py

from core.playwright_manager import PlaywrightManager
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage
from helper.landing_page_helper import LandingPageHelper

import traceback
from playwright.sync_api import expect
from core.settings import framework_logger
import test_flows_common.test_flows_common as common

def landing_page_faq_links(stage_callback):
    framework_logger.info("=== C38421768 - Consumer Landing Page FAQ links flow started ===")
    common.setup()

    timeout_ms = 120000

    with PlaywrightManager() as page:
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)

            # Launch the Consumer Landing Page
            page.goto(common._instantink_url, timeout=timeout_ms)
            framework_logger.info("Launched Consumer Landing Page")

            # Accept privacy banner
            privacy_banner_page.accept_privacy_banner()

            # Verify landing page is loaded
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Landing page loaded successfully")

            # Validate FAQ links
            LandingPageHelper.validate_faq_links(page)
            framework_logger.info("FAQ links validation completed")

            framework_logger.info("=== C38421768 - Consumer Landing Page FAQ links flow ended ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Landing Page FAQ links test: {e}\n{traceback.format_exc()}")
            raise e