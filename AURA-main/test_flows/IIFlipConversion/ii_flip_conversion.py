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

def ii_flip_conversion(stage_callback) -> None:
    framework_logger.info("=== Enrollment OOBE flow started ===")
    common.setup()
    test_requirements = GlobalState.requirements
    hpplus_action = test_requirements.get("hpplus")
    flip_conversion = test_requirements.get("flip_conversion")
    plan_pages= test_requirements.get("plan_pages")

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

            EnrollmentHelper.flip_skip_free_months(page)
            framework_logger.info(f"No shipping and no billing selected")   

            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== Enrollment completed successfully ===")

            DashboardHelper.access(page)
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("=== Dashboard launched successfully ===")
            new_tab = None

            if flip_conversion in ("enroll_now", "enter_address", "modal_enter_address"):
                popup_action_map = {
                    "enroll_now": DashboardHelper.flip_conversion_enroll_now,
                    "enter_address": DashboardHelper.flip_conversion_enter_address,
                    "modal_enter_address": DashboardHelper.flip_conversion_modal_enter_address,
                }
                with page.expect_popup() as popup_info:
                    popup_action_map[flip_conversion](page)
                    framework_logger.info(f"Clicked on {flip_conversion.replace('_', ' ').title()} button")
                new_tab = popup_info.value
                new_tab.wait_for_load_state()
                framework_logger.info(f"Switched to new tab after {flip_conversion.replace('_', ' ').title()}")
            else:
                framework_logger.error(f"Unknown flip_conversion value: {flip_conversion}")

            if new_tab:
                EnrollmentHelper.add_shipping(new_tab)
                framework_logger.info("Added shipping info")
                
                EnrollmentHelper.close_billing_or_shipping_modal(new_tab)
                framework_logger.info("Closed billing or shipping modal if it appeared")

                EnrollmentHelper.edit_plan(new_tab, plan_pages)
                framework_logger.info(f"Changed plan to {plan_pages} pages")

                confirmation_page = ConfirmationPage(new_tab)
                assert confirmation_page.enroll_step_skip_button.is_visible(), "Skip Now button is not enabled"
                framework_logger.info("Skip Now button is enabled")
                assert confirmation_page.shipping_card.is_visible(), "Shipping card is not visible"
                framework_logger.info("Shipping card is visible")

                EnrollmentHelper.add_billing(new_tab)
                framework_logger.info("Added billing info")
                
                assert confirmation_page.billing_card.is_visible(), "Billing card is not visible"
                framework_logger.info("Billing card is visible")

                EnrollmentHelper.finish_enrollment(new_tab)
                framework_logger.info("=== Enrollment completed successfully ===")
            else:
                framework_logger.error("New tab was not created. Enrollment steps could not be completed.")

        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
