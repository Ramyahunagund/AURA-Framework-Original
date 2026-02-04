# test_flows/BillingCycleChargeWithOverageGooglePay/billing_cycle_charge_with_overage_google_pay.py

from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC = "C61516703"

def billing_cycle_charge_with_overage_google_pay(stage_callback):
    framework_logger.info("BYS Equivalent: 52374835, C52374836, C52374837, C52374838, C52374839, C52374840")
    framework_logger.info(f"=== {TC} - Billing Cycle Charge with Overage - Items, Events and Transactions (Google Pay) flow started ===")

    # Create subscription with Google Pay payment method, 50-page plan, and shipping
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"Subscription created with Google Pay for tenant: {tenant_email}")

    with PlaywrightManager() as page:
        try:
            # Get plan data - 100 pages plan with 3 overage blocks
            plan_data = common.get_filtered_plan_data(value=100)[0]
            pages_amount = 100
            overage_blocks = 3
            overage_pages = plan_data["overageBlockSize"] * overage_blocks

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
           
            # Charge a new billing cycle with overage (130 pages for 100-page plan = 3 overage blocks)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "37")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount + overage_pages))
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"Billing cycle charged with {pages_amount + overage_pages} pages (base: {pages_amount}, overage: {overage_pages})")

            # Wait for charge processing to complete
            GeminiRAHelper.manual_retry_until_complete(page=page)
            framework_logger.info(f"Charge processing completed")

            # Verify Charge complete is true
            GeminiRAHelper.verify_charge_complete(page)
            framework_logger.info("Verified charge complete is true")

            # Verify Status code equals to CPT-100
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            assert status_code == "CPT-100", f"Expected status code 'CPT-100', got '{status_code}'"
            framework_logger.info(f"Verified status code: {status_code}")

            # Verify Invoice items include BaseChargeInvoiceItem
            links = RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "BaseChargeInvoiceItem")
            assert len(links) > 0, "BaseChargeInvoiceItem link not found"
            framework_logger.info("Verified BaseChargeInvoiceItem exists in Invoice items")

            # Verify Invoice items include OverageInvoiceItem
            links = RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "OverageInvoiceItem")
            assert len(links) > 0, "OverageInvoiceItem link not found"
            framework_logger.info("Verified OverageInvoiceItem exists in Invoice items")

            # Click on BaseChargeInvoiceItem and verify fields
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "BaseChargeInvoiceItem")[0].click()
            base_quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            base_amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")

            base_price_expected = plan_data["priceCents"]
            assert base_quantity == "1", f"Expected base charge quantity '1', got '{base_quantity}'"
            assert int(base_amount_in_cents) == base_price_expected, f"Expected base charge amount in cents '{base_price_expected}', got '{base_amount_in_cents}'"
            framework_logger.info(f"Verified BaseChargeInvoiceItem: quantity={base_quantity}, amount_in_cents={base_amount_in_cents}")

            # Go back and click on OverageInvoiceItem and verify fields
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "OverageInvoiceItem")[0].click()
            overage_quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            overage_amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")

            overage_price_expected = plan_data["overageBlockPriceCents"] * overage_blocks
            assert int(overage_quantity) == overage_blocks, f"Expected overage quantity '{overage_blocks}', got '{overage_quantity}'"
            assert int(overage_amount_in_cents) == overage_price_expected, f"Expected overage amount in cents '{overage_price_expected}', got '{overage_amount_in_cents}'"
            framework_logger.info(f"Verified OverageInvoiceItem: quantity={overage_quantity}, amount_in_cents={overage_amount_in_cents}")

            # Go back to billing cycle
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            # Verify Payment Events - Charge Payment Event
            payment_event_links = RABaseHelper.get_links_with_text_by_title(page, "Payment events", "PaymentEvent")
            assert len(payment_event_links) > 0, "Payment Event not found"
            framework_logger.info("Verified Payment Event exists")

            # Click on Charge Payment Event and verify fields
            payment_event_links[0].click()

            # Verify Event Type is 'charge'
            event_type = RABaseHelper.get_field_text_by_title(page, "Event type")
            assert event_type == "charge", f"Expected event type 'charge', got '{event_type}'"
            framework_logger.info(f"Verified Payment Event type: {event_type}")

            # Verify Payment Engine is payment_gateway
            payment_engine = RABaseHelper.get_field_text_by_title(page, "Payment engine")
            assert payment_engine == "payment_gateway", f"Expected payment engine 'payment_gateway', got '{payment_engine}'"
            framework_logger.info(f"Verified Payment Engine: {payment_engine}")

            # Verify Pretax cents is positive
            GeminiRAHelper.verify_field_is_positive(page, "Pretax cents")
            framework_logger.info("Verified Pretax cents is positive")

            # Verify Tax cents is appropriate
            GeminiRAHelper.verify_field_is_positive(page, "Tax cents")
            framework_logger.info("Verified Tax cents is positive")

            # Go back to billing cycle
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            # Verify Request Events - Charge request event
            request_event_links = RABaseHelper.get_links_with_text_by_title(page, "Request events", "CPT-100")
            assert len(request_event_links) > 0, "Charge request event with CPT-100 status not found"
            framework_logger.info("Verified Charge request event with CPT-100 status exists")

            # Click on Charge request event and verify fields
            request_event_links[0].click()

            # Verify Response status is 'CPT-100'
            response_status = RABaseHelper.get_field_text_by_title(page, "Response status")
            assert response_status == "CPT-100", f"Expected response status 'CPT-100', got '{response_status}'"
            framework_logger.info(f"Verified Request Event response status: {response_status}")

            # Verify Charge amount cents is positive
            GeminiRAHelper.verify_field_is_positive(page, "Charge amount cents")
            framework_logger.info("Verified Charge amount cents is positive")

            # Verify Payment Engine is payment_gateway
            payment_engine_req = RABaseHelper.get_field_text_by_title(page, "Payment engine")
            assert payment_engine_req == "payment_gateway", f"Expected payment engine 'payment_gateway', got '{payment_engine_req}'"
            framework_logger.info(f"Verified Request Event Payment Engine: {payment_engine_req}")

            # Go back to billing cycle
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            # Verify Billing Transactions
            billing_transaction_links = RABaseHelper.get_links_with_text_by_title(page, "Billing transactions", "BillingTransaction")
            assert len(billing_transaction_links) > 0, "Billing Transaction not found"
            framework_logger.info("Verified Billing Transaction exists")

            # Click on Billing Transaction and verify fields
            billing_transaction_links[0].click()

            # Verify Transaction type is 'charge'
            transaction_type = RABaseHelper.get_field_text_by_title(page, "Transaction type")
            assert transaction_type == "charge", f"Expected transaction type 'charge', got '{transaction_type}'"
            framework_logger.info(f"Verified Transaction type: {transaction_type}")

            # Verify Status is 'succeeded'
            transaction_status = RABaseHelper.get_field_text_by_title(page, "Status")
            assert transaction_status == "succeeded", f"Expected status 'succeeded', got '{transaction_status}'"
            framework_logger.info(f"Verified Transaction status: {transaction_status}")

            # Verify Invoice Status is 'ready_to_invoice'
            invoice_status = RABaseHelper.get_field_text_by_title(page, "Invoice status")
            assert invoice_status == "ready_to_invoice", f"Expected invoice status 'ready_to_invoice', got '{invoice_status}'"
            framework_logger.info(f"Verified Invoice status: {invoice_status}")

            # Verify Pretax cents is positive
            GeminiRAHelper.verify_field_is_positive(page, "Pretax cents")
            framework_logger.info("Verified Transaction Pretax cents is positive")

            # Verify Tax cents is positive
            GeminiRAHelper.verify_field_is_positive(page, "Tax cents")
            framework_logger.info("Verified Transaction Tax cents is positive")

            framework_logger.info(f"=== {TC} - Billing Cycle Charge with Overage - Items, Events and Transactions (Google Pay) flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
       