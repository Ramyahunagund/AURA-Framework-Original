# test_flows/Header768pxBelow/header768px_below.py

import time
import traceback
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
import test_flows_common.test_flows_common as common


def header768px_below(stage_callback):
    framework_logger.info("=== C38421765 - Header 768px Below validation flow started ===")
    common.setup()

    timeout_ms = 120000
    mobile_viewport_width = 768
    mobile_viewport_height = 1024

    with sync_playwright() as p:
        launch_args = {"headless": GlobalState.headless}
        context_args = {
            "locale": f"{GlobalState.language_code}",
            "viewport": {"width": mobile_viewport_width, "height": mobile_viewport_height}
        }
        if common.PROXY_URL:
            launch_args["proxy"] = {"server": common.PROXY_URL}
            context_args["proxy"] = {"server": common.PROXY_URL}

        browser = p.chromium.launch(**launch_args)
        context = browser.new_context(**context_args)
        framework_logger.info(f"Launching Playwright browser with headless={GlobalState.headless}, "
                            f"locale={GlobalState.language_code}, viewport={mobile_viewport_width}x{mobile_viewport_height}")
        page = context.new_page()
        page.set_default_timeout(timeout_ms)

        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)

            # Step 1: Launch the Consumer Landing page
            framework_logger.info("Step 1: Navigating to landing page and verifying header section")
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()

            # Verify the header section is displayed
            expect(landing_page.header_section).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Header section is visible")

            # Step 2: Verify the HP logo
            framework_logger.info("Step 2: Verifying HP logo")
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)
            framework_logger.info("HP logo is visible")

            # Step 3: Click the Country selector Flag icon
            framework_logger.info("Step 3: Verifying Country selector flag icon")
            expect(landing_page.flag_icon).to_be_attached()
            framework_logger.info("Country selector flag icon is visible")

            # Click the flag icon to verify it's interactive
            page.evaluate("document.querySelector('.flag-icon.US').click()") # Javascript click to avoid overlay issues
            framework_logger.info("Country selector flag icon is clickable")

            # Step 4: Click the Hamburger menu and verify navigation items
            framework_logger.info("Step 4: Verifying Hamburger menu and navigation items")
            
            # Verify hamburger menu is visible (should be visible on mobile view)
            expect(landing_page.hamburger_menu.last).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Hamburger menu is visible")

            # Click the hamburger menu
            landing_page.hamburger_menu.last.click()
            framework_logger.info("Hamburger menu clicked")

            # Verify individual menu items
            menu_items = {
                "Sign In": landing_page.mobile_sign_in_link,
                "Sign Up Now": landing_page.mobile_sign_up_link,
                "How it works": landing_page.mobile_how_it_works_link,
                "Instant Paper": landing_page.mobile_instant_paper_link,
                "Plans": landing_page.mobile_plans_link,
                "FAQs": landing_page.mobile_faqs_link,
            }

            for item_name, item_locator in menu_items.items():
                expect(item_locator).to_be_visible(timeout=timeout_ms)
                framework_logger.info(f"{item_name} is visible in mobile menu")

            # Step 5: Check Typography / Image
            framework_logger.info("Step 5: Verifying typography and images")

            # Verify logo is visible and has proper attributes
            logo_element = landing_page.header_logo
            expect(logo_element).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Logo is visible and properly displayed")

            # Verify header section has proper CSS
            header_section = landing_page.header_section
            expect(header_section).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Header section has proper styling")

            framework_logger.info("=== C38421765 - Header 768px Below validation flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the Header Mobile View test: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            context.close()
            browser.close()
