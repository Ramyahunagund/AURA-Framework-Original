import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from core.settings import GlobalState
from helper.dashboard_helper import DashboardHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.shipping_billing_page import ShippingBillingPage
from pages.update_plan_page import UpdatePlanPage
from pages.confirmation_page import ConfirmationPage
from pages.confirmation_page import ConfirmationPage
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.hpid_helper import HPIDHelper
from pages.overview_page import OverviewPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
from playwright.sync_api import expect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#TC="C41853744"
def special_offers_balance_billing_section(stage_callback):
    framework_logger.info("=== C41853744 Special Offers Balance Billing Section ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # Create virtual printer   
    printer = common.create_virtual_printer()

    # HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer
        common.create_and_claim_virtual_printer()

    with PlaywrightManager() as page:
        try:
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            shipping_billing_page = ShippingBillingPage(page)
            overview_page = OverviewPage(page)
            update_plan_page = UpdatePlanPage(page)
            confirmation_page = ConfirmationPage(page)
            # start enrollment
            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # sign in method
            HPIDHelper.complete_sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in")

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # choose HP checkout
            EnrollmentHelper.choose_hp_checkout(page)

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Add prepaid code
            prepaid_code = common.get_offer_code("prepaid")
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 30)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")

            # Finish enrollment flow
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment flow finished successfully")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)

            # Verify Plan Details card
            DashboardHelper.verify_no_payment_method_added_on_plan_details_card(page)
            framework_logger.info("no payment method has been added message is displayed")

            # Access Shipping Billing Page
            DashboardHelper.access_shipping_billing_page(page)
            framework_logger.info("Shipping & Billing page accessed successfully")

            # Verify prepaid value on Update Plan Page
            dashboard_side_menu_page.click_update_plan()
            expect(update_plan_page.prepaid_code_link).to_be_visible(timeout=90000)
            DashboardHelper.verify_special_offer_value(page, 30)
            framework_logger.info("The Value of the prepaid appears correctly on Update Plan Page")

            # Add prepaid code
            prepaid_code = common.get_offer_code("prepaid")
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 30)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")

            # Verify prepaid value on Update Plan Page
            DashboardHelper.verify_special_offer_value(page, 60)
            framework_logger.info("The total Value of the prepaid appears correctly on Update Plan Page")

            framework_logger.info("Special Offers Balance + Billing Section completed successfully")

        except Exception as e:
            framework_logger.error(f"An error occurred during the Special Offers Balance + Billing Section flow: {e}\n{traceback.format_exc()}")
            raise e
