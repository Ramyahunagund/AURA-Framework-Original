from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def click_next_on_value_proposition(stage_callback) -> None:
    framework_logger.info("=== C30663045 - Click Next on Value Proposition Page flow started ===")
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

            # Continue on value proposition page
            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")

            # Accept automatic printer updates
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Accepted automatic printer updates")

            framework_logger.info("=== C30663045 - Click Next on Value Proposition Page flow finished ===")   
            return tenant_email
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()