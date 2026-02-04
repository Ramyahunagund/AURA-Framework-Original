from helper.ra_base_helper import RABaseHelper
from pages.cancellation_page import CancellationPage
from pages.overview_page import OverviewPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_payment_events_status_of_full_refund_payment_and_status_code_prepaid(stage_callback):
    framework_logger.info("=== C46073766 - Billing Cycle - Payment Events, Status of full Refund Payment and Status Code - Prepaid Started ===")
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
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 100 pages")
            
            # Charge a new billing cycle for 37 days with 130 pages and makes Full/Remaining refund for current billing cycle
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.event_shift(page, "37")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "130")
            GeminiRAHelper.submit_charge(page)
            GeminiRAHelper.make_refund_option(page, "Full/Remaining Amount")
            framework_logger.info(f"New billing cycle charged with 130 pages")

            # See Status code equals to REFUNDED on Billing cycle page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.click_billing_cycle_by_status(page, "REFUNDED")   
            success_message = page.locator(".refund_complete_field > div > div > span")
            assert common.find_field_text_by_header(page, "Refund complete") == success_message.inner_text()
            framework_logger.info("Status code equals to REFUNDED verified on Billing cycle page")

            # Clicks link with text BaseChargeInvoiceItem in the Invoice item page
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "BaseChargeInvoiceItem")[0].click()
            framework_logger.info("Accessed BaseChargeInvoiceItem page")

            # Sees Quantity equals to 1 on and Amount in cents equals to 799 Details for Invoice page
            assert common.find_field_text_by_header(page, "Quantity") == "1"
            assert common.find_field_text_by_header(page, "Amount in cents") == "799"
            framework_logger.info("Quantity and Amount in cents verified on Details for Invoice page")

            # Clicks link with text OverageInvoiceItem in the Invoice item page
            page.go_back()
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "OverageInvoiceItem")[0].click()
            framework_logger.info("Accessed OverageInvoiceItem page")

            # Sees Quantity equals to 3 on and Amount in cents equals to 450 Details for Invoice page
            assert common.find_field_text_by_header(page, "Quantity") == "3"
            assert common.find_field_text_by_header(page, "Amount in cents") == "450"
            framework_logger.info("Quantity and Amount in cents verified on Details for Invoice page")

            # Clicks link with text Billing::PaymentEvent in the Payment events on the Billing cycle page and confirm details
            page.go_back()
            RABaseHelper.get_links_with_text_by_title(page, "Payment events", "Billing::PaymentEvent")[0].click()
            assert common.find_field_text_by_header(page, "Event type") == "refund"
            assert common.find_field_text_by_header(page, "Payment engine") == "pegasus"
            assert common.find_field_text_by_header(page, "Pretax cents") == "-1249"
            assert common.find_field_text_by_header(page, "Tax cents") == "-110"
            framework_logger.info("Payment event details verified on Billing::PaymentEvent page")

            # On Refunded page on Billing Cycle page confirm details
            page.go_back()
            RABaseHelper.get_links_with_text_by_title(page, "Request events", "PEGASUS-REFUNDED")[0].click()
            assert common.find_field_text_by_header(page, "Response status") == "PEGASUS-REFUNDED"
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

            framework_logger.info("=== C46073766 - Billing Cycle - Payment Events, Status of full Refund Payment and Status Code - Prepaid Finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
