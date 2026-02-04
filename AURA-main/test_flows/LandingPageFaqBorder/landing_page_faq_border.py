# test_flows/LandingPageFaqBorder/landing_page_faq_border.py

from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage

import traceback
from playwright.sync_api import expect
from core.settings import framework_logger
from core.playwright_manager import PlaywrightManager
import test_flows_common.test_flows_common as common

def landing_page_faq_border(stage_callback):
    framework_logger.info("=== C38471736 - Landing page FAQ border validation flow started ===")
    common.setup()

    timeout_ms = 120000

    with PlaywrightManager() as page:
        page.set_default_timeout(timeout_ms)

        privacy_banner_page = PrivacyBannerPage(page)
        landing_page = LandingPage(page)

        try:

            # Navigate to the landing page
            framework_logger.info(f"Navigating to: {common._instantink_url}")
            page.goto(common._instantink_url, timeout=timeout_ms)

            # Accept privacy banner
            privacy_banner_page.accept_privacy_banner()

            # Scroll down to the FAQ section
            framework_logger.info("Scrolling to FAQ section")
            landing_page.faqs_section.scroll_into_view_if_needed()

            # Verify the FAQ section is visible
            framework_logger.info("Verifying FAQ section is visible")
            expect(landing_page.faqs_section).to_be_visible(timeout=timeout_ms)

            # Verify the FAQ section has no border
            framework_logger.info("Checking FAQ section border properties")
            border_properties = page.evaluate('''(selector) => {
                const element = document.querySelector(selector);
                if (!element) return null;
                const styles = window.getComputedStyle(element);
                return {
                    borderTopWidth: styles.borderTopWidth,
                    borderRightWidth: styles.borderRightWidth,
                    borderBottomWidth: styles.borderBottomWidth,
                    borderLeftWidth: styles.borderLeftWidth,
                    borderTopStyle: styles.borderTopStyle,
                    borderRightStyle: styles.borderRightStyle,
                    borderBottomStyle: styles.borderBottomStyle,
                    borderLeftStyle: styles.borderLeftStyle,
                    border: styles.border
                };
            }''', landing_page.get_selector("faqs_section"))

            framework_logger.info(f"FAQ section border properties: {border_properties}")

            # Check that all border widths are 0px or border style is none
            border_top_width = border_properties.get("borderTopWidth", "0px")
            border_right_width = border_properties.get("borderRightWidth", "0px")
            border_bottom_width = border_properties.get("borderBottomWidth", "0px")
            border_left_width = border_properties.get("borderLeftWidth", "0px")

            border_top_style = border_properties.get("borderTopStyle", "none")
            border_right_style = border_properties.get("borderRightStyle", "none")
            border_bottom_style = border_properties.get("borderBottomStyle", "none")
            border_left_style = border_properties.get("borderLeftStyle", "none")

            # A border has no visual effect if:
            # 1. The border-style is 'none' or 'hidden', OR
            # 2. The border-width is '0px'
            has_no_border = (
                (border_top_style in ["none", "hidden"] or border_top_width == "0px") and
                (border_right_style in ["none", "hidden"] or border_right_width == "0px") and
                (border_bottom_style in ["none", "hidden"] or border_bottom_width == "0px") and
                (border_left_style in ["none", "hidden"] or border_left_width == "0px")
            )

            assert has_no_border, (
                f"FAQ section should have no border, but found: "
                f"top={border_top_width} ({border_top_style}), "
                f"right={border_right_width} ({border_right_style}), "
                f"bottom={border_bottom_width} ({border_bottom_style}), "
                f"left={border_left_width} ({border_left_style})"
            )

            framework_logger.info("FAQ section has no border (validation passed)")
            framework_logger.info("=== C38471736 - Landing Page FAQ border validation flow ended successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the Landing Page FAQ border test: {e}\n{traceback.format_exc()}")
            raise e
        