from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage

import time
import traceback
from core.playwright_manager import PlaywrightManager
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
import re

def landing_page_validation(stage_callback):
    framework_logger.info("=== Landing page flow started ===")
    common.setup()

    timeout_ms = 120000

    # with sync_playwright() as p:
    #     launch_args = {"headless": GlobalState.headless}
    #     context_args = {
    #         "locale": f"{GlobalState.language_code}",
    #         "viewport": {"width": 1650, "height": 600}
    #     }
    #     if common.PROXY_URL:
    #         launch_args["proxy"] = {"server": common.PROXY_URL}
    #         context_args["proxy"] = {"server": common.PROXY_URL}

    #     browser = p.chromium.launch(**launch_args)
    #     context = browser.new_context(**context_args)
    #     framework_logger.info(f"Launching Playwright browser with headless={GlobalState.headless}, locale={GlobalState.language_code}")
    #     page = context.new_page()
    #     page.set_default_timeout(timeout_ms)
    with PlaywrightManager() as page:
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()
            framework_logger.info("Starting validation for #box-container screenshot")
            stage_callback("landing_page", page, screenshot_only=True)
            framework_logger.info("Validation completed for #box-container screenshot")
            landing_page.country_selector.click()
            landing_page.country_selector.scroll_into_view_if_needed()
            landing_page.country_selector_it.click()
            with landing_page.page.expect_popup() as popup_info:
                landing_page.footer_accessibility.scroll_into_view_if_needed()
                landing_page.footer_accessibility.click()
            new_page = popup_info.value
            time.sleep(3) 
            new_page.close()

            framework_logger.info("=== Landing Page validation completed ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Landing Page test: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            browser.close()
