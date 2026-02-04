
import time
import urllib3
import traceback

import test_flows_common.test_flows_common as common
from core.playwright_manager import PlaywrightManager
from helper.enrollment_helper import EnrollmentHelper
from core.settings import framework_logger
from core import utils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"


def oobe_enroll_step(stage_callback):
    framework_logger.info("=== Instant Ink - OOBE Core - Enroll Step ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # Create a new HP ID account
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)
            stage_callback("ii_v2_account", page, screenshot_only=True)

            # Click on Sign Up Now button
            with page.context.expect_page() as new_page_info:
                EnrollmentHelper.signup_now(page)
                framework_logger.info("Sign Up Now button clicked")
            page = new_page_info.value
            stage_callback("signup_now", page, screenshot_only=True)

            # Accept Terms of Service
            EnrollmentHelper.accept_terms_of_service(page)
            framework_logger.info("Terms of Service accepted")

            # Select monthly plan type card
            EnrollmentHelper.select_plan_type(page)
            framework_logger.info("Plan type card selected successfully")
            stage_callback("monthly_plan_type_selected", page, screenshot_only=True)

            # # Modal close: https://hp-testrail.external.hp.com/index.php?/cases/view/27368504
            framework_logger.info("==== C27368504-Your Plan-Modal Close ====")
            EnrollmentHelper.click_learn_more(page, paper=False, callback=stage_callback)

            # Save button: https://hp-testrail.external.hp.com/index.php?/cases/view/27368505
            framework_logger.info("==== C27368505-Your Plan-Save Button ====")
            EnrollmentHelper.select_plan_v3(page, plan_value='100', paper=False, callback=stage_callback)
            framework_logger.info("Select plan successfully")
            stage_callback("ink_only_selected", page, screenshot_only=True)

            # # Different plans: https://hp-testrail.external.hp.com/index.php?/cases/view/27368506
            framework_logger.info("==== C27368506-Your Plan-Different Plans ====")
            EnrollmentHelper.edit_plan_check(page, plan_value='300', paper=True, callback=stage_callback)
            framework_logger.info("Edit plan successfully")
            stage_callback("edit_ink_only_selected", page, screenshot_only=True)

            # Choose HP Checkout
            stage_callback("hp_checkout", page, screenshot_only=True)
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Choose HP Checkout")

            # Shipping card: https://hp-testrail.external.hp.com/index.php?/cases/view/27368507
            # Shipping modal: https://hp-testrail.external.hp.com/index.php?/cases/view/27368508
            # Save button: https://hp-testrail.external.hp.com/index.php?/cases/view/27368511
            framework_logger.info("==== C27368507-Shipping-Shipping Card ====")
            framework_logger.info("==== C27368508-Shipping-Shipping modal ====")
            framework_logger.info("==== C27368511-Shipping-Save button====")
            EnrollmentHelper.add_shipping(page, additional_check=True)
            framework_logger.info(f"Add shipping successfully")

            # Modal Close: https://hp-testrail.external.hp.com/index.php?/cases/view/27368510
            # Mandatory Fields: https://hp-testrail.external.hp.com/index.php?/cases/view/27368515
            framework_logger.info("==== C27368510-Shipping-Modal Close ====")
            framework_logger.info("==== C27368515-Shipping-Mandatory Fields ====")
            EnrollmentHelper.shipping_modal_close(page, callback=stage_callback, mandatory_fields_check=True)
            framework_logger.info("Shipping Modal & Mandatory Fields Successfully.")

            # Edit Shipping: https://hp-testrail.external.hp.com/index.php?/cases/view/27368514
            framework_logger.info("==== C27368514-Shipping-Edit Shipping ====")
            EnrollmentHelper.edit_shipping_check(page, callback=stage_callback)
            framework_logger.info("Edit Shipping successfully.")

            # Enter Promo or PIN code link: https://hp-testrail.external.hp.com/index.php?/cases/view/31628346
            # Special Offer Benefits(SOB) modal: https://hp-testrail.external.hp.com/index.php?/cases/view/31628345
            # Special Offers section: https://hp-testrail.external.hp.com/index.php?/cases/view/31628347
            # Breakdown of credits section: https://hp-testrail.external.hp.com/index.php?/cases/view/31628348
            # Promo code: https://hp-testrail.external.hp.com/index.php?/cases/view/29548951
            # RaF code: https://hp-testrail.external.hp.com/index.php?/cases/view/29548952
            # EK code: https://hp-testrail.external.hp.com/index.php?/cases/view/29548953
            # framework_logger.info("==== C31628346-C31628345-C31628347-C31628348-C29548951-C29548952-C29548953-SOB-Enter Promo or PIN code link-Special Offer Benefits(SOB) modal-Special Offers section-Breakdown of credits section-Promo code-RaF code-EK code ====")
            framework_logger.info("==== C31628346-Entering Special Offer Benefits ====")
            framework_logger.info("==== C31628345-SOB Modal Verification ====")
            framework_logger.info("==== C31628347-Special Offers Section Verification ====")
            framework_logger.info("==== C31628348-Breakdown of credits section Verification ====")
            framework_logger.info("==== C29548951-Promo Code Entry ====")
            framework_logger.info("==== C29548952-RaF Code Entry ====")
            framework_logger.info("==== C29548953-EK Code Entry ====")
            EnrollmentHelper.special_offer_benefits(page, 'vb5tyb', callback=stage_callback)
            framework_logger.info(f"Special Offer benefit added successfully")

            # framework_logger.info("======== Billing: Billing card ========")
            framework_logger.info("==== C27368518-Billing-Billing card ====")
            framework_logger.info("==== C27368519-Billing-Billing card enabled ====")
            EnrollmentHelper.billing_card(page, card_type="credit_card_master")
            stage_callback("billing_card_selected", page, screenshot_only=True)
            framework_logger.info("Billing card selected successfully")

        except Exception as e:
            framework_logger.error(f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
