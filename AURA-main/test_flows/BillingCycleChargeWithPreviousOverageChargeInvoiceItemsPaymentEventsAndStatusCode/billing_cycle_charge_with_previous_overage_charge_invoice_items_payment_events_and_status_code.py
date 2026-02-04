from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.ra_base_helper import RABaseHelper
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_charge_with_previous_overage_charge_invoice_items_payment_events_and_status_code(stage_callback):
    framework_logger.info("=== C44678908/C39493904 - Billing Cycle Charge with previous overage charge with Invoice Items, Payment Events, Status Code flow started ===")
    tenant_email = create_ii_subscription(stage_callback)
    with PlaywrightManager() as page:
        try:
            plan_data = common.get_filtered_plan_data()[0]
            pages_amount = 100
            overage_blocks = 5
            overage_pages = plan_data["overageBlockSize"] * overage_blocks

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.remove_free_months(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status changed to 'subscribed'")

            # Charge the first billing cycle
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount))
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"First billing cycle charged with page tally")

            # Charge the second billing cycle without page tally
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page) 
            GeminiRAHelper.event_shift(page, event_shift="37")
            GeminiRAHelper.access_second_billing_cycle(page) 
            GeminiRAHelper.calculate_page_tally(page)               
            GeminiRAHelper.submit_charge(page)   
            GeminiRAHelper.manual_retry_until_complete(page=page) 
            framework_logger.info(f"Second billing cycle charged without page tally")

            # Sees BaseChargeInvoiceItem on Invoice items
            RABaseHelper.get_field_text_by_title(page, "Invoice items") == "BaseChargeInvoiceItem"
            framework_logger.info("Invoice items verified as BaseChargeInvoiceItem")

            # Add the page tally on the second billing cycle to generate overage charge
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount + overage_pages))
            framework_logger.info(f"Page tally updated on the second billing cycle")

            # Sees status code
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            assert status_code == common.billing_status_code(), f"Expected status code {common.billing_status_code()}, got '{status_code}'"
            framework_logger.info(f"Status code verified: {status_code}")
           
            # Charge the third billing cycle with page tally to generate overage charge
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "37")
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount + overage_pages))
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Third billing cycle charged")

            base_price_expected = plan_data["priceCents"]
            overage_price_expected = plan_data["overageBlockPriceCents"] * overage_blocks
            previous_price_expected = plan_data["overageBlockPriceCents"] * overage_blocks

            # Invoice items - Base charge
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "BaseChargeInvoiceItem")[0].click()
            quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")

            assert quantity == "1", f"Expected quantity '1', got '{quantity}'"
            assert int(amount_in_cents) == base_price_expected, f"Expected amount in cents '799', got '{amount_in_cents}'"
            framework_logger.info(f"Invoice items Base Charge verified: quantity={quantity}, amount_in_cents={amount_in_cents}")
            
            # Invoice items - Overage charge
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "OverageInvoiceItem")[0].click()
            quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")

            assert int(quantity) == overage_blocks, f"Expected quantity {overage_blocks}, got '{quantity}'"
            assert int(amount_in_cents) == overage_price_expected, f"Expected amount in cents '{overage_price_expected}', got '{amount_in_cents}'"
            framework_logger.info("Invoice items Overage Charge verified")

            # Invoice items - Previous charge
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "PreviousOverageInvoiceItem")[0].click()
            quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")

            assert int(quantity) == overage_blocks, f"Expected quantity {overage_blocks}, got '{quantity}'"
            assert int(amount_in_cents) == previous_price_expected, f"Expected amount in cents '{previous_price_expected}', got '{amount_in_cents}'"
            framework_logger.info("Invoice items Previous Charge verified")

            # Sees charge complete status
            page.go_back()
            GeminiRAHelper.verify_charge_complete(page)
            framework_logger.info("Sees charge complete status")

            # Payment Events
            RABaseHelper.get_links_by_title(page, "Payment events").first.click()
            payment_engine = RABaseHelper.get_field_text_by_title(page, "Payment engine")
            int_pretax_cents = int(RABaseHelper.get_field_text_by_title(page, "Pretax cents"))
            int_tax_cents = int(RABaseHelper.get_field_text_by_title(page, "Tax cents"))
            event_type = RABaseHelper.get_field_text_by_title(page, "Event type")

            assert payment_engine == common.payment_engine(), f"Expected payment engine '{common.payment_engine()}', got '{payment_engine}'"
            if ( plan_data["taxIncluded"] == True ):
                assert int_pretax_cents < overage_price_expected + base_price_expected, f"Expected pretax cents '{overage_price_expected + base_price_expected}', got '{int_pretax_cents}'"
                assert int_pretax_cents > 0, f"Expected pretax cents greater than '0', got '{int_pretax_cents}'"
            else:
                assert int_pretax_cents == overage_price_expected + base_price_expected + previous_price_expected, f"Expected pretax cents '{overage_price_expected + base_price_expected + previous_price_expected}', got '{int_pretax_cents}'"

            assert int_tax_cents > 0, f"Expected tax cents greater than '0', got '{int_tax_cents}'"
            assert event_type == "charge", f"Expected event type 'charge', got '{event_type}'"
            framework_logger.info("Payment events verified")

            framework_logger.info("=== C44678908/C39493904 - Billing Cycle Charge with previous overage charge with Invoice Items, Payment Events, Status Code flow completed ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
