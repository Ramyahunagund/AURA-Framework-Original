import code
from helper.ra_base_helper import RABaseHelper
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
from helper.enrollment_helper import EnrollmentHelper
import time
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_charge_with_prepaid(stage_callback):
    framework_logger.info("=== C39356858, C39365038, C32321129 - Billing Cycle Charge with Prepaid started ===")
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

            price = None
            try:
                price = EnrollmentHelper.get_total_price_by_plan_card(page)
            except Exception:
                framework_logger.info(f"Failed to get price from plan card")           
            
            # Apply prepaid code
            EnrollmentHelper.add_prepaid_by_value(page, price, amount_greater=False)
            framework_logger.info(f"Prepaid code applied")

             # billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing added")

            # Finish enrollment
            EnrollmentHelper.finish_enrollment_with_prepaid(page)
            framework_logger.info(f"Finished enrollment with prepaid")

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription status updated to 'subscribed' and remove free months")

            # Shifts for 31 days and set paged used to 100
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            framework_logger.info("Shifted for 31 days and seted paged used to 100")

            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            if (status_code == "DIRECT-DEBIT-PENDING"):
                RABaseHelper.access_menu_of_page(page, 'Edit')
                page.locator("#billing_cycle_pgs_direct_debit_override").select_option("SETTLED", force=True)
                page.wait_for_selector(".btn.btn-primary", timeout=120000).click()
                GeminiRAHelper.access(page)
                GeminiRAHelper.access_tenant_page(page, tenant_email)
                GeminiRAHelper.access_subscription_by_tenant(page)
                GeminiRAHelper.event_shift(page, "8", False)
               
                RABaseHelper.complete_jobs(page, common._instantink_url, ["TransitionBillingCycleStateDispatcherJob"])
                
                GeminiRAHelper.access(page)
                GeminiRAHelper.access_tenant_page(page, tenant_email)
                GeminiRAHelper.access_subscription_by_tenant(page)
                GeminiRAHelper.access_second_billing_cycle(page)
                RABaseHelper.wait_page_to_load(page, "Billing cycle")              
            
            # Verify charge complete
            GeminiRAHelper.verify_charge_complete(page)            
            framework_logger.info("Verified Charge complete")

            # Verify status code
            status_code = common.billing_status_code()
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", status_code)
            framework_logger.info(f"Status code verified as {status_code}")

            # Request events include PAY-PAL-SUCCESS and PEGASUS-PARTIAL on Billing cycle page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Request events", status_code)
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Request events", "PEGASUS-PARTIAL")
            framework_logger.info("Request events verified")

            framework_logger.info("=== C39356858, C39365038, C32321129 - Billing Cycle Charge with Prepaid successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        