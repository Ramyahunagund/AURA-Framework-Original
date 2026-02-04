# test_flows/AccountCreation/account_creation.py

import time
import traceback
from playwright.sync_api import expect
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from pages import plan_selector_v3_page
from pages.landing_page import LandingPage
from pages.hpid_page import HPIDPage
from pages.confirmation_page import ConfirmationPage
from helper.landing_page_helper import LandingPageHelper
from helper.hpid_helper import HPIDHelper
from pages.plan_selector_v3_page import PlanSelectorV3Page
import test_flows_common.test_flows_common as common
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def account_creation(stage_callback):
    framework_logger.info("=== C38421781 - Account Creation flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    with PlaywrightManager() as page:
        try:
            landing_page = LandingPage(page)
            hpid_page = HPIDPage(page)
            plan_selector_page = PlanSelectorV3Page(page)

            # Launch consumer landing page
            LandingPageHelper.access(page)
            expect(landing_page.header_logo).to_be_visible(timeout=60000)
            framework_logger.info("Landing page loaded successfully")

            # Click Manage Account button (Sign In button)
            landing_page.sign_in_button.click()
            framework_logger.info("Sign In button clicked")

            # Click "Create account" link on HPID Sign In page
            HPIDHelper.dismiss_select_country(page)
            hpid_page.wait.create_account_button_data(timeout=20000).click()
            framework_logger.info("Create account link clicked")

            # Verify the HPID Create Account page is displayed well
            expect(hpid_page.firstName).to_be_visible(timeout=30000)
            expect(hpid_page.lastName).to_be_visible(timeout=30000)
            expect(hpid_page.email).to_be_visible(timeout=30000)
            expect(hpid_page.password).to_be_visible(timeout=30000)
            expect(hpid_page.market).to_be_visible(timeout=30000)
            expect(hpid_page.create_account_button).to_be_visible(timeout=30000)
            framework_logger.info("HPID Create Account page is displayed correctly with all required fields")

            # Fill in valid info and click CREATE ACCOUNT button
            hpid_page.firstName.fill(common.DEFAULT_FIRSTNAME)
            hpid_page.lastName.fill(common.DEFAULT_LASTNAME)
            hpid_page.email.fill(tenant_email)
            hpid_page.password.fill(common.DEFAULT_PASSWORD)
            hpid_page.market.click()
            framework_logger.info(f"Form filled with: FirstName={common.DEFAULT_FIRSTNAME}, LastName={common.DEFAULT_LASTNAME}, Email={tenant_email}")

            hpid_page.create_account_button.click()
            framework_logger.info("CREATE ACCOUNT button clicked")

            # Wait for verification code page
            hpid_page.wait.submit_code(timeout=30000)
            framework_logger.info("Reached verification code page")

            # Step 6: Complete verification and confirm redirect to plan selection         
            HPIDHelper.confirm_account_code(page, tenant_email)
            framework_logger.info("Account created and verified successfully")

            # Verify redirection to Select a plan type page (enrollment flow)                  
            expect(plan_selector_page.pay_as_you_print_plan_card).to_be_visible(timeout=600000)
            expect(plan_selector_page.monthly_plan_card).to_be_visible()
            framework_logger.info("Successfully redirected to plan selection page")     
          
            # Go to Rails Admin Stratus tenant info
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_stratus_tenant_info(page)

            # Verify program level is ucde
            json_content = page.locator('pre, code').first
            expect(json_content).to_contain_text('"program_level": "ucde"', timeout=30000)
            framework_logger.info("Program level 'ucde' found in JSON content")
                       
            framework_logger.info("=== C38421781 - Account Creation flow finished successfully ===")
           
        except Exception as e:
            framework_logger.error(f"An error occurred during the Account Creation flow: {e}\n{traceback.format_exc()}")
            raise e
        