from helper.ra_base_helper import RABaseHelper
import test_flows_common.test_flows_common as common

class FulfillmentSimulatorRAHelper:
    @staticmethod
    def access(page):
        page.goto(common._fulfillmentsimulator_url+"/rails_admin")
        page.wait_for_load_state("networkidle"); page.wait_for_load_state("load")
        page.locator('a.nav-link[href="/"]').click()

    @staticmethod
    def access_order_by_trigger_id(page, trigger_id):
        RABaseHelper.access_page(page, "Orders")
        page.locator("input[name='query']").type(trigger_id)
        page.click("button[type='submit']")
        options_td = "tr.order_row td.last ul.nav"
        link_selector = f"{options_td} li[title='Show'] a"
        page.click(link_selector)
        RABaseHelper.wait_page_to_load(page, "Order")

    @staticmethod
    def update_order(page, status="statusShipped", tracking_number="123456789"):
        page.wait_for_selector("ul.nav.nav-tabs li a:has-text('Update order')").click()
        page.select_option("#order_status", value=status)
        page.select_option("select[id^='part_']", value=status)
        vendor = "DHL"
        page.locator("#shipping_vendor").fill(vendor)
        page.locator("#tracking_number").fill(tracking_number)
        page.locator('input[type=submit][value="Update"]').click()
        status_locator = page.locator('text=Call to Fulfillment Service returned status 201')
        status_locator.wait_for(state="visible")
        assert status_locator.is_visible(), "status 201' not found"

    @staticmethod
    def process_order(page, trigger_id, status="statusShipped", tracking_number="123456789"):
        FulfillmentSimulatorRAHelper.access(page)

        # FSMRA access order
        FulfillmentSimulatorRAHelper.access_order_by_trigger_id(page, trigger_id)

        # FSMRA update order
        FulfillmentSimulatorRAHelper.update_order(page, status, tracking_number)

        # FSVRA resque
        RABaseHelper.complete_jobs(page, common._fulfillmentservice_url, ["CheckSqsOrderStatusUpdateJob"])
        RABaseHelper.complete_jobs(page, common._fulfillmentservice_url, ["GeminiCallbackDispatcherJob"])