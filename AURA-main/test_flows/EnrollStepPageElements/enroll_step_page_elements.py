from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from pages.confirmation_page import ConfirmationPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enroll_step_page_elements(stage_callback):
    framework_logger.info("=== C44401629 - Enroll step page elements flow started ===")
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

            # Verify shipping card elements
            expect(confirmation_page.shipping_card).to_be_visible()
            expect(confirmation_page.shipping_card_title).to_be_visible()
            expect(confirmation_page.shipping_card_description).to_be_visible()
            framework_logger.info(f"Verified shipping card elements on confirmation page")

            # Verify Shipping modal
            confirmation_page.add_shipping_button.click()
            expect(confirmation_page.first_name).to_be_visible(timeout=60000)
            expect(confirmation_page.last_name).to_be_visible()
            expect(confirmation_page.company_name_input).to_be_visible()
            expect(confirmation_page.phone_number_input).to_be_visible()
            expect(confirmation_page.street1_input).to_be_visible()
            expect(confirmation_page.street2_input).to_be_visible()
            expect(confirmation_page.city_input).to_be_visible()
            expect(confirmation_page.state_dropdown).to_be_visible()
            expect(confirmation_page.zip_code_input).to_be_visible()
            expect(confirmation_page.country).to_be_visible()
            expect(confirmation_page.checkbox_text_message).not_to_be_checked()
            expect(confirmation_page.cancel_button).to_be_visible()
            expect(confirmation_page.save_button).to_be_visible()
            confirmation_page.cancel_button.click()
            expect(confirmation_page.first_name).not_to_be_visible()
            framework_logger.info(f"Verified Shipping modal elements")

            # Verify Shipping modal is empty
            confirmation_page.add_shipping_button.click()
            expect(confirmation_page.first_name).to_be_visible(timeout=60000)
            expect(confirmation_page.company_name_input).to_be_empty()
            expect(confirmation_page.phone_number_input).to_be_empty()
            expect(confirmation_page.street1_input).to_be_empty()
            expect(confirmation_page.street2_input).to_be_empty()
            expect(confirmation_page.city_input).to_be_empty()
            expect(confirmation_page.state_dropdown.locator("span")).to_have_text("")
            expect(confirmation_page.zip_code_input).to_be_empty()
            confirmation_page.cancel_button.click()
            framework_logger.info(f"Verified Shipping modal fields are empty")

            # Add invalid shipping address
            confirmation_page.add_shipping_button.click()
            confirmation_page.phone_number_input.fill("6508571501")
            confirmation_page.street1_input.fill("10300 ENERGY DR")
            confirmation_page.city_input.fill("SPRING")
            confirmation_page.state_dropdown.click()
            page.locator("ul#state-listbox li[data-value='CA']").click()
            confirmation_page.zip_code_input.fill("77389-1864")
            confirmation_page.save_button.click()
            framework_logger.info(f"Added invalid shipping address")

            # See Verify your shipping address modal
            expect(confirmation_page.suggested_address_modal).to_be_visible(timeout=60000)
            suggested_label = confirmation_page.suggested_address_option.locator("xpath=..")
            original_label = confirmation_page.original_address_option.locator("xpath=..")
            expect(suggested_label).to_be_visible()
            expect(original_label).to_be_visible()
            expect(confirmation_page.ship_to_address_button).to_be_visible()
            framework_logger.info(f"Verified Verify your shipping address modal elements")

            # Selects and ships to the original shipping address
            address_option = confirmation_page.original_address_option.locator("xpath=..").locator('span[class^="vn-radio-button"]')
            address_option.click()
            confirmation_page.ship_to_address_button.click()
            expect(confirmation_page.suggested_address_modal).not_to_be_visible()
            framework_logger.info(f"Selected and shipped to the original shipping address")

            # See Please verify your address before you continue error message on shipping modal
            expect(confirmation_page.error_message).to_be_visible(timeout=60000)
            framework_logger.info(f"Verified error message on shipping modal")

            # Click save button on shipping modal
            confirmation_page.save_button.click()
            framework_logger.info(f"Clicked save button on shipping modal")

            # See invalid shipping address on confirmation page
            expect(confirmation_page.shipping_card).to_be_visible(timeout=60000)
            expect(confirmation_page.shipping_card).to_contain_text("InstantInk User", timeout=10000)
            expect(confirmation_page.shipping_card).to_contain_text("10300 ENERGY DR")
            expect(confirmation_page.shipping_card).to_contain_text("SPRING")
            expect(confirmation_page.shipping_card).to_contain_text("CA")
            expect(confirmation_page.shipping_card).to_contain_text("77389-1864")
            framework_logger.info(f"Verified invalid shipping address on confirmation page")

            # Click edit address on confirmation page
            confirmation_page.edit_shipping_button.click()
            framework_logger.info(f"Clicked edit address on confirmation page")

            # Save shipping address with all mandatory fields empty
            confirmation_page.first_name.clear()
            confirmation_page.last_name.clear()
            confirmation_page.company_name_input.clear()
            confirmation_page.phone_number_input.clear()
            confirmation_page.street1_input.clear()
            confirmation_page.street2_input.clear()
            confirmation_page.city_input.clear()
            confirmation_page.zip_code_input.clear()
            confirmation_page.save_button.click()
            framework_logger.info(f"Clicked save button on shipping modal with empty fields")

            # See Please verify your address before you continue error message on shipping modal
            expect(confirmation_page.error_message).to_be_visible(timeout=60000)
            framework_logger.info(f"Verified error message on shipping modal")

            # Click the close button on shipping modal
            confirmation_page.close_shipping_modal_button.click()
            framework_logger.info(f"Clicked close button on shipping modal")

            # Click edit address on confirmation page
            confirmation_page.edit_shipping_button.click()
            framework_logger.info(f"Clicked edit address on confirmation page")

            # Add shipping address with special characters
            confirmation_page.street1_input.fill("149 New Montgomery St!@#")
            confirmation_page.street2_input.fill("10300 ENERGY DR!@#$")
            confirmation_page.save_button.click()
            framework_logger.info(f"Added shipping address with special characters")

            # See Please verify your address before you continue error message on shipping modal
            expect(confirmation_page.error_message).to_be_visible(timeout=60000)
            framework_logger.info(f"Verified error message on shipping modal")

            # Add invalid shipping address
            confirmation_page.phone_number_input.fill("6508571501")
            confirmation_page.street1_input.fill("10300 ENERGY DR")
            confirmation_page.street2_input.clear()
            confirmation_page.city_input.fill("SPRING")
            confirmation_page.state_dropdown.click()
            page.locator("ul#state-listbox li[data-value='CA']").click()
            confirmation_page.zip_code_input.fill("77389-1864")
            confirmation_page.save_button.click()
            framework_logger.info(f"Added invalid shipping address")

            # See Verify your shipping address modal
            expect(confirmation_page.suggested_address_modal).to_be_visible(timeout=60000)
            suggested_label = confirmation_page.suggested_address_option.locator("xpath=..")
            original_label = confirmation_page.original_address_option.locator("xpath=..")
            expect(suggested_label).to_be_visible()
            expect(original_label).to_be_visible()
            expect(confirmation_page.ship_to_address_button).to_be_visible()
            framework_logger.info(f"Verified Verify your shipping address modal elements")

            # Selects and ships to the suggested shipping address
            address_option = confirmation_page.suggested_address_option.locator("xpath=..").locator('span[class^="vn-radio-button"]')
            address_option.click()
            confirmation_page.ship_to_address_button.click()
            expect(confirmation_page.suggested_address_modal).not_to_be_visible()
            framework_logger.info(f"Selected and shipped to the original shipping address")

            # See corrected shipping address on confirmation page
            expect(confirmation_page.shipping_card).to_be_visible(timeout=60000)
            expect(confirmation_page.shipping_card).to_contain_text("InstantInk User", timeout=10000)
            expect(confirmation_page.shipping_card).to_contain_text("10300 ENERGY DR")
            expect(confirmation_page.shipping_card).to_contain_text("SPRING")
            expect(confirmation_page.shipping_card).to_contain_text("TX")
            expect(confirmation_page.shipping_card).to_contain_text("77389-1864")
            framework_logger.info(f"Verified corrected shipping address on confirmation page")

            # Click edit address on confirmation page
            confirmation_page.edit_shipping_button.click()
            framework_logger.info(f"Clicked edit address on confirmation page")

            # Add valid shipping address
            confirmation_page.phone_number_input.fill("6508571501")
            confirmation_page.street1_input.fill("149 New Montgomery St")
            confirmation_page.street2_input.clear()
            confirmation_page.city_input.fill("San Francisco")
            confirmation_page.state_dropdown.click()
            page.locator("ul#state-listbox li[data-value='CA']").click()
            confirmation_page.zip_code_input.fill("94105-3739")
            confirmation_page.save_button.click()
            framework_logger.info(f"Added valid shipping address")

            # See valid shipping address on confirmation page
            expect(confirmation_page.shipping_card).to_be_visible(timeout=60000)
            expect(confirmation_page.shipping_card).to_contain_text("InstantInk User", timeout=10000)
            expect(confirmation_page.shipping_card).to_contain_text("149 New Montgomery St")
            expect(confirmation_page.shipping_card).to_contain_text("San Francisco")
            expect(confirmation_page.shipping_card).to_contain_text("CA")
            expect(confirmation_page.shipping_card).to_contain_text("94105-3739")
            framework_logger.info(f"Verified valid shipping address on confirmation page")

            # Click edit address on confirmation page
            confirmation_page.edit_shipping_button.click()
            framework_logger.info(f"Clicked edit address on confirmation page")

            # See shipping address on shipping modal
            expect(confirmation_page.phone_number_input).to_have_value("6508571501")
            expect(confirmation_page.street1_input).to_have_value("149 New Montgomery St")
            expect(confirmation_page.street2_input).to_have_value("")
            expect(confirmation_page.city_input).to_have_value("San Francisco")
            expect(confirmation_page.state_dropdown.locator("span")).to_have_text("California")
            expect(confirmation_page.zip_code_input).to_have_value("94105-3739")
            confirmation_page.close_shipping_modal_button.click()
            framework_logger.info(f"Verified shipping address on shipping modal")

            # See the billing card on confirmation page
            expect(confirmation_page.billing_card).to_be_visible()
            expect(confirmation_page.billing_card_title).to_be_visible()
            expect(confirmation_page.billing_card_description).to_be_visible()
            expect(confirmation_page.add_billing_button).to_be_visible()
            expect(confirmation_page.enter_promo_or_pin_code_button).to_be_visible()
            framework_logger.info(f"Verified billing card on confirmation page")

            # Verify special offers modal
            confirmation_page.enter_promo_or_pin_code_button.click()
            expect(confirmation_page.promotion_code_input).to_be_visible()
            expect(confirmation_page.promotion_apply_button).to_be_visible()
            confirmation_page.close_modal_button.click()
            framework_logger.info(f"Verified special offers modal")

            # Verify billing modal
            confirmation_page.add_billing_button.click()
            expect(confirmation_page.consumer_radio_button).to_be_visible()
            expect(confirmation_page.business_radio_button).to_be_visible()
            expect(confirmation_page.credit_card_radio_option).to_be_visible()
            expect(confirmation_page.use_shipping_address).to_be_visible()
            expect(confirmation_page.cancel_button).to_be_visible()

            confirmation_page.business_radio_button.locator("xpath=..").click()
            expect(confirmation_page.billing_company_input).to_be_visible()
            expect(confirmation_page.tax_id_input).to_be_visible()
            confirmation_page.tax_id_tooltip.hover()
            expect(confirmation_page.tax_id_tooltip_msg).to_be_visible()
            confirmation_page.billing_continue_button.click()

            expect(confirmation_page.iframe_pgs).to_be_visible(timeout=60000)
            expect(confirmation_page.google_pay_button).to_be_visible()
            expect(confirmation_page.paypal_button).to_be_visible()
            frame = page.frame_locator(confirmation_page.elements.iframe_pgs)
            expect(frame.locator(confirmation_page.elements.card_number)).to_be_visible()
            expect(frame.locator(confirmation_page.elements.exp_month)).to_be_visible()
            expect(frame.locator(confirmation_page.elements.exp_year)).to_be_visible()
            expect(frame.locator(confirmation_page.elements.cvv_input)).to_be_visible()
            expect(frame.locator(confirmation_page.elements.billing_next_button)).to_be_visible()
            confirmation_page.close_billing_button.click()
            framework_logger.info(f"Verified billing modal elements")

            # Add billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing method added successfully")

            # Verify billing data on confirmation page
            payment_data = common.get_payment_method_data()
            card_number = payment_data["credit_card_number"]
            exp_month = payment_data["expiration_month"]
            exp_year = payment_data["expiration_year"]

            last_four_digits = card_number[-4:]
            expected_masked_card = f"XXXX-XXXX-XXXX-{last_four_digits}"
            expected_expiration = f"{exp_month}/{exp_year}"

            billing_card = page.locator(confirmation_page.elements.billing_card)
            expect(billing_card).to_be_visible()
            expect(billing_card).to_contain_text(expected_masked_card)
            expect(billing_card).to_contain_text(expected_expiration)
            framework_logger.info(f"Verified credit card number {expected_masked_card} and expiration date {expected_expiration} on billing card")

            framework_logger.info("=== C44401629 - Enroll step page elements flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e