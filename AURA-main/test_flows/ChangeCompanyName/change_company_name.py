from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState, framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.confirmation_page import ConfirmationPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.shipping_billing_page import ShippingBillingPage
from playwright.sync_api import expect, sync_playwright
from core.settings import GlobalState
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def change_company_name(stage_callback):
    framework_logger.info("=== C38567047 - Change Company Name flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # 1) HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer
        common.create_and_claim_virtual_printer()

    with PlaywrightManager() as page:
        confirmation_page = ConfirmationPage(page)
        overview_page = OverviewPage(page)
        side_menu = DashboardSideMenuPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        try:
            # Start enrollment
            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # Sign in method
            HPIDHelper.complete_sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in")

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Choose hp checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add Shipping
            EnrollmentHelper.add_shipping(page, company_name="HP")
            framework_logger.info(f"Shipping added successfully")

            # Add billing method
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing method added successfully")

            # Finish enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info(f"Finished enrollment with prepaid")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page for tenant: {tenant_email}")

            # Access Shipping & Billing
            side_menu.click_shipping_billing()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Shipping & Billing page")

            # Click on Manage Shipping Address
            shipping_billing_page.manage_shipping_address.click()
            expect(shipping_billing_page.shipping_form_modal).to_be_visible(timeout=90000)
            framework_logger.info(f"Clicked on Manage Shipping Address")

            # Change company name on Edit Shipping Address page
            confirmation_page.company_name_input.fill("New Company Name")
            confirmation_page.save_button.click()
            framework_logger.info(f"Changed company name to 'New Company Name'")

            # See success message on Shipping & Billing page
            expect(shipping_billing_page.update_shipping_billing_message).to_be_visible(timeout=90000)
            expect(shipping_billing_page.update_shipping_billing_message).to_have_text("Your Instant Ink shipping information has been saved")
            framework_logger.info(f"Verified success message on Shipping & Billing page")

            # Sees company name on Shipping modal
            shipping_billing_page.manage_shipping_address.click()
            expect(confirmation_page.company_name_input).to_have_value("New Company Name", timeout=90000)
            framework_logger.info(f"Verified company name on Shipping modal")

            # Clear company name on Shipping modal
            confirmation_page.company_name_input.clear()
            expect(confirmation_page.company_name_input).to_be_empty()
            confirmation_page.save_button.click()
            framework_logger.info(f"Cleared company name on Shipping modal")

            # See success message on Shipping & Billing page
            expect(shipping_billing_page.update_shipping_billing_message).to_be_visible(timeout=90000)
            expect(shipping_billing_page.update_shipping_billing_message).to_have_text("Your Instant Ink shipping information has been saved")
            framework_logger.info(f"Verified success message on Shipping & Billing page")

            # Does not see company name on Shipping modal
            shipping_billing_page.manage_shipping_address.click()
            expect(confirmation_page.company_name_input).to_be_empty()
            framework_logger.info(f"Verified company name is empty on Shipping modal")

            framework_logger.info(" C38567047 - Change Company Name flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e