from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.overview_page import OverviewPage
from playwright.sync_api import expect, sync_playwright
from core.settings import GlobalState
import test_flows_common.test_flows_common as common
import time
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cartridge_status_card_with_wk(stage_callback):
    framework_logger.info("=== C42543599 - Cartridge Status Card with wk flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)

            # Create and Claim virtual printer
            common.create_and_claim_virtual_printer()

            # Start enrollment
            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Select plan
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Choose hp checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Apply a prepaid with Welcome Kit
            prepaid_code = common.get_offer_code("prepaid", amount_equal=3000)
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 30)
            framework_logger.info(f"Prepaid code applied and validated")

            # Add Billing (Remove the billing step if not needed)
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            # Finish enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info(f"Finished enrollment with prepaid")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page for tenant: {tenant_email}")

            # Validate Cartridge Status Card with Welcome Kit
            overview_page = OverviewPage(page)
            expect(overview_page.cartridge_status_card).to_be_visible(timeout=60000)
            expect(overview_page.cartridge_status_card).to_contain_text("Your service hasn't started yet")
            expect(overview_page.cartridge_status_card_description).to_have_text("We shipped you ink, however your billing won't begin until you "
                                                                                 "install an HP Instant Ink cartridge. Use your current cartridges "
                                                                                 "until empty, then install the shipped cartridge.")
            framework_logger.info(f"Validated Cartridge Status Card with Welcome Kit")
            framework_logger.info("=== C42543599 - Cartridge Status Card with wk flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the C42543599 - Cartridge Status Card with wk flow: {e}\n{traceback.format_exc()}")
