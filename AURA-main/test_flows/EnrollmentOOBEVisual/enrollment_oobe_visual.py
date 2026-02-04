from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
from core import utils
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def enrollment_oobe_visual(stage_callback) -> None:
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
            

            try:
                page.wait_for_selector(f"div.option[id='{common._tenant_country_short}']", timeout=10000)
                page.locator(f"div.option[id='{common._tenant_country_short}']").click()
                page.locator('[class="footer-2"] button').click()
            except Exception as e:
                framework_logger.info(f"Don't need to select country")

            # Decline
            OssEmulatorHelper.decline_hp_plus(page)
            framework_logger.info(f"Declined HP+")

            # Continue on dynamic security notice
            OssEmulatorHelper.continue_dynamic_security_notice(page)
            framework_logger.info(f"Continued on dynamic security notice")

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

            price = None
            try:
                price = EnrollmentHelper.get_total_price_by_plan_card(page)
            except Exception:
                framework_logger.info(f"Failed to get price from plan card")
            
            # # Modal close: https://hp-testrail.external.hp.com/index.php?/cases/view/27368504
            framework_logger.info("==== C27368504-Your Plan-Modal Close ====")
            EnrollmentHelper.click_learn_more(page, paper=False, callback=stage_callback)

            # # Save button: https://hp-testrail.external.hp.com/index.php?/cases/view/27368505
            # framework_logger.info("==== C27368505-Your Plan-Save Button ====")
            # EnrollmentHelper.select_plan_v3(page, plan_value='100', paper=False, callback=stage_callback)
            # framework_logger.info("Ink only plan selected")
            # stage_callback("ink_only_selected", page, screenshot_only=True)

            # # # Different plans: https://hp-testrail.external.hp.com/index.php?/cases/view/27368506
            # framework_logger.info("==== C27368506-Your Plan-Different Plans ====")
            # EnrollmentHelper.edit_plan_check(page, plan_value='300', paper=True, callback=stage_callback)
            # framework_logger.info("Ink only edit plan")
            # stage_callback("edit_ink_only_selected", page, screenshot_only=True)

            # Choose HP Checkout
            stage_callback("hp_checkout", page, screenshot_only=True)
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Choose HP Checkout")

            # Shipping card: https://hp-testrail.external.hp.com/index.php?/cases/view/27368507
            # Shipping modal: https://hp-testrail.external.hp.com/index.php?/cases/view/27368508
            # Save button: https://hp-testrail.external.hp.com/index.php?/cases/view/27368511
            framework_logger.info("==== C27368507-C27368508-C27368511-Shipping-Shipping Card-shipping modal-save button ====")
            EnrollmentHelper.add_shipping(page, additional_check=True)
            framework_logger.info(f"Shipping added successfully")

            # Modal Close: https://hp-testrail.external.hp.com/index.php?/cases/view/27368510
            # Mandatory Fields: https://hp-testrail.external.hp.com/index.php?/cases/view/27368515
            framework_logger.info("==== C27368510-C27368515-Shipping-Modal Close-Mandatory Fields ====")
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
            framework_logger.info("==== C31628346-C31628345-C31628347-C31628348-C29548951-C29548952-C29548953-SOB-Enter Promo or PIN code link-Special Offer Benefits(SOB) modal-Special Offers section-Breakdown of credits section-Promo code-RaF code-EK code ====")
            EnrollmentHelper.special_offer_benefits(page, 'vb5tyb', callback=stage_callback)
            framework_logger.info(f"Special Offer benefit added successfully")

            # framework_logger.info("======== Billing: Billing card ========")
            EnrollmentHelper.billing_card(page, card_type="credit_card_master")
            stage_callback("billing_card_selected", page, screenshot_only=True)

            # # Add Shipping
            # EnrollmentHelper.add_shipping(page)
            # framework_logger.info(f"Added shipping info")

            # Add Billing
            EnrollmentHelper.add_billing(page, plan_value=price)
            framework_logger.info(f"Billing Added successfully")

            # Skip Paper Offer
            EnrollmentHelper.skip_paper_offer(page)
            framework_logger.info(f"Skipped paper offer")

            # Finish Enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== OOBE Enrollment completed successfully ===")

            return tenant_email
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
