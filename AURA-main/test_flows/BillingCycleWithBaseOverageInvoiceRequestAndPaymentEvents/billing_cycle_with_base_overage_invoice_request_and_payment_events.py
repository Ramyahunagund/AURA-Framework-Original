from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_with_base_overage_invoice_request_and_payment_events(stage_callback):
    framework_logger.info("=== C31747195 - billing cycle with base overage invoice request and payment events ===")
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
            
            # Charge a billing cycle - Overage Charge
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_second_billing_cycle(page, "-")
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount + overage_pages))
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            GeminiRAHelper.submit_charge(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            if (status_code == "DIRECT-DEBIT-PENDING"):
                RABaseHelper.access_menu_of_page(page, 'Edit')
                page.locator("#billing_cycle_pgs_direct_debit_override").select_option("SETTLED", force=True)
                page.wait_for_selector(".btn.btn-primary", timeout=120000).click()
                GeminiRAHelper.access(page)
                GeminiRAHelper.access_tenant_page(page, tenant_email)
                GeminiRAHelper.access_subscription_by_tenant(page)
                GeminiRAHelper.event_shift(page, "8", False)

            GeminiRAHelper.complete_jobs(page, 
                                         ["SubscriptionUnsubscriberJob",
                                          "SubscriptionBillingJob", 
                                          "FetchImmutableDataDispatcherJob",
                                          "PrepareImmutableInvoiceDispatcherJob",
                                          "PrepareIdocsForFinanceDispatcherJob",
                                          "PrepareInvoicesForQtcaJob",
                                          "SendInvoicesToQtcaJob",
                                          "TransitionBillingCycleStateDispatcherJob"
                                         ])

            overage_price_expected = plan_data["overageBlockPriceCents"] * overage_blocks
            base_price_expected = plan_data["priceCents"]

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_second_billing_cycle(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")

            GeminiRAHelper.verify_charge_complete(page)
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            assert status_code == common.billing_status_code(), f"Expected status code {common.billing_status_code()}, got '{status_code}'"
            framework_logger.info("Charge complete")

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
                assert int_pretax_cents == overage_price_expected + base_price_expected, f"Expected pretax cents '{overage_price_expected + base_price_expected}', got '{int_pretax_cents}'"

            assert int_tax_cents > 0, f"Expected tax cents greater than '0', got '{int_tax_cents}'"
            assert event_type == "charge", f"Expected event type 'charge', got '{event_type}'"
            framework_logger.info("Payment events verified")

            # Billing Transactions
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            RABaseHelper.get_links_by_title(page, "Billing transactions").first.click()
            transaction_type = RABaseHelper.get_field_text_by_title(page, "Transaction type")
            invoice_status = RABaseHelper.get_field_text_by_title(page, "Invoice status")
            pretax_cents = RABaseHelper.get_field_text_by_title(page, "Pretax cents")
            tax_cents = RABaseHelper.get_field_text_by_title(page, "Tax cents")

            assert transaction_type == "charge", f"Expected transaction type 'charge', got '{transaction_type}'"
            assert invoice_status == "ready_to_invoice", f"Expected invoice status 'ready_to_invoice', got '{invoice_status}'"
            assert int(pretax_cents) == int_pretax_cents, f"Expected pretax cents '{int_pretax_cents}', got '{pretax_cents}'"
            assert int(tax_cents) == int_tax_cents, f"Expected tax cents greater than '0', got '{tax_cents}'"
            framework_logger.info("Billing transactions verified")

            # Request Events
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            RABaseHelper.get_links_by_title(page, "Request events").first.click()
            charge_amout_cents = RABaseHelper.get_field_text_by_title(page, "Charge amount cents")
            response_status = RABaseHelper.get_field_text_by_title(page, "Response status")
            payment_engine = RABaseHelper.get_field_text_by_title(page, "Payment engine")

            if ( plan_data["taxIncluded"] == True ):
                assert int(charge_amout_cents) == overage_price_expected + base_price_expected, f"Expected charge amount cents '{overage_price_expected + base_price_expected}', got '{charge_amout_cents}'"
            else:
                assert int(charge_amout_cents) == overage_price_expected + base_price_expected + int_tax_cents, f"Expected charge amount cents '{overage_price_expected + base_price_expected + int_tax_cents}', got '{charge_amout_cents}'"
            assert response_status == common.billing_status_code(), f"Expected response status '{common.billing_status_code()}', got '{response_status}'"
            assert payment_engine == common.payment_engine(), f"Expected payment engine '{common.payment_engine()}', got '{payment_engine}'"
            framework_logger.info("Request events verified")

            # Invoice items Base
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "BaseChargeInvoiceItem")[0].click()
            quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")

            assert quantity == "1", f"Expected quantity '1', got '{quantity}'"
            assert int(amount_in_cents) == base_price_expected, f"Expected amount in cents '799', got '{amount_in_cents}'"
            framework_logger.info("Invoice items BASE verified")
            
            # Invoice items Overage
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "OverageInvoiceItem")[0].click()
            quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")

            assert int(quantity) == overage_blocks, f"Expected quantity {overage_blocks}, got '{quantity}'"
            assert int(amount_in_cents) == overage_price_expected, f"Expected amount in cents '{overage_price_expected}', got '{amount_in_cents}'"
            framework_logger.info("Invoice items Overage verified")

            # Base
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)

            # Charge a billing cycle
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            GeminiRAHelper.calculate_and_define_page_tally(page, pages_amount - 10)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            GeminiRAHelper.submit_charge(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
                                           
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            if (status_code == "DIRECT-DEBIT-PENDING"):
                RABaseHelper.access_menu_of_page(page, 'Edit')
                page.locator("#billing_cycle_pgs_direct_debit_override").select_option("SETTLED", force=True)
                page.wait_for_selector(".btn.btn-primary", timeout=120000).click()
                GeminiRAHelper.access(page)
                GeminiRAHelper.access_tenant_page(page, tenant_email)
                GeminiRAHelper.access_subscription_by_tenant(page)
                GeminiRAHelper.event_shift(page, "8", False)

            GeminiRAHelper.complete_jobs(page, 
                                         ["SubscriptionUnsubscriberJob",
                                          "SubscriptionBillingJob", 
                                          "FetchImmutableDataDispatcherJob",
                                          "PrepareImmutableInvoiceDispatcherJob",
                                          "PrepareIdocsForFinanceDispatcherJob",
                                          "PrepareInvoicesForQtcaJob",
                                          "SendInvoicesToQtcaJob",
                                          "TransitionBillingCycleStateDispatcherJob"
                                         ])

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_second_billing_cycle(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            GeminiRAHelper.verify_charge_complete(page)
            framework_logger.info("Second Charge complete")

            framework_logger.info("=== C31747195 - billing cycle with base overage invoice request and payment events ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
