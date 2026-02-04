# test_flows/TwoCheckoutFlow/two_checkout_flow.py

import time
import traceback
import urllib3
from pages.confirmation_page import ConfirmationPage
import test_flows_common.test_flows_common as common
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.hpid_helper import HPIDHelper
from pages.overview_page import OverviewPage
from pages.shipping_billing_page import ShippingBillingPage
from playwright.sync_api import expect

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def two_checkout_flow(stage_callback):
    framework_logger.info("=== C28565444 - 2Checkout flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        confirmation_page = ConfirmationPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        try:
            # Step 1: Access Dashboard and navigate to Billing page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Navigate to Billing page
            DashboardHelper.access_shipping_billing_page(page)
            framework_logger.info("Accessed Shipping and Billing page")

            # Click on "Change Payment Method" link
            shipping_billing_page.manage_your_payment_method_link.click()
            framework_logger.info("Clicked 'Change Payment Method' link")

            # Wait more than 15 minutes (901 seconds)
            framework_logger.info("Waiting for 901 seconds (15+ minutes)...")
            time.sleep(901)
            framework_logger.info("Waited 901 seconds")

            # Sees the sign in again modal after timeout
            confirmation_page.billing_continue_button.click()
            shipping_billing_page.manage_your_payment_method_link.click()
            framework_logger.info("Clicked 'Change Payment Method' link after timeout")

            # Verify user is redirected to HPID Sign In page
            overview_page.expired_session_login.click()

            page.wait_for_load_state("load", timeout=60000)
            if "login" in page.url.lower() or "signin" in page.url.lower():
                framework_logger.info("User redirected to HPID Sign In page as expected")
            else:
                framework_logger.warning(f"Expected HPID Sign In page, but current URL is: {page.url}")

            # Step 2: Login with the same account
            HPIDHelper.sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in with email: {tenant_email}")

            # Navigate to Billing page
            DashboardHelper.access_shipping_billing_page(page)
            framework_logger.info("Accessed Shipping and Billing page")

            # Click on "Change Payment Method" link
            shipping_billing_page.manage_your_payment_method_link.click()
            framework_logger.info("Clicked 'Change Payment Method' link")

            # Add 2checkout billing details
            DashboardHelper.add_billing(page, "credit_card_master")
            framework_logger.info("Added 2checkout billing details")

            # Verify user is redirected to the Billing page
            page.wait_for_load_state("load", timeout=60000)
            expect(shipping_billing_page.page_title).to_be_visible(timeout=120000)
            framework_logger.info("Successfully redirected to Billing page after sign in")

            # Step 3: Check the billing info and verify no error displayed
            expect(shipping_billing_page.billing_section).to_be_visible(timeout=30000)
            framework_logger.info("Billing section is visible")

            # Verify no error messages
            error_selector = shipping_billing_page.elements.error_message
            if page.locator(error_selector).count() > 0:
                error_text = page.locator(error_selector).first.text_content()
                framework_logger.error(f"Error displayed: {error_text}")
                raise AssertionError(f"Unexpected error message displayed: {error_text}")
            else:
                framework_logger.info("No error messages displayed - billing info check passed")

            # Step 4: Click "Change Payment Method" again and add new 2checkout billing
            shipping_billing_page.manage_your_payment_method_link.click()
            framework_logger.info("Clicked 'Change Payment Method' link again")

            # Add 2checkout billing details again
            DashboardHelper.add_billing(page, "credit_card_master_2_series")
            framework_logger.info("Added 2checkout billing details for the second time")

            # Verify the new information for billing is saved successfully
            expect(shipping_billing_page.update_shipping_billing_message.first).to_be_visible(timeout=60000)
            success_message = shipping_billing_page.update_shipping_billing_message.first.text_content()
            framework_logger.info(f"Success message displayed: {success_message}")
            framework_logger.info("New billing information saved successfully")

            framework_logger.info("=== C28565444 - 2Checkout flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
