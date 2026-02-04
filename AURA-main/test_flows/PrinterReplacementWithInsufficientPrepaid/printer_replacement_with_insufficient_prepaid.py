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
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
from playwright.sync_api import expect
from helper.update_plan_helper import UpdatePlanHelper
from pages.update_plan_page import UpdatePlanPage
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC="C41398323" 
def printer_replacement_with_insufficient_prepaid(stage_callback):
    framework_logger.info("=== C41398323 - printer_replacement_with_insufficient_prepaid started ===")
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
        common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:      
        try:
            side_menu = DashboardSideMenuPage(page)
         
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
            framework_logger.info(f"Prepaid code fetched: {prepaid_code}")
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 30)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")

            # Finish enrollment flow
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment flow finished successfully")  
            
            # Move subscription to subscribed state
            GeminiRAHelper.access(page)           
            GeminiRAHelper.access_tenant_page(page, tenant_email)           
            GeminiRAHelper.access_subscription_by_tenant(page)            
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription status updated")          
            
            # Go to Smart Dashboar and change to a higher plan
            DashboardHelper.first_access(page, tenant_email=tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")
            
            # Access Update Plan page
            side_menu = DashboardSideMenuPage(page)
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")
                         
           # Select plan 700
            UpdatePlanHelper.select_plan(page, 700)
            UpdatePlanHelper.select_plan_button(page, 700)
            framework_logger.info("Plan 700 selection completed")
            
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
           
            # Verify the message is not displayed
            confirmation_page = ConfirmationPage(page)
            expect(confirmation_page.message_add_billing_info).not_to_be_visible()
            
            # Add billing button enabled
            confirmation_page = ConfirmationPage(page)  
            expect(confirmation_page.add_billing_button).to_be_enabled(timeout=60000)

            # Add prepaid code
            prepaid_code = common.get_offer_code("prepaid", amount_equal=300)
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 33)
            framework_logger.info(f"Prepaid code applied successfully: {prepaid_code}")
            
            # Verify the message is not displayed
            confirmation_page = ConfirmationPage(page)
            expect(confirmation_page.message_add_billing_info).not_to_be_visible()
            framework_logger.info(f"Add billing info message is not visible")

            # Add billing button enabled
            confirmation_page = ConfirmationPage(page)    
            expect(confirmation_page.add_billing_button).to_be_enabled()
            framework_logger.info(f"Add billing button is enabled")

            # Add continue button disabled
            confirmation_page = ConfirmationPage(page)    
            expect(confirmation_page.continue_enrollment_button).to_be_disabled()
            framework_logger.info(f"Continue enrollment button is disabled")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully") 

            EnrollmentHelper.skip_paper_offer(page)
            framework_logger.info(f"Skipped paper offer")

            # Finish enrollment flow
            EnrollmentHelper.finish_enrollment_with_prepaid(page)

            framework_logger.info("=== C41398323 printer_replacement_with_insufficient_prepaid completed successfully ===") 

        except Exception as e:
            framework_logger.error(f"An error occurred during the printer_replacement_with_insufficient_prepaidd flow: {e}\n{traceback.format_exc()}")
            raise e
        