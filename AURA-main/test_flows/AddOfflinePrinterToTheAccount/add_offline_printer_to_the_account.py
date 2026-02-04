import time
import re
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from pages.printer_selection_page import PrinterSelectionPage
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def add_offline_printer_to_the_account(stage_callback):
    framework_logger.info("=== C41036079 - Add offline printer to the account flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # Claim virtual printer and add address
        printer = common.create_and_claim_virtual_printer_and_add_address()
        entity_id = printer[0]

        # Set printer to offline
        common.remove_printer_webservices(entity_id=entity_id)

    with PlaywrightManager() as page:
        printer_selection_page = PrinterSelectionPage(page)
        try:
            # Start enrollment and sign in
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)

            # Verify if the offline message is displayed
            page.wait_for_selector(printer_selection_page.elements.printer_selection_page, state="visible", timeout=180000)
            expect(printer_selection_page.printer_offline_message).to_be_visible(timeout=30000)
            framework_logger.info(f"Offline printer message is displayed")

            # Validate the Printer card
            EnrollmentHelper.printer_card_validation(page,[printer])
            framework_logger.info(f"Offline printer card is validated")

            # Validate the Add a different printer card
            EnrollmentHelper.add_card_validation(page)
            framework_logger.info(f"Add different printer card is validated")

            # Validate the Continue button
            assert not printer_selection_page.continue_button.is_enabled(), "Continue button is not disabled"
            printer_selection_page.printer_radio_button.nth(1).click()
            assert printer_selection_page.continue_button.is_enabled(), "Continue button is not enabled"
            framework_logger.info(f"Continue button is validated")
            
            # Validate the Connectivity guide link
            with page.context.expect_page() as new_page_info:
                printer_selection_page.connectivity_guide_link.click()
            new_tab = new_page_info.value
            new_tab.bring_to_front()
            time.sleep(10)
            expect(new_tab).to_have_url(re.compile(r'https://support.hp.com/'))
            new_tab.close()
            framework_logger.info(f"Connectivity guide link is validated")

            framework_logger.info("=== C41036079 - Add offline printer to the account flow completed ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the enrollment: {e}\n{traceback.format_exc()}")
            raise e
