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

def cast_smart_quotes_to_ascii_in_shipping_and_billing(stage_callback):
    framework_logger.info("=== C40965594 - Cast smart quotes to ASCII in shipping and billing flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # 1) HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer
        common.create_and_claim_virtual_printer()

    with PlaywrightManager() as page:
        confirmation_page = ConfirmationPage(page)
        try:
             # Start enrollment and sign in
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            framework_logger.info(f"Enrollment started and signed in with email: {tenant_email}")

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")
            
            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Choose hp checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add shipping address with smart quotes
            confirmation_page.add_shipping_button.click()
            confirmation_page.first_name.fill("‘InstantInk’")
            confirmation_page.last_name.fill("‘User’")
            confirmation_page.company_name_input.fill("‘HP’")
            confirmation_page.phone_number_input.fill("6508571501")
            confirmation_page.street1_input.fill("‘149 New Montgomery St’")
            confirmation_page.street2_input.fill("‘Apt 600’")
            confirmation_page.city_input.fill("San Francisco")
            confirmation_page.state_dropdown.click()
            page.locator("ul#state-listbox li[data-value='CA']").click()
            confirmation_page.zip_code_input.fill("94105-3739")
            confirmation_page.save_button.click()
            framework_logger.info(f"Added shipping address with smart quotes")

            # Selects and ships to the original shipping address
            address_option = confirmation_page.original_address_option.locator("xpath=..").locator('span[class^="vn-radio-button"]')
            address_option.click()
            confirmation_page.ship_to_address_button.click()
            expect(confirmation_page.suggested_address_modal).not_to_be_visible()
            framework_logger.info(f"Selected and shipped to the original shipping address")

            # Click save button on shipping modal
            confirmation_page.save_button.click()
            framework_logger.info(f"Clicked save button on shipping modal")

            # Click edit address on confirmation page
            confirmation_page.edit_shipping_button.click()
            framework_logger.info(f"Clicked edit address on confirmation page")

            # Sees shipping address with straight quotes on shipping modal
            expect(confirmation_page.first_name).to_have_value("'InstantInk'")
            expect(confirmation_page.last_name).to_have_value("'User'")
            expect(confirmation_page.company_name_input).to_have_value("'HP'")
            expect(confirmation_page.phone_number_input).to_have_value("6508571501")
            expect(confirmation_page.street1_input).to_have_value("'149 New Montgomery St'")
            expect(confirmation_page.street2_input).to_have_value("'Apt 600'")
            expect(confirmation_page.city_input).to_have_value("San Francisco")
            expect(confirmation_page.state_dropdown.locator("span")).to_have_text("California")
            expect(confirmation_page.zip_code_input).to_have_value("94105-3739")
            confirmation_page.close_shipping_modal_button.click()
            framework_logger.info(f"Verified shipping address with straight quotes on shipping modal")
            
            # Click on add billing button 
            confirmation_page.add_billing_button.click()
            framework_logger.info(f"Clicked on add billing button")

            # Click billing address checkbox in the billing page
            confirmation_page.use_shipping_address.click()
            expect(confirmation_page.use_shipping_address).not_to_be_checked()
            framework_logger.info(f"Clicked billing address checkbox in the billing page")

            # Set address with smart quotes billing address and continue on billing page
            confirmation_page.first_name.fill("‘InstantInk’")
            confirmation_page.last_name.fill("‘User’")
            confirmation_page.street1_input.fill("‘149 New Montgomery St’")
            confirmation_page.street2_input.fill("‘Apt 600’")
            confirmation_page.city_input.fill("San Francisco")
            confirmation_page.state_dropdown.click()
            page.locator("ul#state-listbox li[data-value='CA']").click()
            confirmation_page.zip_code_input.fill("94105-3739")
            confirmation_page.billing_continue_button.click()
            framework_logger.info(f"Set address with smart quotes billing address and continued on billing page")

            # Click back on billing modal
            confirmation_page.back_button.click()
            framework_logger.info(f"Clicked back on billing modal")

            # See address with smart quotes on billing modal
            expect(confirmation_page.first_name).to_have_value("‘InstantInk’")
            expect(confirmation_page.last_name).to_have_value("‘User’")
            expect(confirmation_page.street1_input).to_have_value("‘149 New Montgomery St’")
            expect(confirmation_page.street2_input).to_have_value("‘Apt 600’")
            expect(confirmation_page.city_input).to_have_value("San Francisco")
            expect(confirmation_page.state_dropdown.locator("span")).to_have_text("California")
            expect(confirmation_page.zip_code_input).to_have_value("94105-3739")
            framework_logger.info(f"Verified billing address with smart quotes on billing modal")

            # Set credit_card_visa data on billing modal (Sparse between visa, Mastercard, AmEx/Discover)
            payment_data = common.get_payment_method_data()
            page.locator(confirmation_page.elements.billing_continue_button).click()
            page.locator(confirmation_page.elements.iframe_pgs).wait_for(state="visible", timeout=120000)
            frame = page.frame_locator(confirmation_page.elements.iframe_pgs)
            card_input = frame.locator(confirmation_page.elements.card_number)
            card_input.fill(payment_data["credit_card_number"])
            frame.locator(confirmation_page.elements.exp_month).select_option(payment_data.get("expiration_month"))
            frame.locator(confirmation_page.elements.exp_year).select_option(payment_data.get("expiration_year"))
            frame.locator(confirmation_page.elements.cvv_input).type(payment_data["cvv"])        
            if frame.locator(confirmation_page.elements.billing_next_button).count() > 0:
                frame.locator(confirmation_page.elements.billing_next_button).click()
            else:
                frame.locator(confirmation_page.elements.sca_save_button).click()
                challenge_frame = None
                submit_selector = None
                try:
                    frame.locator("iframe#redirectTo3ds1Frame").wait_for(state="visible", timeout=5000)
                    challenge_frame = frame.frame_locator("#redirectTo3ds1Frame")
                    submit_selector = 'input[type="submit"][value="Submit"]'
                except:
                    frame.locator("iframe" + confirmation_page.elements.iframe_2fa).wait_for(state="visible", timeout=5000)
                    challenge_frame = frame.frame_locator(confirmation_page.elements.iframe_2fa)
                    submit_selector = confirmation_page.elements.acs_submit
                challenge_frame.locator(confirmation_page.elements.authentication_result_2fa).wait_for(state="visible", timeout=10000)
                challenge_frame.locator(confirmation_page.elements.authentication_result_2fa).select_option(payment_data.get("3ds_auth_result", "AUTHENTICATED"))
                challenge_frame.locator(submit_selector).wait_for(state="visible")
                challenge_frame.locator(submit_selector).click()
            page.wait_for_selector(confirmation_page.elements.edit_billing_button, state="visible", timeout=120000)

            # See user name with straight quotes on billing card on confirmation page
            expect(confirmation_page.billing_card).to_contain_text("'InstantInk' 'User'")
            framework_logger.info(f"Verified user name with straight quotes on billing card on confirmation page")

            # Click billing card Edit link on confirmation page
            confirmation_page.edit_billing_button.click()
            framework_logger.info(f"Clicked billing card Edit link on confirmation page")

            # See address with straight quotes billing address on billing modal
            expect(confirmation_page.first_name).to_have_value("'InstantInk'", timeout=90000)
            expect(confirmation_page.last_name).to_have_value("'User'")
            expect(confirmation_page.street1_input).to_have_value("'149 New Montgomery St'")
            expect(confirmation_page.street2_input).to_have_value("'Apt 600'")
            expect(confirmation_page.city_input).to_have_value("San Francisco")
            expect(confirmation_page.state_dropdown.locator("span")).to_have_text("California")
            expect(confirmation_page.zip_code_input).to_have_value("94105-3739")
            framework_logger.info(f"Verified billing address with straight quotes on billing modal")           
            
            framework_logger.info("=== C40965594 - Cast smart quotes to ASCII in shipping and billing completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e