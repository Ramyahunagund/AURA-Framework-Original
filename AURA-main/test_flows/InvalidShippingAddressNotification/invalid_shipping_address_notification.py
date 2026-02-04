from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.ra_base_helper import RABaseHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def invalid_shipping_address_notification(stage_callback):
    framework_logger.info("=== C27803395 - Invalid Shipping Address Notification flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        dashboard_side_menu_page = DashboardSideMenuPage(page)

        try:
            # Access subscription and ensure it's in subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Update subscription RPL state to clear
            GeminiRAHelper.update_subscription_rpl(page)
            framework_logger.info(f"Subscription RPL state updated to clear")

            # Ship welcome kit (standard shipping speed)
            trigger_id = GeminiRAHelper.ship_cartridge(page, "welcome", colors=None)
            framework_logger.info(f"Gemini Rails Admin: Welcome kit sent with trigger_id: {trigger_id}")

            # Verify if the fulfillment service receives order with standard shipping speed and send that order
            fulfillment_service_order_link = FFSRV.receive_and_send_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} received and sent. Order link: {fulfillment_service_order_link}")

            # Go to fulfillment simulator and update order with statusError status, DHL shipping vendor and tracking number
            FFSIML.access(page)
            FFSIML.access_order_by_trigger_id(page, trigger_id)
            FFSIML.update_order(page, "statusError", tracking_number="123124")
            framework_logger.info(f"Fulfillment Simulator: Order {trigger_id} updated with statusError")

            # IIC and IPH are ink-based supply variants, so default to error code 3
            supply_variant = common._supplyvariant
            error_code = "3" 

            if supply_variant and "toner" in supply_variant.lower():
                error_code = "4"

            # Update error code in Fulfillment Service
            FFSRV.access(page)
            FFSRV.access_order_by_trigger_id(page, trigger_id)
            FFSRV.update_order_error_code(page, error_code)
            framework_logger.info(f"Fulfillment Service: Error code {error_code} set for order {trigger_id} (supply variant: {supply_variant})")

            # Run resque jobs: CheckSqsOrderStatusUpdateJob and GeminiCallbackJob
            RABaseHelper.complete_jobs(page, 
                                        common._fulfillmentservice_url, 
                                        ["CheckSqsOrderStatusUpdateJob", 
                                        "GeminiCallbackDispatcherJob"])
            framework_logger.info("Resque jobs CheckSqsOrderStatusUpdateJob and GeminiCallbackDispatcherJob completed")

            # Verify Rails Admin notification event
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "shipment_issue", "Notification events")
            framework_logger.info("Accessed shipment_issue from Notification events")

            # Verify Status equals to 'sent' or 'complete'
            status_text = RABaseHelper.get_field_text_by_title(page, "Status")
            assert status_text in ["sent", "complete"], f"Expected status 'sent' or 'complete', but got '{status_text}'"
            framework_logger.info(f"Notification event status verified: {status_text}")

            # Access Dashboard page and verify Smart Dashboard notifications
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Dashboard first access completed successfully")

            # Expand My Account Menu and click on Notifications
            dashboard_side_menu_page.expand_my_account_menu()
            dashboard_side_menu_page.click_notifications()
            framework_logger.info("Accessed Smart Dashboard Notifications page")

            # Verify "Shipment undeliverable!" notification
            DashboardHelper.see_notification_on_dashboard(page, "Shipment undeliverable!")
            framework_logger.info("Verified 'Shipment undeliverable!' notification on Smart Dashboard")

            framework_logger.info("=== C27803395 - Invalid Shipping Address Notification flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the invalid shipping address notification flow: {e}\n{traceback.format_exc()}")
            raise e