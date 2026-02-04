from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.shipping_billing_page import ShippingBillingPage
from playwright.sync_api import expect, sync_playwright
from core.settings import GlobalState
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import test_flows_common.test_flows_common as common
import time
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def add_billing_paypal(stage_callback):
    framework_logger.info("=== C42409830 - Add Billing Paypal flow started ===")
    common.setup()
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        try:
            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page for tenant: {tenant_email}")

            # Access Shipping Billing Page
            side_menu.click_shipping_billing()
            framework_logger.info(f"Clicked on Shipping & Billing in side menu")
            
            # Sees billing section on Shipping & Billing page
            expect(shipping_billing_page.billing_section).to_be_visible(timeout=90000)
            framework_logger.info(f"Billing section is visible on Shipping & Billing page")

            # Click Add your payment method on Shipping & Billing page
            shipping_billing_page.add_payment_method.click()
            framework_logger.info(f"Clicked on Add your payment method on Shipping & Billing page")

            # Verify Billing modal with billing address
            expect(shipping_billing_page.billing_form_modal).to_be_visible(timeout=90000)
            expect(shipping_billing_page.address_billing_form_modal).to_be_visible(timeout=90000)
            framework_logger.info(f"Billing modal with billing address is visible")

            # Close the Billing modal
            shipping_billing_page.close_modal_button.click()
            framework_logger.info(f"Closed the Billing modal")

            # Click Add your payment method on Shipping & Billing page
            shipping_billing_page.add_payment_method.click()
            expect(shipping_billing_page.billing_form_modal).to_be_visible(timeout=90000)
            framework_logger.info(f"Clicked on Add your payment method on Shipping & Billing page")

            # Add Paypal as payment method
            DashboardHelper.add_billing(page, "paypal")
            framework_logger.info(f"Added Paypal as payment method")

            # Verify Billing information
            expect(shipping_billing_page.paypal_logo).to_be_visible(timeout=90000)
            framework_logger.info(f"Verified Paypal information is visible")

            # See Manage your payment method link on Shipping & Billing page
            expect(shipping_billing_page.manage_your_payment_method_link).to_be_visible()
            framework_logger.info(f"Manage your payment method link is visible on Shipping & Billing page")

            framework_logger.info("=== C42409830 - Add Billing Paypal completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e