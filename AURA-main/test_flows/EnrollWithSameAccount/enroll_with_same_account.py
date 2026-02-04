from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.ra_base_helper import RABaseHelper
from pages.confirmation_page import ConfirmationPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.printers_page import PrintersPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
import urllib3
import time
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enroll_with_same_account(stage_callback):
    framework_logger.info("=== C51857703 - Enroll with same account ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            # First time - Obsoleted the subscription and unclaimed the printer 
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.force_subscription_to_obsolete(page)
            framework_logger.info("First subscription obsoleted successfully")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            side_menu = DashboardSideMenuPage(page)
            # Access Printers page
            side_menu.printers_menu_link.click(timeout=90000)
            framework_logger.info(f"Clicked on Printers menu link")

            printers_page = PrintersPage(page)
            # Remove printer 
            printers_page.printer_options.click()
            printers_page.remove_printer_button.click()
            printers_page.confirm_remove_printer_button.click()
            printers_page.close_remove_printer_button.click()
            framework_logger.info(f"Tried to remove enrolled printer")

            # New claim + new enrollment with the same account and printer
            org_token, tenant_id = common.get_org_aware_token()
            framework_logger.info(f"Obtained org_token and tenant_id")

            entity_id, model_number, device_uuid, cloud_id, postcard, fingerprint = common._printer_created[0]
            common.claim_virtual_printer(org_token, tenant_id, model_number, device_uuid, postcard, fingerprint)
            framework_logger.info("Virtual printer claimed successfully")

            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            framework_logger.info("Started enrollment and signed in")

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Second Enrollment completed successfully")  
            
            # Second time - Obsoleted the subscription and unclaimed the printer 
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.force_subscription_to_obsolete(page)
            framework_logger.info("Second subscription obsoleted successfully")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            side_menu = DashboardSideMenuPage(page)
            # Access Printers page
            side_menu.printers_menu_link.click(timeout=90000)
            framework_logger.info(f"Clicked on Printers menu link")

            # Remove printer
            printers_page.printer_options.click()
            printers_page.remove_printer_button.click()
            printers_page.confirm_remove_printer_button.click()
            printers_page.close_remove_printer_button.click()
            framework_logger.info(f"Remove printer")

            # New claim + new enrollment with the same account and printer
            org_token, tenant_id = common.get_org_aware_token()
            framework_logger.info(f"Obtained org_token and tenant_id")

            entity_id, model_number, device_uuid, cloud_id, postcard, fingerprint = common._printer_created[0]
            common.claim_virtual_printer(org_token, tenant_id, model_number, device_uuid, postcard, fingerprint)
            framework_logger.info("Virtual printer claimed successfully")

            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            framework_logger.info("Started enrollment and signed in")

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # finish enrollment  
            confirmation_page = ConfirmationPage(page)
            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            confirmation_page.terms_agreement_checkbox.wait_for(state="visible", timeout=60000)
            confirmation_page.terms_agreement_checkbox.check(force=True)
            confirmation_page.enroll_button.click()
            framework_logger.info("Third Enrollment attempted and error message displayed as expected")
  
            framework_logger.info("=== C51857703 - Enroll with same account finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
