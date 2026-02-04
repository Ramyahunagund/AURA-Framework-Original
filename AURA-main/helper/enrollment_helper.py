from itertools import count

from email.mime import text
import re
from time import sleep

from helper.gemini_ra_helper import GeminiRAHelper
from helper.hpid_helper import HPIDHelper
from pages.landing_page import LandingPage
from pages import plan_selector_v3_page
from pages.oss_emulator_page import OssEmulatorPage
from pages.plan_selector_v3_page import PlanSelectorV3Page
from pages.privacy_banner_page import PrivacyBannerPage
from pages.printer_selection_page import PrinterSelectionPage
from pages.printer_updates_page import PrinterUpdatesPage
from pages.confirmation_page import ConfirmationPage
from pages.thank_you_page import ThankYouPage
from pages.tos_hp_smart_page import TermsOfServiceHPSmartPage
from pages.dashboard_hp_smart_page import DashboardHPSmartPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
from core.settings import framework_logger, GlobalState
import time


class EnrollmentHelper:

    @staticmethod
    def accept_terms_of_service(page):
        tos_page = TermsOfServiceHPSmartPage(page)
        tos_page.wait.continue_button(state="visible", timeout=60000)
        tos_page.continue_button.click()
        expect(tos_page.continue_button).not_to_be_visible(timeout=60000)


    @staticmethod
    def accept_all_preferences(page):
        product_setup_page = OverviewPage(page)
        product_setup_page.accept_all_preferences.click()
        expect(product_setup_page.accept_all_preferences).not_to_be_visible(timeout=60000)

    @staticmethod
    def start_enrollment(page):
        privacy_banner = PrivacyBannerPage(page)
        page.goto(common._instantink_v3_url, timeout=120000)
        page.wait_for_load_state("load")
        privacy_banner.accept_privacy_banner()
        page.wait_for_load_state("load")

    @staticmethod
    def start_enrollment_and_sign_in(page, tenant_email, timeout=720):
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                EnrollmentHelper.start_enrollment(page)
                framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

                if "printer-selection" in page.url:
                    break
                # sign in method
                HPIDHelper.complete_sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
                framework_logger.info(f"Signed in")
            except Exception:
                pass

            if "printer-selection" in page.url:
                break

            time.sleep(10)

    @staticmethod
    def signup_now(page):
        smart_dashboard = DashboardHPSmartPage(page)
        smart_dashboard.signup_now_button.wait_for(state="visible", timeout=180000)
        smart_dashboard.signup_now_button.click()

    @staticmethod
    def select_printer(page, printer_index=0):
        printer_selection = PrinterSelectionPage(page)
        page.wait_for_selector(printer_selection.elements.printer_selection_page, state="visible", timeout=180000)
        printer_selection.printer_radio_button.nth(printer_index).click()
        printer_selection.continue_button.click()

    @staticmethod
    def accept_automatic_printer_updates(page):
        printer_updates = PrinterUpdatesPage(page)
        printer_updates.accept_automatic_updates()

    @staticmethod
    def select_plan_type(page, type="monthly"):
        confirmation_page = ConfirmationPage(page)
        try:
            if type=="monthly":
                confirmation_page.monthly_plan.click(timeout=60000)
        except Exception as e:
            print("Plan type card not displayed, continuing flow")

    @staticmethod
    def select_plan(page, plan_value: str = "100", plan_type: str = "ink_only"):
        confirmation_page = ConfirmationPage(page)
        monthly_plan = False

        try:
            confirmation_page.monthly_plan.click(timeout=60000)
            monthly_plan = True
        except:
            print("Monthly plan card not displayed, continuing flow")

        if page.locator(confirmation_page.elements.select_plan_button).count() == 0:
            confirmation_page.edit_plan_button.click()

        if page.locator(confirmation_page.elements.ink_cartridges_tab).count() > 0:
            if plan_type == "ink_only":
                confirmation_page.ink_cartridges_tab.click()
                confirmation_page.select_ink_plan(plan_value)
            elif plan_type == "ink_and_paper":
                confirmation_page.paper_cartridges_tab.click()
                confirmation_page.select_paper_plan(plan_value)
            else:
                raise ValueError("Invalid plan_type")
        else:                                             # Added this else for OOBE flow
            confirmation_page.select_ink_plan(plan_value) # OOBE Plan selection while in enrollment stage does not have tabs
        confirmation_page.select_plan_button.click()

        if monthly_plan:
            EnrollmentHelper.accept_automatic_printer_updates(page)

    @staticmethod
    def verify_selected_plan_on_card(page, expected_plan: str):
        confirmation_page = ConfirmationPage(page)
        expect(confirmation_page.plan_pages).to_be_visible(timeout=90000)
        plan_selected = common.extract_numbers_from_text(confirmation_page.plan_pages.text_content())[0]
        assert str(plan_selected) == str(expected_plan), f"Expected plan {expected_plan}, got {plan_selected}"

    @staticmethod
    def select_plan_v3(page, plan_value: str, paper=False, callback=None, confirm=True):
        plan_selector_page = PlanSelectorV3Page(page)
        confirmation_page = ConfirmationPage(page)

        try:
            if confirmation_page.monthly_plan.is_visible(timeout=60000):
                confirmation_page.monthly_plan.click()
        except:
            pass

        try:
            plan_selector_page.plans_selector_v3.click(timeout=120000)

            if callback: callback("plan_selection_options_v3", page, screenshot_only=True)

            plan_selector_page.select_plan(plan_value)

        except Exception as e:
            framework_logger.warning(f"Error selecting plan: {plan_value}, {e}")

        if confirm: # 'Select Plan' button click
            if callback: callback("plan_selection", page, screenshot_only=True)

            if paper:
                plan_selector_page.ink_paper_button.click()
            else:
                plan_selector_page.ink_only_button.click()

            # Handle auto printer update page if it appears
            time.sleep(10)  # Wait for potential auto printer update page to load
            if confirmation_page.auto_printer_update.is_visible():
                framework_logger.info("Auto printer update page is visible, clicking continue.")
                confirmation_page.auto_printer_continue.click()

            # confirmation_page.blue_inf_icon.wait_for(state='visible', timeout=180000) # Could not find the locator during run
            # framework_logger.info('Blue info icon is visible')
            confirmation_page.plan_card_title.wait_for(state='visible', timeout=180000)
            framework_logger.info('Plan card title text is visible')

    @staticmethod
    def click_learn_more(page, paper=False, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            if paper:
                confirmation_page.click_learn_more.nth(1).click(timeout=60000)
                framework_logger.info('Clicked on "Learn more" link, Ink + Paper Plan.')
            else:
                confirmation_page.click_learn_more.first.click(timeout=60000)
                framework_logger.info('Clicked on "Learn more" link, Ink Plan.')
            confirmation_page.how_it_works.wait_for(state="visible", timeout=10000)
            framework_logger.info('"How it works" section is visible')
            if callback: callback('learn_more_clicked', page, screenshot_only=True)
            confirmation_page.close_x_button.first.click(timeout=60000)
            framework_logger.info("Closed the 'How it works' modal")
            confirmation_page.click_learn_more.nth(1).wait_for(state="visible", timeout=10000)
            framework_logger.info("Learn more link clicked")
        except Exception as e:
            if callback: callback('error_learn_more_clicked', page, screenshot_only=True)
            framework_logger.error(f"Error: click_learn_more: {e}")

    @staticmethod
    def edit_plan_check(page, plan_value: str = "100", paper=False, callback=None):
        plan_selector_page = PlanSelectorV3Page(page)
        confirmation_page = ConfirmationPage(page)
        try:
            # To confirm on the right page
            confirmation_page.blue_inf_icon.wait_for(state='visible', timeout=180000)
            confirmation_page.edit_plan_button.click()

            try:
                plan_selector_page.plans_selector_v3.click(timeout=120000)  # click on dropdown
                if callback: callback("update_plan_selection", page, screenshot_only=True)
                plan_selector_page.select_plan(plan_value)
            except Exception as e:
                framework_logger.warning(f"Error Update plan: {plan_value}, {e}")

            if callback: callback("update_plan_selection", page, screenshot_only=True)

            if paper:
                plan_selector_page.ink_paper_button.click()
            else:
                plan_selector_page.ink_only_button.click()

            confirmation_page.blue_inf_icon.wait_for(state='visible', timeout=180000)
            framework_logger.info('Blue info icon is visible')
        except Exception as e:
            if callback: callback("update_plan_failure", page, screenshot_only=True)
            framework_logger.warning(f"Error editing plan: {e}")

    @staticmethod
    def choose_hp_checkout(page):
        confirmation_page = ConfirmationPage(page)
        try:
            page.wait_for_selector(confirmation_page.elements.hp_checkout_button, state="visible", timeout=600000)
            if page.locator(confirmation_page.elements.hp_checkout_button).is_enabled():
                confirmation_page.hp_checkout_button.click()
        except Exception as e:
            print("HP checkout button not displayed or not enabled, continuing flow")

    @staticmethod
    def _paypal_login_popup(paypal_page, confirmation_page, paypal_email, paypal_password):
        paypal_page.wait_for_selector(confirmation_page.elements.paypal_email_input, state="visible", timeout=60000)
        paypal_page.fill(confirmation_page.elements.paypal_email_input, paypal_email)
        paypal_page.click(confirmation_page.elements.paypal_next_button)

        paypal_page.wait_for_selector(confirmation_page.elements.paypal_use_password_instead_button, state="visible", timeout=60000)
        paypal_page.click(confirmation_page.elements.paypal_use_password_instead_button) # Try another way button
        paypal_page.wait_for_selector(confirmation_page.elements.paypal_use_password_instead_option, state="visible", timeout=20000)
        paypal_page.click(confirmation_page.elements.paypal_use_password_instead_option)
        print("Clicked 'Use Password Instead' button.")
        # try:
        #     paypal_page.wait_for_selector(confirmation_page.elements.paypal_use_password_instead_button, state="visible", timeout=30000)
        #     paypal_page.click(confirmation_page.elements.paypal_use_password_instead_button)
        #     print("Clicked 'Use Password Instead' button.")
        # except Exception:
        #     pass
        paypal_page.wait_for_selector(confirmation_page.elements.paypal_password_input, state="visible", timeout=20000)
        paypal_page.locator(confirmation_page.elements.paypal_password_input).focus()
        paypal_page.fill(confirmation_page.elements.paypal_password_input, paypal_password)
        paypal_page.click(confirmation_page.elements.paypal_login_button)
        try:
            paypal_page.wait_for_selector(confirmation_page.elements.paypal_agree_button, state="visible", timeout=10000)
            paypal_page.click(confirmation_page.elements.paypal_agree_button)
        except Exception:
            print("PayPal agree button not displayed, continuing flow.")
            pass
        try:
            paypal_page.wait_for_selector(confirmation_page.elements.paypal_continue_button, state="visible", timeout=5000)
            paypal_page.click(confirmation_page.elements.paypal_continue_button)
        except Exception:
            print("PayPal continue button not displayed, continuing flow.")
            pass
        paypal_page.wait_for_event("close", timeout=60000)

    @staticmethod
    def choose_paypal_checkout(page):
        confirmation_page = ConfirmationPage(page)
        paypal_iframe_locator = confirmation_page.elements.paypal_checkout_button_iframe
        paypal_button_locator = confirmation_page.elements.paypal_checkout_button
        page.wait_for_selector(paypal_iframe_locator, state="attached", timeout=30000)
        page.frame_locator(paypal_iframe_locator).locator(paypal_button_locator).wait_for(state="visible", timeout=30000)

        with page.context.expect_page() as new_page_info:
            page.frame_locator(paypal_iframe_locator).locator(paypal_button_locator).click()
            print("Waiting for PayPal page to open...")

        paypal_page = new_page_info.value
        payment_data = common.get_payment_method_data("paypal")
        paypal_email = f"{payment_data['email'].rsplit('@', 1)[0]}-{GlobalState.country_code}@{payment_data['email'].rsplit('@', 1)[1]}"
        paypal_password = payment_data["password"]
        EnrollmentHelper._paypal_login_popup(paypal_page, confirmation_page, paypal_email, paypal_password)
        try:
            page.wait_for_selector("[data-testid='phone-modal-text-box']", state="visible", timeout=10000)
            page.fill("[data-testid='phone-modal-text-box']", (GlobalState.address_payload[0] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload).get("phoneNumber1"))
            page.click("[data-testid='signup-missing-phone-modal'] span")
            print("Entered mobile number in phone modal.")
        except Exception:
            print("Phone modal not shown, skipping.")

    @staticmethod
    def add_shipping(page, index=0, company_name=None, additional_check=False, callback=None):
        confirmation_page = ConfirmationPage(page)
        address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
        state_name = address.get("fullState", address.get(f"fullState_{GlobalState.language_code}"))
        try:
            if confirmation_page.add_shipping_button.is_visible(timeout=60000):
               framework_logger.info("Add shipping button is visible, clicking it.")
               confirmation_page.add_shipping_button.click()
        except Exception:
            framework_logger.info("Add shipping button not displayed, continuing flow")
            pass  # Button not available in Flip
        if company_name:
            confirmation_page.company_name_input.fill(company_name)
        confirmation_page.street1_input.fill(address.get("street1", ""))
        confirmation_page.street2_input.fill(address.get("street2", ""))
        countries_without_city_mandate = ["Hong Kong", "Singapore"]
        if GlobalState.country not in countries_without_city_mandate:
            confirmation_page.city_input.fill(address.get("city", ""))
        countries_without_states_mandate = common.countries_without_states_mandate()
        if GlobalState.country not in countries_without_states_mandate and state_name:
            confirmation_page.state_dropdown.click()
            element_id = confirmation_page.state_dropdown.get_attribute("id")
            select_list_option = f"#{element_id}-listbox li"
            select_state = page.locator(f"{select_list_option}:has-text('{state_name}')")
            select_state.wait_for(state="visible", timeout=2000)
            select_state.click()
        countries_without_zip_mandate = ["Hong Kong"]
        if GlobalState.country not in countries_without_zip_mandate:
            confirmation_page.zip_code_input.fill(address.get("zipCode", ""))
        confirmation_page.phone_number_input.fill(address.get("phoneNumber1", ""))

        # Additional check in 'shipping' section
        if additional_check:
            try:
                # Validate the receive updates message
                confirmation_page.receive_update_msg.wait_for(state="visible", timeout=5000)
                framework_logger.info('Receive updates message is visible')

                # Check if the checkbox is unchecked by default
                try:
                    confirmation_page.receive_update_checkbox.is_checked()
                    framework_logger.info('Receive updates checkbox is checked.')
                    checkbox_state = True
                except:
                    framework_logger.info('Receive updates checkbox is not checked by default')
                    checkbox_state = False

                if checkbox_state:
                    raise Exception("ERROR: Receive updates checkbox checked by default.")

                # check 'x' button is visible
                confirmation_page.close_shipping_modal_button.wait_for(state="visible", timeout=5000)
                framework_logger.info("Close 'x' button is visible.")

                # check if 'cancel' button is visible
                confirmation_page.cancel_button.wait_for(state="visible", timeout=5000)
                framework_logger.info("Cancel button is visible.")

                # check if 'save' button is visible
                confirmation_page.save_button.wait_for(state="visible", timeout=5000)
                framework_logger.info("Save button is visible.")
            except Exception as e:
                framework_logger.error(f"ERROR: Failed at Add Shipping - additional check: {e}")
                if callback: callback("error_add_shipping_additional_check_failed1", page, screenshot_only=True)

        # Save shipping address
        confirmation_page.save_button.click()

        try:
            page.wait_for_selector(confirmation_page.elements.suggested_address_modal, state="visible", timeout=5000)
            if page.wait_for_selector(confirmation_page.elements.suggested_address_modal).is_enabled():
                confirmation_page.ship_to_address_button.click()
        except Exception as e:
            framework_logger.error("Suggested address modal not displayed or button not available")
            print("Suggested address modal not displayed or button not available")
            if callback: callback("error_no_suggested_address_modal", page, screenshot_only=True)

        # Additional check to validate address after save
        if additional_check:
            try:
                page.locator(f'text={address.get("street1", "")}').wait_for(state="visible", timeout=10000)
                page.locator(f'text={address.get("street2", "")}').wait_for(state="visible", timeout=10000)
                addr = f'text={address.get("city", "")}, {address.get("state", "")} {address.get("zipCode", "")} '
                page.locator(addr).wait_for(state="visible", timeout=10000)
                framework_logger.info("Shipping address validated successfully after save")
            except Exception as e:
                framework_logger.error(f"ERROR: Failed validate shipping address after save: {e}")
                if callback: callback("error_add_shipping_additional_check_failed2", page, screenshot_only=True)

    @staticmethod
    def modal_boundary_check(page, modal_locator="data-testid=shipping-modal"):
        # Get modal bounding box
        modal = page.locator(modal_locator)
        box = modal.bounding_box()

        # Calculate a point outside the modal (e.g., above or to the left)
        outside_x = box["x"] - 10
        outside_y = box["y"] - 10

        # Click outside the modal
        page.mouse.click(outside_x, outside_y)
        framework_logger.info("Click outside box is visible.")
        if not page.locator('//*[text()="Select your printing plan"]').is_visible(): # Check is done only for Shipping & Billing modal
            # Assert modal is still visible
            assert modal.is_visible(), "Modal closed after clicking outside"

    @staticmethod
    def shipping_modal_close(page, index=2, company_name=None, callback=None, mandatory_fields_check=False):
        confirmation_page = ConfirmationPage(page)
        try:
            current_addr = confirmation_page.shipping_address_details.text_content()

            address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
            state_name = address.get("fullState", address.get(f"fullState_{GlobalState.language_code}"))

            # click on 'edit' shipping address
            confirmation_page.edit_shipping_button.click()

            if mandatory_fields_check:
                # Keep some mandatory fields empty.
                confirmation_page.first_name.fill("")
                confirmation_page.street1_input.fill("")

                confirmation_page.save_button.click()
                mand_msg = confirmation_page.error_message.text_content()
                if mand_msg == "Please complete required fields correctly":
                    framework_logger.info("Mandatory field validation message is visible.")
                else:
                    framework_logger.error("ERROR: Mandatory field validation message is NOT visible.")
                if callback: callback("mandatory_fields_check1", page, screenshot_only=True)

                # Make some required fields are incorrectly filled.
                confirmation_page.close_shipping_modal_button.click()
                confirmation_page.edit_shipping_button.wait_for(state="visible", timeout=10000)
                confirmation_page.edit_shipping_button.click()

                confirmation_page.first_name.fill("123")
                confirmation_page.last_name.fill("123")

                mand_msg = confirmation_page.error_message.text_content()
                if mand_msg == "Please complete required fields correctly":
                    framework_logger.info("Mandatory field validation message is visible.")
                else:
                    framework_logger.error("ERROR: Mandatory field validation message is NOT visible.")
                if callback: callback("mandatory_fields_check2", page, screenshot_only=True)
                confirmation_page.close_shipping_modal_button.click()

                confirmation_page.edit_shipping_button.wait_for(state="visible", timeout=10000)
                confirmation_page.edit_shipping_button.click()

            # Enter shipping details
            if company_name:
                confirmation_page.company_name_input.fill(company_name)
            confirmation_page.street1_input.fill(address.get("street1", ""))
            confirmation_page.street2_input.fill(address.get("street2", ""))
            countries_without_city_mandate = ["Hong Kong", "Singapore"]
            if GlobalState.country not in countries_without_city_mandate:
                confirmation_page.city_input.fill(address.get("city", ""))
            countries_without_states_mandate = common.countries_without_states_mandate()
            if GlobalState.country not in countries_without_states_mandate and state_name:
                confirmation_page.state_dropdown.click()
                element_id = confirmation_page.state_dropdown.get_attribute("id")
                select_list_option = f"#{element_id}-listbox li"
                select_state = page.locator(f"{select_list_option}:has-text('{state_name}')")
                select_state.wait_for(state="visible", timeout=2000)
                select_state.click()
            countries_without_zip_mandate = ["Hong Kong"]
            if GlobalState.country not in countries_without_zip_mandate:
                confirmation_page.zip_code_input.fill(address.get("zipCode", ""))
            confirmation_page.phone_number_input.fill(address.get("phoneNumber1", ""))

            #Modal boundary check
            EnrollmentHelper.modal_boundary_check(page, modal_locator="data-testid=shipping-modal")

            # check model is NOT closed after above step
            confirmation_page.save_button.wait_for(state="visible", timeout=5000)
            framework_logger.info("Shipping Model is visible after clicking outside the model.")

            # Click on 'x' button
            confirmation_page.close_shipping_modal_button.click()
            framework_logger.info("Click on 'X' button")

            # Validate address isn't changed
            confirmation_page.edit_shipping_button.wait_for(state="visible", timeout=10000)
            edit_addr = confirmation_page.shipping_address_details.text_content()
            if current_addr == edit_addr:
                framework_logger.info("Address is same after modal close.")
            else:
                framework_logger.error("ERROR: Address updated after modal close.")
        except Exception as e:
            framework_logger.error(f"Error: Shipping Modal Close: {e}")
            if callback: callback("error_shipping_modal", page, screenshot_only=True)

    @staticmethod
    def edit_shipping_check(page, index=1, company_name=None, additional_check=False, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
            state_name = address.get("fullState", address.get(f"fullState_{GlobalState.language_code}"))

            confirmation_page.edit_shipping_button.click()

            if company_name:
                confirmation_page.company_name_input.fill(company_name)
            confirmation_page.street1_input.fill(address.get("street1", ""))
            confirmation_page.street2_input.fill(address.get("street2", ""))
            countries_without_city_mandate = ["Hong Kong", "Singapore"]
            if GlobalState.country not in countries_without_city_mandate:
                confirmation_page.city_input.fill(address.get("city", ""))
            countries_without_states_mandate = common.countries_without_states_mandate()
            if GlobalState.country not in countries_without_states_mandate and state_name:
                confirmation_page.state_dropdown.click()
                element_id = confirmation_page.state_dropdown.get_attribute("id")
                select_list_option = f"#{element_id}-listbox li"
                select_state = page.locator(f"{select_list_option}:has-text('{state_name}')")
                select_state.wait_for(state="visible", timeout=2000)
                select_state.click()
            countries_without_zip_mandate = ["Hong Kong"]
            if GlobalState.country not in countries_without_zip_mandate:
                confirmation_page.zip_code_input.fill(address.get("zipCode", ""))
            confirmation_page.phone_number_input.fill(address.get("phoneNumber1", ""))

            # Save shipping address
            confirmation_page.save_button.click()
        except Exception as e:
            framework_logger.error(f"Error: edit_shipping: {e}")
            if callback: callback("error_edit_shipping_failed", page, screenshot_only=True)

        # Additional check to validate address after save
        if additional_check:
            try:
                page.locator(f'text={address.get("street1", "")}').wait_for(state="visible", timeout=30000)
                page.locator(f'text={address.get("street2", "")}').wait_for(state="visible", timeout=10000)
                addr = f'text={address.get("city", "")}, {address.get("state", "")} {address.get("zipCode", "")} '
                page.locator(addr).wait_for(state="visible", timeout=10000)
                framework_logger.info("Shipping address validated successfully after save")
            except Exception as e:
                framework_logger.error(f"ERROR: Failed validate shipping address after save: {e}")
                if callback: callback("error_add_shipping_additional_check_failed2", page, screenshot_only=True)

    @staticmethod
    def verify_shipping_card_layout(page):
        """
        Validates the Shipping Card layout (visible, not cutoff, edit button visible).
        """
        confirmation_page = ConfirmationPage(page)
        expect(confirmation_page.shipping_card).to_be_visible(timeout=60000)
        bbox = confirmation_page.shipping_card.bounding_box()
        assert bbox and bbox['width'] > 0 and bbox['height'] > 0, "Shipping card dimensions invalid"
        expect(confirmation_page.edit_shipping_button).to_be_visible()

    @staticmethod
    def verify_shipping_tick_color(page, data_testid: str = "shipping-card", expected_color: str = "rgb(0, 0, 0)"):
        """
        Verifies that the tick mark icon is visible and has the expected color inside a given card.
        :param data_testid: The data-testid of the card (e.g., 'plan-card', 'shipping-card', 'billing-card')
        :param expected_color: Expected CSS color value (default is black: 'rgb(0, 0, 0)')
        """
        try:
            tick_icon_locator = page.locator(f"div[data-testid='{data_testid}'] svg[class*='base-Icon']")
            tick_icon_locator.nth(0).wait_for(state="visible", timeout=60000)
            color = tick_icon_locator.nth(0).evaluate("el => window.getComputedStyle(el).color")
            assert color == expected_color, f" Tick mark in '{data_testid}' card is not {expected_color}, got: {color}"
            framework_logger.info(f" Tick mark for '{data_testid}' card is visible and has expected color: {color}")
        except Exception as e:
            framework_logger.error(f"Error verifying tick mark color for '{data_testid}': {e}")
            raise

    @staticmethod
    def validate_edit_shipping_fields_and_close(page, index=0, additional_check=True, callback=None):
        """
        After clicking edit_shipping_button, validate all fields match expected address, then close modal.
        """
        confirmation_page = ConfirmationPage(page)
        address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
        framework_logger.info(f"Validating shipping address : {address}")
        # Click edit shipping button
        confirmation_page.edit_shipping_button.wait_for(state="visible", timeout=60000)
        confirmation_page.edit_shipping_button.click()

        # Validate the receive updates message
        confirmation_page.receive_update_msg.wait_for(state="visible", timeout=60000)
        framework_logger.info('Receive updates message is visible')

        # Validate each field matches the expected address
        assert confirmation_page.first_name.input_value() == address.get("firstName", ""), "First name does not match"
        assert confirmation_page.last_name.input_value() == address.get("lastName", ""), "Last name does not match"
        assert confirmation_page.company_name_input.input_value() == address.get("company", ""), "Company name does not match"
        assert confirmation_page.street1_input.input_value() == address.get("street1", ""), "Street1 does not match"
        assert confirmation_page.street2_input.input_value() == address.get("street2", ""), "Street2 does not match"
        assert confirmation_page.city_input.input_value() == address.get("city", ""), "City does not match"
        assert confirmation_page.state_dropdown.text_content().strip() == address.get("fullState", ""), "State does not match"
        assert confirmation_page.zip_code_input.input_value() == address.get("zipCode", ""), "Zip code does not match"
        assert confirmation_page.phone_number_input.input_value() == address.get("phoneNumber1", ""), "Phone number does not match"
        framework_logger.info("All fields match the expected address.")

        if additional_check:
            confirmation_page.zip_code_input.fill('97439')
            confirmation_page.save_button.click()
            confirmation_page.blacklist_zipcode_error_text.wait_for(state="visible", timeout=30000)
            confirmation_page.blacklist_zipcode_back_button.click()
            framework_logger.info("Blacklisted Zipcode PBL message check completed.")

        # Close the shipping modal
        confirmation_page.close_shipping_modal_button.click()
        framework_logger.info("Closed shipping modal after validation.")

    @staticmethod
    def validate_pre_billing_section_info(page, callback=None):
        """
        1. Wait for billing button to be enabled.
        2. Verify preenroll continue button is disabled.
        3. Check billing info icon is visible.
        4. Move mouse to info icon and validate tooltip text.
        5. Move mouse away and verify tooltip disappears.
        6. Verify 'Enter promo or PIN code' link is enabled
        """
        confirmation_page = ConfirmationPage(page)
        # 1. Wait for billing button to be enabled
        confirmation_page.add_billing_button.wait_for(state="visible", timeout=60000)
        assert confirmation_page.add_billing_button.is_enabled(), "Billing button is not enabled"

        # 2. Verify preenroll continue button is disabled
        confirmation_page.preenroll_continue_button.wait_for(state="visible", timeout=30000)
        assert not confirmation_page.preenroll_continue_button.is_enabled(), "Continue button should be disabled"

        # 3. Validate the info icon is visible
        confirmation_page.billing_info_icon.wait_for(state="visible", timeout=20000)
        assert confirmation_page.billing_info_icon.is_visible(), "Info icon is not visible"

        # 4. Move mouse to info icon and validate tooltip text
        confirmation_page.billing_info_icon.hover()
        tooltip = page.locator(confirmation_page.elements.tooltip_content)
        tooltip.wait_for(state="visible", timeout=5000)
        tooltip_text = tooltip.text_content().strip()
        expected_text = "Your billing information is used to continue your subscription after the trial."
        # Normalize whitespace in both strings before comparison
        tooltip_text = " ".join(tooltip_text.split())
        expected_text = " ".join(expected_text.split())
        assert expected_text in tooltip_text, f"Expected tooltip text '{expected_text}' but found '{tooltip_text}'"

        # 5. Move mouse away and verify tooltip disappears
        page.mouse.move(0, 0)
        tooltip.wait_for(state="hidden", timeout=5000)

        # 6. Verify 'Enter promo or PIN code' link is enabled
        confirmation_page.enter_promo_or_pin_code_button.wait_for(state="visible", timeout=10000)
        assert confirmation_page.enter_promo_or_pin_code_button.is_enabled(), "'Enter promo or PIN code' link is not enabled"

    @staticmethod
    def add_billing(page, payment_method=None, plan_value=None):
        if payment_method is None:
            payment_method = common._payment_method

        if payment_method:
            if payment_method == "paypal":
                EnrollmentHelper.add_paypal_billing(page)
                return
            elif payment_method == "google_pay":
                EnrollmentHelper.add_google_pay_billing(page)
                return
            elif payment_method == "direct_debit":
                EnrollmentHelper.add_direct_debit_billing(page)
                return
            elif payment_method == "prepaid_only":
                EnrollmentHelper.add_prepaid_by_value(page, plan_value)
            else:
                card_payment_gateway = getattr(GlobalState, "card_payment_gateway")
                if card_payment_gateway == "PGS":
                    EnrollmentHelper.add_pgs_billing(page, payment_method)
                elif card_payment_gateway == "2CO":
                    EnrollmentHelper.add_2co_billing(page, payment_method)
        else:
            # raise ValueError(f"Unsupported payment provider: {card_payment_gateway}")
            raise ValueError("Unsupported payment provider")

    @staticmethod
    def billing_card(page, card_type=None):
        try:
            confirmation_page = ConfirmationPage(page)
            payment_data = common.get_payment_method_data(card_type)
            if confirmation_page.add_billing_button.is_enabled(timeout=60000):
                framework_logger.info("Billing button is enabled.")
                confirmation_page.enter_promo_or_pin_code_button.is_enabled(timeout=60000)
                framework_logger.info("Promo/Pin code button is enabled.")

                confirmation_page.billing_card_info.wait_for(state='visible', timeout=60000)
                framework_logger.info("Billing info icon is visible.")
                confirmation_page.billing_card_info.hover()
                bill_info = confirmation_page.billing_card_info.text_content()
                if bill_info.replace('\u00A0',
                                      ' ') == "Your billing information is used to continue your subscription after the trail.":
                    framework_logger.info("Billing info message validated successfully")
                else:
                    framework_logger.info(f"Billing Info: {bill_info}")
                    framework_logger.error("Billing info message validation failed")

                confirmation_page.add_billing_button.click(timeout=60000)

                confirmation_page.business_radio_button.wait_for(state="visible", timeout=60000)
                confirmation_page.consumer_radio_button.wait_for(state="visible", timeout=60000)

                confirmation_page.consumer_radio_button.is_checked(timeout=60000)
                framework_logger.info("Consumer radio button is selected by default.")
                confirmation_page.billing_continue_button.click(timeout=60000)

                frame = page.frame_locator(confirmation_page.elements.iframe_pgs)
                card_input = frame.locator(confirmation_page.elements.card_number)
                card_input.fill(payment_data["credit_card_number"])
                confirmation_page.card_number.wait_for(state="visible", timeout=100000)
                confirmation_page.card_number.fill(payment_data["credit_card_number"])
                confirmation_page.exp_month.select_option(payment_data.get("expiration_month"))
                confirmation_page.exp_year.select_option(payment_data.get("expiration_year"))
                confirmation_page.cvv_input.type(payment_data["cvv"])
                framework_logger.info("Card details filled successfully.")

                confirmation_page.btn_pgs_card_cancel.wait_for(state="visible", timeout=60000)
                confirmation_page.close_billing_button.wait_for(state="visible", timeout=60000)
                confirmation_page.billing_next_button.wait_for(state="visible", timeout=60000)
                framework_logger.info("Billing cancel, close and next buttons are visible.")
            else:
                framework_logger.error("ERROR: Billing button is disabled.")
        except Exception as e:
            framework_logger.error(f"Error billing_card: {e}")

    @staticmethod
    def add_pgs_billing(page, card_type=None):
        confirmation_page = ConfirmationPage(page)
        payment_data = common.get_payment_method_data(card_type)
        framework_logger.info(f"Using card type: {card_type}")
        try:
             if confirmation_page.add_billing_button.is_visible(timeout=10000):
                confirmation_page.add_billing_button.click()
        except Exception:
            pass  # Button not available in Flip
        
        if GlobalState.country_code == "IT":
            page.fill(confirmation_page.elements.tax_id_input, "MRTMTT91D08F205J")
        else:
            try:
                page.locator(f"{confirmation_page.elements.use_shipping_address}:checked").wait_for(timeout=120000)
            except Exception:
                framework_logger.info("Use shipping address checkbox not displayed or checked, continuing flow")

        page.locator(confirmation_page.elements.billing_continue_button).is_enabled()
        page.locator(confirmation_page.elements.billing_continue_button).click()
        page.locator(confirmation_page.elements.iframe_pgs).wait_for(state="visible", timeout=120000)
        frame = page.frame_locator(confirmation_page.elements.iframe_pgs)
        card_input = frame.locator(confirmation_page.elements.card_number)
        card_input.fill(payment_data["credit_card_number"])
        frame.locator(confirmation_page.elements.exp_month).select_option(payment_data.get("expiration_month"))
        frame.locator(confirmation_page.elements.exp_year).select_option(payment_data.get("expiration_year"))
        frame.locator(confirmation_page.elements.cvv_input).type(payment_data["cvv"])
        time.sleep(15)  # Wait for a moment to ensure next button check works consistently
        if frame.locator(confirmation_page.elements.billing_next_button).count() > 0:
            page.wait_for_timeout(10000) # Wait for a moment to ensure next button click works consistently
            frame.locator(confirmation_page.elements.billing_next_button).click()
            # time.sleep(15) # Wait for a moment to ensure next button check works consistently
            # if frame.locator(confirmation_page.elements.billing_next_button).is_visible():
            #     frame.locator(confirmation_page.elements.billing_next_button).click()
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
            challenge_frame.locator(confirmation_page.elements.authentication_result_2fa).select_option(
                payment_data.get("3ds_auth_result", "AUTHENTICATED"))
            challenge_frame.locator(submit_selector).wait_for(state="visible")
            challenge_frame.locator(submit_selector).click()
        page.wait_for_selector(confirmation_page.elements.edit_billing_button, state="visible", timeout=120000)

    @staticmethod
    def add_2co_billing(page, card_type=None):
        confirmation_page = ConfirmationPage(page)
        payment_data = common.get_payment_method_data(card_type)
        framework_logger.info(f"Using card type: {card_type}")
        confirmation_page.add_billing_button.click()
        framework_logger.info("Add billing button clicked")
        page.wait_for_selector(confirmation_page.elements.iframe_2co, state="visible", timeout=120000)
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(
            confirmation_page.elements.continue_to_billing).wait_for(state="visible", timeout=60000)
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(
            confirmation_page.elements.continue_to_billing).click()
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(
            confirmation_page.elements.continue_to_payment).wait_for(state="visible", timeout=60000)
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(
            confirmation_page.elements.continue_to_payment).click()
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(
            confirmation_page.elements.card_name_2co).wait_for(state="attached", timeout=3000)
        if page.frame_locator(confirmation_page.elements.iframe_2co).locator(
                confirmation_page.elements.card_name_2co).is_visible():
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(
                confirmation_page.elements.card_name_2co).fill("John Doe")
        else:
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(
                confirmation_page.elements.first_name_2co).wait_for(state="visible")
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(
                confirmation_page.elements.first_name_2co).type("John")
            page.keyboard.press("Tab")
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(
                confirmation_page.elements.last_name_2co).wait_for(state="visible")
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(
                confirmation_page.elements.last_name_2co).type("Doe")
        page.keyboard.press("Tab")
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(
            confirmation_page.elements.card_number_2co).type(payment_data["credit_card_number"])
        page.keyboard.press("Tab")
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.exp_date_2co).type(
            f"{payment_data.get('expiration_month')}/{payment_data.get('expiration_year')[-2:]}")
        page.keyboard.press("Tab")
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.cvv_2co).type(
            payment_data["cvv"])
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(
            confirmation_page.elements.place_order_button).wait_for(state="visible", timeout=60000)
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(
            confirmation_page.elements.place_order_button).click()

    @staticmethod
    def add_direct_debit_billing(page):
        """Handle Direct Debit payment method"""
        confirmation_page = ConfirmationPage(page)
        payment_data = common.get_payment_method_data("direct_debit")

        confirmation_page.add_billing_button.click()

        # Select Direct Debit option
        page.locator("[data-testid='direct-debit-radio-button'], [data-testid='direct-debit-radio-option']").click(
            force=True, timeout=60000)
        confirmation_page.billing_continue_button.click()

        # Fill IBAN and bank details
        frame = page.frame_locator(confirmation_page.elements.iframe_pgs)

        account = frame.locator("[id='txtAccountHolderName']")
        account.fill(payment_data["bank_name"])

        iban = frame.locator("[id='txtIBAN']")
        iban.press_sequentially(payment_data["iban"])

        # Accept SEPA mandate
        frame.locator("[id='btn_pgs_directdebit_add']").click()
        framework_logger.info("Direct Debit billing successfully added")

    @staticmethod
    def validate_billing_step_one_layout(page):
        confirmation_page = ConfirmationPage(page)
        framework_logger.info("Validating billing card elements layout")
        elements = [
            confirmation_page.elements.account_type_section,
            confirmation_page.elements.credit_card_payment_box,
            confirmation_page.elements.address_preview_card,
            confirmation_page.elements.billing_continue_button,
            confirmation_page.elements.cancel_button
        ]
        EnrollmentHelper.validate_elements_layout(page, elements)

    @staticmethod
    def validate_elements_layout(page, elements, frame=None):
        """
        Validates that all elements in the list are visible and not cutoff/overlap/missing.
        If frame is provided, uses frame.locator; otherwise, uses page.locator.
        """    
        for selector in elements:
            locator = frame.locator(selector) if frame else page.locator(selector)
            locator.wait_for(state="visible", timeout=20000)
            bbox = locator.bounding_box()
            assert bbox and bbox['width'] > 0 and bbox['height'] > 0, f"Element {selector} is missing or cutoff"
            viewport = page.viewport_size
            framework_logger.info(f"Viewport size: {viewport}, Element {selector} bbox: {bbox}")
            assert bbox['x'] >= 0 and bbox['y'] >= 0, f"Element {selector} is out of view (negative position)"
            assert bbox['x'] + bbox['width'] <= viewport['width'], f"Element {selector} is cutoff horizontally"
            assert bbox['y'] + bbox['height'] <= viewport['height'], f"Element {selector} is cutoff vertically"
            framework_logger.info(f"Element {selector} is visible and properly positioned.")
    
    @staticmethod
    def validate_billing_step_two_layout(page):
        """
        Validates the layout of GPay, PayPal, and card input fields inside the iframe on billing step two.
        """
        confirmation_page = ConfirmationPage(page)
        framework_logger.info("Validating step two billing card elements layout")

        # 1. Validate GPay and PayPal buttons
        elements = [
        confirmation_page.elements.google_pay_button,
        confirmation_page.elements.paypal_button,
        confirmation_page.elements.btn_pgs_card_cancel,
        confirmation_page.elements.pgs_card_continue,
        ]
        EnrollmentHelper.validate_elements_layout(page, elements)

        # 2. Validate card input fields inside the iframe
        page.locator(confirmation_page.elements.iframe_pgs).wait_for(state="visible", timeout=20000)
        frame = page.frame_locator(confirmation_page.elements.iframe_pgs)
        card_fields = [
        confirmation_page.elements.card_number,
        confirmation_page.elements.exp_month,
        confirmation_page.elements.exp_year,
        confirmation_page.elements.cvv_input
        ]
        EnrollmentHelper.validate_elements_layout(page, card_fields, frame=frame)

    @staticmethod
    def validate_billing_step_one_card_elements_layout(page, index=0, layout_check=True, shipping_addr_check=True):
        """
        Validates that all key Billing Card elements are visible and not cutoff/overlap/missing.
        """
        confirmation_page = ConfirmationPage(page)
        address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
        framework_logger.info(f"Validating shipping address : {address}")

        # Wait for add billing button to be visible
        confirmation_page.add_billing_button.wait_for(state="visible", timeout=50000)
        assert confirmation_page.add_billing_button.is_enabled(), "Add billing button is not enabled"

        # Click the add billing button
        confirmation_page.add_billing_button.click()

        time.sleep(5)
        #expect(page.locator("text=Billing")).to_be_visible(timeout=60000)
        expect(confirmation_page.bill_head).to_be_visible(timeout=60000)

        # Wait for billing step one section to be visible
        expect(confirmation_page.billing_step_one).to_be_visible(timeout=60000)

        # Validate radio button toggle behavior for account type selection
        consumer_radio = confirmation_page.consumer_radio_button.is_checked()
        business_radio = confirmation_page.business_radio_button.is_checked()
        if layout_check:
            # If Consumer is checked, validate billing modal layout
            if consumer_radio:
                framework_logger.info("Consumer radio button is enabled")
                EnrollmentHelper.validate_billing_step_one_layout(page)
                assert consumer_radio, "Consumer radio button should be selected by default"
                assert not business_radio, "Business radio button should be unselected by default"
                framework_logger.info("Default state verified: Consumer selected, Business unselected")

            confirmation_page.business_radio_button.click()
            page.wait_for_timeout(2000)  # Wait for UI to update
            consumer_radio = confirmation_page.consumer_radio_button.is_checked()
            business_radio = confirmation_page.business_radio_button.is_checked()
            # If Business is checked
            if business_radio:
                framework_logger.info("Business radio button is enabled")
                EnrollmentHelper.validate_billing_step_one_layout(page)
                expect(confirmation_page.billing_company_input).to_be_visible(timeout=10000)
                expect(confirmation_page.tax_id_input).to_be_visible(timeout=10000)
                assert business_radio, "Business radio button should be selected"
                assert not consumer_radio, "Consumer radio button should be unselected"
                framework_logger.info("Business state verified: Business selected, Consumer unselected")  

        # Validate shipping address checkbox behavior
        if shipping_addr_check:
            checkbox = page.locator(confirmation_page.elements.use_shipping_address)
            assert checkbox.is_checked(), "Checkbox should be selected by default"
            checkbox.uncheck()
            page.wait_for_timeout(2000)
            assert not checkbox.is_checked(), "Checkbox should be unselected after unchecking"
            framework_logger.info("Checkbox uncheck behavior verified")
            # Validate each field matches the expected address
            assert confirmation_page.first_name.input_value() == address.get("firstName", ""), "First name does not match"
            assert confirmation_page.last_name.input_value() == address.get("lastName", ""), "Last name does not match"
            assert confirmation_page.street1_input.input_value() == address.get("street1", ""), "Street1 does not match"
            assert confirmation_page.street2_input.input_value() == address.get("street2", ""), "Street2 does not match"
            assert confirmation_page.city_input.input_value() == address.get("city", ""), "City does not match"
            assert confirmation_page.state_dropdown.text_content().strip() == address.get("fullState", ""), "State does not match"
            assert confirmation_page.zip_code_input.input_value() == address.get("zipCode", ""), "Zip code does not match"
        framework_logger.info("All fields match the expected address.")
        # click X button billing modal
        confirmation_page.close_billing_button.click()
        framework_logger.info("Closed billing modal")
    
    @staticmethod
    def validate_billing_step_two_layout_elements(page, layout_check=True):
        # Validate step two billing layout
        confirmation_page = ConfirmationPage(page)
        # Wait for add billing button to be visible
        confirmation_page.add_billing_button.wait_for(state="visible", timeout=50000)
        assert confirmation_page.add_billing_button.is_enabled(), "Add billing button is not enabled"
        confirmation_page.add_billing_button.click()
        # Wait for billing step one in continue button to be visible
        confirmation_page.billing_continue_button.wait_for(state="visible", timeout=60000)
        assert confirmation_page.billing_continue_button.is_enabled(), "Billing continue button is not enabled"
        confirmation_page.billing_continue_button.click()
        confirmation_page.paypal_button.wait_for(timeout=60000)
        if layout_check:
            # Validate 'Step 2 of 2' and 'Complete your payment.' text 
            expect(page.locator(confirmation_page.elements.billing_step_two)).to_be_visible(timeout=10000)
            expect(page.locator(confirmation_page.elements.complete_your_payment)).to_be_visible(timeout=10000)
            # Validate that back, cancel, and continue buttons are enabled
            assert page.locator(confirmation_page.elements.back_button).is_enabled(), "Back button should be enabled"
            assert page.locator(confirmation_page.elements.btn_pgs_card_cancel).is_enabled(), "Cancel button should be enabled"
            assert page.locator(confirmation_page.elements.pgs_card_continue).is_enabled(), "Continue button should be enabled"
            framework_logger.info("Billing step two buttons Back, Cancel, and Continue are enabled")
            EnrollmentHelper.validate_billing_step_two_layout(page)
            # Validate that card number input is empty
            card_number_input = page.locator(confirmation_page.elements.card_number)
            assert card_number_input.input_value() == "", "Card number input should be empty" 
            framework_logger.info("Card number input is empty on billing step two")
            confirmation_page.continue_button.click()
            # validate the error message
            expect(page.locator(confirmation_page.elements.enter_cvv_error)).to_be_visible(timeout=10000)
            framework_logger.info("Enter Card CVV error message is visible")
            # click cancel button
            #confirmation_page.cancel_button.click()
            framework_logger.info("Clicked cancel button on billing step two")

        # Wait for the 'Step 2 of 2' X button to be visible, then click
        confirmation_page.close_billing_button.wait_for(state="visible", timeout=10000)
        confirmation_page.close_billing_button.click()
        framework_logger.info("Closed billing modal from step two")

    @staticmethod
    def validate_company_name_and_tax_id_persistence(page, company_name="test", tax_id="51-2144346", business_check=True):
        """
        Validates that the entered Company Name and Tax ID persist correctly after navigating forward
        to Billing Step Two and then returning back to Billing Step One.    
        """
        confirmation_page = ConfirmationPage(page)

        # Wait for add billing button to be visible and enabled, then click
        confirmation_page.add_billing_button.wait_for(state="visible", timeout=50000)
        assert confirmation_page.add_billing_button.is_enabled(), "Add billing button is not enabled"
        confirmation_page.add_billing_button.click()

        # Wait for Business radio button to be visible, then click
        confirmation_page.business_radio_button.wait_for(state="visible", timeout=10000)
        confirmation_page.business_radio_button.click()
        page.wait_for_timeout(2000)

        if business_check:
        # If Business radio is checked, fill company name and tax ID
            if confirmation_page.business_radio_button.is_checked():
                framework_logger.info("Business radio button is enabled")

                # Wait for and fill Company Name
                page.locator(confirmation_page.elements.billing_company_input).wait_for(state="visible", timeout=10000)
                page.locator(confirmation_page.elements.billing_company_input).fill(company_name)

                # Wait for and fill Tax ID
                page.locator(confirmation_page.elements.tax_id_input).wait_for(state="visible", timeout=10000)
                page.locator(confirmation_page.elements.tax_id_input).fill(tax_id)

                # Wait for and click Continue button
                page.locator(confirmation_page.elements.billing_continue_button).wait_for(state="visible", timeout=10000)
                page.locator(confirmation_page.elements.billing_continue_button).click()

                # Wait for Billing Step Two
                expect(page.locator(confirmation_page.elements.billing_step_two)).to_be_visible(timeout=60000)
                # then click Back
                page.locator(confirmation_page.elements.back_button).wait_for(state="visible", timeout=10000)
                page.locator(confirmation_page.elements.back_button).click()

                # Validate that Company Name and Tax ID persist
                assert page.locator(confirmation_page.elements.billing_company_input).input_value() == company_name, \
                f"Company name value mismatch: expected '{company_name}'"
                assert page.locator(confirmation_page.elements.tax_id_input).input_value() == tax_id, \
                f"Tax ID value mismatch: expected '{tax_id}'"
                framework_logger.info("Company name and Tax ID values persisted after navigation.")

        # Wait for consumer radio button to be visible, then click
        confirmation_page.consumer_radio_button.wait_for(state="visible", timeout=10000)
        confirmation_page.consumer_radio_button.click()
        page.wait_for_timeout(2000)

        # billing step 1 screen cancel button clicked
        confirmation_page.cancel_button.click()
        framework_logger.info("billing step 1 screen cancel button clicked")


    @staticmethod
    def validate_billing_step_two_layout_elements(page, layout_check=True):
        # Validate step two billing layout
        confirmation_page = ConfirmationPage(page)
        # Wait for add billing button to be visible
        confirmation_page.add_billing_button.wait_for(state="visible", timeout=50000)
        assert confirmation_page.add_billing_button.is_enabled(), "Add billing button is not enabled"
        confirmation_page.add_billing_button.click()
        # Wait for billing step one in continue button to be visible
        confirmation_page.billing_continue_button.wait_for(state="visible", timeout=60000)
        assert confirmation_page.billing_continue_button.is_enabled(), "Billing continue button is not enabled"
        confirmation_page.billing_continue_button.click()
        confirmation_page.paypal_button.wait_for(timeout=60000)
        if layout_check:
            # Validate 'Step 2 of 2' and 'Complete your payment.' text
            expect(page.locator(confirmation_page.elements.billing_step_two)).to_be_visible(timeout=10000)
            expect(page.locator(confirmation_page.elements.complete_your_payment)).to_be_visible(timeout=10000)
            # Validate that back, cancel, and continue buttons are enabled
            assert page.locator(confirmation_page.elements.back_button).is_enabled(), "Back button should be enabled"
            assert page.locator(confirmation_page.elements.btn_pgs_card_cancel).is_enabled(), "Cancel button should be enabled"
            assert page.locator(confirmation_page.elements.pgs_card_continue).is_enabled(), "Continue button should be enabled"
            framework_logger.info("Billing step two buttons Back, Cancel, and Continue are enabled")
            EnrollmentHelper.validate_billing_step_two_layout(page)
            # Validate that card number input is empty
            card_number_input = page.locator(confirmation_page.elements.card_number)
            assert  card_number_input.input_value() == "", "Card number input should be empty"
            framework_logger.info("Card number input is empty on billing step two")
            confirmation_page.continue_button.click()
            # validate the error message
            expect(page.locator(confirmation_page.elements.enter_cvv_error)).to_be_visible(timeout=10000)
            framework_logger.info("Enter Card CVV error message is visible")
            # click cancel button
            #confirmation_page.cancel_button.click()
            framework_logger.info("Clicked cancel button on billing step two")

        # Wait for the 'Step 2 of 2' X button to be visible, then click
        confirmation_page.close_billing_button.wait_for(state="visible", timeout=10000)
        confirmation_page.close_billing_button.click()
        framework_logger.info("Closed billing modal from step two")

    @staticmethod
    def validate_company_name_and_tax_id_persistence(page, company_name="test", tax_id="51-2144346", business_check=True):
        """
        Validates that the entered Company Name and Tax ID persist correctly after navigating forward
        to Billing Step Two and then returning back to Billing Step One.
        """
        confirmation_page = ConfirmationPage(page)

        # Wait for add billing button to be visible and enabled, then click
        confirmation_page.add_billing_button.wait_for(state="visible", timeout=50000)
        assert confirmation_page.add_billing_button.is_enabled(), "Add billing button is not enabled"
        confirmation_page.add_billing_button.click()

        # Wait for Business radio button to be visible, then click
        confirmation_page.business_radio_button.wait_for(state="visible", timeout=10000)
        confirmation_page.business_radio_button.click()
        page.wait_for_timeout(2000)

        if business_check:
            # If Business radio is checked, fill company name and tax ID
            if confirmation_page.business_radio_button.is_checked():
                framework_logger.info("Business radio button is enabled")

                # Wait for and fill Company Name
                page.locator(confirmation_page.elements.billing_company_input).wait_for(state="visible", timeout=10000)
                page.locator(confirmation_page.elements.billing_company_input).fill(company_name)

                # Wait for and fill Tax ID
                page.locator(confirmation_page.elements.tax_id_input).wait_for(state="visible", timeout=10000)
                page.locator(confirmation_page.elements.tax_id_input).fill(tax_id)

                # Wait for and click Continue button
                page.locator(confirmation_page.elements.billing_continue_button).wait_for(state="visible", timeout=10000)
                page.locator(confirmation_page.elements.billing_continue_button).click()

                # Wait for Billing Step Two
                expect(page.locator(confirmation_page.elements.billing_step_two)).to_be_visible(timeout=60000)

                # then click Back
                page.locator(confirmation_page.elements.back_button).wait_for(state="visible", timeout=10000)
                page.locator(confirmation_page.elements.back_button).click()

                # Validate that Company Name and Tax ID persist
                assert page.locator(confirmation_page.elements.billing_company_input).input_value() == company_name, \
                    f"Company name value mismatch: expected '{company_name}'"
                assert page.locator(confirmation_page.elements.tax_id_input).input_value() == tax_id, \
                    f"Tax ID value mismatch: expected '{tax_id}'"
                framework_logger.info("Company name and Tax ID values persisted after navigation.")

                # Wait for consumer radio button to be visible, then click
                confirmation_page.consumer_radio_button.wait_for(state="visible", timeout=10000)
                confirmation_page.consumer_radio_button.click()
                page.wait_for_timeout(2000)

        # billing step 1 screen cancel button clicked
        confirmation_page.cancel_button.click()
        framework_logger.info("billing step 1 screen cancel button clicked")

    @staticmethod
    def add_paypal_billing(page,  payment_method="paypal", edit_mode=False): # payment_method enables multiple paypal accounts selection
        confirmation_page = ConfirmationPage(page)
        original_page = page
        if not edit_mode:
            confirmation_page.add_billing_button.click()
        else:
            confirmation_page.edit_billing_button.click()
        page.wait_for_timeout(10000)
        confirmation_page.billing_continue_button.click()
        try:
            confirmation_page.paypal_button.wait_for(timeout=60000)
        except Exception as e:
            if confirmation_page.btn_link_payment_method.is_visible():
                with page.context.expect_page() as new_tab_info:
                    page.wait_for_timeout(8000)
                    confirmation_page.btn_link_payment_method.click()
                    framework_logger.info("New paypal flow - clicked link payment method button")
                page = new_tab = new_tab_info.value # page is made as same as new_tab for use outside this conditional scope
                page.wait_for_load_state("domcontentloaded")
                frame = page.frame_locator(confirmation_page.elements.paypal_checkout_button_iframe)
                frame.locator(confirmation_page.elements.paypal_method_btn).wait_for(state="visible", timeout=60000)
            elif confirmation_page.elements.billing_continue_button.is_enabled():
                confirmation_page.billing_continue_button.click()
                confirmation_page.paypal_button.wait_for(timeout=60000)
                framework_logger.info("Old paypal flow - clicked continue button")
            else:
                raise Exception(f"Payment iframe not found: {e}")

        with page.context.expect_page() as new_page_info:
            page.wait_for_timeout(2000)
            if confirmation_page.paypal_button.is_visible():
                confirmation_page.paypal_button.click()
            elif frame.locator(confirmation_page.elements.paypal_method_btn).is_visible(): # new flow
                frame.locator(confirmation_page.elements.paypal_method_btn).click()
                framework_logger.info("New paypal flow - clicked paypal method button inside iframe")
            print("Waiting for PayPal page to open...")

        paypal_page = new_page_info.value
        payment_data = common.get_payment_method_data(payment_method)
        paypal_email = payment_data["email"]
        paypal_password = payment_data["password"]

        EnrollmentHelper._paypal_login_popup(paypal_page, confirmation_page, paypal_email, paypal_password)
        if new_tab:
            new_tab.close()
            framework_logger.info("closed secondary tab for payment method selection")

    @staticmethod
    def add_google_pay_billing(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.add_billing_button.click()
        time.sleep(5)
        confirmation_page.billing_continue_button.click()
        payment_data = common.get_payment_method_data("google_pay")
        gpay_button = page.locator(confirmation_page.elements.google_pay_button)
        gpay_button.wait_for(state="visible", timeout=30000)
        gpay_button.click()
        time.sleep(5)
        iframe_element = page.wait_for_selector(confirmation_page.elements.google_pay_iframe, timeout=15000)
        gpay_frame = iframe_element.content_frame()
        if not gpay_frame:
            raise Exception("Could not switch to Google Pay iframe.")
        payment_data = common.get_payment_method_data("google_pay")
        gpay_email = payment_data["email"]
        gpay_password = payment_data["password"]
        login_page = gpay_frame
        login_page.wait_for_selector(confirmation_page.elements.google_pay_email_input, state="visible", timeout=20000)
        login_page.fill(confirmation_page.elements.google_pay_email_input, gpay_email)
        login_page.click(confirmation_page.elements.google_pay_email_next)
        login_page.wait_for_selector(confirmation_page.elements.google_pay_password_input, state="visible",
                                     timeout=20000)
        login_page.fill(confirmation_page.elements.google_pay_password_input, gpay_password)
        login_page.click(confirmation_page.elements.google_pay_password_next)
        gpay_frame.wait_for_selector(confirmation_page.elements.google_pay_pay_button, state="visible", timeout=20000)
        gpay_frame.click(confirmation_page.elements.google_pay_pay_button)

    @staticmethod
    def add_prepaid_by_value(page, plan_value, amount_greater: bool = True):
        if plan_value is None:
            raise ValueError("plan_value is None, it must be provided for prepaid_only payment method")
        if amount_greater:
            prepaid = common.get_offer(GlobalState.country_code, "prepaid", amount_greater=plan_value)
        else:
            prepaid = common.get_offer(GlobalState.country_code, "prepaid", amount_less=plan_value)
        identifier = prepaid.get("identifier")
        if not identifier:
            raise ValueError(f"No identifier found for region: {GlobalState.country_code}")
        prepaid_code = common.offer_request(identifier)

        prepaid_value = int(prepaid.get("amountCents")) / 100
        EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, prepaid_value)

    @staticmethod
    def apply_promotion_code(page, code: str):
        confirmation_page = ConfirmationPage(page)
        page.wait_for_selector(confirmation_page.elements.enter_promo_or_pin_code_button)
        confirmation_page.enter_promo_or_pin_code_button.click()
        confirmation_page.promotion_code_input.fill(code)
        confirmation_page.promotion_apply_button.click()

    @staticmethod
    def special_offer_benefits(page, promo_code, callback=None):
        try:
            confirmation_page = ConfirmationPage(page)
            confirmation_page.enter_promo_or_pin_code_button.click(timeout=100000)
            confirmation_page.promo_text.wait_for(state="visible", timeout=100000)
            confirmation_page.special_offer_text.wait_for(state="visible", timeout=100000)
            confirmation_page.whats_this.hover()
            whats_this = confirmation_page.whats_this_tooltip.text_content()
            if whats_this.replace('\u00A0', ' ') == "Please redeem the promo or PIN code you have available on your flyer, HP Instant Ink prepaid card, or email.":
                framework_logger.info("What's this message validated successfully")
            else:
                framework_logger.info(whats_this)
                framework_logger.error("What's this message validation failed")
            apply_status = confirmation_page.apply_button.is_enabled()
            framework_logger.info(f"Apply button status before promo applied: {apply_status}")
            confirmation_page.special_offer_text.click(timeout=100000)
            confirmation_page.promotion_code_input.fill(promo_code)
            confirmation_page.promotion_apply_button.click(timeout=100000)
            confirmation_page.special_offer_applied_text.wait_for(state="visible", timeout=100000)

            if promo_code == "vb5tyb":
                confirmation_page.refer_a_friend_text.wait_for(state="visible", timeout=100000)
                confirmation_page.one_month.wait_for(state="visible", timeout=100000)

            if callback: callback("special_offer_applied1", page, screenshot_only=True)
            page.locator("[data-testid='special-offers-modal']").locator("[aria-label='Close modal']").click()

            if promo_code == "vb5tyb":
                promo_details = confirmation_page.summary_benefits_header.text_content()
                if promo_details == "1 Redeemed month + credits":
                    framework_logger.info("Promo code applied successfully.")
                else:
                    framework_logger.error("Promo code applied failed.")
            if callback: callback("special_offer_applied2", page, screenshot_only=True)
        except Exception as e:
            framework_logger.error(f"ERROR: special offer benefits {e}")
            if callback: callback("error_special_offer_benefits", page, screenshot_only=True)

    @staticmethod
    def validate_promotion(page, element_selector: str, expected_value: int, timeout: int = 30):
        start_time = time.time()
        last_actual_value = None
        last_value_text = None

        while time.time() - start_time < timeout:
            try:
                value_text = page.wait_for_selector(element_selector).inner_text().strip()
                numbers = common.extract_numbers_from_text(value_text)
                if numbers:
                    # Convert string to float, then to int for comparison
                    actual_value = int(float(numbers[0]))
                else:
                    actual_value = None

                if actual_value == expected_value:
                    return  # Success - assertion passed

                last_actual_value = actual_value
                last_value_text = value_text
                time.sleep(1)  # Wait 1 second before retrying

            except Exception as e:
                # Continue trying if element is not found or other errors
                time.sleep(1)
                continue

        # If we reach here, timeout was exceeded
        assert False, \
            f"Promotion validation failed after {timeout}s timeout: expected '{expected_value}', but got '{last_actual_value}' from text '{last_value_text}'"

    @staticmethod
    def apply_and_validate_prepaid_code(page, code: str, value: int = 1, billing_message=False):
        EnrollmentHelper.apply_promotion_code(page, code)
        confirmation_page = ConfirmationPage(page)
        EnrollmentHelper.validate_promotion(page, confirmation_page.elements.prepaid_value, value)

        if billing_message:
            expect(confirmation_page.require_billing_message).to_be_visible(timeout=60000)
        try:
            expect(confirmation_page.require_billing_message).to_be_visible(timeout=60000)
            framework_logger.info("Billing information is required message is displayed")    
        except Exception:
            pass
            framework_logger.info("Billing information is required message is not displayed")    

        confirmation_page.close_modal_button.click()

    @staticmethod
    def apply_and_validate_ek_code(page, code: str, months: int = 1):
        EnrollmentHelper.apply_promotion_code(page, code)
        confirmation_page = ConfirmationPage(page)
        EnrollmentHelper.validate_promotion(page, confirmation_page.elements.ek_months, months)
        confirmation_page.close_modal_button.click()

    @staticmethod
    def apply_and_validate_raf_code(page, code: str, months: int = 3):
        EnrollmentHelper.apply_promotion_code(page, code)
        confirmation_page = ConfirmationPage(page)
        EnrollmentHelper.validate_promotion(page, confirmation_page.elements.raf_months, months)
        confirmation_page.close_modal_button.click()

    @staticmethod
    def apply_and_validate_promo_code(page, code: str, months: int = 1):
        EnrollmentHelper.apply_promotion_code(page, code)
        confirmation_page = ConfirmationPage(page)
        EnrollmentHelper.validate_promotion(page, confirmation_page.elements.promo_code_months, months)
        confirmation_page.close_modal_button.click()

    @staticmethod
    def verify_raf_months_and_total_benefits(page, raf_months: int = 1, total_benefits: int = 4):
        confirmation_page = ConfirmationPage(page)
        page.wait_for_selector(confirmation_page.elements.enter_promo_or_pin_code_button)
        confirmation_page.enter_promo_or_pin_code_button.click()
        EnrollmentHelper.validate_promotion(page, confirmation_page.elements.raf_months, raf_months)
        confirmation_page.close_modal_button.click()
        EnrollmentHelper.validate_promotion(page, confirmation_page.elements.summary_benefits_header, total_benefits)

    @staticmethod
    def validate_benefits_header(page, benefits_header_number: int):
        actual_months = EnrollmentHelper.get_redeemed_months_and_credits(page)
        assert actual_months == benefits_header_number, \
            f"Benefits header validation failed: expected '{benefits_header_number}', but got '{actual_months}'"

    @staticmethod
    def validate_special_offer_benefits(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        page.wait_for_selector(confirmation_page.elements.enter_promo_or_pin_code_button)
        confirmation_page.enter_promo_or_pin_code_button.click()
        framework_logger.info("Clicked promo or pin code section")
        assert confirmation_page.special_offer_box.is_visible(), "Special offer box is not visible"
        assert confirmation_page.break_down_credits.is_visible(), "Breakdown of credits is not visible"
        # Validate Apply button is present and disabled
        expect(confirmation_page.promotion_apply_button).to_be_disabled()
        framework_logger.info("Apply button is present and disabled as expected")

        # Validate 'What’s this?' text color
        whats_this = confirmation_page.tooltip_link
        color = whats_this.evaluate("el => window.getComputedStyle(el).color")
        framework_logger.info(f"'What's this?' text color: {color}")

        # Optional strict color validation
        if "0, 115, 168" in color or "blue" in color.lower():
            framework_logger.info("'Whats this?' text is blue")
        else:
            framework_logger.info("'Whats this?' text is not exactly blue")

        # Hover over 'What’s this?' to display tooltip and validate content
        whats_this.hover()
        page.wait_for_selector(confirmation_page.elements.tooltip_content, timeout=5000)
        expect(confirmation_page.tooltip_content).to_be_visible()

        if callback: callback("SpecialOfferBenefits Modal", page, screenshot_only=True)

        tooltip_text = confirmation_page.tooltip_content.inner_text()
        expected_text = "Please redeem the promo or PIN code you have available on your flyer, HP Instant Ink prepaid card, or email."
        # Normalize whitespace in both strings before comparison
        tooltip_text = " ".join(tooltip_text.split())
        expected_text = " ".join(expected_text.split())
        assert expected_text in tooltip_text, f"Expected tooltip text '{expected_text}' but found '{tooltip_text}'"
        confirmation_page.close_modal_button.click()

    @staticmethod
    def validate_breakdown_credits_section(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        page.wait_for_selector(confirmation_page.elements.enter_promo_or_pin_code_button)
        confirmation_page.enter_promo_or_pin_code_button.click()
        framework_logger.info("Clicked promo or pin code section")
        assert confirmation_page.raf_months.is_visible(), "RAF months section is not visible"
        assert confirmation_page.ek_months.is_visible(), "EK months section is not visible"
        assert confirmation_page.promo_code_months.is_visible(), "Promo code months section is not visible"
        #assert confirmation_page.prepaid_value.is_visible(), "Prepaid value section is not visible"
        #assert confirmation_page.free_trial_months.is_visible(), "Free trial months section is not visible"
        if callback: callback("BreakdownCredits Section", page, screenshot_only=True)
        confirmation_page.close_modal_button.click()

    @staticmethod
    def validate_order_summary_section(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        page.wait_for_selector(confirmation_page.elements.plan_details)
        assert confirmation_page.plan_details.is_visible(), "Plan details are not visible in order summary"
        assert confirmation_page.due_now.is_visible(), "Total due now is not visible in order summary"
        assert confirmation_page.due_after.is_visible(), "Total due after trial is not visible in order summary"

        if callback: callback("OrderSummary Section", page, screenshot_only=True)

        # Validate inner_text of elements
        plan_details_text = confirmation_page.plan_details.inner_text().strip()
        due_now_text = confirmation_page.due_now.inner_text().strip()
        due_after_text = confirmation_page.due_after.inner_text().strip()

        # Log the retrieved text for debugging
        framework_logger.info(f"Plan Details: {plan_details_text}")
        framework_logger.info(f"Due Now: {due_now_text}")
        framework_logger.info(f"Due After Trial: {due_after_text}")

        # Expected patterns for validation
        expected_due_now = "Total due now\n\n$0.00"
        expected_due_after = "Total due after trial\n\n$7.99/month + tax"

        # Validate plan details with flexible date matching
        plan_pattern = r"Ink Plan\n\n\$7\.99/month \+ tax\n\n5 month trial ends \d{2}/\d{2}/\d{4}"
        assert re.match(plan_pattern, plan_details_text), f"Plan details pattern mismatch: got '{plan_details_text}'"

        # Validate due amounts exactly
        assert due_now_text == expected_due_now, f"Due now mismatch: expected '{expected_due_now}', got '{due_now_text}'"
        assert due_after_text == expected_due_after, f"Due after trial mismatch: expected '{expected_due_after}', got '{due_after_text}'"

        # Extract and validate the trial end date format
        date_match = re.search(r'5 month trial ends (\d{2}/\d{2}/\d{4})', plan_details_text)
        if date_match:
            trial_end_date = date_match.group(1)
            framework_logger.info(f"Trial end date: {trial_end_date}")
        else:
            framework_logger.warning("Could not extract trial end date from plan details")

    @staticmethod
    def validate_enroll_button_on_automatic_renewal_notice_modal(page, callback=None):
        try:
            confirmation_page = ConfirmationPage(page)
            thank_you_page = ThankYouPage(page)

            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            confirmation_page.automatic_renewal_notice.wait_for(state="visible", timeout=60000)
            framework_logger.info("Automatic renewal notice modal is displayed")
            if callback: callback("AutomaticRenewalNoticeModal", page, screenshot_only=True)

            # click agreement checkbox
            is_checked = confirmation_page.terms_agreement_checkbox.is_checked()
            if not is_checked:
                confirmation_page.terms_agreement_checkbox.click()
                framework_logger.info("Checked the terms agreement checkbox")
            else:
                framework_logger.info("Terms agreement checkbox was already checked")

            # Validate enroll button is enabled after checking terms
            confirmation_page.enroll_button.wait_for(state="visible", timeout=60000)
            assert confirmation_page.enroll_button.is_enabled(), "Enroll button should be enabled after terms agreement is checked"
            framework_logger.info("Enroll button is enabled after terms agreement is checked")
            if callback: callback("Enroll_Button", page, screenshot_only=True)

            # click enroll button
            confirmation_page.enroll_button.click()
            framework_logger.info("Clicked on Enroll button")

            thank_you_page.thank_you_card.wait_for(state="visible", timeout=60000)
            assert thank_you_page.thank_you_card.is_visible(), "Enrollment success message is not displayed"
            framework_logger.info("Enrollment success message is displayed")
            if callback: callback("EnrollmentSuccessMessage", page, screenshot_only=True)

        except Exception as e:
            framework_logger.warning(f"Automatic renewal modal enroll button validation failed: {e}")

    @staticmethod
    def get_redeemed_months_and_credits(page):
        confirmation_page = ConfirmationPage(page)
        benefits = confirmation_page.summary_benefits_header.inner_text().strip()
        numbers = common.extract_numbers_from_text(benefits)
        actual_months = int(numbers[0]) if numbers else None

        if actual_months is None:
            raise ValueError(f"No numbers found in benefits text: '{benefits}'")

        return actual_months

    @staticmethod
    def validate_months_trial_billing_card(page, benefits_header_number: int):
        actual_months = EnrollmentHelper.get_months_trial_applied(page)
        assert actual_months == benefits_header_number, \
            f"Benefits header validation failed: expected '{benefits_header_number}', but got '{actual_months}'"

    @staticmethod
    def get_months_trial_applied(page):
        confirmation_page = ConfirmationPage(page)
        benefits = confirmation_page.billing_card.inner_text().strip()
        numbers = common.extract_numbers_from_text(benefits)
        actual_months = int(numbers[0]) if numbers else None

        if actual_months is None:
            raise ValueError(f"No numbers found in benefits text: '{benefits}'")

        return actual_months

    @staticmethod
    def skip_paper_offer(page):
        confirmation_page = ConfirmationPage(page)
        try:
            confirmation_page.skip_paper_offer.click()
        except Exception as e:
            print(f"Skip paper offer button not found or could not be clicked: {e}")

    @staticmethod
    def connect_printer(page):
        connect_page = ConfirmationPage(page)
        page.wait_for_selector(connect_page.elements.preenroll_continue_button, state="visible", timeout=9000)
        connect_page.preenroll_continue_button.click()
        page.wait_for_load_state("load")
        page.wait_for_selector(connect_page.elements.connect_later_button, timeout=30000)
        connect_page.connect_later_button.click()
        page.wait_for_selector(connect_page.elements.go_back_button, timeout=30000)
        connect_page.go_back_button.click()

    @staticmethod
    def validate_automatic_renewal_notice_modal(page, expected_phone="1-855-785-2777", callback=None):
        try:
            confirmation_page = ConfirmationPage(page)
            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            confirmation_page.automatic_renewal_notice.wait_for(state="visible", timeout=60000)
            framework_logger.info("Automatic renewal notice modal is displayed")
            if callback: callback("AutomaticRenewalNoticeModal", page, screenshot_only=True)
            # Scroll down the page
            page.mouse.wheel(0, 600)
            # Scroll up the page
            page.mouse.wheel(0, -600)
            framework_logger.info("Scrolled down and up the page")

            #Checking the AFU section available on page
            confirmation_page.auto_firmware_update_info.wait_for(state="visible", timeout=60000)
            framework_logger.info("AFU section is displayed")

            #Verify disclaimer content
            confirmation_page.disclaimer.wait_for(state="visible", timeout=60000)
            framework_logger.info("disclaimer content is displayed")
            if callback: callback("disclaimer", page, screenshot_only=True)

            # Validate terms agreement checkbox is not pre-checked
            is_checked = confirmation_page.terms_agreement_checkbox.is_checked()
            assert not is_checked, "Checkbox should not be pre-checked"

            # Validate enroll button is disabled before checking terms
            confirmation_page.enroll_button.wait_for(state="visible", timeout=60000)
            assert confirmation_page.enroll_button.is_disabled(), "Enroll button should be disabled before terms agreement is checked"
            framework_logger.info("Enroll button is disabled before terms agreement is checked")
            if callback: callback("Enroll_Button", page, screenshot_only=True)

            #Verify Terms of service link and HERE link are displayed well
            confirmation_page.tos_link.wait_for(state="visible", timeout=60000)
            if callback: callback("TOS_Link", page, screenshot_only=True)

            confirmation_page.here_link.wait_for(state="visible", timeout=60000)
            if callback: callback("HERE_Link", page, screenshot_only=True)

            # Validate support phone number using regular expression
            confirmation_page.support_description_arn_component.wait_for(state="visible", timeout=60000)
            support_text = confirmation_page.support_description_arn_component.inner_text()

            # Regular expression to match phone number pattern (1-XXX-XXX-XXXX)
            phone_pattern = r'1-\d{3}-\d{3}-\d{4}'
            phone_match = re.search(phone_pattern, support_text)

            if phone_match:
                found_phone = phone_match.group()
                framework_logger.info(f"Support phone number found: {found_phone}")
                assert found_phone == expected_phone, f"Expected phone '{expected_phone}', but found '{found_phone}'"
                framework_logger.info("Support phone number validation passed")
            else:
                framework_logger.error(f"No phone number found in support text: {support_text}")
                raise AssertionError("Support phone number not found in expected format")

            if callback: callback("Support_Phone_Number", page, screenshot_only=True)

            # Click on 'x' button
            confirmation_page.arn_close_modal.click()
            framework_logger.info("Clicked on 'X' button")

        except Exception as e:
            framework_logger.warning(f"Automatic renewal modal validation failed: {e}")

    @staticmethod
    def validate_arn_modal_close(page, callback=None):
        try:
            confirmation_page = ConfirmationPage(page)
            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            confirmation_page.automatic_renewal_notice.wait_for(state="visible", timeout=60000)
            framework_logger.info("Automatic renewal notice modal is displayed")
            if callback: callback("AutomaticRenewalNoticeModal", page, screenshot_only=True)

            # Click on 'x' button
            time.sleep(6)
            assert confirmation_page.arn_close_modal.is_visible(), "'X' button is not visible on ARN modal"
            confirmation_page.arn_close_modal.click()
            framework_logger.info("Clicked on 'X' button")
            if callback: callback("ARN_Close_X_Button", page, screenshot_only=True)

            # Validate returned to confirmation page
            confirmation_page.continue_enrollment_button.wait_for(state="visible", timeout=60000)
            assert confirmation_page.continue_enrollment_button.is_visible(), "Did not return to confirmation page after closing ARN modal"
            framework_logger.info("Returned to confirmation page successfully after closing ARN modal")
            if callback: callback("Returned_Confirmation_Page", page, screenshot_only=True)

            # Reopen ARN modal to test enroll button status
            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            confirmation_page.automatic_renewal_notice.wait_for(state="visible", timeout=60000)
            framework_logger.info("Reopened Automatic renewal notice modal")
            if callback: callback("ReopenedAutomaticRenewalNoticeModalEnroll", page, screenshot_only=True)

            # check the TOS checkbox and verify the enroll button enabled
            confirmation_page.terms_agreement_checkbox.check(force=True)
            assert confirmation_page.enroll_button.is_enabled(), "Enroll button should be enabled after checking terms agreement checkbox"
            framework_logger.info("Enroll button is enabled after checking terms agreement checkbox")
            if callback: callback("Enroll_Button_Checked", page, screenshot_only=True)

            # close the arn modal by clicking on 'X' button
            confirmation_page.arn_close_modal.click()
            framework_logger.info("Clicked on 'X' button to close ARN modal")
            confirmation_page.continue_enrollment_button.wait_for(state="visible", timeout=60000)
            assert confirmation_page.continue_enrollment_button.is_visible(), "Did not return to confirmation page after closing ARN modal"
            framework_logger.info("Returned to confirmation page successfully after closing ARN modal")

            # Reopen ARN modal to test check box remains checked and enroll button enabled
            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            confirmation_page.automatic_renewal_notice.wait_for(state="visible", timeout=60000)
            framework_logger.info("Reopened Automatic renewal notice modal")
            if callback: callback("ReopenedAutomaticRenewalNoticeModal", page, screenshot_only=True)
            assert confirmation_page.terms_agreement_checkbox.is_checked(), "Terms agreement checkbox should remain checked after reopening ARN modal"
            assert confirmation_page.enroll_button.is_enabled(), "Enroll button should remain enabled after reopening ARN modal"
            framework_logger.info("Terms agreement checkbox remains checked and Enroll button remains enabled after reopening ARN modal")
            if callback: callback("Enroll_Button_Rechecked", page, screenshot_only=True)
            # close the arn modal by clicking on 'X' button
            confirmation_page.arn_close_modal.click()

        except Exception as e:
            framework_logger.warning(f"ARN modal close validation failed: {e}")

    @staticmethod
    def validate_links_on_automatic_renewal_notice_modal(page, expected_phone="1-855-785-2777", callback=None):
        try: 
            confirmation_page = ConfirmationPage(page)
            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            confirmation_page.automatic_renewal_notice.wait_for(state="visible", timeout=60000)
            framework_logger.info("Automatic renewal notice modal is displayed")
            if callback: callback("AutomaticRenewalNoticeModal", page, screenshot_only=True)

            #Verify Terms of service link opened on same webpage
            tos = confirmation_page.tos_link
            tos.wait_for(state="visible", timeout=60000)
            target = tos.get_attribute("target")
            framework_logger.info(f"TOS link target attribute: {target}")
            try:
                if target != "_blank":
                    framework_logger.info("Link will open in the same page.")
                else:
                    framework_logger.info("Link will open in a new tab/window.")
            except:
                framework_logger.info("No target attribute found; link will open in the same page.")
            tos.scroll_into_view_if_needed()
            tos.click()
            page.wait_for_load_state("load", timeout=60000)
            framework_logger.info("Clicked on TOS link")
            if callback: callback("TOS_Link", page, screenshot_only=True)

            #validate Back button available on TOS page
            confirmation_page.back_button_arn.wait_for(state="visible", timeout=60000)
            assert confirmation_page.back_button_arn.is_visible(), "Back button is not visible in arn modal"
            confirmation_page.back_button_arn.click()
            page.wait_for_load_state("load", timeout=60000)

            framework_logger.info("Clicked on Back button and navigated to order summary page")
            confirmation_page.continue_enrollment_button.wait_for(state="visible", timeout=60000)
            assert confirmation_page.continue_enrollment_button.is_visible(), "Continue enrollment button is not visible after navigating back from TOS page"
            framework_logger.info("Navigated back to order summary page successfully")

            #click on continue button to go back to ARN modal
            confirmation_page.continue_enrollment_button.click()

            try:
                confirmation_page.here_link.wait_for(state="visible", timeout=60000)
                assert confirmation_page.here_link.is_visible(), "HERE link is not visible"
                with page.expect_popup() as new_page_info:
                    confirmation_page.here_link.click()
                    framework_logger.info("Clicked on HERE link")
                    new_tab = new_page_info.value
                    framework_logger.info(f"printing new tab url: {new_tab.url()}")
                new_tab.wait_for_load_state(timeout=120000)
                framework_logger.info("Switched to new tab after Enroll Now")
                
                # Check if username field is present on the page (indicates login page loaded correctly)
                username_field = new_tab.locator("#username")
                username_field.wait_for(state="visible", timeout=120000)
                assert username_field.is_visible(), "Username field not found - page may not have loaded correctly"
            except:
                framework_logger.error("HERE link did not open the expected page.")
                new_tab.close()
            framework_logger.info("Closed the new tab")
            # confirmation_page.here_link.click()
            # framework_logger.info("Clicked on HERE link")
            if callback: callback("HERE_Link", page, screenshot_only=True)
            confirmation_page.arn_close_modal.click()
            framework_logger.info("Clicked on 'X' button")

        except Exception as e:
            framework_logger.warning(f"Automatic renewal modal validation failed: {e}")

    @staticmethod
    def finish_enrollment(page):
        confirmation_page = ConfirmationPage(page)
        thank_you_page = ThankYouPage(page)
        try :
            confirmation_page.wait.continue_enrollment_button(state="visible", timeout=15000)
            confirmation_page.wait.continue_enrollment_button().click(timeout=15000)
            confirmation_page.Tos_link_ARN.wait_for(state="visible", timeout=15000)
            with page.expect_popup() as popup_info:
                confirmation_page.Tos_link_ARN.click()
                framework_logger.info("Clicked on TOS link")
                new_tab = popup_info.value
                
            new_tab.wait_for_load_state()
            framework_logger.info("Switched to new tab after clicking TOS link")
            assert not new_tab.text_content("Something went wrong. We apologize for the inconvenience.", timeout=10000), "Error page displayed in new tab"
            new_tab.close()
            framework_logger.info("Closed the new tab")
        except Exception:
            pass
               
        confirmation_page.terms_agreement_checkbox.wait_for(state="visible", timeout=60000)
        confirmation_page.terms_agreement_checkbox.check(force=True)
        confirmation_page.enroll_button.click()
        thank_you_page.continue_button.wait_for(state="visible", timeout=60000)
        thank_you_page.continue_button.click()

    @staticmethod
    def finish_enrollment_with_prepaid(page):
        confirmation_page = ConfirmationPage(page)
        thank_you_page = ThankYouPage(page)
        confirmation_page.continue_enrollment_button.wait_for(state="visible", timeout=120000)
        confirmation_page.continue_enrollment_button.click()
        confirmation_page.terms_agreement_checkbox.wait_for(state="visible", timeout=60000)
        confirmation_page.terms_agreement_checkbox.check(force=True)
        confirmation_page.prepaid_terms_agreement_checkbox.check(force=True)
        confirmation_page.enroll_button.click()
        thank_you_page.thank_you_card.wait_for(state="visible", timeout=60000)
        thank_you_page.continue_button.click()
        return page.url

    @staticmethod
    def validate_total_due_after_trial(page, value):
        confirmation_page = ConfirmationPage(page)
        text = confirmation_page.total_due_after_trial.text_content(timeout=60000)
        assert value in text, f"Expected '{value}' in '{text}'"

    @staticmethod
    def validate_thank_you_page_for_moobe(page, additional_check: bool = False, continue_flow: bool = False, callback=None):
        thank_you_page = ThankYouPage(page)

        expect(thank_you_page.thank_you_card).to_be_visible(timeout=60000)
        expect(thank_you_page.continue_button).to_be_visible()
        if additional_check:
            # Check if "You're signed up" text is present (manual check to handle encoding issues)
            card_text = thank_you_page.subtitle.inner_text()
            framework_logger.info(f"Thank You card text: {type(card_text)}")
            assert "You’re signed up." in card_text, f"Expected 'You’re signed up.' in thank you card text, but got: {card_text}"
            expect(thank_you_page.cartridge_image).to_be_visible()
            expect(thank_you_page.email).to_be_visible()
            email_text = thank_you_page.email.inner_text().strip()
            framework_logger.info(f"Email displayed on Thank You page: {email_text}")
            # Check that Back button is not visible by verifying it doesn't exist or is hidden
            back_button_locator = page.locator("text=Back")
            expect(back_button_locator).not_to_be_visible()
            if callback: callback("ThankYouPage_MOOBE", page, screenshot_only=True)

        if continue_flow:
            thank_you_page.continue_button.click()
            if callback: callback("ThankYouPage_Continue_MOOBE", page, screenshot_only=True)
        return page.url

    @staticmethod
    def validate_thank_you_page(page, continue_flow: bool = False):
        thank_you_page = ThankYouPage(page)
        terms_of_service = TermsOfServiceHPSmartPage(page)
        overview_page = OverviewPage(page)

        expect(thank_you_page.thank_you_card).to_be_visible(timeout=60000)
        expect(thank_you_page.continue_button).to_be_visible()
        if continue_flow:
            thank_you_page.continue_button.click()
            terms_of_service.continue_button.wait_for(state="visible", timeout=60000)
            terms_of_service.continue_button.click()
            overview_page.page_title.wait_for(state="visible", timeout=120000)

    @staticmethod
    def get_total_price_by_plan_card(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.wait.plan_value()
        text = confirmation_page.plan_value.inner_text()
        numbers = common.extract_numbers_from_text(text)

        price = float(numbers[0])
        return int(price * 100)

    @staticmethod
    def printer_card_validation(page, printers):
        printer_selection = PrinterSelectionPage(page)
        for index, printer in enumerate(printers):
            assert printer_selection.printer_image.nth(index).is_visible(), f"Printer image {index} is not visible"

            printer_serial_text = printer_selection.printer_serial.nth(index).inner_text()
            assert printer.entity_id in printer_serial_text, f"Expected printer serial to contain {printer.entity_id}, but found {printer_serial_text}"

            assert printer_selection.printer_benefits.nth(
                index).is_visible(), f"Printer benefits {index} are not visible"

            printer_benefits_text = printer_selection.printer_benefits.nth(index).inner_text()
            printer_benefits = common.extract_numbers_from_text(printer_benefits_text)
            assert len(printer_benefits) > 0, f"No printer benefits found for printer {index}"

    @staticmethod
    def add_card_validation(page):
        printer_selection = PrinterSelectionPage(page)
        assert printer_selection.add_printer.is_visible(), "Add printer button is not visible"
        assert printer_selection.add_printer_image.is_visible(), "Add printer image is not visible"
        assert printer_selection.add_printer_title.is_visible(), "Add printer title is not visible"
        assert printer_selection.add_printer_body.is_visible(), "Add printer body is not visible"
        assert printer_selection.add_printer_check.is_visible(), "Add printer check is not visible"

    @staticmethod
    def verify_waiver_pages_on_disclaimer_modal(page, pages_waiver: str):
        confirmation_page = ConfirmationPage(page)
        expect(confirmation_page.checkout_enroll_summary).to_be_visible(timeout=30000)
        pages_waiver_text = confirmation_page.checkout_enroll_summary.inner_text()
        assert pages_waiver in pages_waiver_text, \
            f"Expected waiver pages text '{pages_waiver}' not found in '{pages_waiver_text}'"

    @staticmethod
    def fill_shipping(page, index=0, company_name=None):
        confirmation_page = ConfirmationPage(page)
        address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
        state_name = address.get("fullState", address.get(f"fullState_{GlobalState.language_code}"))
        if company_name:
            confirmation_page.company_name_input.fill(company_name)
        confirmation_page.street1_input.fill(address.get("street1", ""))
        confirmation_page.street2_input.fill(address.get("street2", ""))
        countries_without_city_mandate = ["Hong Kong", "Singapore"]
        if GlobalState.country not in countries_without_city_mandate:
            confirmation_page.city_input.fill(address.get("city", ""))
        countries_without_states_mandate = common.countries_without_states_mandate()
        if GlobalState.country not in countries_without_states_mandate and state_name:
            confirmation_page.state_dropdown.click()
            element_id = confirmation_page.state_dropdown.get_attribute("id")
            select_list_option = f"#{element_id}-listbox li"
            select_state = page.locator(f"{select_list_option}:has-text('{state_name}')")
            select_state.wait_for(state="visible", timeout=2000)
            select_state.click()
        countries_without_zip_mandate = ["Hong Kong"]
        if GlobalState.country not in countries_without_zip_mandate:
            confirmation_page.zip_code_input.fill(address.get("zipCode", ""))
        confirmation_page.phone_number_input.fill(address.get("phoneNumber1", ""))

    @staticmethod
    def selectable_plan_info(page):
        confirmation_page = ConfirmationPage(page)
        try:
            confirmation_page.current_monthly_plan.wait_for(state="visible", timeout=30000)
            monthly_plan = confirmation_page.current_monthly_plan.text_content()
            monthly_charges = confirmation_page.current_monthly_charges.text_content()
            print(f"Monthly plan: {monthly_plan}, Monthly charges: {monthly_charges}")
            return monthly_plan, monthly_charges

        except Exception as e:
            raise Exception(f"Monthly plan details not found or could not be extracted: {e}")

    @staticmethod
    def selectable_plan_info_oobe(page, page_index="2"):
        confirmation_page = ConfirmationPage(page)
        current_monthly_name = f"[data-testid='plans-selector-plan-card-{page_index}-plan-name-title']"
        current_monthly_pages = f"[data-testid='plans-selector-plan-card-{page_index}-pages-container']"
        current_monthly_charges = f"[data-testid='plans-selector-plan-card-{page_index}-price-title']"
        plan_value = ["10", "50", "100", "300", "700"]
        try:
            confirmation_page.edit_plan_button.wait_for(state="visible", timeout=20000)
            confirmation_page.edit_plan_button.click()
            page.wait_for_timeout(8000)
            monthly_plan_name = page.locator(current_monthly_name).text_content().upper() + " INK PLAN"
            monthly_plan_pages = page.locator(current_monthly_pages).text_content()
            monthly_plan_charges = (page.locator(current_monthly_charges).text_content()).lstrip('$£€')
            framework_logger.info(f"monthly_plan_name: {monthly_plan_name}, monthly_plan_pages: {monthly_plan_pages}, monthly_plan_charges: {monthly_plan_charges}")
            if confirmation_page.ink_cartridges_tab.is_visible(timeout=3000):
                confirmation_page.ink_cartridges_tab.click()
            confirmation_page.select_ink_plan(plan_value[int(page_index)])
            confirmation_page.select_plan_button.click()
            return monthly_plan_name, monthly_plan_pages.replace('p',' p'), monthly_plan_charges

        except Exception as e:
            raise Exception(f"Monthly plan details not found or could not be extracted: {e}")

    @staticmethod
    def selected_plan_info(page, onboarded=True, plan_type="ink_only"): # can pass plan_type as ink_only or ink_paper
        confirmation_page = ConfirmationPage(page)
        try:
            plan_details = confirmation_page.review_plan_card_description.text_content().split('/')
            framework_logger.info(f"Selected plan details: {plan_details}")
            string = plan_details[0]
            match = re.match(r'([A-Z ]+)(\d+ pages)', string)
            if match:
                monthly_review_plan = match.group(1).strip()
                monthly_pages = match.group(2).strip()
            else:
                monthly_review_plan = None
                monthly_pages = None
            monthly_review_pages = f"{monthly_pages}/{plan_details[2].lstrip(' ')}"
            monthly_review_charges = plan_details[1][6:].rstrip(' ')
            print(f"Review page plan info: {monthly_review_plan}, {monthly_review_pages}, Monthly charges: {monthly_review_charges}")
            if onboarded and (plan_type == "ink_paper"):
                assert page.locator(confirmation_page.review_trial_period).count() > 0, "Trial month end date text not found on review page"
            return monthly_review_plan, monthly_review_pages, monthly_review_charges

        except Exception as e:
            raise Exception(f"Monthly plan details not found or could not be extracted: {e}")

    @staticmethod
    def selected_plan_edit_validate(page, page_value="100", callback=None):
        confirmation_page = ConfirmationPage(page)
        plan_index = {"10": "0", "50": "1", "100": "2", "300": "3", "700": "4"}
        plan_card = f'[data-testid="plans-selector-desktop-plan-card-{plan_index[page_value]}"]'
        try:
            confirmation_page.edit_plan_button.wait_for(state="visible", timeout=20000)
            confirmation_page.edit_plan_button.click()
            if confirmation_page.monthly_plan_title.is_visible(timeout=8000): # For Chrome browser
                assert confirmation_page.current_plan_text.is_visible(), "Current plan text not visible after clicking edit"
                assert confirmation_page.plan_selection_box.is_visible(), "Plan selection box not visible after clicking edit"
                assert confirmation_page.ink_plan_card.is_visible(), "Ink plan card not visible after clicking edit"
                assert confirmation_page.ink_selection_button.is_visible(), "Ink plan selection button not visible after clicking edit"
                assert confirmation_page.ink_paper_plan_card.is_visible(), "Ink & Paper plan card not visible after clicking edit"
                assert confirmation_page.ink_paper_selection_button.is_visible(), "Ink & Paper plan selection button not visible after clicking edit"

            elif confirmation_page.monthly_plan_oobe_title.is_visible(timeout=8000): # For windows_app (OOBE)
                assert confirmation_page.plan_modal_subtitle.is_visible(), "Plan modal subtitle not visible in plan modal"
                assert page.locator(plan_card).is_visible(), "Plan card of current plan is not visible in plan modal"
                assert page.locator(f'div{plan_card} input[checked]').is_visible(), "Radio button is not checked for current plan in plan modal"
            else:
                raise RuntimeError("Neither plan selection page opened nor plan modal popped up after clicking edit")
            confirmation_page.select_plan_button.click()
        except Exception as e:
            if callback:
                callback("error_review_page_shipping_info_validation", page, screenshot_only=True)
            raise Exception(f"Plan edit validation could not be performed in Review page: {e}")

    @staticmethod
    def plan_recommended_validate(page, page_index="2", callback=None):
        confirmation_page = ConfirmationPage(page)
        recommended_plan = f'[data-testid="plans-selector-plan-card-{page_index}-plan-tag-title"]'  # Recommended plan is "100 pages/month" for OOBE
        try:
            confirmation_page.edit_plan_button.wait_for(state="visible", timeout=20000)
            confirmation_page.edit_plan_button.click()
            if confirmation_page.monthly_plan_title.is_visible(timeout=8000):  # For Chrome browser
                recommended_monthly_plan = confirmation_page.current_monthly_plan.text_content()
                assert recommended_monthly_plan == "Occasional (50 pages/month)", \
                    f"Expected recommended plan 'Occasional (50 pages/month)', but got '{recommended_monthly_plan}'"
            elif confirmation_page.monthly_plan_oobe_title.is_visible(timeout=8000):  # For windows_app (OOBE)
                page.locator(recommended_plan).get_by_text("RECOMMENDED").wait_for(state="visible", timeout=8000)
            else:
                raise RuntimeError("plan selection page or plan modal is not opened after clicking edit plan")
            confirmation_page.select_plan_button.click()
        except Exception as e:
            if callback:
                callback("error_recommended_plan_validation", page, screenshot_only=True)
            raise Exception(f"Recommended plan validation could not be performed during plan selection: {e}")

    @staticmethod
    def select_plan_and_get_value(page, plan_value='50', callback=None, confirm=True): # returns plan value info in format '50 pages/month $5.49'
        EnrollmentHelper.select_plan_v3(page, plan_value=plan_value, paper=False, callback=callback, confirm=confirm)
        monthly_plan, monthly_plan_charges = EnrollmentHelper.selectable_plan_info(page)
        monthly_plan_name = monthly_plan.split(" (")[1].rstrip(')')
        return str(monthly_plan_name) + (' $' + monthly_plan_charges)


    @staticmethod
    def plan_pagesprice_modal_agena_list_validate(page, callback=None, oobe=False):
        try:
            plans_input = [10,50,100,300,700]
            plan_expected = ['10 pages/month $1.79', '50 pages/month $5.49', '100 pages/month $7.99', '300 pages/month $15.99', '700 pages/month $31.99']
            i = 0
            for _ in plans_input:
                plan_value = str(_)
                if not oobe:
                    plan_and_value = EnrollmentHelper.select_plan_and_get_value(page,plan_value=plan_value, callback=callback, confirm=False)
                else:
                    monthly_plan_name, monthly_plan_pages, monthly_plan_charges = EnrollmentHelper.selectable_plan_info_oobe(page, page_index=i)
                    framework_logger.info(f"monthly_plan_name: {monthly_plan_name}, monthly_plan_pages: {monthly_plan_pages}, monthly_plan_charges: {monthly_plan_charges}")
                    plan_and_value = f"{monthly_plan_pages} ${monthly_plan_charges}"

                assert plan_and_value == plan_expected[i], f"Expected plan and value '{plan_expected[i]}', but got '{plan_and_value}'"
                i+=1
                framework_logger.info(f"Plan and value validated for {plan_and_value}")
        except Exception as e:
            if callback: callback("error_plan_pages_agena_pricing_list_validation", page, screenshot_only=True)
            raise Exception (f"Plan pages & pricing list validation as per agena could not be performed in plan selection page/modal: {e}")

    @staticmethod
    def plan_review_modal_validate(page):
        confirmation_page = ConfirmationPage(page)
        # Plan Modal is not available at current stage
        try:
            # click on 'edit' button on Plan card
            confirmation_page.edit_plan_button.wait_for(state="visible", timeout=20000)
            confirmation_page.edit_plan_button.click()
            page.wait_for_timeout(8000)
            #Modal boundary check
            EnrollmentHelper.modal_boundary_check(page, modal_locator="data-testid=plan-modal")

            # Change plan again going back to the modal
            if page.locator(confirmation_page.elements.select_plan_button).count() == 0:
                confirmation_page.edit_plan_button.click()
                confirmation_page.select_ink_plan("300")

            # Click on 'x' button without clicking select plan button
            confirmation_page.close_plan_modal_button.click()
            framework_logger.info("Clicked on 'X' button")

            # Validate old plan remains same after closing modal
            monthly_plan_review, monthly_pages_review, monthly_charges_review = EnrollmentHelper.selected_plan_info(page,onboarded=False) # If running test post onboarding, change to "Yes"
            framework_logger.info(f"monthly_plan_review: {monthly_plan_review}, monthly_pages_review: {monthly_pages_review}, monthly_charges_review: {monthly_charges_review}")
            assert monthly_pages_review == "50 pages/month", f"Expected plan pages '50 pages/month', but got '{monthly_pages_review}'"
        except Exception as e:
            raise Exception(f"Plan review modal validation could not be performed in Review page: {e}")

    @staticmethod
    def enroll_summary_validate_all_plans(page, callback=None, oobe=False):
        confirmation_page = ConfirmationPage(page)
        plan_selector_page = PlanSelectorV3Page(page)
        try:
            plans_input = [10,100,300,700,50]  #  50 is listed last to keep default plan for subsequent actions
            i = 0
            for _ in plans_input:
                plan_value = str(_)
                if not oobe:
                    EnrollmentHelper.select_plan_v3(page, plan_value=plan_value, paper=False, callback=callback, confirm=False)
                    monthly_plan, monthly_plan_charges = EnrollmentHelper.selectable_plan_info(page)
                    monthly_plan_name = monthly_plan.split(" (")[0].upper()+" INK PLAN"
                    monthly_plan_pages = monthly_plan.split("(")[1].rstrip(")")
                    plan_selector_page.ink_only_button.click()
                    confirmation_page.plan_card_title.wait_for(state='visible', timeout=180000)
                    monthly_plan_review, monthly_pages_review, monthly_charges_review = EnrollmentHelper.selected_plan_info(page,onboarded=False) # If running test post onboarding, change to "Yes"

                else:
                    monthly_plan_name, monthly_plan_pages, monthly_plan_charges = EnrollmentHelper.selectable_plan_info_oobe(page, page_index=i)
                    monthly_plan_review, monthly_pages_review, monthly_charges_review = EnrollmentHelper.selected_plan_info(page,onboarded=False)

                framework_logger.info(f"Enroll Summary plan info validated for {monthly_plan_pages}")
                framework_logger.info("Enroll Summary validation begins")
                expect(confirmation_page.plan_card_black_tick).to_be_visible()
                assert monthly_plan_name == monthly_plan_review, f"Expected plan name '{monthly_plan_name}', but got '{monthly_plan_review}'"
                assert monthly_plan_pages == monthly_pages_review, f"Expected plan pages '{monthly_plan_pages}', but got '{monthly_pages_review}'"
                assert monthly_plan_charges == monthly_charges_review, f"Expected charges '{monthly_plan_charges}', but got '{monthly_charges_review}'"
                i+=1
            confirmation_page.edit_plan_button.click()
            if oobe:
                assert confirmation_page.monthly_plan_title.is_visible(timeout=8000), \
                    "Select plan page title not visible after clicking edit"  # For Chrome browser
            else:
                assert confirmation_page.monthly_plan_oobe_title.is_visible(timeout=8000), \
                    "Selected plan modal title not visible after clicking edit"  # For windows_app (OOBE)
            confirmation_page.select_plan_button.click()

        except Exception as e:
            if callback: callback("error_enroll_summary_all_plans_validation", page, screenshot_only=True)
            raise Exception(f"Enroll Summary validation could not be performed in Review page: {e}")

    @staticmethod
    def selected_shipping_info_validate(page, index=0, callback=None):
        plan_selector_page = PlanSelectorV3Page(page)
        confirmation_page = ConfirmationPage(page)
        expected_adrs = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload,list) else GlobalState.address_payload
        if expected_adrs["fullState"] == "Washington":
            expected_adrs.update({"zipCode": "98683-8556"}) # Existing Zipcode in JSON is incorrect for WA state
        try:
            if plan_selector_page.ink_only_button.is_visible():
                plan_selector_page.ink_only_button.click()
            confirmation_page.plan_card_title.wait_for(state='visible', timeout=180000)
            card_adrs = confirmation_page.shipping_address_details.text_content().split()
            item3, item4 = card_adrs[1], card_adrs[4] # check the address in card_adrs list then modify accordingly when needed
            if expected_adrs["fullState"] == "Washington":
                expected_adrs.update({"zipCode": "98683-8556"})  # Existing Zipcode in JSON is incorrect for WA state
                item3 = ' '.join([str(card_adrs[1][-4:]), str(card_adrs[2]), str(card_adrs[3]), str(card_adrs[4][:3])])
                item4 = ' '.join([str(card_adrs[4][-3:]), str(card_adrs[5][:3])])
            actual_adrs = [card_adrs[0],card_adrs[1][:4],item3,item4,card_adrs[5][3:].lower().capitalize().rstrip(','),card_adrs[6],card_adrs[7]]
            for item in actual_adrs:
                if item in expected_adrs.values():
                    continue
                else:
                    raise Exception(f"Actual shipping info '{item}' not found in '{expected_adrs}'")

        except Exception as e:
            if callback:
                callback("error_review_page_shipping_info_validation", page, screenshot_only=True)
            raise Exception(f"Selected shipping info could not be validated in Review page: {e}")

    @staticmethod
    def shipping_review_modal_msgs_validate(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            # click on 'edit' shipping address
            confirmation_page.edit_shipping_button.wait_for(state='visible', timeout=20000)
            confirmation_page.edit_shipping_button.click()
            framework_logger.info("Clicked on Edit shipping button")
            # Checking modal information
            page.locator('//*[text()="Edit shipping address"]').wait_for(state='visible', timeout=180000)
            if page.locator('//*[@data-testid="shipping-fields"]/div/p').is_visible():
                assert confirmation_page.receive_update_msg.is_visible() ,"Add mobile number for update message not visible in shipping modal"
            assert confirmation_page.receive_update_checkbox.is_visible(), " Receive update checkbox not visible in shipping modal"
            assert confirmation_page.receive_update_checkbox_text.is_visible(), " Receive update checkbox text not visible in shipping modal"

        except Exception as e:
            if callback:
                callback("error_Shipping_review_modal_validation", page, screenshot_only=True)
            raise Exception(f"Shipping review modal validation could not be performed in Review page: {e}")

    @staticmethod
    def shipping_review_modal_modify_validate(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            page.locator('//*[text()="Edit shipping address"]').wait_for(state='visible', timeout=180000)
            framework_logger.info("Shipping Review modal Zipcode PBL message modal popup check begins:")
            confirmation_page.zip_code_input.fill('97439')
            confirmation_page.save_button.click()
            confirmation_page.blacklist_zipcode_error_text.wait_for(state="visible", timeout=30000)
            confirmation_page.blacklist_zipcode_back_button.click()
            framework_logger.info("Blacklisted Zipcode PBL message check completed.")

            framework_logger.info("Shipping modal close button boundary check begins:")
            #Modal boundary check
            EnrollmentHelper.modal_boundary_check(page, modal_locator="data-testid=shipping-modal")
            # check modal is NOT closed after above step
            confirmation_page.save_button.wait_for(state="visible", timeout=5000)
            framework_logger.info("Shipping Model is visible after clicking outside the model.")
            # Click on 'x' button
            confirmation_page.close_shipping_modal_button.click()
            time.sleep(10)
            assert confirmation_page.shipping_card.is_visible(), "Shipping card is not visible after closing the modal"
            framework_logger.info("Shipping modal close button boundary check completed.")

            confirmation_page.edit_shipping_button.wait_for(state='visible', timeout=20000)
            confirmation_page.edit_shipping_button.click()

            framework_logger.info("Shipping modal mandatory field check begins:")
            page.locator('//*[text()="Edit shipping address"]').wait_for(state='visible', timeout=180000)
            confirmation_page.first_name.fill("")
            confirmation_page.street1_input.fill("")
            confirmation_page.save_button.click()
            mand_msg = confirmation_page.error_message.text_content()
            assert mand_msg == "Please complete required fields correctly", "Mandatory field validation message not visible in shipping modal"
            if callback: callback("mandatory_fields_check1", page, screenshot_only=True)
            framework_logger.info("Mandatory field error message is visible.")
            confirmation_page.close_shipping_modal_button.click()

            framework_logger.info("Checking shipping address updated in modal edit and validate shipping card in review page-C27368545")
            EnrollmentHelper.edit_shipping_check(page, callback=callback, additional_check=True)
            expect(confirmation_page.shipping_card_black_tick).to_be_visible()
            expect(confirmation_page.edit_shipping_button).to_be_visible()

        except Exception as e:
            if callback: callback("error_Shipping_review_modal_modification_validation", page, screenshot_only=True)
            raise Exception(f"Shipping review modal modification validation could not be performed in Review page: {e}")

    @staticmethod
    def billing_card_validate(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            expect(confirmation_page.billing_card).to_be_visible(timeout=30000)
            assert confirmation_page.billing_card_black_tick.is_visible(), "Billing card black tick is not visible"
            assert confirmation_page.edit_billing_button.is_visible(), "Edit billing button is not visible"
            expect(confirmation_page.billing_info_icon).not_to_be_visible()
            assert confirmation_page.billing_card_promo_link.is_visible(), "Billing card promo link is not visible"

        except Exception as e:
            if callback: callback("error_Billing_card_validation", page, screenshot_only=True)
            raise Exception(f"Billing card validation could not be performed in Review page: {e}")

    @staticmethod
    def post_edit_billing_validate(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            expect(confirmation_page.edit_billing_button).to_be_visible(timeout=30000)
            confirmation_page.edit_billing_button.click()
            page.locator('//*[text()="Please enter your billing information."]').wait_for(state="visible", timeout=60000)
            assert page.locator('//*[text()="Step 1 of 2"]').is_visible(), "Step 1 of 2 text not visible in billing modal"

            framework_logger.info("Account Type Validation begins:")
            radio1 = confirmation_page.elements.consumer_radio_button
            radio1_selected = f'{radio1}:checked'
            assert page.locator('//*[text()="Select an account type"]').is_visible(), "Select an account type text not visible in billing modal"
            assert page.locator(radio1_selected).is_visible(), "Consumer radio button is not selected by default under account type"
            assert confirmation_page.business_radio_button.is_visible(), "Business radio button is not visible under account type"

            framework_logger.info("Payment Method Validation begins:")
            radio2 = confirmation_page.elements.creditcard_radio_button
            radio2_selected = f'{radio2}:checked'
            assert page.locator('//*[text()="Choose a payment method"]').is_visible(), "Choose a payment method text not visible in billing modal"
            assert page.locator(radio2).is_visible(), "Credit Card radio button is not selected by default payment type"
            # For Direct Debit supported:
            if GlobalState.country in common.countries_with_direct_debit():
                assert confirmation_page.direct_debit_radio_button.is_visible(), "Direct Debit radio button is not visible under payment method"

            framework_logger.info("Address section validation begins:")
            assert page.locator(
                '//*[text()="Billing address"]').is_visible(), "Billing address text not visible in billing modal"
            expect(confirmation_page.same_as_shipping_checkbox).not_to_be_visible()
            fields = [
                (confirmation_page.first_name_2co, "First name"),
                (confirmation_page.last_name_2co, "Last name"),
                (confirmation_page.street_name1_billing, "Street1"),
                (confirmation_page.city_billing, "City"),
                (confirmation_page.zip_code_billing, "Zip code"),
            ]
            for field, name in fields:
                assert field.is_visible(), f"{name} input is not visible in billing modal"
                assert field.input_value() != "", f"{name} input is not pre-filled in billing modal"

            framework_logger.info("Cancel,Continue and Close buttons Validation begins:")
            buttons = [(confirmation_page.cancel_button, "cancel"), (confirmation_page.billing_continue_button, "continue"), (confirmation_page.close_billing_button,"close")]
            for button, name in buttons:
                assert button.is_visible(), f"{name} button is not visible in billing modal"

            if callback: callback("billing_step1_modal", page, screenshot_only=True)
            # Close billing modal if still open
            confirmation_page.close_billing_button.click()

        except Exception as e:
            if callback: callback("error_Post_edit_billing_validation", page, screenshot_only=True)
            raise Exception(f"Post edit billing validation could not be performed in Review page: {e}")

    @staticmethod
    def billing_review_modal_validate(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            framework_logger.info("Billing modal step 1of2 Close button validation:")
            expect(confirmation_page.edit_billing_button).to_be_visible(timeout=30000)
            confirmation_page.edit_billing_button.click()
            page.locator('//*[text()="Please enter your billing information."]').wait_for(state="visible", timeout=60000)
            confirmation_page.close_billing_button.click()
            expect(confirmation_page.edit_billing_button).to_be_visible(timeout=30000)

            framework_logger.info("Billing modal step 1of2 Cancel button validation:")
            confirmation_page.edit_billing_button.click()
            page.locator('//*[text()="Please enter your billing information."]').wait_for(state="visible", timeout=60000)
            confirmation_page.cancel_button.click()
            assert confirmation_page.billing_card.is_visible(), "Cancel button did not close the billing modal step 1of2"

            framework_logger.info("Billing modal step1 boundary check begins:")
            confirmation_page.edit_billing_button.click()
            EnrollmentHelper.modal_boundary_check(page, modal_locator="data-testid=billing-modal")
            # check modal is NOT closed after above step
            page.locator('//*[text()="Please enter your billing information."]').wait_for(state="visible", timeout=60000)
            framework_logger.info("Clicking outside the modal did not close Billing Modal.")
            if callback: callback("Billing_modal_step1", page, screenshot_only=True)

            framework_logger.info("Billing step2 modal boundary check:")
            confirmation_page.billing_continue_button.click()
            page.locator('//*[text()="Step 2 of 2"]').wait_for(state="visible", timeout=40000)
            #Modal step1 boundary check
            EnrollmentHelper.modal_boundary_check(page, modal_locator="data-testid=billing-modal")

            framework_logger.info("Clicking Back button in Modal Step 2of2 to navigate to Step 1of2:")
            confirmation_page.back_button.click()
            assert page.locator('//*[text()="Step 1 of 2"]').is_visible(), "Back button in Modal Step 2of2 did not navigate to Step 1of2"

            framework_logger.info("Billing step2 modal close button validation:")
            confirmation_page.billing_continue_button.click()
            page.locator('//*[text()="Step 2 of 2"]').wait_for(state="visible", timeout=40000)
            confirmation_page.close_billing_button.click()
            assert confirmation_page.billing_card.is_visible(), "Close button in Modal Step 2of2 did not close the billing modal"

        except Exception as e:
            if callback: callback("error_Billing_modal_validation", page, screenshot_only=True)
            raise Exception(f"Billing modal validation could not be performed for order review: {e}")

    @staticmethod
    def edit_billing_for_pgs_card(page, payment_method=None):
        confirmation_page = ConfirmationPage(page)
        try:
            EnrollmentHelper.edit_billing(page)  # Navigate to billing modal step1
            page.locator('//*[text()="Please enter your billing information."]').wait_for(state="visible", timeout=60000)

            framework_logger.info("Switching payment method to PGS credit/debit card:")
            confirmation_page.billing_continue_button.click()
            payment_data = common.get_payment_method_data(payment_method)
            frame = page.frame_locator(confirmation_page.elements.iframe_pgs)
            page.locator('//*[text()="Step 2 of 2"]').wait_for(state="visible", timeout=40000)
            card_input = frame.locator(confirmation_page.elements.card_number)
            card_input.fill(payment_data.get("credit_card_number"))
            frame.locator(confirmation_page.elements.exp_month).select_option(payment_data.get("expiration_month"))
            frame.locator(confirmation_page.elements.exp_year).select_option(payment_data.get("expiration_year"))
            frame.locator(confirmation_page.elements.cvv_input).type(payment_data["cvv"])
            page.wait_for_timeout(10000) # Wait for a moment to ensure next button click works consistently
            frame.locator(confirmation_page.elements.billing_next_button).click()
            time.sleep(15) # Wait for a moment to ensure next button check works consistently
            if frame.locator(confirmation_page.elements.billing_next_button).is_visible():
                frame.locator(confirmation_page.elements.billing_next_button).click()
            confirmation_page.edit_billing_button.wait_for(state="visible", timeout=60000)
            page.wait_for_timeout(60000) # Wait for a moment to ensure billing details are updated consistently

        except Exception as e:
            raise Exception(f"Editing billing to PGS credit/debit card could not be performed: {e}")

    @staticmethod
    def billing_review_modal_creditcard_modify(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            EnrollmentHelper.edit_billing(page) # Navigate to billing modal step1
            page.locator('//*[text()="Please enter your billing information."]').wait_for(state="visible", timeout=60000)
            framework_logger.info("Billing step2 modal boundary check:")
            confirmation_page.billing_continue_button.click()
            page.locator('//*[text()="Step 2 of 2"]').wait_for(state="visible", timeout=40000)

            framework_logger.info("Leaving mandatory fields empty and clicking Continue button:")
            payment_data = common.get_payment_method_data("credit_card_master")
            frame = page.frame_locator(confirmation_page.elements.iframe_pgs)
            frame.locator(confirmation_page.elements.billing_next_button).wait_for(state="visible", timeout=60000)
            frame.locator(confirmation_page.elements.billing_next_button).click()
            assert frame.locator(confirmation_page.enter_cvv_error).is_visible(), "Mandatory field error message not visible when left empty"
            if callback: callback("card_details_mandatory_error", page, screenshot_only=True)
            framework_logger.info("Mandatory field error message validated.")
            # Filling correct card details:
            # EnrollmentHelper.edit_billing_for_pgs_card(page)
            card_input = frame.locator(confirmation_page.elements.card_number)
            card_input.fill(payment_data["credit_card_number"])
            frame.locator(confirmation_page.elements.exp_month).select_option(payment_data.get("expiration_month"))
            frame.locator(confirmation_page.elements.exp_year).select_option(payment_data.get("expiration_year"))
            frame.locator(confirmation_page.elements.cvv_input).type(payment_data["cvv"])
            page.wait_for_timeout(10000) # Wait for a moment to ensure next button click works consistently
            frame.locator(confirmation_page.elements.billing_next_button).click()
            time.sleep(15) # Wait for a moment to ensure next button check works consistently
            if frame.locator(confirmation_page.elements.billing_next_button).is_visible():
                frame.locator(confirmation_page.elements.billing_next_button).click()

            framework_logger.info("Billing card validation after editing credit card details:")
            confirmation_page.edit_billing_button.wait_for(state="visible", timeout=60000)
            page.wait_for_timeout(60000) # Wait for a moment to ensure billing details are updated consistently
            billing_details = confirmation_page.billing_card_details.text_content().split() # billing_card_payment_details
            framework_logger.info(f"expected billing details: {payment_data} Billing details from billing card: {billing_details}")
            assert (payment_data["credit_card_number"][-4:] == billing_details[1][-12:-8]), "Billing card last 4 digits do not match expected value after edit"
            assert (payment_data["expiration_month"] == billing_details[2][0:2]), "Billing card expiration month do not match expected value after edit"
            assert payment_data["expiration_year"] == billing_details[2][-4:], f'Billing card expiration year: {billing_details[2][-4:]} does not match: {payment_data["expiration_year"]} expected value after edit'
            assert confirmation_page.plan_card_black_tick.is_visible(), "Billing card black tick is not visible"
            assert confirmation_page.edit_billing_button.is_visible(), "Edit billing button is not visible"

        except Exception as e:
            if callback: callback("error_Billing_modal_creditcard_modification", page, screenshot_only=True)
            raise Exception(f"Billing modal credit card modification could not be performed for order review: {e}")

    @staticmethod
    def billing_review_modal_paypal_modify(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            framework_logger.info("Editing billing to PayPal payment method then to credit card begins:")
            confirmation_page.edit_billing_button.wait_for(state="visible", timeout=60000)
            EnrollmentHelper.edit_billing_for_paypal(page, payment_method="paypal") # Switch to PayPal payment method
            if callback: callback("PaypalDetails_PlanReview", page, screenshot_only=True)
            EnrollmentHelper.edit_billing_for_pgs_card(page) # Switch back to credit/debit card payment method
            if callback: callback("CreditCardDetails_PlanReview", page, screenshot_only=True)

        except Exception as e:
            if callback: callback("error_Billing_modal_paypal_modification", page, screenshot_only=True)
            raise Exception(f"Billing modal PayPal modification could not be performed for order review: {e}")


    @staticmethod
    def plan_type_page_validation(page, callback=None):
        confirmation_page = ConfirmationPage(page)
        try:
            assert not page.locator('//*[text()="FAQ" or text()="F.A.Q"]').is_visible(), "FAQ link is visible on plan type page"
            assert page.locator(confirmation_page.elements.plan_type_title).is_visible(), "Plan type page title is not visible on plan type page"
            assert confirmation_page.pay_as_you_print_card.is_visible(), "Pay As You Print plan card is not visible on plan type page"
            assert confirmation_page.pay_as_you_print_select_btn.is_enabled(), "Pay As You Print plan selection button is not enabled on plan type page"
            assert confirmation_page.monthly_plan_card.is_visible(), "Monthly plan card is not visible on plan type page"
            assert page.locator(confirmation_page.elements.most_popular_plan_identifier).is_visible(), "Most popular plan element & text is not visible on plan type page"
            assert confirmation_page.monthly_plan.is_enabled(), "Monthly plan selection button is not visible on plan type page"
            assert confirmation_page.yearly_plan_card.is_visible(), "Yearly plan card is not visible on plan type page"
            assert page.locator(confirmation_page.elements.best_savings_plan_identifier).is_visible(), "Best savings plan element & text is not visible on plan type page"
            assert confirmation_page.yearly_plan_select_btn.is_enabled(), "Yearly plan selection button is not visible on plan type page"

        except Exception as e:
            if callback: callback("error_Plan_type_page_validation", page, screenshot_only=True)
            raise Exception(f"Plan type page validation could not be performed: {e}")

    @staticmethod
    def is_add_shipping_button_enabled(page):
        """
        Checks if the 'Add Shipping' button is visible on the page.

        :param page: The Playwright page object.
        :return: True if the button is visible, False otherwise.
        """
        confirmation_page = ConfirmationPage(page)
        try:
            return confirmation_page.add_shipping_button.is_enabled(timeout=5000)
        except Exception as e:
            framework_logger.error(f"Error checking visibility of 'Add Shipping' button: {e}")
            return False

    @staticmethod
    def is_add_billing_button_disabled(page):
        """
        Checks if the 'Add Shipping' button is disabled on the page.

        :param page: The Playwright page object.
        :return: True if the button is disabled, False otherwise.
        """
        confirmation_page = ConfirmationPage(page)
        try:
            return not confirmation_page.add_billing_button.is_enabled(timeout=5000)
        except Exception as e:
            framework_logger.error(f"Error checking if 'Add Shipping' button is disabled: {e}")
            return False

    @staticmethod
    def is_billing_information_text_visible(page, expected_text):
        """
        Checks if the 'Enter your billing Details' text is visible and matches the expected text.

        :param page: The Playwright page object.
        :param expected_text: The expected text to validate.
        :return: True if the text is visible and matches the expected text, False otherwise.
        """
        confirmation_page = ConfirmationPage(page)
        try:
            if confirmation_page.billing_information.is_visible(timeout=5000):
                actual_text = confirmation_page.billing_information.text_content().strip()
                return actual_text == expected_text
            return False
        except Exception as e:
            framework_logger.error(f"Error validating 'Enter your billing Details' text: {e}")
            return False

    @staticmethod
    def flip_continue(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.flip_next_button.wait_for(state="visible", timeout=60000)
        confirmation_page.flip_next_button.click()

    @staticmethod
    def flip_skip_free_months(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.skip_free_months.wait_for(state="visible", timeout=60000)
        confirmation_page.skip_free_months.click() 
        time.sleep(5)     

    @staticmethod
    def finish_flip_enroll(page):
        confirmation_page = ConfirmationPage(page)
        thank_you_page = ThankYouPage(page)
        confirmation_page.flip_terms_agreement_checkbox.wait_for(state="visible", timeout=100000)
        confirmation_page.flip_terms_agreement_checkbox.check(force=True)
        confirmation_page.flip_start_free_trial.click()
        thank_you_page.continue_button.wait_for(state="visible", timeout=60000)
        thank_you_page.continue_button.click()

    @staticmethod
    def add_shipping_flip_auto_fill(page,index=0):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.skip_free_months.is_visible()
        confirmation_page.flip_next_button.is_visible()
        address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
        state_name = address.get("fullState", address.get(f"fullState_{GlobalState.language_code}"))
        confirmation_page.auto_fill_address.wait_for(state="visible", timeout=90000)
        confirmation_page.auto_fill_address.click()
        confirmation_page.auto_fill_address.fill(address.get("street1",""))
        confirmation_page.address_option.click()
        confirmation_page.phone_number_input.fill(address.get("phoneNumber1", ""))
        confirmation_page.save_button.click()

    @staticmethod
    def close_billing_or_shipping_modal(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.cancel_button.wait_for(state="visible", timeout=60000)
        confirmation_page.cancel_button.click()   

    @staticmethod
    def add_paper_to_your_plan_flip(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.flip_paper_addon_container.is_visible()
        confirmation_page.paper_addon_learn_more.click()
        framework_logger.info("Learn more about paper addon clicked")
        confirmation_page.learn_more_faq_back_button.wait_for(state="visible", timeout=10000)
        confirmation_page.learn_more_faq_back_button.click()
        framework_logger.info("Learn more about paper back button clicked")
        confirmation_page.add_paper_to_your_plan.wait_for(state="visible", timeout=10000)
        confirmation_page.add_paper_to_your_plan.click()
        framework_logger.info("Add paper to your plan clicked")

    @staticmethod
    def flip_paper_not_offered(page):
        confirmation_page = ConfirmationPage(page)
        assert not confirmation_page.flip_paper_addon_container.is_visible(timeout=60000)

    @staticmethod
    def flip_skip_trial(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.flip_skip_button.wait_for(state="visible", timeout=60000)
        confirmation_page.flip_skip_button.click()   
        confirmation_page.view_offer.is_visible()
        confirmation_page.remind_me.is_visible()
        confirmation_page.skip_offer_link.is_visible()
        confirmation_page.skip_offer_link.click()

    @staticmethod
    def flip_remind_me_later(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.flip_skip_button.wait_for(state="visible", timeout=60000)
        confirmation_page.flip_skip_button.click() 
        confirmation_page.remind_me.wait_for(state="visible", timeout=60000)
        confirmation_page.remind_me.click()

    @staticmethod
    def flip_view_offer(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.flip_skip_button.wait_for(state="visible", timeout=60000)
        confirmation_page.flip_skip_button.click() 
        confirmation_page.before_you_go.is_visible()
        assert confirmation_page.before_you_go.text_content(), "Before you go"
        confirmation_page.view_offer.wait_for(state="visible", timeout=60000)
        confirmation_page.view_offer.click()    

    @staticmethod
    def enter_address_manually_flip(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.enter_address_manually.wait_for(state="visible", timeout=100000)
        confirmation_page.enter_address_manually.click()  

    @staticmethod
    def edit_plan(page,plan_pages: str):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.edit_plan_button.wait_for(state="visible", timeout=60000)
        confirmation_page.edit_plan_button.click()
        confirmation_page.plan_more_info.click()
        confirmation_page.plan_back_button.click()
        plan_selector = f"label:has([data-testid='plan-radio-button-i_ink-{plan_pages}'])"
        page.locator(plan_selector).click()
        confirmation_page.select_plan_button.click()

    @staticmethod
    def edit_shipping(ppage):
        confirmation_page = ConfirmationPage(ppage)
        confirmation_page.edit_shipping_button.wait_for(state="visible", timeout=60000)
        confirmation_page.edit_shipping_button.click()

    @staticmethod
    def edit_billing(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.edit_billing_button.wait_for(state="visible", timeout=60000)
        confirmation_page.edit_billing_button.click()    

    @staticmethod
    def see_details_special_offer(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.see_details.click()
        confirmation_page.close_modal_button.click()

    @staticmethod
    def add_paper_offer(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.add_paper.click()

    @staticmethod
    def remove_paper_offer(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.remove_paper.click()

    @staticmethod
    def payment_method_required(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.billing_card.wait_for(state="visible", timeout=60000)
        text = confirmation_page.billing_card.text_content()
        assert "Payment method required" in text, "Payment method required message not found"

    @staticmethod
    def optional_payment_method(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.billing_card.wait_for(state="visible", timeout=60000)
        text = confirmation_page.billing_card.text_content()
        assert "Optional: Add your billing information to avoid service interruptions" in text, "Payment method required message not found" 

    @staticmethod
    def prepaid_funds_do_not_cover(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.billing_card.wait_for(state="visible", timeout=60000)
        text = confirmation_page.billing_card.text_content()
        assert "Prepaid funds do not cover selected plan" in text, "Prepaid funds do not cover message not found"    

    @staticmethod
    def validate_plan_price(page,page_values, prices,ink_and_paper=True):
        confirmation_page = ConfirmationPage(page)
        plan_selector_v3_page = PlanSelectorV3Page(page)
        confirmation_page.edit_plan_button.wait_for(state="visible", timeout=60000)
        confirmation_page.edit_plan_button.click()

        assert len(page_values) == len(prices), "Page values and prices must have the same length"
        for page_value, price in zip(page_values, prices):
            page_value_locator = f"//*[contains(@data-testid,'plans-selector-plan-card')]//*[text()='{page_value}']"
            price_value_locator = f"//*[contains(@data-testid,'plans-selector-plan-card')]//*[text()='{price}']"
            page_text = page.locator(page_value_locator).text_content(timeout=10000)
            price_text = page.locator(price_value_locator).text_content(timeout=10000)
            assert str(page_value) in page_text, f"Expected page value '{page_value}' not found in '{page_text}'"
            assert str(price) in price_text, f"Expected price '{price}' not found in '{price_text}'"
        if ink_and_paper == True:
            confirmation_page.paper_cartridges_tab.wait_for(state="visible", timeout=60000)
            confirmation_page.paper_cartridges_tab.click()
            confirmation_page.plan_more_info.wait_for(state="visible", timeout=60000)
            confirmation_page.plan_more_info.click()
            confirmation_page.learn_more_faq_modal.wait_for(state="visible", timeout=60000)
            confirmation_page.learn_more_faq_modal.click()
            #confirmation_page.learn_more_faq_back_button.wait_for(state="visible", timeout=60000)
            #confirmation_page.learn_more_faq_back_button.click()
            confirmation_page.close_modal_button.wait_for(state="visible", timeout=60000)
            confirmation_page.close_modal_button.click()
        else:
            confirmation_page.ink_cartridges_tab.wait_for(state="visible", timeout=60000)
            confirmation_page.ink_cartridges_tab.click()
            confirmation_page.plan_more_info.wait_for(state="visible", timeout=60000)
            confirmation_page.plan_more_info.click() 
            confirmation_page.plan_back_button.wait_for(state="visible", timeout=60000)
            confirmation_page.plan_back_button.click()   
        plan_selector_v3_page = PlanSelectorV3Page(page)
        plan_selector_v3_page.continue_button.click()
        page.wait_for_load_state("load")  

    @staticmethod
    def header_of_enroll_summary_page(page):
        confirmation_page = ConfirmationPage(page)
        expect(confirmation_page.header_logo).to_be_visible(timeout=60000)
        expect(confirmation_page.virtual_assistant).to_be_visible()
        expect(confirmation_page.virtual_assistant).to_be_enabled(timeout=60000)
        expect(confirmation_page.support_phone_number).to_be_visible()
        expect(confirmation_page.support_phone_number).to_be_enabled(timeout=60000)
        expect(confirmation_page.account_button).to_be_visible()
        expect(confirmation_page.country_sector).to_be_visible()

    @staticmethod
    def clicking_virtual_assistant_link(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.virtual_assistant.wait_for(state="visible", timeout=60000)

        with page.context.expect_page() as new_page_info:
            confirmation_page.virtual_assistant.click()
        new_page = new_page_info.value
        new_page.wait_for_load_state("load")
        actual_title = new_page.title()
        expected_title= "HPChat"
        assert actual_title == expected_title, f"Expected title '{expected_title}', but got '{actual_title}'"
        expect(new_page.locator('text=Virtual Assistant')).to_be_visible(timeout=60000)
        #checking user able to chat with agent
        new_page.locator('[data-testid="send box text area"]').fill("Hello")
        new_page.keyboard.press("Enter")
        new_page.close()


    # @staticmethod
    # def verifying_phone_number_link(page):
    #     confirmation_page = ConfirmationPage(page)
    #     confirmation_page.support_phone_number.wait_for(state="visible", timeout=60000)
    #     phone_number_text= confirmation_page.support_phone_number.text_content()
    #     expected_ph_number_pattern = r"^\+?\d+([-.\s]?\d+)+$"
    #     assert re.match(expected_ph_number_pattern, phone_number_text), f"Phone number '{phone_number_text}' does not match the expected pattern"
    #     with page.context.expect_page() as new_page_info:
    #         confirmation_page.support_phone_number.click()
    #     new_page = new_page_info.value
    #     new_page.wait_for_load_state("load")
    #     # Use expect_event to handle the dialog
    #     # with new_page.expect_event("dialog") as dialog_info:
    #     #     new_page.once("dialog", lambda dialog: dialog.dismiss())
    #     # dialog = dialog_info.value
    #     # print("Alert message:", dialog.message)
    #     dialog = new_page.wait_for_event("dialog")
    #     print("Alert message:", dialog.message)
    #     assert "https://onboardingcenter.stage.portalshell.int.hp.com wants to open this application." in dialog.message
    #     dialog.dismiss()
    #     #assert "https://onboardingcenter.stage.portalshell.int.hp.com wants to open this application." in dialog.message
    #     #validate url
    #     page_url=new_page.url
    #     expected_pattern = r"^tel:\+?\d+([-.\s]?\d+)+$"
    #     assert re.match(expected_pattern, page_url), f"URL '{page_url}' does not match the expected pattern"
    #     #new_page.close()

    @staticmethod
    def verifying_phone_number_link(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.support_phone_number.wait_for(state="visible", timeout=60000)

        # Get and validate the visible phone number
        phone_number_text = confirmation_page.support_phone_number.text_content()
        expected_ph_number_pattern = r"^\+?\d+([-.\s]?\d+)+$"
        assert re.match(expected_ph_number_pattern, phone_number_text), \
            f"Phone number '{phone_number_text}' does not match expected pattern"

        # Check that the href is a valid tel: link without clicking
        phone_link = confirmation_page.support_phone_number.get_attribute("href")
        print("Phone link:", phone_link)
        assert phone_link.startswith("tel:"), f"Expected a tel: link, got '{phone_link}'"

        # Validate the phone number pattern inside href
        expected_url_pattern = r"^tel:\+?\d+([-.\s]?\d+)+$"
        assert re.match(expected_url_pattern, phone_link), \
            f"Phone link '{phone_link}' does not match expected pattern"

        print("Verified phone number and tel: link without opening system popup.")

    def verify_signout_link(page):
        confirmation_page = ConfirmationPage(page)
        landing_page=LandingPage(page)
        confirmation_page.account_button.wait_for(state="visible", timeout=60000)
        expect(confirmation_page.account_button).to_be_enabled(timeout=60000)
        confirmation_page.account_button.click()
        expect(confirmation_page.sign_out_link).to_be_visible(timeout=60000)
        confirmation_page.sign_out_link.click()
        expect(landing_page.sign_up_header_button).to_be_visible(timeout=120000)

    def verify_country_sector_modal_dropdown_country(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.country_sector.wait_for(state="visible", timeout=60000)
        confirmation_page.country_sector.click()
        confirmation_page.modal_header.wait_for(state="visible", timeout=60000)
        dropdown_country=confirmation_page.country_dropdown
        dropdown_country.wait_for(state="visible", timeout=60000)
        dropdown_country.click()
        country_option = confirmation_page.country_options
        expect(country_option).to_have_count_greater_than(0)
        country_list = country_option.all_text_contents()
        print("Countries shown in dropdown:", country_list)


    def verify_country_sector_modal_dropdown_language(page):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.country_sector.wait_for(state="visible", timeout=60000)
        confirmation_page.country_sector.click()
        confirmation_page.modal_header.wait_for(state="visible", timeout=60000)
        dropdown_language=confirmation_page.language_dropdown
        dropdown_language.wait_for(state="visible", timeout=60000)
        dropdown_language.click()
        language_option = confirmation_page.language_options
        expect(language_option).to_have_count_greater_than(0)
        language_list = language_option.all_text_contents()
        print("Languages shown in dropdown:", language_list)


    def verify_closing_country_sector_modal_x(page):
        close_pop = page.locator('[aria-label="Close modal"]').nth(2)
        close_pop.click()
        # Optionally, wait for the modal to disappear here
        confirmation_page = ConfirmationPage(page)
        expect(confirmation_page.country_sector).to_be_visible(timeout=60000)

    def verify_closing_country_sector_modal_save(page):
        close_pop = page.locator('xapth=//*[text()="Save"]')
        close_pop.click()
        # Optionally, wait for the modal to disappear here
        confirmation_page = ConfirmationPage(page)
        expect(confirmation_page.country_sector).to_be_visible(timeout=60000)

    @staticmethod
    def validate_plan_page_header_elements(page):
        plan_selector_page = PlanSelectorV3Page(page)
        expect(plan_selector_page.virtual_agent_link).to_be_visible(timeout=60000)
        expect(plan_selector_page.support_phone_number_link).to_be_visible(timeout=60000)
        expect(plan_selector_page.country_selector_button).to_be_visible(timeout=60000)
        expect(plan_selector_page.account_button).to_be_visible(timeout=60000)        
