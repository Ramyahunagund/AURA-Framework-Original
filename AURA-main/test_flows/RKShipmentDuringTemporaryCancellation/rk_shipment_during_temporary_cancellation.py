from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.email_helper import EmailHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from helper.gemini_ra_helper import GeminiRAHelper
from helper.shipment_tracking_helper import ShipmentTrackingHelper
from helper.hpid_helper import HPIDHelper
from pages.cancellation_page import CancellationPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def rk_shipment_during_temporary_cancellation(stage_callback):
    framework_logger.info("=== C43905973 - RK shipment during temporary cancellation flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)

            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Clicks on Cancel Instant Ink Subscription button
            overview_page.plan_details_card.wait_for(timeout=90000)
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Cancel Instant Ink Subscription button clicked")

            # Pause InstantInk for 2 Months]
            DashboardHelper.pause_plan(page, 2, "Cancellation")
            framework_logger.info(f"Paused plan for 2 months on Overview page")

            # Charge a new billing cycle with 30 pages
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "30")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 30 pages")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Sees Plan pause pending banner on Overview page
            DashboardHelper.sees_plan_pause_banner(page)
            framework_logger.info(f"Verified Plan Pause banner on Overview page")

            # Update subscription RPL state to clear and Replenishment kit shipped with c,m,y,k or k,cmy colors 
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

            # Access Dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Dashboard first access completed successfully")
            
            # Access Shipment Tracking page
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.click_shipment_tracking()
            framework_logger.info("Dashboard Shipment Tracking page accessed successfully")

            # Verify shipment tracking table
            ShipmentTrackingHelper.verify_shipment_tracking_table(page)
            framework_logger.info("Dashboard shipment tracking table verification completed successfully")
            
            # Sees a new RK on Shipment Tracking
            ShipmentTrackingHelper.cartridge_installed_message(page)
            framework_logger.info("New RK verified on Shipment Tracking page")

            # Sees the Notification:Cartridge shipment confirmation!
            DashboardHelper.see_notification_on_bell_icon(page, "Cartridge shipment confirmation!")
            framework_logger.info("Notification: Cartridge shipment confirmation! verified")

            framework_logger.info("=== C43905973 - RK shipment during temporary cancellation flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the enrollment: {e}\n{traceback.format_exc()}")
