from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_payment_events_status_of_partial_refund_payment_and_status_code_prepaid(stage_callback):
    framework_logger.info("=== C47933531 - Billing Cycle - Payment Events, Status of partial Refund Payment and Status Code - Prepaid Started ===")
    tenant_email = create_ii_subscription(stage_callback)
    with PlaywrightManager() as page:
        try:
            plan_data = common.get_filtered_plan_data()[0]
            pages_amount = 100
            overage_blocks = 3
            overage_pages = plan_data["overageBlockSize"] * overage_blocks

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
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            overage_price_expected = plan_data["overageBlockPriceCents"] * overage_blocks
            base_price_expected = plan_data["priceCents"]
            framework_logger.info(f"New billing cycle charged with 100 pages")
            
            # Charge a new billing cycle for 37 days with 130 pages and makes Full/Remaining refund for current billing cycle
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.event_shift(page, "37")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page,  str(pages_amount + overage_pages))
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            GeminiRAHelper.submit_charge(page)
            GeminiRAHelper.make_refund_option(page, "Instant Ink Overage Blocks", '3')
            framework_logger.info(f"New billing cycle charged with 130 pages")

            # See Status code equals to REFUNDED on Billing cycle page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.click_billing_cycle_by_status(page, "PARTIAL-REFUND")   
            no_success_message = page.locator('div:nth-child(51) > .card > .card-body > .badge.bg-danger')
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            assert common.find_field_text_by_header(page, "Refund complete") == no_success_message.inner_text()
            framework_logger.info("Status code equals to REFUNDED false verified on Billing cycle page")

            # Clicks link with text 3 * OverageInvoiceItem in the Invoice item page
            RABaseHelper.get_links_with_text_by_title(page, "Refunded invoice items", "RefundedInvoiceItem")[0].click()
            assert common.find_field_text_by_header(page, "Invoice item") != "BaseChargeInvoiceItem", "BaseChargeInvoiceItem is present in Invoice items"
            RABaseHelper.get_links_with_text_by_title(page, "Invoice item", "3 * OverageInvoiceItem")[0].click()
            framework_logger.info("Accessed OverageInvoiceItem page")

            # Sees Quantity equals to 3 on and Amount in cents equals to 450 Details for Invoice page
            quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")

            assert int(quantity) == overage_blocks, f"Expected quantity {overage_blocks}, got '{quantity}'"
            assert int(amount_in_cents) == overage_price_expected, f"Expected amount in cents '{overage_price_expected}', got '{amount_in_cents}'"
            framework_logger.info("Quantity and Amount in cents verified on Details for Invoice page")

            # Clicks link with text Billing::PaymentEvent in the Payment events on the Billing cycle page and confirm details
            page.go_back()
            RABaseHelper.get_links_with_text_by_title(page, "Payment events", "Billing::PaymentEvent")[0].click()
            payment_engine = RABaseHelper.get_field_text_by_title(page, "Payment engine")
            int_pretax_cents = int(RABaseHelper.get_field_text_by_title(page, "Pretax cents"))
            int_tax_cents = int(RABaseHelper.get_field_text_by_title(page, "Tax cents"))

            assert payment_engine == common.payment_engine(), f"Expected payment engine '{common.payment_engine()}', got '{payment_engine}'"
            assert int_pretax_cents < overage_price_expected + base_price_expected, f"Expected pretax cents '{overage_price_expected + base_price_expected}', got '{int_pretax_cents}'"
            assert int_tax_cents < 0, f"Expected tax cents less than '0', got '{int_tax_cents}'"
            assert common.find_field_text_by_header(page, "Event type") == "partial-refund"
            framework_logger.info("Payment event details verified on Billing::PaymentEvent page")

            # On Refunded page on Billing Cycle page confirm details
            RABaseHelper.get_links_with_text_by_title(page, "Billing cycle", "PARTIAL-REFUND")[0].click()
            RABaseHelper.get_links_with_text_by_title(page, "Request events", "PEGASUS-PARTIAL-REFUNDED ")[0].click()
            assert common.find_field_text_by_header(page, "Response status") == "PEGASUS-PARTIAL-REFUNDED"
            assert common.find_field_text_by_header(page, "Charge amount cents") < "0"
            assert common.find_field_text_by_header(page, "Payment engine") == "pegasus"
            framework_logger.info("Refund event details verified on PEGASUS-REFUNDED page")

            # Go to BillingTransaction and confirm details
            page.go_back()
            RABaseHelper.get_links_with_text_by_title(page, "Billing transactions", "BillingTransaction")[0].click()
            assert common.find_field_text_by_header(page, "Transaction type") == "refund"
            assert common.find_field_text_by_header(page, "Status") == "succeeded"
            assert common.find_field_text_by_header(page, "Invoice status") == "ready_to_invoice"
            assert common.find_field_text_by_header(page, "Pretax cents") < "0"
            assert common.find_field_text_by_header(page, "Tax cents") < "0"
            framework_logger.info("Billing transaction details verified on BillingTransaction page")

            framework_logger.info("=== C47933531 - Billing Cycle - Payment Events, Status of partial Refund Payment and Status Code - Prepaid Finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
