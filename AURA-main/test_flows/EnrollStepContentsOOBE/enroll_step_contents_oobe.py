# test_flows/EnrollStepContentOOBE/enroll_step_content_oobe.py

from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from pages.confirmation_page import ConfirmationPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def enroll_step_contents_oobe(stage_callback) -> None:

    framework_logger.info("=== C27368493 - Enroll Step Contents OOBE flow started ===")
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

            # Continue on value proposition
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

            # Initialize confirmation page for validations
            confirmation_page = ConfirmationPage(page)
            
            # Verify plan card is displayed
            expect(confirmation_page.plan_card).to_be_visible()
            expect(confirmation_page.plan_card_title).to_be_visible()
            expect(confirmation_page.plan_box_footer).to_be_visible()
            framework_logger.info(f"Verified plan card is displayed")
           
            # Verify shipping card is displayed
            expect(confirmation_page.shipping_card).to_be_visible()
            expect(confirmation_page.shipping_card_title).to_be_visible()
            expect(confirmation_page.add_shipping_button).to_be_visible()
            framework_logger.info(f"Verified shipping card is displayed with title and description")

            # Verify billing card is displayed
            expect(confirmation_page.billing_card).to_be_visible()
            expect(confirmation_page.billing_card_title).to_be_visible()
            expect(confirmation_page.enter_promo_or_pin_code_button).to_be_visible()
            framework_logger.info(f"Verified billing card is displayed with title and description")

            # Verify Continue button is displayed and disabled
            expect(confirmation_page.continue_enrollment_button).to_be_visible()
            expect(confirmation_page.continue_enrollment_button).to_be_disabled()
            framework_logger.info(f"Verified Continue button is displayed and disabled")

            framework_logger.info("=== C27368493 - Enroll Step Content OOBE flow completed successfully ===")
            return tenant_email

        except Exception as e:
            framework_logger.error(f"An error occurred during the OOBE Enrollment validation: {e}\n{traceback.format_exc()}")
            raise e
  