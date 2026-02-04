# test_flows/GetPaperDelivered/get_paper_delivered.py

from core.playwright_manager import PlaywrightManager
from pages import landing_page
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage
from playwright.sync_api import expect
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
import re
import time
import traceback

def get_paper_delivered(stage_callback):
    framework_logger.info("=== Get Paper Delivered flow started ===")
    common.setup()

    timeout_ms = 120000

    with PlaywrightManager() as page:
        privacy_banner_page = PrivacyBannerPage(page)
        landing_page = LandingPage(page)
        
        try:
            # Step 1: Launch the Consumer Landing page
            framework_logger.info("Step 1: Navigating to landing page")
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()

            # Ensure the page is loaded by checking a key element
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)

            # Scroll down the page to make the paper delivery section visible
            framework_logger.info("Scrolling down to reveal paper delivery section")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            time.sleep(1) 

            # Step 2: Verify the "Get paper delivered with your plan" section is displayed
            framework_logger.info("Step 2: Verifying paper delivery section is visible")
            expect(landing_page.paper_delivery_section).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Paper delivery section is visible")

            # Step 3: Check Typography / Image
            framework_logger.info("Step 3: Checking typography and image elements")
            expect(landing_page.paper_delivery_title).to_be_visible(timeout=timeout_ms)
            expect(landing_page.paper_delivery_description).to_be_visible(timeout=timeout_ms)
            expect(landing_page.paper_delivery_image).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Typography and image elements are present")

            # Validate the title text
            title_text = landing_page.paper_delivery_title.text_content()
            framework_logger.info(f"Paper delivery title: {title_text}")

            # Step 4: Check the link style
            framework_logger.info("Step 4: Checking 'Learn about pricing and offers' link")
            expect(landing_page.paper_delivery_learn_more_link).to_be_visible(timeout=timeout_ms)

            # Get link text
            link_text = landing_page.paper_delivery_learn_more_link.text_content()
            framework_logger.info(f"Link text: {link_text}")
            assert "Learn about pricing and offers" in link_text or "pricing" in link_text.lower(), \
                f"Expected 'Learn about pricing and offers' text but got: {link_text}"

            # Step 5: Check the superscript
            framework_logger.info("Step 5: Checking superscript for footnote reference")
            
            # Verify the superscript is present and get its text
            expect(landing_page.paper_delivery_superscript).to_be_visible(timeout=timeout_ms)
            superscript_text = landing_page.paper_delivery_superscript.text_content()
            framework_logger.info(f"Superscript text: {superscript_text}")

            # Validate the superscript text            
            assert superscript_text != "", "Superscript should not be empty"

            # Verify that the superscript references a footnote
            expect(landing_page.combined_savings_footnote).to_be_visible(timeout=timeout_ms)
            combined_savings_footnote = landing_page.combined_savings_footnote.text_content().strip()

            # Validate the footnote text
            assert combined_savings_footnote != "", "Footnote text should not be empty"

            # Check that the superscript text is mentioned in the footnote
            assert superscript_text in combined_savings_footnote, \
                f"Footnote does not reference superscript '{superscript_text}'"
            framework_logger.info(f"Superscript '{superscript_text}' correctly references footnote.")

            # Step 6: Click the "Learn about pricing and offers" link
            framework_logger.info("Step 6: Clicking the 'Learn about pricing and offers' link")
            with page.expect_popup() as popup_info:
                landing_page.paper_delivery_learn_more_link.click()
            new_page = popup_info.value
            new_page.wait_for_load_state("networkidle", timeout=timeout_ms)
            current_url = new_page.url

            # Verify the URL navigation
            framework_logger.info(f"Navigated to URL: {current_url}")
            expected_url_pattern = r"/l/v2/paper"
            assert re.search(expected_url_pattern, current_url), \
                f"Expected URL to match pattern '{expected_url_pattern}' but got: {current_url}"
            framework_logger.info(f"Successfully navigated to paper page: {current_url}")
            
            framework_logger.info("=== Get Paper Delivered flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Get Paper Delivered test: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
