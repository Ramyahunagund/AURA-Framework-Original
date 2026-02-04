from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.confirmation_page import ConfirmationPage
from pages.overview_page import OverviewPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def edit_billing_link_paypal_form_with_subscriptions(stage_callback):
    framework_logger.info("=== C46058260 - Edit billing link PayPal form with subscriptions flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Create and claim a new virtual printer
            common.create_and_claim_virtual_printer()
            framework_logger.info(f"Claimed a new virtual printer")

            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status updated to subscribed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")
            
            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            # Click on enroll printer button on the Enroll or Replace Printer modal at UCDE
            with page.context.expect_page() as new_page_info:
                overview_page.enroll_printer_button.click()
                new_tab = new_page_info.value
            framework_logger.info("Clicked on enroll printer button on the Enroll or Replace Printer modal at UCDE")

            # Click on continue button in printer selection page
            EnrollmentHelper.accept_terms_of_service(new_tab)
            EnrollmentHelper.select_printer(new_tab)
            framework_logger.info(f"Selected printer and accepted terms of service")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(new_tab)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Select plan 100
            EnrollmentHelper.select_plan(new_tab, 100)
            framework_logger.info(f"Plan selected: 100")

            # Click to edit billing link
            confirmation_page = ConfirmationPage(new_tab)
            confirmation_page.edit_billing_button.click()
            framework_logger.info("Clicked edit billing button on confirmation page")

            # Wait 901 seconds
            framework_logger.info("Waiting for 901 seconds...")
            time.sleep(901)
            framework_logger.info("Waited 901 seconds")

            # Click continue button on billing modal
            confirmation_page.billing_continue_button.click()
            framework_logger.info("Clicked continue button on billing modal")

            # Fill email and password to sign in on HPID page
            HPIDHelper.sign_in(new_tab, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in with email: {tenant_email}")

            # Add billing method
            EnrollmentHelper.add_billing(new_tab, "paypal")
            framework_logger.info(f"Billing method added successfully")

            # Finish enrollment
            EnrollmentHelper.finish_enrollment(new_tab)
            framework_logger.info(f"Finished enrollment")

            framework_logger.info("=== C46058260 - Edit billing link PayPal form with subscriptions flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e