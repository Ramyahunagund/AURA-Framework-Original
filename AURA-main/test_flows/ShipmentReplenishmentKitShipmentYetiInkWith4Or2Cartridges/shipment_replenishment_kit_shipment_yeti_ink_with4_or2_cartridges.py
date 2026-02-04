from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from helper.ra_base_helper import RABaseHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def shipment_replenishment_kit_shipment_yeti_ink_with4_or2_cartridges(stage_callback):
    tenant_email = create_ii_subscription(stage_callback)

    colors = common.printer_colors()
    if len(colors) == 2:
        tc = "C32208348"
    elif len(colors) == 4:
        tc = "C32225182"

    framework_logger.info(f"=== {tc} - Shipment Replenishment Kit Shipment Yeti ink with {len(colors)} cartridges flow started ===")

    with PlaywrightManager() as page:
        try:            
            # Replenishment kit shipped with c,m,y,k or k,cmy colors 
            trigger_id = GeminiRAHelper.process_new_kit(page, tenant_email, "replenishment")
            framework_logger.info(f"Gemini Rails Admin: New cartridge send by trigger_id: {trigger_id}")

            # Verify if the fulfillment service receives order with standard shipping speed and send that order
            fulfillment_service_order_link = FFSRV.receive_and_send_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} received and sent. Order link: {fulfillment_service_order_link}")

            # Update order with statusShipped, DHL shipping vendor, random tracking number and run CheckSqsOrderStatusUpdateJob and GeminiCallbackDispatcherJob
            FFSIML.process_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Simulator: Order {trigger_id} processed successfully")

            # Verify order data
            FFSRV.validate_order_received(page, "statusShipped", "standard", trigger_id=trigger_id, order_link=fulfillment_service_order_link)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} updated and verified successfully")

            # Click link with text Shipment in the Shipments on Subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "Shipment", "Shipments")
            framework_logger.info(f"Accessed Details for Shipment page")

            # Sees Status equals to statusClosed on Details for Shipment page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "statusClosed")

            framework_logger.info(f"=== {tc} - Shipment Replenishment Kit Shipment Yeti ink with {len(colors)} cartridges flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
