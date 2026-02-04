# test_flows/IIFlipConversionCAYesShippingNoBilling/ii_flip_conversion_ca_yes_shipping_no_billing.py

# test_flows/IIFlipConversion/ii_flip_conversion.py
import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from pages.confirmation_page import ConfirmationPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def ii_flip_conversion_ca_yes_shipping_no_billing(stage_callback) -> None:
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

            EnrollmentHelper.add_shipping_flip_auto_fill(page, index=1)
            framework_logger.info("Added shipping info")   
            EnrollmentHelper.close_billing_or_shipping_modal(page)
            framework_logger.info("Closed billing or shipping modal if it appeared")
        
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== Enrollment completed successfully ===")

            DashboardHelper.access(page)
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("=== Dashboard launched successfully ===")
            new_tab = None
            with page.expect_popup() as popup_info:
                DashboardHelper.flip_conversion_enroll_now(page)
                framework_logger.info(f"Clicked on Enroll Now button")
            new_tab = popup_info.value
            new_tab.wait_for_load_state()
            framework_logger.info("Switched to new tab after Enroll Now")
           

            if new_tab:
                confirmation_page = ConfirmationPage(new_tab)
                EnrollmentHelper.close_billing_or_shipping_modal(new_tab)
                framework_logger.info("Closed billing or shipping modal if it appeared")
                EnrollmentHelper.edit_plan(new_tab, 50)
                framework_logger.info("Changed plan to 50 pages")
                confirmation_page = ConfirmationPage(new_tab)
                assert confirmation_page.enroll_step_skip_button.is_visible(), "Skip Now button is not visible"
                framework_logger.info("Skip Now button is visible")
                assert confirmation_page.enroll_step_skip_button.is_enabled(), "Skip Now button is not enabled"
                framework_logger.info("Skip Now button is enabled")
                assert confirmation_page.shipping_card.is_visible(), "Shipping card is not visible"
                framework_logger.info("Shipping card is visible")
                EnrollmentHelper.see_details_special_offer(new_tab)
                framework_logger.info("Clicked on See details for special offers")
                EnrollmentHelper.payment_method_required(new_tab)
                framework_logger.info("Payment method is required as expected")

                EnrollmentHelper.add_billing(new_tab)
                framework_logger.info("Added billing info")
                
                assert confirmation_page.billing_card.is_visible(), "Billing card is not visible"
                framework_logger.info("Billing card is visible")
                time.sleep(5)  # Wait for 5 seconds to ensure all elements are loaded    
                assert confirmation_page.flip_paper_addon_container.is_visible(timeout=100000), "Flip paper addon container is not visible"
                framework_logger.info("Flip paper addon container is visible")

                EnrollmentHelper.finish_enrollment(new_tab)
                framework_logger.info("=== Enrollment completed successfully ===")
            else:
                framework_logger.error("New tab was not created. Enrollment steps could not be completed.")

        except Exception as e:
            framework_logger.error(f"An error occurred during the Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
