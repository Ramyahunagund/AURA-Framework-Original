# test_flows/AlertBanner/alert_banner.py

from core.playwright_manager import PlaywrightManager
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage

import time
import traceback
from playwright.sync_api import expect
from core.settings import framework_logger
import test_flows_common.test_flows_common as common

def alert_banner(stage_callback):
    framework_logger.info("=== C38569201 - Alert banner flow started ===")
    common.setup()

    timeout_ms = 120000

    with PlaywrightManager() as page:  
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)

            # Navigate to landing page
            page.goto(common._instantink_url, timeout=timeout_ms)
            framework_logger.info(f"Navigated to landing page: {common._instantink_url}")

            # Accept privacy banner if present
            privacy_banner_page.accept_privacy_banner()

            # Verify the alert banner is displayed
            expect(landing_page.alert_banner).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Alert banner container is visible")

            # Verify alert banner components
            alert_banner_container = page.locator(landing_page.elements.alert_banner_container).first
            expect(alert_banner_container).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Alert banner module is visible")

            # Verify alert banner icon is visible
            alert_icon = page.locator(landing_page.elements.alert_banner_icon)
            expect(alert_icon).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Alert banner icon is visible")

            # Verify alert banner content is visible
            alert_content = page.locator(landing_page.elements.alert_banner_content)
            expect(alert_content).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Alert banner content is visible")

            # Get the banner text content
            banner_text = alert_content.text_content()
            framework_logger.info(f"Alert banner text: {banner_text}")

            # Verify close button is visible
            close_button = page.locator(landing_page.elements.alert_banner_close)
            expect(close_button).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Alert banner close button is visible")

            framework_logger.info("=== C38569201 - Alert banner flow ended successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Alert Banner test: {e}\n{traceback.format_exc()}")
            raise e
