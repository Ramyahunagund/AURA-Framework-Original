
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from pages.confirmation_page import ConfirmationPage
import test_flows_common.test_flows_common as common
import time
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
TEMP_DIR = "temp"
 
# C28364108
def enrollment_moobe_visual(stage_callback) -> None:
    framework_logger.info("=== Enrollment MOOBE flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")
 
    # Create virtual printer
    printer = common.create_virtual_printer()
   
    # Create new HPID account and setup OSS Emulator
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)
            framework_logger.info(f"HPID account created successfully with email={tenant_email}")
           
            # Setup OSS Emulator for MOOBE
            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info(f"OSS Emulator setup completed")
 
            # Resize the window resolution
            page.set_viewport_size({"width": 400, "height": 740})
            framework_logger.info(f"Set viewport size to 400x740")
 
            # # Accept connected printing services
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info(f"Accepted connected printing services")
 
            # # Decline HP+ offer
            OssEmulatorHelper.decline_hp_plus(page)
            framework_logger.info(f"Declined HP+")
           
            # Continue on dynamic security notice
            OssEmulatorHelper.continue_dynamic_security_notice(page)
            framework_logger.info(f"Continued on dynamic security notice")
           
            # # Continue on value proposition
            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")
           
            # Select plan
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Selected plan 100")
 
            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")
 
            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Added shipping info") 
            
            # Pre Billing Ui validation
            # Billing card Enabled: https://hp-testrail.external.hp.com/index.php?/cases/view/51973575
            # Info icon : https://hp-testrail.external.hp.com/index.php?/cases/view/51973580
            EnrollmentHelper.validate_pre_billing_section_info(page)
            framework_logger.info("==== C51973575-Pre Billing Card Enabled  ====")
            framework_logger.info("==== C51973580-Pre Billing Info Icon Validation ====")

            # Billing Card : https://hp-testrail.external.hp.com/index.php?/cases/view/51973574
            # Add Billing : https://hp-testrail.external.hp.com/index.php?/cases/view/51973576
            # Billing modal(Step 1 of 2) : https://hp-testrail.external.hp.com/index.php?/cases/view/51973581
            # Select an account type : https://hp-testrail.external.hp.com/index.php?/cases/view/51973582
            # Billing section : https://hp-testrail.external.hp.com/index.php?/cases/view/51973584
            EnrollmentHelper.validate_billing_step_one_card_elements_layout(page)
            framework_logger.info("==== C51973574-Billing Card step_01 Layout Validation ====")
            framework_logger.info("==== C51973576-Add Billing step_01 pops up Validation ====")
            framework_logger.info("==== C51973581-Billing Section step_01 of 2 Layout Validation ====")
            framework_logger.info("==== C51973582-Billing Section account type radio button enable or disable ====")
            framework_logger.info("==== C51973584-Billing Section shipping add Validation ====")

            # Billing Modal (Step 2 of 2) : https://hp-testrail.external.hp.com/index.php?/cases/view/51973585
            # Credit card/PayPal option: https://hp-testrail.external.hp.com/index.php?/cases/view/51973586
            # Modal Close : https://hp-testrail.external.hp.com/index.php?/cases/view/51973578
            # Mandatory fields : https://hp-testrail.external.hp.com/index.php?/cases/view/51973579
            EnrollmentHelper.validate_billing_step_two_layout_elements(page)
            EnrollmentHelper.validate_company_name_and_tax_id_persistence(page)
            framework_logger.info("==== C51973585-Billing Modal step_02 of 2 Layout Validation ====")
            framework_logger.info("==== C51973586-Billing Modal Credit card/PayPal option Validation ====")
            framework_logger.info("==== C51973578-Billing Modal Close button Validation ====")

            #Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            # Layout: https://hp-testrail.external.hp.com/index.php?/cases/view/27368707
            framework_logger.info("========C27368707-Shipping Card Layout and button color ========")
            EnrollmentHelper.verify_shipping_card_layout(page)
            EnrollmentHelper.verify_shipping_tick_color(page)

            # Edit Shipping Address: https://hp-testrail.external.hp.com/index.php?/cases/view/27368708
            # blacklist postal code: https://hp-testrail.external.hp.com/index.php?/cases/view/27598826
            framework_logger.info("========C27368708&C27598826-Edit screen Existing shipping address ========")
            EnrollmentHelper.validate_edit_shipping_fields_and_close(page, additional_check=True)

            # Modal close: https://hp-testrail.external.hp.com/index.php?/cases/view/27368710
            # Empty Shipping : https://hp-testrail.external.hp.com/index.php?/cases/view/27368714
            framework_logger.info("========C27368710&C27368714-Shipping Modal & Mandatory Fields ========")
            EnrollmentHelper.shipping_modal_close(page, callback=stage_callback, mandatory_fields_check=True)
            framework_logger.info("Edit screen Existing shipping add & Shipping Modal & Mandatory Fields Successfully.")

            # Save Shipping: https://hp-testrail.external.hp.com/index.php?/cases/view/27368712
            framework_logger.info("========C27368712-Edit Shipping and Validation ========")
            EnrollmentHelper.edit_shipping_check(page, additional_check=True)
            EnrollmentHelper.verify_shipping_tick_color(page)
            framework_logger.info("Edit Shipping and Validation successfully.")

            # # Skip Paper Offer
            # EnrollmentHelper.skip_paper_offer(page)
            # framework_logger.info(f"Skipped paper offer")
            
            # # Finish Enrollment
            # EnrollmentHelper.finish_enrollment(page)
            # framework_logger.info("=== MOOBE Enrollment completed successfully ===") 

        except Exception as e:
            framework_logger.error(f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
