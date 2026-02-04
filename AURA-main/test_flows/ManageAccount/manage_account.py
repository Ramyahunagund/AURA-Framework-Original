# test_flows/ManageAccount/manage_account.py

from core.playwright_manager import PlaywrightManager
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage
from pages.hpid_page import HPIDPage
from pages.plan_selector_v3_page import PlanSelectorV3Page

import time
import traceback
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
import test_flows_common.test_flows_common as common

def manage_account(stage_callback):
    framework_logger.info("=== C38421780 - Manage Account flow started ===")
    common.setup()

    timeout_ms = 120000
    test_email = "hello.instantink+y3rsd02l@gmail.com"

    with PlaywrightManager() as page:
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)
            hpid_page = HPIDPage(page)
            plan_selector_page = PlanSelectorV3Page(page)

            # Open landing page
            framework_logger.info("Opening landing page")
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()
            framework_logger.info("Landing page opened and privacy banner accepted")

            # Click on Manage Account button (Sign In button)
            framework_logger.info("Clicking on Sign In button (Manage Account)")
            expect(landing_page.sign_in_button).to_be_visible(timeout=timeout_ms)
            landing_page.sign_in_button.click()
            framework_logger.info("Sign In button clicked")

            # Verify user is directed to HPID sign in page     
            expect(hpid_page.username).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Username field is visible on HPID sign in page")

            # Check the URL of the page and verify the redirect path
            current_url = page.url                                
            assert "/login3" in current_url, f"Expected '/login3' in URL"
            assert "login3.stg.cd.id.hp.com" in current_url, f"Expected HP ID domain 'login3.stg.cd.id.hp.com' in URL"
            assert current_url.startswith("https://"), f"Expected HTTPS URL, but got: {current_url}"
            framework_logger.info(f"URL verification passed - redirect path is correct: {current_url}")

            # Login with the account
            framework_logger.info(f"Logging in with account: {test_email}")
            hpid_page.username.fill(test_email)
            hpid_page.user_name_form_submit.click()

            # Wait for password field to appear
            expect(hpid_page.password).to_be_visible(timeout=timeout_ms)
            hpid_page.password.fill(common.DEFAULT_PASSWORD)
            hpid_page.sign_in.click()
            framework_logger.info("Login credentials submitted")
           
            # Verify user able to sign in successfully and the Select a plan type page is displayed           
            time.sleep(3)             
            expect(plan_selector_page.content_area_v3).to_be_visible(timeout=30000)             
            framework_logger.info("Successfully verified - Select a plan type page is displayed")
            
            framework_logger.info("=== C38421780 - Manage Account flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Manage Account test: {e}\n{traceback.format_exc()}")
            raise e
     