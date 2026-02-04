from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.shipping_billing_page import ShippingBillingPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def credit_card_update_in_progress(stage_callback):
    framework_logger.info("=== C52427639 - Credit Card Update In Progress flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        side_menu = DashboardSideMenuPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Shift subscription and add page tally
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            framework_logger.info(f"Event shift by 32 days and page tally set to 100 pages")

            # Update Pgs override response to payment problem
            GeminiRAHelper.update_to_payment_problem(page)
            framework_logger.info(f"PGS override response updated to 'payment problem'")

            # Submit charge on billing cycle
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Submitted charge")

            # See Payment state equals to problem on subscription page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "problem")

            # Shift subscription for 14 days
            GeminiRAHelper.event_shift(page, "14")
            framework_logger.info("Shifted subscription by 14 days")

            # Executes the job: SubscriptionSuspenderJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionSuspenderJob"])
            framework_logger.info("SubscriptionSuspenderJob executed")

            # See Payment state equals to suspended on subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "suspended", True)

            # Open instant ink dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page")

            # Click on Update Payment Method button at UCDE
            overview_page.update_payment_method.click()
            framework_logger.info("Clicked on Update Payment Method on Overview page")

            # Click Manage your payment method on Shipping & Billing page
            shipping_billing_page.manage_your_payment_method_link.click()
            expect(shipping_billing_page.billing_form_modal).to_be_visible(timeout=90000)
            framework_logger.info(f"Clicked on Manage your payment method on Shipping & Billing page")

            # Sets credit_card_visa credit card billing data at UCDE
            DashboardHelper.add_billing(page, "credit_card_visa")
            framework_logger.info(f"Added Visa credit card as payment method")

            # Access Overview Menu at UCDE
            side_menu.click_overview()
            framework_logger.info(f"Accessed Overview in side menu")
           
            # See "Billing Update in Progress" notification on Notification Icon
            DashboardHelper.see_notification_on_icon(page, "Billing Update in Progress")
            framework_logger.info(f"'Billing Update in Progress' notification is visible on bell icon")

            # Access Notifications Menu
            side_menu.click_notifications()
            framework_logger.info(f"Accessed Notifications in side menu")

            # See "Billing Update in Progress" notification on Notification page
            DashboardHelper.see_notification_on_dashboard(page, "Billing Update in Progress")
            framework_logger.info(f"'Billing Update in Progress' notification is visible on Notifications page")

            # Billing cycle with problem is set to successfully approved for status CPT-201
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            for attempt in range(10):
                try:
                    GeminiRAHelper.click_billing_cycle_by_status(page, "CPT-201")
                    framework_logger.info("Billing cycle with problem is set to successfully approved for status CPT-201")
                    break
                except Exception as e:
                    if attempt == 9: 
                        raise e
                    page.reload()
                    page.go_back()
            GeminiRAHelper.set_pgs_override_response_successfully(page)
            GeminiRAHelper.manual_retry_until_complete(page)

            # And the user shifts its subscription for 1 days
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.event_shift(page, "1")
            framework_logger.info("Shifted subscription by 1 day")

            # Executes the job: RetryBillingParallelJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["RetryBillingParallelJob"])
            framework_logger.info("RetryBillingParallelJob executed")

            # See Payment state equals to ok on subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "ok", True)

            # And rails admin user clicks link with text payment_update in the Notification events on the Subscription page
            RABaseHelper.access_link_by_title(page, "payment_update", "Notification events")
            framework_logger.info("Clicked on payment_update link in Notification events")

            # See Status equals to sent/complete on Notification event page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "sent")

            # Open instant ink dashboard page
            DashboardHelper.access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page")

            # Access Notifications Menu
            side_menu.click_notifications()
            framework_logger.info(f"Accessed Notifications in side menu")

            # See "Payment method successfully updated" notification on Notification page
            DashboardHelper.see_notification_on_dashboard(page, "Payment method successfully updated")
            framework_logger.info(f"'Payment method successfully updated' notification is visible on Notifications page")

            # Access Print History link
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # And the user sees "HP Instant Ink Service Restored" notification on Print History card
            PrintHistoryHelper.see_notification_on_print_history(page, "HP Instant Ink Service Restored")
            framework_logger.info(f"'HP Instant Ink Service Restored' notification is visible on Print History page")

            framework_logger.info("=== C52427639 - Credit Card Update In Progress flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
