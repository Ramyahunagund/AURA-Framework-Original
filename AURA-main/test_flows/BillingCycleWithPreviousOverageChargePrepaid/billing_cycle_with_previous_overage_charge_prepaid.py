from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_with_previous_overage_charge_prepaid(stage_callback):
    framework_logger.info("=== C48543395 -  Billing Cycle with previous Overage Charge - Prepaid Started ===")
    tenant_email = create_ii_subscription(stage_callback)
    with PlaywrightManager() as page:
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.remove_free_months(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status changed to 'subscribed'")

            # Charge a new billing cycle with 100 pages
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "140")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 140 pages")

            # Go to BillingTransaction and confirm details
            RABaseHelper.get_links_with_text_by_title(page, "Billing transactions", "BillingTransaction")[0].click()
            assert common.find_field_text_by_header(page, "Transaction type") == "charge"
            assert common.find_field_text_by_header(page, "Status") == "succeeded"
            assert common.find_field_text_by_header(page, "Invoice status") == "ready_to_invoice"
            assert common.find_field_text_by_header(page, "Pretax cents") > "0"
            assert common.find_field_text_by_header(page, "Tax cents") > "0"
            framework_logger.info("Billing transaction details verified on BillingTransaction page")

            framework_logger.info("=== C48543395 -  Billing Cycle with previous Overage Charge - Prepaid Finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()