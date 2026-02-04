# test_flows/LandingPageFAQsContentLayout/landing_page_faqs_content_layout.py

from core.playwright_manager import PlaywrightManager
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage

import time
import traceback
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
import test_flows_common.test_flows_common as common

def landing_page_faq_content_layout(stage_callback):
    framework_logger.info("=== C38421770 - Consumer Landing Page FAQs Content & Layout flow started ===")
    common.setup()

    timeout_ms = 120000

    with PlaywrightManager() as page:
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)

            # Launch the Consumer Landing page
            framework_logger.info("Navigating to Consumer Landing page")
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()

            # Scroll down to the FAQs section
            framework_logger.info("Scrolling to FAQs section")
            landing_page.faqs_section.scroll_into_view_if_needed()
            time.sleep(1)  # Allow time for animations/rendering

            # Verify the FAQs section is displayed
            framework_logger.info("Verifying FAQs section is visible")
            expect(landing_page.faqs_section).to_be_visible(timeout=timeout_ms)
            framework_logger.info("FAQs section is visible")

            # Verify the General/Monthly plans/Yearly plans/Pay As You Print plans option are displayed.
            expect(landing_page.faq_general_tab).to_be_visible()
            expect(landing_page.faq_monthly_plans_tab).to_be_visible()
            expect(landing_page.faq_yearly_plans_tab).to_be_visible()
            expect(landing_page.faq_pay_as_you_print_tab).to_be_visible()  
            framework_logger.info("FAQ tab options are visible")   
                               
            # Verify typography and styling
            framework_logger.info("Verifying typography and styling")
     
            # Get computed styles for typography validation
            faq_section_element = landing_page.faqs_section

            # Validate font properties
            try:
                font_family = faq_section_element.evaluate("el => window.getComputedStyle(el).fontFamily")
                font_size = faq_section_element.evaluate("el => window.getComputedStyle(el).fontSize")
                font_weight = faq_section_element.evaluate("el => window.getComputedStyle(el).fontWeight")
                line_height = faq_section_element.evaluate("el => window.getComputedStyle(el).lineHeight")

                framework_logger.info(f"FAQ section typography:")
                framework_logger.info(f"  - Font family: {font_family}")
                framework_logger.info(f"  - Font size: {font_size}")
                framework_logger.info(f"  - Font weight: {font_weight}")
                framework_logger.info(f"  - Line height: {line_height}")

                # Basic validation - ensure font properties are set
                assert font_family is not None and font_family != "", "Font family should be defined"
                assert font_size is not None and font_size != "", "Font size should be defined"

            except Exception as e:
                framework_logger.error(f"Error validating typography: {e}")
                raise

            framework_logger.info("=== C38421770 - Consumer Landing Page FAQs Content & Layout flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the Consumer Landing Page FAQs test: {e}\n{traceback.format_exc()}")
            raise e
 