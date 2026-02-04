from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def enrollment_oobe(stage_callback) -> None:
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

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Added shipping info")

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
