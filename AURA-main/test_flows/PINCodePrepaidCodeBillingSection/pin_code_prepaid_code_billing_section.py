import time
from tracemalloc import start
from playwright.sync_api import sync_playwright
from tenacity import sleep
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState, framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.hpid_helper import HPIDHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages import confirmation_page
from pages.confirmation_page import ConfirmationPage
from pages.overview_page import OverviewPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.shipping_billing_page import ShippingBillingPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
from playwright.sync_api import expect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pin_code_prepaid_code_billing_section(stage_callback):
    framework_logger.info("=== C42545963 - PIN Code + Prepaid Code + Billing Section flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer and add address
        common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        confirmation_page = ConfirmationPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        overview_page = OverviewPage(page)
        try:
            # start enrollment 
            EnrollmentHelper.start_enrollment(page)
            framework_logger.info(f"Enrollment started with tenant: {tenant_email}")

            # sign in method
            HPIDHelper.complete_sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
            framework_logger.info(f"Signed in")

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")
            
            # Add prepaid code
            prepaid_code = common.get_offer_code("prepaid", amount_equal=3000)
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 30)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")                                   
                     
            # Finish enrollment flow
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment flow finished successfully")

            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            framework_logger.info("Login on Gemini Rails Admin")
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            framework_logger.info("Fetch tenant from email")
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info("Subscription accessed by tenant")
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription status updated")

            # Access Smart Dashboard and skip preconditions
            DashboardHelper.first_access(page, tenant_email=tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")
           
            # Verify Plan Details card
            DashboardHelper.verify_no_payment_method_added_on_plan_details_card(page)
            framework_logger.info("no payment method has been added message is displayed")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")
            
            # Select plan 300
            UpdatePlanHelper.select_plan(page, 300)
            UpdatePlanHelper.select_plan_button(page, 300)
            framework_logger.info("Plan 300 selection completed")

            # Access Overview page
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")
            
            # Verify Plan Details card
            DashboardHelper.verify_add_payment_method_message_on_plan_details_card(page, message_type="alert")
            framework_logger.info("To continue with Instant Ink, add your billing information. Alert message is displayed")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")
            
            # Select plan 700
            UpdatePlanHelper.select_plan(page, 700)
            UpdatePlanHelper.select_plan_button(page, 700)
            framework_logger.info("Plan 700 selection completed")

            # Access Overview page
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify Plan Details card
            DashboardHelper.verify_add_payment_method_message_on_plan_details_card(page, message_type="critical")
            framework_logger.info("To continue with Instant Ink, add your billing information. Critical message is displayed")

            # Click Change Billing Info link in Overview page           
            overview_page.change_billing_link.click()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=30000)
            framework_logger.info("Clicked Manage your shipping address link")

             # Access Overview page
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")
            
            # Check the 'Apply' button
            overview_page.redeem_code_link.click()
            expect(overview_page.modal_offers).to_be_visible(timeout=30000)
            expect(overview_page.apply_promo_code_button).to_be_disabled()
            overview_page.close_promo_code_modal.click()
            framework_logger.info("verified the Apply button is disabled when no code is entered")

            # Add prepaid code
            prepaid_code = common.get_offer_code("prepaid", amount_equal=300)
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 3)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")   

            # Apply a valid "Free Month" code with additional payment required and valid for dashboard.
            prepaid_code = common.get_offer_code("prepaid", amount_equal=500)
            EnrollmentHelper.apply_promotion_code(page, prepaid_code)
            DashboardHelper.verify_this_PIN_or_promo_code_requires_an_additional_payment_method_message(page)
            confirmation_page.close_modal_button.click()
            framework_logger.info("The PIN is applied and the message 'This PIN or promo code requires an additional payment method.' is displayed")

            framework_logger.info("=== C42545963 - PIN Code + Prepaid Code + Billing Section flow completed successfully ===")
           
        except Exception as e:
            framework_logger.error(f"An error occurred during PIN Code + Prepaid Code + Billing Section flow: {e}\n{traceback.format_exc()}")
            raise e
