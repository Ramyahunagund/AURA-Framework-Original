import traceback
from helper.landing_page_helper import LandingPageHelper
import test_flows_common.test_flows_common as common
from test_flows import LandingPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
from pages.landing_page import LandingPage

def carousel(stage_callback):
    framework_logger.info("=== C38569234 - Carousel (For Desktop/ Tablet) flow started ===")
    common.setup()

    viewport_width = 1190
    viewport_height = 1024

    with PlaywrightManager() as page:
        try:
            landing_page = LandingPage(page)

            # Access Consumer Landing page
            LandingPageHelper.access(page)
            framework_logger.info("Landing page accessed successfully")

            # Go to Plans section by clicking Plan tab in Header.
            landing_page.header_plan.click(timeout=10000)
            expect(landing_page.ink_plans_tab).to_be_visible()

            # Check if the 5th card is shown. If shown, the arrow should not be shown. 
            if landing_page.ink_plans_card(4).is_visible():
                expect(landing_page.ink_plans_card_right_arrow).not_to_be_visible()
                expect(landing_page.ink_plans_card_left_arrow).not_to_be_visible()
                page.set_viewport_size({"width": viewport_width, "height": viewport_height})
                
            # Check the Plans card with Right arrow.
            landing_page.ink_plans_card_right_arrow.scroll_into_view_if_needed()
            expect(landing_page.ink_plans_card_right_arrow).to_be_visible()
            framework_logger.info("Verify the Plans card with Right arrow is displayed well.")              

            #Upon clicking Left/Right arrow. Click the right arrow button and left arrow button is visible.
            landing_page.ink_plans_card_right_arrow.click()           
            expect(landing_page.ink_plans_card(4)).to_be_hidden()
            landing_page.ink_plans_card_right_arrow.click()
            # expect(landing_page.ink_plans_card(4)).to_be_visible()
            stage_callback("landing_page_ink_plans_card", page)
            assert landing_page.ink_plans_card(4).count() > 0, "The 5th card is found."
            landing_page.ink_plans_card_left_arrow.scroll_into_view_if_needed()
            expect(landing_page.ink_plans_card_left_arrow).to_be_visible()            
            framework_logger.info("Verify it navigates 5th on the carousel and the Left arrow is displayed.")   

            # Click the left arrow button, the 5th card should not be shown.
            landing_page.ink_plans_card_left_arrow.click()
            landing_page.ink_plans_card_right_arrow.scroll_into_view_if_needed()
            expect(landing_page.ink_plans_card(4)).not_to_be_visible()
            framework_logger.info("Verify user is able to navigate back and 5th carousel is not shown.")              
                     
            framework_logger.info("=== C38569234 - Carousel (For Desktop/ Tablet) flow finished")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e