from helper.ra_base_helper import RABaseHelper
from core.settings import framework_logger
import test_flows_common.test_flows_common as common

class FulfillmentServiceRAHelper:
    @staticmethod
    def access(page):
        page.goto(common._fulfillmentservice_url + common._agena_cps_and_fulfillment_rails_admin_login_url, timeout=120000)

        alert_locator = page.locator("div.alert-warning.alert.alert-dismissible")
        if alert_locator.is_visible():
            framework_logger.info("[FulfillmentServiceRAHelper] You are already signed in. Skipping login.")
            page.locator('a.nav-link[href="/"]').click()
            return

        page.locator("#admin_email, #admin_user_email").fill(common._rails_admin_user)
        page.locator("#admin_password, #admin_user_password").fill(common._rails_admin_password)
        page.locator("input[type='submit'][name='commit']").click()
        page.wait_for_load_state("networkidle", timeout=120000)

        if page.url == common._fulfillmentservice_url + common._agena_cps_and_fulfillment_rails_admin_login_url:
            page.locator("#admin_email, #admin_user_email").type(common._client_secrets.get("rails_admin_user"))
            page.locator("#admin_password, #admin_user_password").type(common._client_secrets.get("rails_admin_password"))
            page.locator("[name='commit']").click()

        page.locator('a.nav-link[href="/"]').click()

    @staticmethod
    def access_order_by_trigger_id(page, trigger_id):
        RABaseHelper.access_page(page, "Orders")
        page.locator("input[name='query']").type(trigger_id)
        page.click("button[type='submit']")

        options_td = "tr.order_row td.last ul.nav"
        link_selector = f"{options_td} li[title='Show'] a"
        link = page.wait_for_selector(link_selector, state="visible", timeout=5000)
        link.click()
        RABaseHelper.wait_page_to_load(page, "Order")

    @staticmethod
    def receive_and_send_order(page, trigger_id):
        order_link = FulfillmentServiceRAHelper.validate_order_received(page, trigger_id=trigger_id)
        FulfillmentServiceRAHelper.send_order(page)

        return order_link
    
    @staticmethod
    def send_order(page):
        RABaseHelper.access_menu_of_page(page, "Send Order")
        page.wait_for_selector("[class^='alert-']")

    @staticmethod
    def validate_order_received(page, status="statusNew", shipping="standard", trigger_id=None, order_link=None):
        if trigger_id:
            FulfillmentServiceRAHelper.access(page)
            FulfillmentServiceRAHelper.access_order_by_trigger_id(page, trigger_id)
        elif order_link:
            FulfillmentServiceRAHelper.access(page)
            page.goto(order_link)

        FulfillmentServiceRAHelper.validate_shipping_fields(page, status, shipping)
        return page.url
    
    @staticmethod
    def validate_shipping_fields(page, status, shipping):  
        assert common.find_field_text_by_header(page, "Status from fulfiller") == status, (
            f"Status from fulfiller mismatch: expected '{status}', "
            f"got '{common.find_field_text_by_header(page, 'Status from fulfiller')}'"
        )

        assert common.find_field_text_by_header(page, "Overall part status") == status, (
            f"Overall part status mismatch: expected '{status}', "
            f"got '{common.find_field_text_by_header(page, 'Overall part status')}'"
        )

        assert common.find_field_text_by_header(page, "Shipping option") == shipping, (
            f"Shipping option mismatch: expected '{shipping}', "
            f"got '{common.find_field_text_by_header(page, 'Shipping option')}'"
        )

    @staticmethod
    def update_order_error_code(page, error_code):
        # Access the Edit menu
        RABaseHelper.access_menu_of_page(page, "Edit")

        # Set the error code field
        error_code_field = page.locator("#order_error_code")
        error_code_field.fill(error_code)
        framework_logger.info(f"Set error code field to: {error_code}")

        save_button = page.locator("[name='_save'][type='submit']")
        save_button.scroll_into_view_if_needed()
        save_button.click()
        framework_logger.info(f"Order updated with error code: {error_code}")
