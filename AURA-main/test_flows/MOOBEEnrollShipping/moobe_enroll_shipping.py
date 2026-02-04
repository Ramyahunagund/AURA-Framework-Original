
import time
import urllib3
import traceback

import test_flows_common.test_flows_common as common
from core.playwright_manager import PlaywrightManager
from helper.enrollment_helper import EnrollmentHelper
from core.settings import framework_logger
from core import utils
from helper.oss_emulator_helper import OssEmulatorHelper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"


def moobe_enroll_shipping(stage_callback):

    framework_logger.info("=== MOOBE order review flow started ===")
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

            #Select plan
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Selected plan 100")

            #again vinod code start from here

            # Save button: https://hp-testrail.external.hp.com/index.php?/cases/view/27368505
            # framework_logger.info("==== C27368505-Your Plan-Save Button ====")
            # EnrollmentHelper.select_plan_v3(page, plan_value='100', paper=False, callback=stage_callback,confirm=False)
            # framework_logger.info("Ink only plan selected")
            # stage_callback("ink_only_selected", page, screenshot_only=True)

            # Choose HP Checkout
            stage_callback("hp_checkout", page, screenshot_only=True)
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Choose HP Checkout")

            # Shipping modal: https://hp-testrail.external.hp.com/index.php?/cases/view/27368680
            # Save button: https://hp-testrail.external.hp.com/index.php?/cases/view/27368682
            framework_logger.info("==== C27368507-C27368508-C27368511-Shipping-Shipping Card-shipping modal-save button ====")
            EnrollmentHelper.add_shipping(page, additional_check=True)
            framework_logger.info(f"Shipping added successfully")

            # Modal Close: https://hp-testrail.external.hp.com/index.php?/cases/view/27368681
            # Mandatory Fields: https://hp-testrail.external.hp.com/index.php?/cases/view/27368687
            framework_logger.info("==== C27368510-C27368515-Shipping-Modal Close-Mandatory Fields ====")
            EnrollmentHelper.shipping_modal_close(page, callback=stage_callback, mandatory_fields_check=True)
            framework_logger.info("Shipping Modal & Mandatory Fields Successfully.")

            # Edit Shipping: https://hp-testrail.external.hp.com/index.php?/cases/view/27368686
            framework_logger.info("==== C27368514-Shipping-Edit Shipping ====")
            EnrollmentHelper.edit_shipping_check(page, callback=stage_callback)
            framework_logger.info("Edit Shipping successfully.")

            # Enter Promo or PIN code link: https://hp-testrail.external.hp.com/index.php?/cases/view/31628339
            # Special Offer Benefits(SOB) modal: https://hp-testrail.external.hp.com/index.php?/cases/view/31628338
            # Special Offers section: https://hp-testrail.external.hp.com/index.php?/cases/view/31628340
            # Breakdown of credits section: https://hp-testrail.external.hp.com/index.php?/cases/view/31628341
            # Promo code: https://hp-testrail.external.hp.com/index.php?/cases/view/27819821
            # RaF code: https://hp-testrail.external.hp.com/index.php?/cases/view/28005024
            # EK code: https://hp-testrail.external.hp.com/index.php?/cases/view/28093862
            framework_logger.info("==== C31628346-C31628345-C31628347-C31628348-C29548951-C29548952-C29548953-SOB-Enter Promo or PIN code link-Special Offer Benefits(SOB) modal-Special Offers section-Breakdown of credits section-Promo code-RaF code-EK code ====")
            EnrollmentHelper.special_offer_benefits(page, 'vb5tyb', callback=stage_callback)
            framework_logger.info(f"Special Offer benefit added successfully")


        except Exception as e:
            framework_logger.error(f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
