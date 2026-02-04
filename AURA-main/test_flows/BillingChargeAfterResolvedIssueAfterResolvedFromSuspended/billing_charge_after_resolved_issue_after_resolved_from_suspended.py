
from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from pages.shipping_billing_page import ShippingBillingPage
import test_flows_common.test_flows_common as common
import urllib3
import time
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_charge_after_resolved_issue_after_resolved_from_suspended(stage_callback):
    framework_logger.info("=== C39540143 - Billing charge after resolved issue - After resolved from suspended flow started ===")
    tenant_email = create_ii_subscription(stage_callback)
    
    with PlaywrightManager() as page:
        shipping_billing_page = ShippingBillingPage(page)
        try:
            # Move subscription to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Add the Page Tally 100 and Shifts for 32 days and update to Payment Problem
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.update_to_payment_problem(page)
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Charge submited for payment problem")

            # Sees Payment state equals to problem on subscription page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            assert RABaseHelper.get_field_text_by_title(page, "Payment state") == "problem"
            framework_logger.info("Payment state verified as 'problem'")

            # New event shift - 14 days
            GeminiRAHelper.event_shift(page, "14")
            framework_logger.info("Event shifted by 14 days")

            # Execute the resque job: SubscriptionSuspenderJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionSuspenderJob"])
            framework_logger.info("SubscriptionSuspenderJob executed")

            # Sees Payment state equals to suspended on subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            time.sleep(10)
            page.reload()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "suspended")
            framework_logger.info("Subscription state verified as 'suspended'")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Shipping & Billing page
            DashboardHelper.access_shipping_billing_page(page)
            framework_logger.info("Accessed Shipping & Billing page")
           
            # Change payment method to credit_card_master
            shipping_billing_page.manage_your_payment_method_link.click()
            DashboardHelper.add_billing(page, "credit_card_master_2_series")
            framework_logger.info("Changed payment method to credit_card_master")

            # Billing cycle with problem is set to successfully approved for status CPT-201
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            time.sleep(60)
            page.reload()

            GeminiRAHelper.click_billing_cycle_by_status(page, "CPT-201")
            GeminiRAHelper.set_pgs_override_response_successfully(page)
            GeminiRAHelper.manual_retry_until_complete(page)
            framework_logger.info("Billing cycle with problem set to successfully approved")

            # New event shift - 1 day
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.event_shift(page, "1", force_billing=False)
            framework_logger.info("Event shifted by 1 day")  

            # Executes the resque job: RetryBillingParallelJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["RetryBillingParallelJob"])
            framework_logger.info("RetryBillingParallelJob executed")

            # Sees Payment state equals to ok on subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            time.sleep(60)
            page.reload()
            assert RABaseHelper.get_field_text_by_title(page, "Payment state") == "ok"
            framework_logger.info("Payment state verified as 'ok'")

            # Add the Page Tally 100 and Shifts for 32 days and Update to Payment Approved
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.access_second_billing_cycle(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Charge submited to payment approved")

            # Makes Full/Remaining refund for current billing cycle
            GeminiRAHelper.make_refund_option(page, "Full/Remaining Amount")
            framework_logger.info("Full/Remaining refund made for current billing cycle")

            # See Status code equals to REFUNDED on Billing cycle page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.click_billing_cycle_by_status(page, "REFUNDED")   
            success_message = page.locator(".refund_complete_field > div > div > span")
            assert common.find_field_text_by_header(page, "Refund complete") == success_message.inner_text()

            framework_logger.info("=== C39540143 - Billing charge after resolved issue - After resolved from suspended flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()