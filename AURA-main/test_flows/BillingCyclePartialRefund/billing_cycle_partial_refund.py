from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from pages.gemini_admin_page import GeminiAdminPage
from test_flows.EnrollmentOOBE.enrollment_oobe import enrollment_oobe
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_partial_refund(stage_callback):
    framework_logger.info("=== C48514904 - Billing Cycle - Partial Refund Started ===")
    tenant_email = create_ii_subscription(stage_callback)

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
            GeminiRAHelper.remove_free_months(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status changed to 'subscribed'")

            # Charge a new billing cycle with 100 pages + blocks of overage pages
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "37")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount + overage_pages))
            GeminiRAHelper.submit_charge(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            framework_logger.info(f"New billing cycle charged with {pages_amount} pages + {overage_pages} overage pages")

            GeminiRAHelper.update_direct_debit_status(page)
            GeminiRAHelper.complete_jobs(page, 
                                         ["SubscriptionUnsubscriberJob",
                                          "SubscriptionBillingJob", 
                                          "FetchImmutableDataDispatcherJob",
                                          "PrepareImmutableInvoiceDispatcherJob",
                                          "PrepareIdocsForFinanceDispatcherJob",
                                          "PrepareInvoicesForQtcaJob",
                                          "SendInvoicesToQtcaJob"
                                           ])

            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_second_billing_cycle(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            # Verify Status code on Billing cycle page
            expected_status_code = common.billing_status_code()
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", expected_status_code)
            framework_logger.info(f"Verified Status code '{expected_status_code}' on billing cycle page")

            # Sees Charge complete status true on billing cycle page
            GeminiRAHelper.verify_charge_complete(page)
            framework_logger.info(f"Verified Charge complete is 'True' on billing cycle page")
            
            # Makes partial refund for current billing cycle
            GeminiRAHelper.make_refund_option(page, "Instant Ink Overage Blocks", blocks=overage_blocks)
            framework_logger.info("Instant Ink Overage Blocks refund made for current billing cycle")
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            GeminiRAHelper.update_direct_debit_status_after_refund(page)

            refund_complete = RABaseHelper.get_boolean_value_by_title(page, "Refund complete")
            assert refund_complete == False, f"Expected Refund complete to be 'False', got '{refund_complete}'"

            refund_status = common.refund_status()
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", refund_status)
            framework_logger.info("Verified Refund complete is 'False' and correct Status code on billing cycle page")

            # Verify invoice details
            RABaseHelper.get_links_by_title(page, "Refunded invoice items").first.click()
            GeminiRAHelper.verify_rails_admin_info(page, "Quantity", str(overage_blocks))
            GeminiRAHelper.verify_rails_admin_info(page, "Amount in cents", str(plan_data["overageBlockPriceCents"] * overage_blocks))
            invoice = RABaseHelper.get_link_urls_by_title(page, "Invoice item")
            assert len(invoice) > 0, "Invoice link not found"
            framework_logger.info("Refunded invoice items verified")

            page.go_back()

            # payment events
            RABaseHelper.get_links_by_title(page, "Payment events").first.click()
            GeminiRAHelper.verify_rails_admin_info(page, "Event type", "partial-refund")
            pretax = RABaseHelper.get_field_text_by_title(page, "Pretax cents")
            tax = RABaseHelper.get_field_text_by_title(page, "Tax cents")
            expected_pretax = f"-{plan_data['overageBlockPriceCents'] * overage_blocks}"

            if plan_data["taxIncluded"] == False:
                assert pretax == expected_pretax, f"Expected Pretax cents '{expected_pretax}', got '{pretax}'"
                assert int(tax) < 0, f"Expected Tax cents to be negative, got '{tax}'"
            else:
                assert int(pretax) > int(expected_pretax), f"Expected Pretax cents '{expected_pretax}', got '{pretax}'"
                assert int(tax) < 0, f"Expected Tax cents to be positive, got '{tax}'"
                assert int(pretax) + int(tax) == int(expected_pretax), f"Expected Pretax + Tax to be '{expected_pretax}', got '{int(pretax) + int(tax)}'"
            framework_logger.info("Payment event details verified")

            page.go_back()

            # request events
            RABaseHelper.get_links_by_title(page, "Request events").first.click()
            GeminiRAHelper.verify_rails_admin_info(page, "Response status", common.request_event_response_status())
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", common.payment_engine())
            charge_amount = RABaseHelper.get_field_text_by_title(page, "Charge amount cents")

            if plan_data["taxIncluded"] == False:
                assert charge_amount == str(int(expected_pretax) + int(tax)), f"Expected Charge amount cents '{int(expected_pretax) + int(tax)}', got '{charge_amount}'"
            else:
                assert charge_amount == str(int(expected_pretax)), f"Expected Charge amount cents '{int(expected_pretax)}', got '{charge_amount}'"

            page.go_back()

            # Billing transactions
            RABaseHelper.get_links_by_title(page, "Billing transactions").first.click()
            GeminiRAHelper.verify_rails_admin_info(page, "Transaction type", "refund")
            GeminiRAHelper.verify_rails_admin_info(page, "Invoice status", "ready_to_invoice")
            pretax = RABaseHelper.get_field_text_by_title(page, "Pretax cents")
            tax = RABaseHelper.get_field_text_by_title(page, "Tax cents")

            if plan_data["taxIncluded"] == False:
                assert pretax == expected_pretax, f"Expected Pretax cents '{expected_pretax}', got '{pretax}'"
                assert int(tax) < 0, f"Expected Tax cents to be negative, got '{tax}'"
            else:
                assert int(pretax) > int(expected_pretax), f"Expected Pretax cents '{expected_pretax}', got '{pretax}'"
                assert int(tax) < 0, f"Expected Tax cents to be positive, got '{tax}'"
                assert int(pretax) + int(tax) == int(expected_pretax), f"Expected Pretax + Tax to be '{expected_pretax}', got '{int(pretax) + int(tax)}'"

            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_second_billing_cycle(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            # Refund option - Full/Remaining Amount
            GeminiRAHelper.make_refund_option(page, "Full/Remaining Amount")
            framework_logger.info("Refund option 'Full/Remaining Amount' selected")

            GeminiRAHelper.update_direct_debit_status_after_refund(page)
            # Verify refund complete
            GeminiRAHelper.verify_refund_complete(page)
            framework_logger.info("Refund completed successfully")

            # Sees status code - Refunded
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            assert status_code == "REFUNDED", f"Expected status code REFUNDED, got '{status_code}'"
            framework_logger.info(f"Status code verified: {status_code}")

            # Invoice items - RefundedInvoiceItem
            RABaseHelper.get_links_with_text_by_title(page, "Refunded invoice items", "RefundedInvoiceItem")[0].click()
            RABaseHelper.get_links_with_text_by_title(page, "Invoice item", "1 * BaseChargeInvoiceItem")[0].click()
            quantity = RABaseHelper.get_field_text_by_title(page, "Quantity")
            amount_in_cents = RABaseHelper.get_field_text_by_title(page, "Amount in cents")

            assert quantity == "1", f"Expected quantity '1', got '{quantity}'"
            base_price_expected = plan_data["priceCents"]
            assert int(amount_in_cents) == base_price_expected, f"Expected amount in cents {base_price_expected}, got '{amount_in_cents}'"
            page.go_back()
            framework_logger.info(f"Invoice items base charge verified on Refunded Invoice Item page: quantity={quantity}, amount_in_cents={amount_in_cents}")
            
            # Clicks link with text Billing::PaymentEvent on Refunded Invoice Items page and confirm details
            page.go_back()
            RABaseHelper.get_links_with_text_by_title(page, "Payment events", "Billing::PaymentEvent")[0].click()
            assert common.find_field_text_by_header(page, "Event type") == "refund"
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", common.payment_engine())
            assert common.find_field_text_by_header(page, "Pretax cents") < "0"
            assert common.find_field_text_by_header(page, "Tax cents") < "0"
            framework_logger.info("Refunded invoice items details verified on Billing Payment Event page")
            
            # Clicks link with text for refund on the Request Events and confirm details
            page.go_back()

            RABaseHelper.get_links_with_text_by_title(page, "Request events", common.request_event_response_status(full=True))[0].click()
            assert common.find_field_text_by_header(page, "Response status") == common.request_event_response_status(full=True)
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", common.payment_engine())
            assert common.find_field_text_by_header(page, "Charge amount cents") < "0"
            framework_logger.info("Request events details verified on Request Events page")

            # Clicks link with text BillingTransaction in the Billing Transactions and confirm details
            page.go_back()
            RABaseHelper.get_links_with_text_by_title(page, "Billing transactions", "BillingTransaction")[0].click()
            assert common.find_field_text_by_header(page, "Transaction type") == "refund"
            assert common.find_field_text_by_header(page, "Status") == "succeeded"
            assert common.find_field_text_by_header(page, "Invoice status") == "ready_to_invoice"
            assert common.find_field_text_by_header(page, "Pretax cents") < "0"
            assert common.find_field_text_by_header(page, "Tax cents") < "0"
            framework_logger.info("BillingTransaction details verified on Billing Transactions page")

            # Verify refund payment button is not visible
            page.go_back()
            gemini_admin = GeminiAdminPage(page)
            assert gemini_admin.refund_payment_button.count() == 0
            framework_logger.info("Refund payment button is not visible")

            framework_logger.info("=== C48514904 - Billing Cycle - Partial Refund Finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
