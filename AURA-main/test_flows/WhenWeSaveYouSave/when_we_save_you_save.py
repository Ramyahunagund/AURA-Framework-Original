import time
import urllib3
import traceback
from playwright.sync_api import expect
from core.playwright_manager import PlaywrightManager
from pages.landing_page import LandingPage
from core.settings import framework_logger
from helper.landing_page_helper import LandingPageHelper
import test_flows_common.test_flows_common as common


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def when_we_save_you_save(stage_callback):
    framework_logger.info("=== C38471747 - When We save you save flow started ===")
    common.setup()

    with PlaywrightManager() as page:
        try:
            landing_page = LandingPage(page)

            # Access Landing Page
            LandingPageHelper.access(page)

            # Verify basic page elements are visible
            timeout_ms = 120000
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Landing page loaded successfully")

            # Verify the "When we save, you save" section is displayed
            when_we_save_element = landing_page.when_we_save
            when_we_save_element.scroll_into_view_if_needed()
            expect(when_we_save_element).to_be_visible(timeout=timeout_ms)
            framework_logger.info("'When we save, you save' section is visible")

            # Get the section title text
            section_title = when_we_save_element.text_content()
            framework_logger.info(f"Section title text: '{section_title}'")

            # Verify the title is not empty
            assert section_title and len(section_title.strip()) > 0, "Section title should not be empty"
            framework_logger.info("Section title has content")

            # Check if section content exists
            section_content = page.locator(landing_page.elements.when_we_save_section)
            if section_content.count() > 0:
                expect(section_content).to_be_visible(timeout=10000)
                framework_logger.info("Section content area is visible")

            # Check Typography and Images
            framework_logger.info("Checking typography and images")

            # Check if image exists in the section
            section_image = page.locator(landing_page.elements.when_we_save_image)
            if section_image.count() > 0:
                expect(section_image).to_be_visible(timeout=10000)
                framework_logger.info("Section image is visible")

            # Verify image has loaded
                img_src = section_image.get_attribute("src")
                assert img_src and len(img_src) > 0, "Image should have a valid src attribute"
                framework_logger.info(f"Image src: {img_src}")

            # Verify the section is properly positioned
            bounding_box = when_we_save_element.bounding_box()
            if bounding_box:
                framework_logger.info(f"Section position - x: {bounding_box['x']}, y: {bounding_box['y']}, width: {bounding_box['width']}, height: {bounding_box['height']}")
                assert bounding_box['width'] > 0 and bounding_box['height'] > 0, "Section should have valid dimensions"
                framework_logger.info("Section has valid dimensions")

            # Additional verification: Check surrounding context to ensure proper layout
            expect(landing_page.ink_plans_tab).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Related sections are visible, layout appears correct")

            framework_logger.info("=== C38471747 - When We save you save flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the C38471747 - When We save you save test: {e}\n{traceback.format_exc()}")
            raise e
