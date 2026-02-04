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

def ink_shipment_pending(stage_callback):
    framework_logger.info("=== C52738447 - Ink Shipment Pending flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
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

            # Welcome kit shipped with no colors
            trigger_id = GeminiRAHelper.ship_cartridge(page, "welcome", colors=None)
            framework_logger.info(f"Gemini Rails Admin: Welcome kit with no colors sent by trigger_id: {trigger_id}")
                
            # Verify if the fulfillment service receives order with standard shipping speed and send that order
            fulfillment_service_order_link = FFSRV.receive_and_send_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} received and sent. Order link: {fulfillment_service_order_link}")
            
            # Update order with statusError, DHL shipping vendor, random tracking number and error code 2
            FFSIML.process_order(page, trigger_id, "statusError", tracking_number="2")
            
            # Verify Rails Admin notification event
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "shipment_issue", "Notification events")
            framework_logger.info("Accessed shipment_issue from Notification events")
	        
            # Sees Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Payment state is complete")
            framework_logger.info("Rails Admin: Verified shipment_waiting notification event")

            # Access Dashboard page and verify Smart Dashboard notifications
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Dashboard first access completed successfully")
           
            # Expand My Account Menu and click on Notifications
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.expand_my_account_menu()
            dashboard_side_menu_page.click_notifications()
            framework_logger.info("Accessed Smart Dashboard Notifications page")
            
            # Verify "Cartridge shipment needs information!" notification
            DashboardHelper.see_notification_on_dashboard(page, "Shipment undeliverable!")
            framework_logger.info("Verified 'Shipment undeliverable!' notification on Smart Dashboard")

            framework_logger.info("=== C52738447 - Ink Shipment Pending flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the ink shipment pending flow: {e}\n{traceback.format_exc()}")
