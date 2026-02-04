import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.shipment_tracking_helper import ShipmentTrackingHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def ii_enrollment_oobe(stage_callback) -> None:
    framework_logger.info("=== Enrollment OOBE flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    # Create virtual printer
    printer = common.create_virtual_printer()

    # Create new HPID account and setup OSS Emulator
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)

            # Setup OSS Emulator for OOBE
            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info(f"OSS Emulator setup completed")

            # Accept connected printing services
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info(f"Accepted connected printing services")
         
            framework_logger.info(f"Activating HP+")

            # Continue on value proposition
            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")

            # Accept automatic printer updates
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Accepted automatic printer updates")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Select plan
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Selected plan 100")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Added shipping info")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            # Skip Paper Offer
            EnrollmentHelper.skip_paper_offer(page)
            framework_logger.info(f"Skipped paper offer")

            # Finish Enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== OOBE Enrollment completed successfully ===")

            # Launch Dashboard
            DashboardHelper.access(page)
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("=== Dashboard launched successfully ===")
            DashboardHelper.sees_status_card(page)
            framework_logger.info("=== Status card checked ===")
            DashboardHelper.sees_plan_details_card(page)
            plan_value = DashboardHelper.get_plan_value_from_plan_details(page)
            DashboardHelper.verify_plan_value(page, plan_value)
            framework_logger.info("=== Plan details card checked ===")
            DashboardHelper.verify_free_months_value(page,6)
            framework_logger.info("=== Free months value checked ===")

            DashboardHelper.verify_footer_section(page)
            framework_logger.info("=== Footer section verified ===")

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info("=== Gemini RA accessed successfully ===")
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("=== Subscription is in Subscribed status ===")
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info("=== Free months removed successfully ===")
                
            DashboardHelper.access(page)
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("=== Dashboard launched successfully ===")
            
            # Cancel Instant Ink
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("=== Instant Ink subscription canceled ===")
            CancellationPlanHelper.select_cancellation_feedback_option(page, feedback_option="I do not print enough", submit=True)
            framework_logger.info("=== Cancellation feedback option selected ===")
            
            DashboardHelper.sees_cancellation_in_progress(page)
            framework_logger.info("=== Cancellation in progress section is visible ===")
           
            DashboardHelper.verify_end_date_on_cancellation_banner(page)
            framework_logger.info("=== End date on cancellation banner verified ===")
            DashboardHelper.validate_see_cancellation_timeline_feature(page)
            framework_logger.info("=== Cancellation timeline feature validated ===")
            DashboardHelper.keep_subscription(page, confirm=False)
            framework_logger.info("Clicked on back button in Keep Subscription modal")
            time.sleep(10)  # Wait for UI to update after closing modal
            DashboardHelper.keep_subscription(page, confirm=True)
            framework_logger.info("Confirmed to keep the subscription")
            DashboardHelper.verify_subscription_resumed_banner(page,"Your Instant Ink subscription has resumed.")
            framework_logger.info("=== Subscription resumed banner verified ===")

            #Pause Plan
            DashboardHelper.pause_plan(page,1)
            framework_logger.info("=== Plan paused successfully ===")
            DashboardHelper.sees_plan_pause_banner(page)
            framework_logger.info("=== Paused plan is visible ===")
            DashboardHelper.click_resume_plan_banner(page)
            framework_logger.info("=== Resume plan banner clicked ===")
            DashboardHelper.click_keep_paused(page)
            framework_logger.info("=== Keep paused plan clicked ===")
            DashboardHelper.click_resume_plan_banner(page)
            framework_logger.info("=== Resume plan banner clicked ===")
            DashboardHelper.click_resume_plan(page)
            framework_logger.info("=== Resume plan clicked ===")
            DashboardHelper.click_pause_plan_link_and_close_modal(page)
            framework_logger.info("=== Pause plan link clicked and modal closed ===")   

            DashboardHelper.add_paper(page)
            framework_logger.info("=== Paper added successfully ===")  
            time.sleep(20)  

            DashboardHelper.access(page)
            DashboardHelper.first_access(page, tenant_email)

            DashboardHelper.cancel_instant_paper(page)  
            framework_logger.info("=== Instant Paper cancellation initiated successfully ===")
            
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            
            page.close()


