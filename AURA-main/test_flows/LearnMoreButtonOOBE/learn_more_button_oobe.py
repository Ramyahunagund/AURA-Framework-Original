import re
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from playwright.sync_api import expect
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def learn_more_button_oobe(stage_callback) -> None:
    framework_logger.info("=== === C30663041 - Learn More flow started ===")
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

            # Acesse Learn More Page
            OssEmulatorHelper.access_learn_more(page)
            framework_logger.info(f"Accessed Learn More page")

            # "How it works" model with "More Information" link is displayed
            expect(page.locator("text=How it works")).to_be_visible(timeout=120000)
            expect(page.locator("text=More information")).to_be_visible()
            framework_logger.info(f"'How it works' model is displayed")

            # Click on "More Information" and "Show less" link is displayed well.
            page.locator("text=More information").click(timeout=120000)
            expect(page.locator("text=Show less")).to_be_visible()
            framework_logger.info(f"'Show less' link is displayed after clicking on 'More information'")

            # Click on "Show less" link and More Information accordion is shrinked and the "More Information" link is displayed 
            page.locator("text=Show less").click(timeout=120000)
            expect(page.locator("text=More information")).to_be_visible()
            framework_logger.info(f"'More information' link is displayed after clicking on 'Show less'")

            # Click the "Learn More" button to open the model and click outside of the modal
            OssEmulatorHelper.access_learn_more(page)
            page.mouse.click(10, 100)  # Click outside the modal
            expect(page.locator("text=How it works")).not_to_be_visible(timeout=120000)
            framework_logger.info(f"Closed the modal by clicking outside of it")

            framework_logger.info("=== C30663041 - Learn More flow finished ===")   
            return tenant_email
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()