import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
import test_flows_common.test_flows_common as common
from pages.confirmation_page import ConfirmationPage
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def ii_flip_enrollment_with_prepaid_ca(stage_callback) -> None:
    framework_logger.info("=== Enrollment OOBE flow started ===")
    common.setup()
    test_requirements = GlobalState.requirements
    plan_pages = test_requirements.get("plan_pages")
    hpplus_action = test_requirements.get("hpplus")
    amount_greater = test_requirements.get("amount_greater")
    plan_change = test_requirements.get("plan_change")

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
            time.sleep(5)
            EnrollmentHelper.add_shipping_flip_auto_fill(page, index=1)
            framework_logger.info("Added shipping info")
            EnrollmentHelper.close_billing_or_shipping_modal(page)
            framework_logger.info("Closed billing or shipping modal if it appeared")
            confirmation_page = ConfirmationPage(page)
            if plan_change == "False" and amount_greater == "True":
                EnrollmentHelper.add_prepaid_by_value(page,300,True)
                framework_logger.info("Added prepaid card by value") 
                EnrollmentHelper.see_details_special_offer(page)
                framework_logger.info("See details of special offer")
                assert confirmation_page.flip_skip_button.is_enabled(), "Skip Now button is not enabled"
                assert confirmation_page.flip_shipping_container.is_visible(), "Shipping card is not visible"
                assert confirmation_page.flip_paper_addon_container.is_visible(timeout=100000), "Flip paper addon container is not visible"
                framework_logger.info("Flip paper addon container is visible")
            elif plan_change == "False" and amount_greater == "False":
                EnrollmentHelper.add_prepaid_by_value(page,1500,False)
                framework_logger.info("Added prepaid card by value")
                assert confirmation_page.flip_skip_button.is_enabled(), "Skip Now button is not enabled"
                assert confirmation_page.flip_shipping_container.is_visible(), "Shipping card is not visible"        
                #assert confirmation_page.flip_paper_addon_container.is_visible(timeout=100000), "Flip paper addon container is not visible"
            elif plan_change == "True" and amount_greater == "False":
                EnrollmentHelper.add_prepaid_by_value(page,1500,False)
                framework_logger.info("Added prepaid card by value")
                assert confirmation_page.flip_skip_button.is_enabled(), "Skip Now button is not enabled"
                assert confirmation_page.flip_shipping_container.is_visible(), "Shipping card is not visible"
                EnrollmentHelper.edit_plan(page, 10)
                framework_logger.info("Changed plan to 10 pages")
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== Enrollment completed successfully ===")

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info("=== Gemini RA accessed successfully ===")

            approval_date = GeminiRAHelper.flip_approval_date(page)
            if approval_date != "-":
                framework_logger.info(f"Approval date is {approval_date}")
            else:
                framework_logger.info("Approval date is not set")           
  
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
    




