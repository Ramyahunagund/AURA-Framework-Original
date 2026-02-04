from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_with_base_no_charge_free_overage_charge_creditcard(stage_callback):
    framework_logger.info("=== C44678886 - Billing Cycle with BaseNoCharge and FreeOverageCharge Credit Card started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Add the Page Tally 100 and Shifts for 37 days and set paged used to 700
            GeminiRAHelper.event_shift(page, "37")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "700")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Charge submitted for payment problem")

            # Sees that the value of Invoice items include BaseNoChargeInvoiceItem on Billing cycle page
            RABaseHelper.get_field_text_by_title(page, "Invoice items") == "BaseNoChargeInvoiceItem, FreeOverageInvoiceItem"
            framework_logger.info("Invoice items verified as 'BaseNoChargeInvoiceItem, FreeOverageInvoiceItem'")

            # Clicks link with text BaseChargeInvoiceItem in the Invoice item page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "BaseNoChargeInvoiceItem")[0].click()
            framework_logger.info("Accessed BaseNoChargeInvoiceItem page")

            # Verifies that Quantity is 1 and Amount in cents is 0.000
            quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")
            assert quantity == "1", f"Expected Quantity to be '1', but got '{quantity}'"
            assert amount_in_cents == "0", f"Expected Unit amount to be '0', but got '{amount_in_cents}'"
            framework_logger.info("Verified Quantity is 1 and Unit amount is 0")

            # Clicks link with text FreeOverageInvoiceItem in the Invoice item page
            page.go_back()
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "FreeOverageInvoiceItem")[0].click()
            framework_logger.info("Accessed FreeOverageInvoiceItem page")

            # Verifies that Quantity is 60 and Amount in cents is 0
            quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents") 
            assert quantity == "60", f"Expected Quantity to be '60', but got '{quantity}'"
            assert amount_in_cents == "0", f"Expected Amount in cents to be '0', but got '{amount_in_cents}'"
            framework_logger.info("Verified Quantity is 60 and Amount in cents is 0")  

            framework_logger.info("=== C44678886 - Billing Cycle with BaseNoCharge and FreeOverageCharge Credit Card successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e