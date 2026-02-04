import time
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.printers_page import PrintersPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from playwright.sync_api import expect
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enroll_with_different_account(stage_callback):
    framework_logger.info("=== C51907049 - Enroll with Different account started ===")
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

        # 2) Claim virtual printer and add address
        printer = common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        try:
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            price = None
            try:
                price = EnrollmentHelper.get_total_price_by_plan_card(page)
            except Exception:
                framework_logger.info(f"Failed to get price from plan card")

            # billing
            EnrollmentHelper.add_billing(page, plan_value=price)
            framework_logger.info(f"Billing added")

            # finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")
    
            second_tenant_email = common.generate_tenant_email()
            framework_logger.info(f"Generated second_tenant_email={second_tenant_email}")
            confirmation_page = ConfirmationPage(page)
            side_menu = DashboardSideMenuPage(page)
            printers_page = PrintersPage(page)

            # First time - Obsoleted the subscription and unclaimed the printer 
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.force_subscription_to_obsolete(page)
            framework_logger.info("First subscription obsoleted successfully")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Printers page
            side_menu.printers_menu_link.click(timeout=90000)
            framework_logger.info(f"Clicked on Printers menu link")

            # Remove printer 
            printers_page.printer_options.click(timeout=90000)
            printers_page.remove_printer_button.click()
            printers_page.confirm_remove_printer_button.click()
            printers_page.close_remove_printer_button.click()
            framework_logger.info(f"Tried to remove enrolled printer")

            # Sign out
            DashboardHelper.sign_out(page)
            framework_logger.info("Signed out from account")
            
            # New claim + new enrollment with the different account and same printer
            page = common.create_hpid(page, lambda: stage_callback("landing_page", page), email=second_tenant_email)
            time.sleep(5)
            framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
            page = common.onboard_hpid_to_ucde(page)

            org_token, tenant_id = common.get_org_aware_token(email=second_tenant_email)
            framework_logger.info(f"Obtained org_token and tenant_id")

            entity_id, model_number, device_uuid, cloud_id, postcard, fingerprint = printer
            framework_logger.info(f"Printer details - entity_id: {entity_id}, model_number: {model_number}, device_uuid: {device_uuid}, cloud_id: {cloud_id}, postcard: {postcard}, fingerprint: {fingerprint}")
            
            common.claim_virtual_printer(org_token, tenant_id, model_number, device_uuid, postcard, fingerprint)
            framework_logger.info("Virtual printer claimed successfully")

            EnrollmentHelper.start_enrollment_and_sign_in(page, second_tenant_email)
            
            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added")

            # billing
            EnrollmentHelper.add_billing(page, plan_value=100)
            framework_logger.info(f"Billing added")

            # finish enrollment  
            confirmation_page = ConfirmationPage(page)
            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            confirmation_page.terms_agreement_checkbox.wait_for(state="visible", timeout=60000)
            confirmation_page.terms_agreement_checkbox.check(force=True)
            confirmation_page.enroll_button.click()
            framework_logger.info("Third Enrollment attempted and error message displayed as expected")
  
            # printer is no longer eligible for re-enrollment message appears
            expect(confirmation_page.error_message_no_longer_eligible).to_be_visible(timeout=90000)
            framework_logger.info("Printer is no longer eligible for re-enrollment message is visible")         
  
            framework_logger.info("=== C51907049 - Enroll with Different account finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
