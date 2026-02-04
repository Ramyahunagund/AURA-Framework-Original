import os
import time
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
from core.playwright_manager import PlaywrightManager
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_hp_smart_page import DashboardHPSmartPage
import test_flows_common.test_flows_common as common
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage        
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def printers_page(stage_callback):
    framework_logger.info("=== C37981510 - Printers Page flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        hp_smart_page = DashboardHPSmartPage(page)
        update_plan_page = UpdatePlanPage(page)

        try:
            # Create a new HPID account
            page = common.create_ii_v2_account(page)
            
            # Create and Claim virtual printer
            common.create_and_claim_virtual_printer()
            
            # Clicks on printer menu
            side_menu.printers_menu_link.click()
            expect(hp_smart_page.printers_page_title).to_be_visible(timeout=90000)
            framework_logger.info("Clicked on Printers menu item")

            # Clicks on Enroll in HP Instant Ink link
            hp_smart_page.enroll_hp_instant_ink_link.click()            
            expect(hp_smart_page.print_plans_page).to_be_visible(timeout=90000)
            framework_logger.info("Clicked on Enroll in HP Instant Ink link")

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

            # Step 5: Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Step 6: Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            # Step 7: Finish Enrollment
            EnrollmentHelper.finish_enrollment(page)           
            framework_logger.info("Enrollment finished")                
                       
            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Create and Claim virtual printer
            common.create_and_claim_virtual_printer()
            
            # Click on printer menu
            side_menu = DashboardSideMenuPage(page)
            time.sleep(200)
            page.reload()            
            side_menu.printers_menu_link.click()
            expect(hp_smart_page.printers_page_title).to_be_visible(timeout=90000)
            framework_logger.info("Clicked on Printers menu item")

            # Click on Enroll in HP Instant Ink link
            hp_smart_page.enroll_hp_instant_ink_link.click()
            expect(overview_page.page_title).to_be_visible(timeout=60000)
            framework_logger.info("Clicked on Enroll in HP Instant Ink link")

            # Click on printer menu again           
            side_menu.printers_menu_link.click()
            expect(hp_smart_page.printers_page_title).to_be_visible(timeout=90000)
            framework_logger.info("Clicked on Printers menu item")
            
            # Click the Printer Options for enrolled printer on my Printers page
            DashboardHelper.click_printer_options_for_enrolled_printer(page)
            framework_logger.info("Clicked on Printer Options link")

            # Check Update Plan link and Remove Printer link are displayed on my Printers page
            expect(hp_smart_page.update_plan_link).to_be_visible()
            expect(hp_smart_page.remove_printer_link.last).to_be_visible()
            framework_logger.info("Checked visibility of Update Plan and Remove Printer links")

            # Click the Update Plan link on my Printers page
            hp_smart_page.update_plan_link.click()
            expect(update_plan_page.page_title).to_be_visible(timeout=50000)
            framework_logger.info("Clicked on Update Plan link and Update plan page is displayed")

            framework_logger.info("== C37981510 - Printers Page completed successfully")

        except Exception as e:
            framework_logger.error(f"An error occurred during the Ink Web Enrollment: {e}\n{traceback.format_exc()}")
            raise e
