from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enroll_step_content_layout(stage_callback):
    framework_logger.info("=== C33028969 - Content and Layout - Enroll step page validation started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()

    # HPID signup + UCDE onboarding
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        page = common.onboard_hpid_to_ucde(page)
        common.create_and_claim_virtual_printer()

    with PlaywrightManager() as page:
        confirmation_page = ConfirmationPage(page)
        try:
            # Create account until enrollment step page
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            EnrollmentHelper.select_printer(page)
            EnrollmentHelper.accept_automatic_printer_updates(page)
            EnrollmentHelper.select_plan(page, 100)
            EnrollmentHelper.choose_hp_checkout(page)
            
            # Wait for enrollment step page to load          
            expect(confirmation_page.enroll_step_page).to_be_visible(timeout=60000)
            
            # Verify cards are displayed
            expect(confirmation_page.shipping_card).to_be_visible()
            expect(confirmation_page.shipping_card_title).to_be_visible()
            expect(confirmation_page.shipping_card_description).to_be_visible()
            expect(confirmation_page.billing_card).to_be_visible()
            expect(confirmation_page.billing_card_title).to_be_visible()
            expect(confirmation_page.billing_card_description).to_be_visible()
            framework_logger.info("Verified the Your Plan card/ Shipping card/ Billing card are displayed well")

            # Verify Shipping card has focus (blue Add Shipping button)
            expect(confirmation_page.add_shipping_button).to_be_visible()
            expect(confirmation_page.add_shipping_button).to_be_enabled()
            framework_logger.info("Verified the Add Shipping button is displayed and enabled")
        
            # Verify Billing card is disabled
            expect(confirmation_page.add_billing_button).to_be_visible()
            expect(confirmation_page.add_billing_button).to_be_disabled()
            framework_logger.info("Verified the Add Billing button is displayed and disabled")
            
            # Verify Continue button is displayed and disabled
            expect(confirmation_page.continue_enrollment_button).to_be_visible()
            expect(confirmation_page.continue_enrollment_button).to_be_disabled()
            framework_logger.info("Verified the Continue button is displayed and disabled")

            framework_logger.info("=== C33028969 - Content and Layout - Enroll step page validation completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during Content and Layout validation: {e}\n{traceback.format_exc()}")
            raise e
        