import time
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from test_flows.EnrollmentOOBE.enrollment_oobe import enrollment_oobe
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC = "C48844193 | C48462454"
def billing_cycle_full_refund(stage_callback):
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"=== Billing Cycle Full Refund - {common._payment_method} flow started ===")

    with PlaywrightManager() as page:
        try:
            pages_amount = 100
            overage_blocks = 5
            plan_data = common.get_filtered_plan_data(value=pages_amount)[0]
            overage_pages = plan_data["overageBlockSize"] * overage_blocks

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Charge a new billing cycle with 100 pages
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount))
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with {pages_amount} pages")

            GeminiRAHelper.update_direct_debit_status(page)

            # Charge a new billing cycle with 150 pages
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "37")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount + overage_pages))
            GeminiRAHelper.submit_charge(page)
            GeminiRAHelper.manual_retry_until_complete(page)
            framework_logger.info(f"New billing cycle charged with {pages_amount + overage_pages} pages")

            GeminiRAHelper.update_direct_debit_status(page)

            # Verify Status code on Billing cycle page
            expected_status_code = common.billing_status_code()
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", expected_status_code)

            # Sees Charge complete status true on billing cycle page
            GeminiRAHelper.verify_charge_complete(page)

            # Full/Remaining refund for current billing cycle
            GeminiRAHelper.make_refund_option(page, "Full/Remaining Amount")
            framework_logger.info("Full/Remaining refund made for current billing cycle")

            GeminiRAHelper.update_direct_debit_status_after_refund(page)

            # See Refund complete status true on billing cycle page
            GeminiRAHelper.verify_field_is_true(page, "Refund complete")

            # Sees link with text PAYMENT-GATEWAY-REFUNDED in the Request events on the Billing cycle page
            events = RABaseHelper.get_links_with_text_by_title(page, "Request events", common.request_event_response_status(full=True))
            assert len(events) > 0, f"Link with text '{common.request_event_response_status(full=True)}' not found in section 'Request events'"

            # Sees Status code equals to REFUNDED on Billing cycle page
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", "REFUNDED")

            # Click link with text BaseChargeInvoiceItem in the Invoice items on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "BaseChargeInvoiceItem", "Invoice items")
            framework_logger.info("Accessed BaseChargeInvoiceItem from Invoice items")

            # Sees Quantity equals to 1 on Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info(page, "Quantity", "1")

            # Sees Amount in cents equals to 799 on Details for Invoice page
            price_cents = plan_data["priceCents"]
            GeminiRAHelper.verify_rails_admin_info(page, "Amount in cents", str(price_cents))

            # Sees link with text RefundedInvoiceItem in the Refunded invoice items on the Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded invoice items", "RefundedInvoiceItem")

            # Sees link with text BillingTransaction in the Billing transaction on the Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Billing transaction", "BillingTransaction")

            # Click browser back button
            page.go_back()
            framework_logger.info("Returned to Billing cycle page")
            
            # Click link with text OverageInvoiceItem in the Invoice items on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "OverageInvoiceItem", "Invoice items")
            framework_logger.info("Accessed OverageInvoiceItem from Invoice items")

            # Sees Quantity equals to 5 on Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info(page, "Quantity", str(overage_blocks))

            # Sees Amount in cents equals to 500 on Details for Invoice page
            GeminiRAHelper.verify_field_is_positive(page, "Amount in cents")

            # Sees link with text RefundedInvoiceItem in the Refunded invoice items on the Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded invoice items", "RefundedInvoiceItem")

            # Sees link with text BillingTransaction in the Billing transaction on the Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Billing transaction", "BillingTransaction")

            # Click browser back button
            page.go_back()
            framework_logger.info("Returned to Billing cycle page")

            # Click link with text Billing::PaymentEvent in the Payment events on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "Billing::PaymentEvent", "Payment events")
            framework_logger.info("Accessed Billing::PaymentEvent from Payment events")

            # Sees Event type equals to refund on Payment event page
            GeminiRAHelper.verify_rails_admin_info(page, "Event type", "refund")

            # Verify Payment engine on Payment event page
            expected_payment_engine = common.payment_engine()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)

            # Sees Pretax cents equals to -1199 on payment event page
            GeminiRAHelper.verify_field_is_negative(page, "Pretax cents")

            # Sees Tax cents equals to -103 on payment event page
            GeminiRAHelper.verify_field_is_negative(page, "Tax cents")

            # Sees link with text BillingTransaction in the Billing transaction on the Details for Invoice page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Billing transaction", "BillingTransaction")

            # Sees link with text RefundedPaymentEventInvoiceItem in the Refunded payment event invoice items on the Payment event page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded payment event invoice items", "RefundedPaymentEventInvoiceItem")

            # Sees link with text RefundedInvoiceItem in the Refunded invoice items on the Payment event page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded invoice items", "RefundedInvoiceItem")

            # Sees link with text Payment Event in the Reversed Transaction Payment Events on the Payment event page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Reversed Transaction Payment Events", "Payment Event")

            # Click link with text RefundedPaymentEventInvoiceItem in the Refunded payment event invoice items on the Payment event page
            RABaseHelper.access_link_by_title(page, "RefundedPaymentEventInvoiceItem", "Refunded payment event invoice items")
            framework_logger.info("Accessed RefundedPaymentEventInvoiceItem from Refunded payment event invoice items")

            # Sees link with text Billing::PaymentEvent in the Payment event on the Refunded payment event page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Payment event", "Billing::PaymentEvent")

            # Sees link with text RefundedInvoiceItem in the Refunded invoice item on the Refunded payment event page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded invoice item", "RefundedInvoiceItem")

            # Access billing cycle with status code REFUNDED
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_billing_cycle_by_status(page, "REFUNDED")
            framework_logger.info("Accessed Billing cycle with status code REFUNDED")

            # Click link with text PAYMENT-GATEWAY-REFUNDED in the Request events on the Billing cycle page
            RABaseHelper.get_links_with_text_by_title(page, "Request events", common.request_event_response_status(full=True))[0].click()
            framework_logger.info("Accessed REFUNDED from Request events")

            # Sees Response status equals to PAYMENT-GATEWAY-REFUNDED on Billing cycle page
            assert common.find_field_text_by_header(page, "Response status") == common.request_event_response_status(full=True)

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

            # Sees link with text Billing::PaymentEvent in the Payment events on the Billing transaction page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Payment events", "Billing::PaymentEvent")

            # Sees link with text RefundedInvoiceItem in the Refunded invoice items on the Billing transaction page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded invoice items", "RefundedInvoiceItem")

            # Click browser back button
            page.go_back()
            framework_logger.info("Returned to Billing cycle page")

            # Click link with text Billing::PaymentEvent in the Payment events on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "Billing::PaymentEvent", "Payment events")
            framework_logger.info("Accessed Billing::PaymentEvent from Payment events")

            # Click link with text Payment Event in the Reversed Transaction Payment Events on the Payment event page
            RABaseHelper.access_link_by_title(page, "Payment Event", "Reversed Transaction Payment Events")
            framework_logger.info("Accessed Payment Event from Reversed Transaction Payment Events")

            # Sees Event type equals to charge on Payment event page
            GeminiRAHelper.verify_rails_admin_info(page, "Event type", "charge")

            # Verify Payment engine on Payment event page
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)

            # Sees Pretax cents equals to 1199 on payment event page
            GeminiRAHelper.verify_field_is_positive(page, "Pretax cents")

            # Sees Tax cents equals to 103 on payment event page
            GeminiRAHelper.verify_field_is_positive(page, "Tax cents")

            # Sees link with text BillingTransaction in the Billing transaction on the Payment event page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Billing transaction", "BillingTransaction")

            # Sees link with text Payment Event in the Reversed Transaction Payment events on the Payment event page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Reversed Transaction Payment Events", "Payment Event")

            framework_logger.info(f"=== Billing Cycle Full Refund -  flow {common._payment_method} finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
