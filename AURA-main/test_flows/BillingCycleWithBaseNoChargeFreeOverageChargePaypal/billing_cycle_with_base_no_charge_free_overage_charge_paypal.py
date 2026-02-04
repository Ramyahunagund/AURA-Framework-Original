import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_with_base_no_charge_free_overage_charge_paypal(stage_callback):
    framework_logger.info("=== C39479307 - Billing Cycle with BaseNoCharge and FreeOverageCharge PayPal started ===")
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

        # 2) Claim virtual printer and add address
        common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        try:
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            
            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # billing
            EnrollmentHelper.add_billing(page, "paypal")
            framework_logger.info(f"Billing added")

            # Finish enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info(f"Finished enrollment with prepaid")

            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status updated to 'subscribed'")

            # Add the Page Tally 100 and Shifts for 37 days and set paged used to 700
            GeminiRAHelper.event_shift(page, "37")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "700")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Charge submitted for payment problem")

            # Sees that the value of Invoice items include BaseNoChargeInvoiceItem on Billing cycle page
            RABaseHelper.get_field_text_by_title(page, "Invoice items") == "BaseNoChargeInvoiceItem, FreeOverageInvoiceItem"
            framework_logger.info("Invoice items verified as 'BaseNoChargeInvoiceItem, FreeOverageInvoiceItem'")

            framework_logger.info("=== C39479307 - Billing Cycle with BaseNoCharge and FreeOverageCharge PayPal successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e