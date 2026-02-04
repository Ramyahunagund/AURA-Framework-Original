import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from helper.gemini_ra_helper import GeminiRAHelper
from helper.overview_helper import OverviewHelper
from helper.ra_base_helper import RABaseHelper
from helper.shipment_tracking_helper import ShipmentTrackingHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def wk_event_trigger(stage_callback) -> None:
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info("=== C35469623 -  WelcomeKit Event Trigger flow started ===")

    with PlaywrightManager() as page:
        try:
            # Send new WK
            trigger_id = GeminiRAHelper.process_new_kit(page, tenant_email)
            framework_logger.info(f"Gemini Rails Admin: New cartridge sent by trigger_id: {trigger_id}")

            # Verify Order and send it to Fulfillment Simulator
            fulfillment_service_order_link = FFSRV.receive_and_send_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} received and sent. Order link: {fulfillment_service_order_link}")

            # Update order
            FFSIML.process_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Simulator: Order {trigger_id} processed successfully")

            # Verify Order
            FFSRV.validate_order_received(page, "statusShipped", "standard", trigger_id, order_link=fulfillment_service_order_link)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} updated and verified successfully")

            # GRA subscription verify Notification events
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "shipment", "Notification events")
            status = RABaseHelper.get_field_text_by_title(page, "Status")
            assert status == "complete" or status == "sent", f"Expected status to be 'complete' or 'sent', but got '{status}'"
            framework_logger.info(f"Gemini Rails Admin: Notification events verified for tenant {tenant_email}")

            # Click the Template Data and check if "servaccount_consent_ii" is displayed.
            RABaseHelper.access_menu_of_page(page, "Template Data")
            template_data = GeminiRAHelper.get_template_data(page, "servaccount_consent_ii")
            assert template_data is None, f"Expected servaccount_consent_ii to be None, but got '{template_data}'"
            framework_logger.info(f"Gemini Rails Admin: 'servaccount_consent_ii' template data is Null as expected.")

            framework_logger.info("=== C35469623 -  WelcomeKit Event Trigger flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the fulfillment Enrollment: {e}\n{traceback.format_exc()}")
            raise e
