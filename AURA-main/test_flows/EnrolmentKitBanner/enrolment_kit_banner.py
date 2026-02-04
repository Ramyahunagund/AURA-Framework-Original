from core.playwright_manager import PlaywrightManager
from pages.hpid_page import HPIDPage
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage

import traceback
from playwright.sync_api import expect
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enrolment_kit_banner(stage_callback):   
    framework_logger.info("=== Enrolment Kit Banner validation started ===")
    common.setup()

    timeout_ms = 120000

    with PlaywrightManager() as page:
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)
            hpid_page = HPIDPage(page)

            # Step 1: Launch the Consumer Landing page           
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Launch the Consumer Landing page")
            
            # Verify the EK banner is displayed well            
            expect(landing_page.ek_banner).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified the EK banner is displayed well")

            # Verify banner content elements
            expect(landing_page.ek_banner_content).to_be_visible()
            expect(landing_page.ek_message_container).to_be_visible() 
            expect(landing_page.ek_banner_message).to_be_visible()
            expect(landing_page.ek_signup_link).to_be_visible()
            framework_logger.info("Verified the EK banner content elements are displayed well")


            # Click the "Sign up for HP Instant Ink today" link
            expect(landing_page.ek_signup_link).to_be_visible()                   
            landing_page.ek_signup_link.click()
            framework_logger.info("Clicked the 'Sign up for HP Instant Ink today' link") 
            
            # Wait for navigation
            page.wait_for_load_state("networkidle", timeout=30000)

            # Step 5: Verify it navigates to HPID value prop page                     
            expect(hpid_page.hpid_value_prop_page).to_be_visible(timeout=timeout_ms)  
            framework_logger.info("Verified it navigates to HPID value prop page")        

            framework_logger.info("=== C38471740 - Enrolment Kit Banner validation completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during Enrolment Kit Banner validation: {e}\n{traceback.format_exc()}")
            raise e
        