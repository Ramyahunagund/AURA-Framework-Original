import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.email_helper import EmailHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.shipment_tracking_helper import ShipmentTrackingHelper
from helper.hpid_helper import HPIDHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def rk_shipment_for_largest_plan(stage_callback):
    framework_logger.info("=== C38292362 - RK shipment for largest plan flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # Claim virtual printer and add address
        common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        try:
            # start enrollment 
            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # sign in method
            HPIDHelper.complete_sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in")

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 700)
            framework_logger.info(f"Plan selected: 700")

            # billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing added")

            # finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Update subscription RPL state to clear
            GeminiRAHelper.update_subscription_rpl(page)
            framework_logger.info(f"Subscription RPL state updated to clear")

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
            
            # And the user sees the email with subject "subscription cartridges have shipped"
            EmailHelper.sees_email_with_subject(tenant_email, subject="subscription cartridges have shipped")
            framework_logger.info(f"Received email with subject 'subscription cartridges have shipped'")
            framework_logger.info("=== C38292362 - RK shipment for largest plan flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the enrollment: {e}\n{traceback.format_exc()}")
