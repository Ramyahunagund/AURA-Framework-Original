from helper.ra_base_helper import RABaseHelper
from pages.gemini_admin_page import GeminiAdminPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_payment_events_status_of_refund_payment_and_status_code(stage_callback):
    framework_logger.info("=== C44678885 - Billing Cycle - Payment Events, Status of Refund Payment and Status Code flow started ===")
    tenant_email = create_ii_subscription(stage_callback)
    with PlaywrightManager() as page:
        try:
            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
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

            # Verify refund payment button is not visible
            gemini_admin = GeminiAdminPage(page)
            assert gemini_admin.refund_payment_button.count() == 0
            framework_logger.info("Refund payment button is not visible")

            # Clicks link with text Billing::PaymentEvent in the Payment events on the Billing cycle page and confirm details
            RABaseHelper.get_links_with_text_by_title(page, "Payment events", "Billing::PaymentEvent")[0].click()
            int_pretax_cents = int(RABaseHelper.get_field_text_by_title(page, "Pretax cents"))
            int_tax_cents = int(RABaseHelper.get_field_text_by_title(page, "Tax cents"))

            assert common.find_field_text_by_header(page, "Payment engine") == "no_engine"
            assert int_pretax_cents == 0, f"Expected pretax cents to be '0', got '{int_pretax_cents}'"
            assert int_tax_cents == 0, f"Expected tax cents to be '0', got '{int_tax_cents}'"
            assert common.find_field_text_by_header(page, "Event type") == "charge"
            framework_logger.info("Payment event details verified on Payment Event page")

            # Goes to billing summary page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            framework_logger.info("Billing summary page accessed")

            # Verify the last billing cycle data
            GeminiRAHelper.billing_cycle_data(page, plan="100", tally="100", status="NO-CHARGE", charge_complete="true", billable_type="BillingCycle")
            framework_logger.info("Billing cycle data verified")

            framework_logger.info("=== C44678885 - Billing Cycle - Payment Events, Status of Refund Payment and Status Code flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
