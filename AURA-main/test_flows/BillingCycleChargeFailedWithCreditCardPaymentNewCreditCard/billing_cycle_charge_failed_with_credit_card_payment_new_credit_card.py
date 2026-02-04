from helper.dashboard_helper import DashboardHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.shipping_billing_page import ShippingBillingPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import time
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_charge_failed_with_credit_card_payment_new_credit_card(stage_callback):
    framework_logger.info("=== C49152723 - Billing Cycle Charge Failed with CC payment - New CC started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
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
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Billing cycle with page tally 100 and payment problem set")

            # Sees Payment state equals to problem on subscription page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            assert RABaseHelper.get_field_text_by_title(page, "Payment state") == "problem"
            framework_logger.info("Payment state verified as 'problem'")

            # Event Shifts 14 days
            GeminiRAHelper.event_shift(page, "14")
            framework_logger.info("Event shifted by 14 days")

            # Executes the resque job: SubscriptionSuspenderJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionSuspenderJob"])
            framework_logger.info("SubscriptionSuspenderJob executed")

            # Sees Payment state equals to suspended on subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "suspended")
            framework_logger.info("Subscription state verified as 'suspended'")

            # Open instant ink dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page")

            # The user sees the subscription suspension text
            expect(overview_page.suspended_text).to_be_visible()
            framework_logger.info("Suspended text is visible")

            # Clicks on Update Billing button
            DashboardHelper.access_shipping_billing_page(page)
            framework_logger.info("Accessed Shipping and Billing page")

            shipping_billing_page = ShippingBillingPage(page)
            shipping_billing_page.manage_your_payment_method_link.click()

            # Clicks in change payment method
            DashboardHelper.add_pgs_billing(page, card_type='credit_card_visa')
            framework_logger.info("Different Payment method has been added")

            # Billing cycle with problem is set to successfully approved for status CPT-201
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_second_billing_cycle(page)
            GeminiRAHelper.set_pgs_override_response_successfully(page)
            GeminiRAHelper.manual_retry_until_complete(page)  

            # Event Shifts 1 day
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.event_shift(page, "1")
            framework_logger.info("Event shifted by 1 day")

            # Executes the resque job: RetryBillingParallelJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["RetryBillingParallelJob"])
            framework_logger.info("RetryBillingParallelJob executed")

            # Sees Payment state equals to ok on subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "ok")
            framework_logger.info("Payment state verified as 'ok'")

            framework_logger.info("=== C49152723 - Billing Cycle Charge Failed with CC payment - New CC finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()