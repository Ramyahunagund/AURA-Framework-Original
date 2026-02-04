import time
from playwright.sync_api import sync_playwright
from tenacity import sleep
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState, framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.hpid_helper import HPIDHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from pages.confirmation_page import ConfirmationPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
from playwright.sync_api import expect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TC="C41399688" 
def printer_replacement_with_sufficient_prepaid(stage_callback):
    framework_logger.info("=== printer_replacement_with_sufficient_prepaid started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")
    # Create and register virtual printer
    printer = common.create_virtual_printer()
    # Create a new HPID account
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)
        
            # Click on Sign Up Now button
            with page.context.expect_page() as new_page_info:
                EnrollmentHelper.signup_now(page)
                framework_logger.info("Sign Up Now button clicked")
            page = new_page_info.value

            # Accept Terms of Service
            EnrollmentHelper.accept_terms_of_service(page)
            framework_logger.info("Terms of Service accepted")

            # Select plan type card
            EnrollmentHelper.select_plan_type(page)
            
            # Select Ink plan
            EnrollmentHelper.select_plan_v3(page, plan_value=100)
            framework_logger.info("Ink only plan selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            # Add prepaid code
            prepaid_code = common.get_offer_code("prepaid")

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
            
            # Create virtual printer 
            printer = common.create_virtual_printer()

            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info(f"Completed OSS Simulator setup")
            
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info(f"Accepted connected printing services")

            OssEmulatorHelper.decline_hp_plus(page)
            framework_logger.info(f"Declined HP+")
            
            OssEmulatorHelper.continue_dynamic_security_notice(page)
            framework_logger.info(f"Continued on dynamic security notice")
          
            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")
         
            OssEmulatorHelper.select_replace_printer_and_continue(page)
            framework_logger.info(f"Continued on dynamic security notice")

            # Add prepaid code
            prepaid_code = common.get_offer_code("prepaid")
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 60)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")

            # Skip Paper Offer
            EnrollmentHelper.skip_paper_offer(page)
            framework_logger.info(f"Skipped paper offer")
    
            # Verify message to add billing info
            confirmation_page = ConfirmationPage(page)
            expect(confirmation_page.message_add_billing_info).to_have_text("Optional: Add your billing information to avoid service interruptions")
            
            # Finish enrollment flow
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Replacement flow finished successfully")

            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_special_offer_value(page, 60)
            
            framework_logger.info("=== printer_replacement_with_sufficient_prepaid completed successfully ===") 
        
        except Exception as e:
            framework_logger.error(f"An error occurred during the printer_replacement_with_sufficient_prepaid flow: {e}\n{traceback.format_exc()}")
            raise e
    