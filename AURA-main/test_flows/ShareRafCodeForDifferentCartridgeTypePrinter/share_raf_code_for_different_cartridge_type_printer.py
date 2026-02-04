from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.ra_base_helper import RABaseHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def share_raf_code_for_different_cartridge_type_printer(stage_callback):
    framework_logger.info("=== C43905960 - Share RaF code for different Cartridge Type Printer flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # 1) HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer
        common.create_and_claim_virtual_printer()

    with PlaywrightManager() as page:
        try:
            # Get toner free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, "IIQA.automation+stage1_US_20240809_080920_0298@outlook.com")
            GeminiRAHelper.access_subscription_by_tenant(page)
            free_months = RABaseHelper.get_field_text_by_title(page, "Sum of remaining free months")
            free_months = int(free_months) + 1

            # Start enrollment
            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # Sign in method
            HPIDHelper.complete_sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in")

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Choose hp checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add Shipping
            EnrollmentHelper.add_shipping(page, company_name="HP")
            framework_logger.info(f"Shipping added successfully")

            # Apply RaF code
            EnrollmentHelper.apply_and_validate_raf_code(page, "5wrxmh")
            framework_logger.info(f"RaF code applied and validated successfully")

            # Add billing method
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing method added successfully")

            # Finish enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info(f"Finished enrollment with prepaid")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page for tenant: {tenant_email}")

            # Verify free months value
            DashboardHelper.verify_free_months_value(page, 4)
            framework_logger.info(f"Verified free months value successfully")

            # Verify toner free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, "IIQA.automation+stage1_US_20240809_080920_0298@outlook.com")
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "Sum of remaining free months", str(free_months))
            framework_logger.info(f"Verified toner free months has increased")

            framework_logger.info("=== C43905960 - Share RaF code for different Cartridge Type Printer flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e