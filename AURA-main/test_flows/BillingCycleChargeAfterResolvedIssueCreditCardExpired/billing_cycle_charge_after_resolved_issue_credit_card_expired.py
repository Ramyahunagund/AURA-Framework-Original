
from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
import urllib3
import time
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_charge_after_resolved_issue_credit_card_expired(stage_callback):
    framework_logger.info("=== C39509453 - Billing Cycle Charge after resolved issue - Credit Card Expired started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Add the Page Tally 100 and Shifts for 32 days and Update to Payment Problem
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.update_to_payment_problem(page)
            RABaseHelper.access_menu_of_page(page, 'Submit Charge')
            page.wait_for_selector(".btn.btn-warning", timeout=120000).click()
            page.wait_for_selector('.alert-danger.alert.alert-dismissible', timeout=150000)
            assert "Billing cycle could not be charged " in page.inner_text('.alert-danger.alert.alert-dismissible')
            framework_logger.info("Charge submitted for payment problem")

            # Sees Payment state equals to problem on subscription page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            assert RABaseHelper.get_field_text_by_title(page, "Payment state") == "problem"
            framework_logger.info("Payment state verified as 'problem'")


            # user update Pgs override response to payment Successfully Approved
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_billing_cycle_by_status(page, "PAYMENT-GATEWAY-CARD-EXPIRED")
            GeminiRAHelper.set_pgs_override_response_successfully(page)
            GeminiRAHelper.manual_retry_until_complete(page) 
            framework_logger.info("Pgs override response set to successfully approved")

            # Event Shifts 1 day 
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.event_shift(page, "1")
            framework_logger.info("Event shift set to 1 day")

            # Executes the resque job: RetryBillingParallelJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["RetryBillingParallelJob"])
            framework_logger.info("RetryBillingParallelJob executed")

            # Sees Payment state equals to ok on subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            assert RABaseHelper.get_field_text_by_title(page, "Payment state") == "ok"
            framework_logger.info("Payment state verified as 'ok'")

            # Add the Page Tally 100 and Shifts for 32 days and Update to Payment Approved
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.set_pgs_override_response_successfully(page)
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Charge submited")

            # Waits 5 minutes
            time.sleep(300)

            # Gemini Rails Admin user makes Full/Remaining refund for current billing cycle
            GeminiRAHelper.access_second_billing_cycle(page) 
            GeminiRAHelper.make_refund_option(page, "Full/Remaining Amount")

            # See Status code equals to REFUNDED on Billing cycle page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.click_billing_cycle_by_status(page, "REFUNDED")   
            success_message = page.locator(".refund_complete_field > div > div > span")
            assert common.find_field_text_by_header(page, "Refund complete") == success_message.inner_text()

            framework_logger.info("=== C39509453 - Billing Cycle Charge after resolved issue - Credit Card Expired finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()