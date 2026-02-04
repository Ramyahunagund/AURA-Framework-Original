from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.shipping_billing_page import ShippingBillingPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect, sync_playwright

import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def paypal_account_updated(stage_callback):
    framework_logger.info("=== C52792955 - PayPal Account Updated test flow started ===")

    tenant_email = create_ii_subscription(stage_callback)
    with PlaywrightManager() as page:
        try:
            # Step 1: Identify user and move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription moved to subscribed")
                                  
            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            side_menu = DashboardSideMenuPage(page)
            # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")

            # User clicks on Shipping & Billing Menu at UCDE
            side_menu.click_shipping_billing()

            # Click Add your payment method on Shipping & Billing page
            shipping_billing_page = ShippingBillingPage(page)
            shipping_billing_page.wait.manage_your_payment_method_link().click()
            expect(shipping_billing_page.billing_form_modal).to_be_visible(timeout=90000)
            framework_logger.info(f"Clicked on Add your payment method on Shipping & Billing page")

            # Add Paypal as payment method
            DashboardHelper.add_billing(page, "paypal")
            framework_logger.info(f"Added Paypal as payment method")

            # Verify Billing information
            expect(shipping_billing_page.paypal_logo).to_be_visible(timeout=90000)
            framework_logger.info(f"Verified Paypal information is visible")

            side_menu.notifications_submenu_link.click()
            framework_logger.info("Accessed Notifications page")

            # Verify cancellation confirmation notification is visible
            DashboardHelper.see_notification_on_dashboard(page, "Billing Update in Progress")
            framework_logger.info("Verified cancellation confirmation notification is visible")

            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)

            RABaseHelper.access_link_by_title_with_retry(page, "payment_update", "Notification events")

            status = RABaseHelper.get_field_text_by_title(page, "Status")
            assert status == "complete" or status == "sent", f"Expected status to be 'complete' or 'sent', but got '{status}'"
            framework_logger.info("Verified notification events on Rails Admin")

        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
