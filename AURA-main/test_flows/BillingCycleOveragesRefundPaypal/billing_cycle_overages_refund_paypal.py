from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_overages_refund_paypal(stage_callback):
    framework_logger.info("=== C49410846 - Billing Cycle overages Refund Paypal started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            pages_amount = 300
            overage_blocks = 5
            plan_data = common.get_filtered_plan_data(value=pages_amount)[0]
            overage_pages = plan_data["overageBlockSize"] * overage_blocks

            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription status updated to 'subscribed'")

            # Advance 37 days on the subscription and click on submit charge button
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "37")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount + overage_pages))
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with {pages_amount + overage_pages} pages")

            # Sees Charge complete status true on billing cycle page
            GeminiRAHelper.verify_charge_complete(page)
            framework_logger.info("Charge complete status verified as 'true'")

            # Partial refund for current billing cycle
            GeminiRAHelper.make_refund_option(page, "Instant Ink Overage Blocks", "3")
            framework_logger.info("Instant Ink Overage Blocks refund made for current billing cycle")

            # See Refund complete status false on billing cycle page
            GeminiRAHelper.verify_field_is_false(page, "Refund complete")
            framework_logger.info("Refund complete status verified as 'false'")

            # Sees Status code equals to PARTIAL-REFUND on Billing cycle page
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", "PARTIAL-REFUND")
            framework_logger.info("Status code verified as 'PARTIAL-REFUND'")

            # Sees link with text RefundedInvoiceItem in the Refunded invoice items on the Details for Invoice page
            RABaseHelper.get_links_with_text_by_title(page, "Refunded invoice items", "RefundedInvoiceItem")[0].click()
            framework_logger.info("Accessed RefundedInvoiceItem from Refunded invoice items")

            # Sees Quantity equals to 3 on Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info(page, "Quantity", "3")
            framework_logger.info("Quantity verified as '3'")

            # Sees Amount in cents equals to 225 on Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info(page, "Amount in cents", "225")
            framework_logger.info(f"Amount in cents verified as 225")

            # Sees the link with text OverageInvoiceItem in the Invoice items on the Billing cycle page
            RABaseHelper.get_field_text_by_title(page, "Invoice item") == "OverageInvoiceItem"
            framework_logger.info("Invoice items verified as 'OverageInvoiceItem'")

            # Click browser back button
            page.go_back()
            framework_logger.info("Returned to Billing cycle page")

            # Click link with text Billing::PaymentEvent in the Payment events on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "Billing::PaymentEvent", "Payment events")
            framework_logger.info("Accessed Billing::PaymentEvent from Payment events")

            # Payment Events
            expected_payment_engine = common.payment_engine()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)
            GeminiRAHelper.verify_rails_admin_info(page, "Event type", "partial-refund")        
            GeminiRAHelper.verify_field_is_negative(page, "Pretax cents")
            GeminiRAHelper.verify_field_is_negative(page, "Tax cents")
            framework_logger.info("Payment event details verified")

            # Click browser back button
            page.go_back()
            framework_logger.info("Returned to Billing cycle page")

            # Sees link with text PAYMENT-GATEWAY-PARTIAL-REFUNDED in the Request events on the Billing cycle page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Request events", "PAY-PAL-REFUND-PARTIAL")

            # Sees Response status equals to PAY-PAL-REFUND-PARTIAL on Billing cycle page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Response status", "PAY-PAL-REFUND-PARTIAL")

            # Sees Charge amount cents to be negative on Request events page
            GeminiRAHelper.verify_field_is_negative(page, "Charge amount cents")

            # Verify Payment engine on Request events page
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)

            # Click browser back button
            page.go_back()
            framework_logger.info("Returned to Billing cycle page")

             # Click link with text BillingTransaction in the Billing transactions on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "BillingTransaction", "Billing transactions")
            framework_logger.info("Accessed BillingTransaction from Billing transactions")

            # Sees Transaction type equals to refund on Billing transaction page
            GeminiRAHelper.verify_rails_admin_info(page, "Transaction type", "refund")

            # Sees Status equals to succeeded on Billing transaction page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "succeeded")

            # Sees Invoice status equals to ready_to_invoice on Billing transaction page
            GeminiRAHelper.verify_rails_admin_info(page, "Invoice status", "ready_to_invoice")

            # Sees Pretax cents equals to -1199 on payment event page
            GeminiRAHelper.verify_field_is_negative(page, "Pretax cents")

            # Sees Tax cents equals to -103 on payment event page
            GeminiRAHelper.verify_field_is_negative(page, "Tax cents")

            framework_logger.info("=== C49410846 - Billing Cycle overages Refund Paypal successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e