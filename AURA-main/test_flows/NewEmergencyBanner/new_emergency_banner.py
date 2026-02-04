from core.playwright_manager import PlaywrightManager
from helper.landing_page_helper import LandingPageHelper
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage

import time
import traceback
from playwright.sync_api import expect
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def new_emergency_banner(stage_callback):  

    framework_logger.info("=== C38569228 - New Emergency banner flow started ===")
    common.setup()

    timeout_ms = 120000

    with PlaywrightManager() as page:
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)

            # Launch the landing page with basic URL
            framework_logger.info("Step 1: Launch the landing page with basic URL")
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Landing page loaded successfully")
            
            # Test each country's emergency banner
            countries_to_test = ["Finland", "Bulgaria", "Portugal", "Australia", "Norway", "Poland", "Estonia"]
            
            for country in countries_to_test:
                framework_logger.info(f"\n=== Testing {country} Emergency Banner ===")
                
                # Change country
                LandingPageHelper.select_country(page, country)
                page.wait_for_load_state("networkidle", timeout=30000)
                
                # Step 2: Verify the New Emergency banner is displayed as per Figma Design
                framework_logger.info("Verify the New Emergency banner is displayed well as per Figma Design")
                LandingPageHelper.validate_new_emergency_banner(page, country)
                
                # Verify banner is visible
                expect(landing_page.emergency_banner_header).to_be_visible(timeout=timeout_ms)
                banner_element = landing_page.emergency_banner_header.locator("..")

                # Check the banner - Verify expanded by default with detailed information
                framework_logger.info("Check the banner - Verify displayed as expanded by default")
                
                # Verify detailed information is shown well
                title = banner_element.locator(landing_page.alert_banner_title).first                
                body = (landing_page.alert_banner_body).first
                expect(title).to_be_visible(timeout=timeout_ms)
                expect(body).to_be_visible(timeout=timeout_ms)
                framework_logger.info("Title and body are visible")
                
                # Check subtitle (Landing Page only)
                subtitle = banner_element.locator(landing_page.alert_banner_subtitle)
                if subtitle.count() > 0:
                    expect(subtitle.first).to_be_visible(timeout=timeout_ms)
                    framework_logger.info("Subtitle is visible")

                # Check the link on the banner - Verify "Hide" link
                hide_link = banner_element.locator(landing_page.alert_banner_hide_link).first
                expect(hide_link).to_be_visible(timeout=timeout_ms)
                framework_logger.info("Hide link is visible")

                # Click the "Hide" link - Verify short message and "Show" link
                framework_logger.info("Step 5: Click the 'Hide' link")
                hide_link.click()
                time.sleep(2)  # Wait for animation
                
                show_link = banner_element.locator(landing_page.alert_banner_show_link).first
                expect(show_link).to_be_visible(timeout=timeout_ms)
                framework_logger.info("Show link is displayed after hiding")

                # Click the "Show" link - Verify banner expands with full message
                framework_logger.info("Click the 'Show' link")
                show_link.click()
                time.sleep(2)  # Wait for animation
                
                expect(body).to_be_visible(timeout=timeout_ms)
                framework_logger.info("Banner expanded and full message is visible")                

                # Check the Dismiss option - Verify X button
                dismiss_button = banner_element.locator(landing_page.alert_banner_dismiss_button)
                if dismiss_button.count() > 0:
                    expect(dismiss_button.first).to_be_visible(timeout=timeout_ms)
                    framework_logger.info("X button (dismiss) is visible")
                    
                    # Click the X button - Verify banner disappears
                    framework_logger.info("Click the X button")
                    dismiss_button.first.click()
                    time.sleep(2)  # Wait for animation

                    expect(landing_page.emergency_banner_header).not_to_be_visible(timeout=timeout_ms)
                    framework_logger.info("Banner disappeared after clicking X button")
                else:
                    framework_logger.info("This banner is not dismissible (no X button)")

                # Check the Landing page - Verify still displayed well
                expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)
                expect(landing_page.sign_in_button).to_be_visible(timeout=timeout_ms)
                framework_logger.info("Landing page is still displayed well")
                
                framework_logger.info(f"=== {country} Emergency Banner test completed successfully ===\n")

            framework_logger.info("=== C38569228 - All countries Emergency banner test completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the New Emergency Banner test: {e}\n{traceback.format_exc()}")
            raise e