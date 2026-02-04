from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def checkbox_section_with_free_trial_months(stage_callback) -> None:
    framework_logger.info("=== C31619978 - Checkbox section (With Free trial months) flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    # Create virtual printer
    printer = common.create_virtual_printer()

    # Create new HPID account and setup OSS Emulator
    with PlaywrightManager() as page:
        try:
            # Create a new HPID account
            page = common.create_ii_v2_account(page)

            # Setup OSS Emulator for OOBE
            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info(f"OSS Emulator setup completed")

            # Accept connected printing services
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info(f"Accepted connected printing services")

            # Decline
            OssEmulatorHelper.decline_hp_plus(page)
            framework_logger.info(f"Declined HP+")

            # Continue on dynamic security notice
            OssEmulatorHelper.continue_dynamic_security_notice(page)
            framework_logger.info(f"Continued on dynamic security notice")

            # Check Reminder Checkboc, trial text and continue on value proposition page
            OssEmulatorHelper.verify_reminder_checkbox_and_trial_text(page, 2)
            framework_logger.info(f"Verified reminder checkbox and trial text for 2 months")
            
            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")

            framework_logger.info("=== C31619978 - Checkbox section (With Free trial months) flow finished ===")   
            return tenant_email
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()



    framework_logger.info("Reminder checkbox and trial info text verified successfully.")
