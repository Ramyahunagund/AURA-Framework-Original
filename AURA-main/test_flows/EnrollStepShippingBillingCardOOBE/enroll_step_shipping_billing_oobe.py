# test_flows/EnrollStepShippingBillingOOBE/enroll_step_shipping_billing_oobe.py

from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from pages.confirmation_page import ConfirmationPage
from pages.oss_emulator_page import OssEmulatorPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def oobe_enroll_step_shipping_billing_card(stage_callback) -> None:
    framework_logger.info("=== C27368494, C27368495, C27368496  ===")
    framework_logger.info("=== OOBE Enroll Step Shipping and Billing card validation flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    # Create virtual printer
    printer = common.create_virtual_printer()

    # Create new HPID account and setup OSS Emulator
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)

            # Setup OSS Emulator for OOBE
            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info(f"OSS Emulator setup completed")

            # Accept connected printing services
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info(f"Accepted connected printing services")

            try:
                page.wait_for_selector(f"div.option[id='{common._tenant_country_short}']", timeout=10000)
                page.locator(f"div.option[id='{common._tenant_country_short}']").click()
                page.locator('[class="footer-2"] button').click()
            except Exception as e:
                framework_logger.info(f"Don't need to select country")

            # Decline HP+
            OssEmulatorHelper.decline_hp_plus(page)
            framework_logger.info(f"Declined HP+")

            # Continue on dynamic security notice
            OssEmulatorHelper.continue_dynamic_security_notice(page)
            framework_logger.info(f"Continued on dynamic security notice")

            # Continue on value proposition - but we'll need to verify back button later
            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")

            # Accept automatic printer updates
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Accepted automatic printer updates")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Select plan
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Selected plan 100")

            # Now we're at the shipping and billing step - perform validations
            confirmation_page = ConfirmationPage(page)

            # Check the Shipping Card and make sure the "Add Shipping" button is displayed 
            expect(confirmation_page.shipping_card).to_be_visible(timeout=30000)
            expect(confirmation_page.shipping_card_title).to_be_visible()
            expect(confirmation_page.shipping_card_description).to_be_visible()
            expect(confirmation_page.add_shipping_button).to_be_visible()

            # Verify button is enabled (blue implies it's actionable/enabled)
            expect(confirmation_page.add_shipping_button).to_be_enabled()
            framework_logger.info("Add Shipping button is enabled (as expected)")                     

            # Check the Billing Card and verify Billing Card is disabled and free months is displayed
            expect(confirmation_page.billing_card).to_be_visible(timeout=30000)
            expect(confirmation_page.billing_card_title).to_be_visible()
            expect(confirmation_page.billing_card_description).to_be_visible()
            expect(confirmation_page.months_trial_billing_card).to_be_visible()
            framework_logger.info("Verified Billing Card and free months trial is visible")     

            # Verify Add Billing button is visible but billing is disabled
            expect(confirmation_page.add_billing_button).to_be_visible()
            expect(confirmation_page.add_billing_button).to_be_disabled()
            framework_logger.info("Add Billing button is visible but disabled (optional)")

            # Check the buttons - Verify "Back" button and "Continue" button are displayed
            expect(confirmation_page.enroll_back_button).to_be_visible()
            expect(confirmation_page.continue_enrollment_button).to_be_visible()
            framework_logger.info("Back button and Continue button is visible")            

            # Verify the "Back" button is enabled and the "Continue" button is disabled
            expect(confirmation_page.enroll_back_button).to_be_enabled()
            expect(confirmation_page.continue_enrollment_button).to_be_disabled()
            framework_logger.info("Back button is enabled and Continue button is disabled")

            # Click the Back button and verify application navigates back to Value Proposition page
            confirmation_page.enroll_back_button.click()          
            oss_emulator_page = OssEmulatorPage(page)           
            expect(oss_emulator_page.value_prop_title).to_be_visible(timeout=30000)         
            framework_logger.info("Successfully navigated back to Value Proposition page")

            framework_logger.info("=== OOBE Enroll Step Shipping and Billing card validation completed successfully ===")

            return tenant_email
        except Exception as e:
            framework_logger.error(f"An error occurred during the OOBE Enroll Step validation: {e}\n{traceback.format_exc()}")
            raise e