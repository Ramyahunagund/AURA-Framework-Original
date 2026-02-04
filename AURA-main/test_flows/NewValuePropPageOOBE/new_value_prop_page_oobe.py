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


def new_value_prop_page_oobe(stage_callback) -> None:
    framework_logger.info("=== === C30663039 - New Value Prop page flow started ===")
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

            # Continue on value proposition
            not_enable_ink_delivery = page.locator('[data-testid="skip-trial-button"]')
            expect (not_enable_ink_delivery).to_be_visible(timeout = 400000)
            learn_more_button = page.locator("[data-testid='learn-more-button']")
            expect(learn_more_button).to_be_visible(timeout = 400000)

            time.sleep(15)
            assert (re.compile(r"Your new printer includes \d+ months of \d+ and delivery"))
            assert (re.compile(r"(E2E months within grace period|Flex months within grace period)"))
            assert "After the trial, a monthly fee will be automatically charged unless canceled." in page.content()

            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")

            framework_logger.info("=== C30663039 - New Value Prop page flow finished ===")   
            return tenant_email
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
