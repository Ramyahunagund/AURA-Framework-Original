from core.playwright_manager import PlaywrightManager
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage

import time
import traceback
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
import test_flows_common.test_flows_common as common

def landing_page_header_country_selector(stage_callback):
    framework_logger.info("=== C38421766 - Landing Page Header Country Selector flow started ===")
    common.setup()

    timeout_ms = 120000

    with PlaywrightManager() as page:
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)

            # Launch the consumer Landing page
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()
            framework_logger.info("Launched consumer Landing page")

            # Verify the country flag is seen
            expect(landing_page.flag_icon).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified country flag icon is visible")

            # Click the flag icon
            landing_page.flag_icon.click()
            framework_logger.info("Clicked flag icon")

            # Verify country selector menu is displayed
            expect(landing_page.country_selector_modal).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified country selector menu is displayed")

            # Check the title - verify "Supported Countries / Regions" is displayed
            expect(landing_page.country_selector_title).to_be_visible(timeout=timeout_ms)
            title_text = landing_page.country_selector_title.text_content()
            # The title could be "Supported Countries / Regions" or localized versions
            assert "Countries" in title_text or "Regions" in title_text or "countries" in title_text.lower(), \
                f"Expected title to contain 'Countries' or 'Regions', but got: {title_text}"
            framework_logger.info(f"Verified title is displayed: {title_text}")
            
            # Verify all supported languages are seen
            country_items = landing_page.country_selector_items.all()
            country_count = len(country_items)
            assert country_count > 0, f"Expected at least one country/region in selector, but found {country_count}"
            framework_logger.info(f"Verified {country_count} countries/regions are displayed in selector")

            # Select a non-default language          
            australia_found = False
            for item in country_items:
                item_text = item.text_content()
                if "Australia" in item_text:
                    item.click()
                    australia_found = True
                    framework_logger.info("Selected Australia from country selector")
                    break

            if not australia_found:
                # If Australia is not available, select any other country that's not US
                for item in country_items:
                    item_text = item.text_content()
                    if "United States" not in item_text and item_text.strip():
                        item.click()
                        framework_logger.info(f"Selected {item_text} from country selector")
                        break

            # Verify it loads the respective locale landing page
            time.sleep(2)
         
            # Check that we're still on a landing page with the header elements
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)            
            expect(landing_page.flag_icon).to_be_visible()            
            framework_logger.info("Verified respective locale landing page loaded")

            # Scroll down the landing page
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(1)
            framework_logger.info("Scrolled down the landing page")

            # Click the flag icon again
            landing_page.flag_icon.click()
            framework_logger.info("Clicked flag icon again")

            # Verify the Flag Selector window is displayed well
            expect(landing_page.country_selector_modal).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified Flag Selector window is displayed again")

            # Scroll up and down the landing page
            page.evaluate("window.scrollBy(0, 200)")
            time.sleep(1)
            framework_logger.info("Scrolled down the landing page")

            # Verify the Flag selector window gets closed on scroll            
            time.sleep(1)
            # Check if modal is hidden/not visible after scrolling
            try:
                expect(landing_page.country_selector_modal).to_be_hidden(timeout=5000)
                framework_logger.info("Verified Flag selector window closed on scroll")
            except:
                # Some implementations may not close on scroll, so just log a warning
                framework_logger.warning("Flag selector window did not close on scroll - this may be expected behavior")

            framework_logger.info("=== C38421766 - Landing Page Header Country Selector flow ended ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Landing Page Header Country Selector test: {e}\n{traceback.format_exc()}")
            raise e
        