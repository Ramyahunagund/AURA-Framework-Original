import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from pages import dashboard_side_menu_page
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.shipping_billing_page import ShippingBillingPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def ii_flip_shipping_dashboard(stage_callback) -> None:
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
            overview_page = OverviewPage(page)
            side_menu = DashboardSideMenuPage(page)
            shipping_billing_page = ShippingBillingPage(page)
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
            if GlobalState.biz_model == "Flex" and hpplus_action == "decline":
                OssEmulatorHelper.decline_hp_plus(page)
                framework_logger.info(f"Declined HP+")
                
                # Continue on dynamic security notice
                OssEmulatorHelper.continue_dynamic_security_notice(page)
                framework_logger.info(f"Continued on dynamic security notice")
            
            elif(GlobalState.biz_model == "Flex" and hpplus_action == "activate"):
                OssEmulatorHelper.activate_hp_plus(page)
                framework_logger.info(f"Activated HP+")
            elif(GlobalState.biz_model == "E2E" and hpplus_action == "ignore"):
                framework_logger.info(f"Continued flow")
            else:
                   # Continue with the next steps if neither condition is met
                    framework_logger.info("No HP+ action required, continuing enrollment flow.")   

            EnrollmentHelper.flip_skip_free_months(page)
            framework_logger.info("Skipped free months")
        
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== Enrollment completed successfully ===")

            DashboardHelper.first_access(page, tenant_email=tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")

            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.my_account_menu_link.click()
            dashboard_side_menu_page.shipping_billing_submenu_link.click()
            
             # Click Change Billing Info link in Overview page
            shipping_billing_page = ShippingBillingPage(page)
            shipping_billing_page.manage_shipping_address.click()
            framework_logger.info("Clicked Manage your shipping address link")

            DashboardHelper.add_shipping(page)
            framework_logger.info("Added shipping information")

            time.sleep(30)  # Wait for 30 seconds to ensure the changes are saved
    
            # Navigate back to Overview to verify changes
            DashboardHelper.first_access(page, tenant_email=tenant_email)
            framework_logger.info("Navigated back to Overview page")

            with page.expect_popup() as popup_info:
                DashboardHelper.flip_conversion_enroll_now(page)
                framework_logger.info("Clicked on Enroll Now button")
                new_tab = popup_info.value  

            new_tab.wait_for_load_state()
            framework_logger.info("Switched to new tab after Enroll Now")

            EnrollmentHelper.add_billing(new_tab)
            framework_logger.info("Added billing information")

            EnrollmentHelper.finish_enrollment(new_tab)
            framework_logger.info("=== Enrollment completed successfully ===")
            new_tab.close()
            framework_logger.info("Closed the new tab and returned to the original page")

        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()