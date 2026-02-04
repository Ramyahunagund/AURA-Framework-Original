# test_flows/HeroSection/hero_section.py

import traceback
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.landing_page_helper import LandingPageHelper
from pages.landing_page import LandingPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# C38421790, C38471739, C38471742, C38471743, C38471741
def hero_section(stage_callback):
    framework_logger.info("=== Hero Section test flow started ===")
    common.setup()

    with PlaywrightManager() as page:
        try:
            landing_page = LandingPage(page)
            
            # Access Landing Page
            framework_logger.info("Opening Landing Page...")
            LandingPageHelper.access(page)
            framework_logger.info("Landing Page accessed successfully")
            
            # Test 1: Hero Section - Display and Layout
            framework_logger.info("\n=== Test 1: Hero Section Display ===")
            expect(landing_page.hero_section).to_be_visible(timeout=30000)
            framework_logger.info("Hero section is visible")
            stage_callback("hero_section_display", page)
            
            # Test 2: Hero Section - Get Started Button
            framework_logger.info("\n=== Test 2: Hero Section Get Started Button ===")
            expect(landing_page.get_started_button).to_be_visible(timeout=30000)
            framework_logger.info("Get Started button is visible in Hero section")
            stage_callback("hero_get_started_button", page)
            
            # Test 3: Click Get Started Button
            framework_logger.info("\n=== Test 3: Click Get Started Button ===")
            landing_page.get_started_button.click()
            page.wait_for_load_state("load", timeout=30000)
            framework_logger.info("HPID Value prop page loaded")
            stage_callback("hpid_value_prop_page", page)
            
            # Navigate back to landing page
            page.go_back(wait_until="load", timeout=30000)
            framework_logger.info("Navigated back to Landing Page")
            
            # Test 4: Plan Banner Display
            framework_logger.info("\n=== Test 4: Plan Banner Display ===")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            expect(landing_page.plan_banner).to_be_visible(timeout=30000)
            framework_logger.info("Plan Banner is visible")
            stage_callback("plan_banner_display", page)
            
            # Test 5: Plan Section and Plans Container
            framework_logger.info("\n=== Test 5: Plan Section ===")
            expect(landing_page.plan_section).to_be_visible(timeout=30000)
            expect(landing_page.landing_page_plans_container).to_be_visible(timeout=30000)
            framework_logger.info("Plan section and plans container are visible")
            stage_callback("plan_section", page)
            
            # Test 6: Ink Plans Tab
            framework_logger.info("\n=== Test 6: Ink Plans Tab ===")
            expect(landing_page.ink_plans_tab).to_be_visible(timeout=30000)
            framework_logger.info("Ink plans tab is visible")
            stage_callback("ink_plans_tab", page)
            
            # Scroll back to top for navigation tests
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)
            
            # Test 7: Header Sign Up Button
            framework_logger.info("\n=== Test 7: Header Sign Up Button ===")
            expect(landing_page.sign_up_header_button).to_be_visible(timeout=30000)
            button_text = landing_page.sign_up_header_button.text_content()
            assert "Sign up Now" in button_text or "Sign Up Now" in button_text, f"Expected 'Sign Up Now' but found: {button_text}"
            framework_logger.info("Sign Up button is visible with correct text in header")
            stage_callback("sign_up_header_button", page)
            
            # Test 8: Click Header Sign Up Button
            framework_logger.info("\n=== Test 8: Click Header Sign Up Button ===")
            landing_page.sign_up_header_button.click()
            page.wait_for_load_state("load", timeout=30000)
            framework_logger.info("HPID Value prop page loaded")
            stage_callback("hpid_page_from_header_signup", page)
            
            # Navigate back to landing page
            page.go_back(wait_until="load", timeout=30000)
            framework_logger.info("Navigated back to Landing Page")
            
            # Test 9: Support Section
            framework_logger.info("\n=== Test 9: Support Section Display ===")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.8)")
            expect(landing_page.support_section).to_be_visible(timeout=30000)
            framework_logger.info("Support section is visible")
            stage_callback("support_section_display", page)
            
            # Test 10: Support Links - Virtual Agent and Phone
            framework_logger.info("\n=== Test 10: Support Section Links ===")
            expect(landing_page.virtual_agent).to_be_visible(timeout=30000)
            expect(landing_page.support_phone_number).to_be_visible(timeout=30000)
            framework_logger.info("Virtual agent and phone support links are visible")
            stage_callback("support_section_links", page)
            
            # Test 11: Fixed Virtual Assistant Button - Visibility
            framework_logger.info("\n=== Test 11: Fixed Virtual Assistant Button - Visibility ===")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            page.wait_for_timeout(500)
            expect(landing_page.virtual_agent_fixed_button).to_be_visible(timeout=30000)
            framework_logger.info("Fixed virtual assistant button is visible")
            stage_callback("virtual_agent_fixed_button_visibility", page)
            
            # Test 12: Fixed Virtual Assistant Button - Persistence while scrolling
            framework_logger.info("\n=== Test 12: VA Button Persistence ===")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(500)
            expect(landing_page.virtual_agent_fixed_button).to_be_visible(timeout=30000)
            framework_logger.info("VA button remains visible at bottom of page")
            stage_callback("virtual_agent_fixed_button_persistent", page)
            
            framework_logger.info("\n=== Hero Section test flow completed successfully ===")
            
        except Exception as e:
            framework_logger.error(f"An error occurred during the Hero Section test flow: {e}\n{traceback.format_exc()}")
            raise e
