
import os
import time
import random
import string
import base64
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from helper.landing_page_helper import LandingPageHelper
from pages.confirmation_page import ConfirmationPage
from pages.landing_page import LandingPage
from helper.dashboard_helper import DashboardHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
from playwright.sync_api import expect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def start_enrollment_flow_with_raf_link(stage_callback):
    framework_logger.info("=== C43905353 - Start enrollment flow with RaF link started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    
    with PlaywrightManager() as page:
        try:
            # Access RaF link directly for region US
            raf_link = "https://instantink-stage1.hpconnectedstage.com/purl/2nbdy7"
            page.goto(raf_link, timeout=120000)
            page.wait_for_load_state("load")
            
            # Verify RaF banner
            LandingPageHelper.verify_raf_banner_with_free_months(page, 1)
            framework_logger.info("Verified RaF banner")

            # Verify RaF footnote
            LandingPageHelper.verify_raf_footnote_on_landing_page(page)  
            framework_logger.info("Verified footnote")  

            # Create a new HPID account
            page = common.create_ii_v2_account(page)
            
            # Create and Claim virtual printer
            common.create_and_claim_virtual_printer()   

            time.sleep(600)
            page.reload()
            page.wait_for_selector("[data-testid='get-started-button']", timeout=60000)        

            # Start Instant Ink Web enroll flow
            with page.context.expect_page() as new_page_info:
                EnrollmentHelper.signup_now(page)
                framework_logger.info("Sign Up Now button clicked")
            page = new_page_info.value            
                      
            # accept TOS
            EnrollmentHelper.accept_terms_of_service(page)
            framework_logger.info(f"Terms of Services accepted")        

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")
             
            # Verify RaF months and total benefits
            EnrollmentHelper.verify_raf_months_and_total_benefits(page, 1, 4)
            framework_logger.info(f"Verified RaF months and total benefits successfully")

            # Finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            # Go to Smart dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Dashboard first access completed successfully")
            
            # Verify free months remaining value
            DashboardHelper.verify_free_months_value(page, 4)
            framework_logger.info(f"Verified free months remaining value successfully")
            
            framework_logger.info("=== C43905353 - Start enrollment flow with RaF link finished ===")
           
        except Exception as e:
            framework_logger.error(f"Flow 'StartEnrollmentFlowWithRafLink' execution failed: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
    