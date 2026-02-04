from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from helper.gemini_ra_helper import GeminiRAHelper
from helper.overview_helper import OverviewHelper
from helper.shipment_tracking_helper import ShipmentTrackingHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fulfillment(stage_callback) -> None:
    tenant_email = enrollment_ink_web(stage_callback)
    framework_logger.info("=== Fulfillment flow started ===")

    with PlaywrightManager() as page:
        try:
            # Send new WK
            trigger_id = GeminiRAHelper.process_new_wk(page, tenant_email)
            framework_logger.info(f"Gemini Rails Admin: New cartridge send by trigger_id: {trigger_id}")

            # Verify Order and send it to Fulfillment Simulator
            fulfillment_service_order_link = FFSRV.receive_and_send_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} received and sent. Order link: {fulfillment_service_order_link}")

            # Update order
            FFSIML.process_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Simulator: Order {trigger_id} processed successfully")

            # Verify Order
            FFSRV.validate_order_received(page, "statusShipped", "standard", trigger_id=trigger_id, order_link=fulfillment_service_order_link)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} updated and verified successfully")

            # GRA subscription verify Notification events
            GeminiRAHelper.verify_notification_events(page,"welcome_std-i_ink", tenant_email)
            framework_logger.info(f"Gemini Rails Admin: Notification events verified for tenant {tenant_email}")
                                  
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Dashboard first access completed successfully")
            
            # Dashboard verify cartridges on overview  
            OverviewHelper.verify_multiple_cartridge_types_installed_message(page, "k,cmy", "k,c,m,y")
            framework_logger.info("Dashboard cartridges verification completed successfully on Overview page")

            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.click_shipment_tracking()
            framework_logger.info("Dashboard Shipment Tracking page accessed successfully")

            # Dashboard verify cartridges on shipment tracking
            shipment_tracking_page = ShipmentTrackingPage(page)
            shipment_tracking_page.get_page_title()
            ShipmentTrackingHelper.verify_multiple_cartridge_types_installed_message(page, "k,cmy", "k,c,m,y")
            framework_logger.info("Dashboard cartridges verification completed successfully on Shipment Tracking page")

            framework_logger.info("fulfillment Enrollment completed successfully")
        except Exception as e:
            framework_logger.error(f"An error occurred during the fulfillment Enrollment: {e}\n{traceback.format_exc()}")
            raise e
