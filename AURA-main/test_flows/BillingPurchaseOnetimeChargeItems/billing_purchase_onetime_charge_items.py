from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC = "C49476484 | C49476265 | C40707120"
def billing_purchase_onetime_charge_items(stage_callback):

    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"=== Billing Purchase (onetime) Charge items - {common._payment_method} flow started ===")

    with PlaywrightManager() as page:
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Charge a new billing purchase with value 300
            GeminiRAHelper.one_time_charge(page, "300")
            framework_logger.info(f"New billing purchase charged with 300")

            # See Charge complete status true on billing cycle page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.verify_charge_complete(page)

            # Verify Status code on Billing cycle page
            expected_status_code = common.billing_status_code()
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", expected_status_code)

            # Click link with text OneTimeChargeInvoiceItem in the Invoice items on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "OneTimeChargeInvoiceItem", "Invoice items")
            framework_logger.info("Accessed OneTimeChargeInvoiceItem from Invoice items")

            # See Quantity equals to 1 on Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info(page, "Quantity", "1")

            # See Amount in cents equals to 300 on Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info(page, "Amount in cents", "300")

            # Click link with text BillingPurchase in the Billable 
            RABaseHelper.access_link_by_title(page, "BillingPurchase", "Billable")
            framework_logger.info("Accessed BillingPurchase from Billable")

            # Click link with text Billing in the Payment events on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "Billing", "Payment events")
            framework_logger.info("Accessed Billing from Payment events")

            # See Event type equals to charge on payment event page
            GeminiRAHelper.verify_rails_admin_info(page, "Event type", "charge")

            # Verify Payment engine on Payment event page
            expected_payment_engine = common.payment_engine()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)

            # See Pretax cents equals to 300 on payment event page
            GeminiRAHelper.verify_rails_admin_info(page, "Pretax cents", "300")

            # See Tax cents equals to 26 on payment event page
            GeminiRAHelper.verify_rails_admin_info(page, "Tax cents", "26")

            # Click link with text BillingPurchase in the Billable 
            RABaseHelper.access_link_by_title(page, "BillingPurchase", "Billable")
            framework_logger.info("Accessed BillingPurchase from Billable")

            # Click link in the Request events on the Billing cycle page
            RABaseHelper.access_link_by_title(page, expected_status_code, "Request events")
            framework_logger.info(f"Accessed {expected_status_code} from Request events")

            # Verify Response status on Request event page
            GeminiRAHelper.verify_rails_admin_info(page, "Response status", expected_status_code)

            # See Charge amount cents to be positive on Request event page
            GeminiRAHelper.verify_field_is_positive(page, "Charge amount cents")

            # Verify Payment engine on Request event page
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)

            # Click link with text BillingPurchase in the Billable 
            RABaseHelper.access_link_by_title(page, "BillingPurchase", "Billable")
            framework_logger.info("Accessed BillingPurchase from Billable")

            # Click link with text BillingTransaction in the Billing transactions on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "BillingTransaction", "Billing transactions")
            framework_logger.info("Accessed BillingTransaction from Billing transactions")

            # See Transaction type equals to charge on Billing transaction page
            GeminiRAHelper.verify_rails_admin_info(page, "Transaction type", "charge")

            # See Status equals to succeeded on Billing transaction page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "succeeded")

            # See Invoice status equals to ready_to_invoice on Billing transaction page
            GeminiRAHelper.verify_rails_admin_info(page, "Invoice status", "ready_to_invoice")

            # See Pretax cents to be positive on Billing transaction page
            GeminiRAHelper.verify_field_is_positive(page, "Pretax cents")

            # See Tax cents to be positive on Billing transaction page
            GeminiRAHelper.verify_field_is_positive(page, "Tax cents")

            framework_logger.info(f"=== Billing Purchase (onetime) Charge items - {common._payment_method} flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e