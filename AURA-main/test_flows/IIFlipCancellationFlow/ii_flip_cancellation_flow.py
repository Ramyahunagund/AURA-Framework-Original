import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.shipping_billing_page import ShippingBillingPage
from helper.update_plan_helper import UpdatePlanHelper
from helper.cancellation_plan_helper import CancellationPlanHelper
from pages.update_plan_page import UpdatePlanPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def ii_flip_cancellation_flow(stage_callback) -> None:
    framework_logger.info("=== Enrollment OOBE flow started ===")
    common.setup()
    test_requirements = GlobalState.requirements
    hpplus_action = test_requirements.get("hpplus")
  
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
            #select country
            OssEmulatorHelper.country_select(page)
            framework_logger.info("Selected country")
            #if flex DEcline HP+, if flex and want HP+ activate it
            framework_logger.info(f"Activating HP+")  

            EnrollmentHelper.add_shipping_flip_auto_fill(page)
            framework_logger.info("shipping added with autofill")

            EnrollmentHelper.add_billing(page)
            framework_logger.info("Added billing")  
        
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== Enrollment completed successfully ===")

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

            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("=== Instant Ink subscription canceled ===")
            CancellationPlanHelper.select_cancellation_feedback_option(page, feedback_option="I do not print enough", submit=True)
            framework_logger.info("=== Cancellation feedback option selected ===")
            DashboardHelper.sees_cancellation_in_progress(page)
            framework_logger.info("=== Cancellation in progress section is visible ===")
            DashboardHelper.verify_cancellation_banner_message(page, "Your subscription will end on")
            framework_logger.info("Verified cancellation banner message")
            DashboardHelper.verify_end_date_on_cancellation_banner(page)
            framework_logger.info("=== End date on cancellation banner verified ===")
            DashboardHelper.validate_see_cancellation_timeline_feature(page)
            framework_logger.info("=== Cancellation timeline feature validated ===")
 
            DashboardHelper.keep_subscription(page, confirm=False)
            framework_logger.info("Clicked on back button in Keep Subscription modal")
            time.sleep(15)
            DashboardHelper.keep_subscription(page)
            framework_logger.info("=== Subscription kept successfully ===")
            DashboardHelper.verify_subscription_resumed_banner(page,"Your Instant Ink subscription has resumed.")
            framework_logger.info("=== Subscription resumed banner verified ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()