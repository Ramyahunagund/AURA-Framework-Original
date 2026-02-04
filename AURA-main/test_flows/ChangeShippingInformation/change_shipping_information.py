from pages.dashboard_hp_smart_page import DashboardHPSmartPage
from pages.shipping_billing_page import ShippingBillingPage
from test_flows.BillingCycle.billing_cycle import billing_cycle
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import urllib3
import traceback
import test_flows_common.test_flows_common as common
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def change_shipping_information(stage_callback):
    framework_logger.info("=== C38555183 - change shipping information flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        try:
            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            side_menu.click_shipping_billing()
            
            # Click Change Billing Info link in Overview page
            shipping_billing_page = ShippingBillingPage(page)
            shipping_billing_page.manage_shipping_address.click()
            framework_logger.info("Clicked Manage your shipping address link")

            # Change shipping info - using second address (index 1)
            DashboardHelper.add_shipping(page, index=2)
            framework_logger.info(f"Changed shipping information using second address")

            shipping_billing_page = ShippingBillingPage(page)
            shipping_billing_page.wait.go_back_unsupported_shipping(timeout=10000).click()
            shipping_billing_page.cancel_address_button.click(timeout=10000)
            framework_logger.info("Clicked Go Back to unsupported shipping address modal")

            # Obter o valor atual
            shipping_billing_page.manage_shipping_address.click()
            current_value = shipping_billing_page.first_name_field.input_value()
            new_value = f"#{current_value}1"
            shipping_billing_page.first_name_field.fill(new_value)
            expect(shipping_billing_page.error_message).to_be_visible(timeout=10000)
            framework_logger.info("Filled first name field with invalid value")

            shipping_billing_page.first_name_field.fill(current_value)
            assert shipping_billing_page.error_message.count() == 0
            framework_logger.info("First name field filled with valid value")

            current_value = shipping_billing_page.zip_code_field.input_value()
            shipping_billing_page.zip_code_field.fill("99999999999")
            expect(shipping_billing_page.error_message).to_be_visible(timeout=10000),
            framework_logger.info("Filled zip code field with invalid value")

            shipping_billing_page.zip_code_field.fill(current_value)
            assert shipping_billing_page.error_message.count() == 0
            framework_logger.info("Zip code field filled with valid value")

            current_value = shipping_billing_page.street1.input_value()
            shipping_billing_page.street1.fill(current_value[:-1])

            shipping_billing_page.save_button.click()
            framework_logger.info("Clicked Save button with invalid street1 value")
            shipping_billing_page.suggested_address_option.click(force=True)
            shipping_billing_page.ship_to_this_address.click()


            current_saved_address = shipping_billing_page.saved_address.nth(0).inner_html()
            assert current_value in current_saved_address, f"Expected '{current_value}' to be in '{current_saved_address}'"
            framework_logger.info("Saved address updated successfully")

            shipping_billing_page.manage_shipping_address.click()
            shipping_billing_page.wait.street1(timeout=10000)
            field_value = shipping_billing_page.street1.input_value()
            assert current_value in field_value, f"Expected '{current_value}' to be in '{field_value}'"
            framework_logger.info("Street1 field validated")


            if (common._tenant_country not in common.countries_without_states_mandate()):
                current_state = shipping_billing_page.state.input_value()
                # select a state other than current and update current
                current_state = DashboardHelper.select_state(page, current_state, avoid_state=True)
                shipping_billing_page.save_button.click()
                framework_logger.info("Clicked Save button with different state value")
                shipping_billing_page.wait.original_address_option(timeout=10000)
                shipping_billing_page.original_address_option.click(force=True)
                shipping_billing_page.ship_to_this_address.click()
                expect(shipping_billing_page.error_message).to_be_visible(timeout=10000)
                shipping_billing_page.save_button.click()
                framework_logger.info("Clicked Save button with original address option")

            current_saved_address= shipping_billing_page.saved_address.nth(0).inner_html()
            assert current_value in current_saved_address, f"Expected '{current_value}' to be in '{current_saved_address}'"
            framework_logger.info("Saved address updated successfully")

            framework_logger.info("=== C38555183 -change shipping information flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
