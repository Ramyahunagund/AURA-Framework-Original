from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState, framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.hpid_helper import HPIDHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.overview_page import OverviewPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.ra_base_helper import RABaseHelper
from pages.update_plan_page import UpdatePlanPage
import test_flows_common.test_flows_common as common
from helper.overview_helper import OverviewHelper
import urllib3
import traceback
from playwright.sync_api import expect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def downgrade_upgrade_banner_plan_changes(stage_callback):
    framework_logger.info("=== C44481717 - Downgrade/upgrade banner - Upgrade/downgrade plan flow started ===")
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
        overview_page = OverviewPage(page)
        update_plan_page = UpdatePlanPage(page)       
        try:     
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            EnrollmentHelper.select_printer(page)         
            EnrollmentHelper.accept_automatic_printer_updates(page)      
            EnrollmentHelper.select_plan(page, 300)          
            EnrollmentHelper.add_billing(page)         
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page) 
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Set printed pages to 10 in current billing cycle (low usage for plan 300)
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.define_page_tally(page, "40")
            framework_logger.info("Page tally added")
            
            # Click Calculate retention and  Executes the resque job: CalculateRetentionJob
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page) 
            GeminiRAHelper.click_calculate_retention(page)
            RABaseHelper.complete_jobs(page, common._instantink_url, ["CalculateRetentionJob"])
            framework_logger.info("Clicked Calculate retention and executed retention calculation")

            # Access Smart Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")
            
            # Verify downgrading banner on Status card
            OverviewHelper.verify_plan_suggestion_banner(page, banner_type="downgrading")
            framework_logger.info("Downgrading banner is visible on Status card (low usage scenario)")

            # Click Browse plans link on downgrading banner
            overview_page.browse_plans_link.click()
            expect(update_plan_page.page_title).to_be_visible(timeout=60000)
            framework_logger.info("Clicked Browse plans link - navigated to Update Plan page")
                        
            # Navigate back to Gemini to set high usage
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            
            # Set printed pages to 200 in current billing cycle and executed retention calculation
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.define_page_tally(page, "500")  
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)             
            GeminiRAHelper.click_calculate_retention(page)
            RABaseHelper.complete_jobs(page, common._instantink_url, ["CalculateRetentionJob"])
            framework_logger.info("Set printed pages to 500 and executed retention calculation")

            # Return to Smart Dashboard
            DashboardHelper.first_access(page, tenant_email)  
            framework_logger.info("Returned to Smart Dashboard Overview page")

            # Verify upgrade banner on Status card          
            OverviewHelper.verify_plan_suggestion_banner(page, banner_type="upgrading")           
            framework_logger.info("Upgrade banner is visible on Status card (high usage scenario)")

            # Click Browse plans link on upgrade banner
            overview_page.browse_plans_link.click()
            expect(update_plan_page.page_title).to_be_visible(timeout=60000)
            framework_logger.info("Clicked Browse plans link - navigated to Update Plan page")        
            
            # Pause Instant Ink plan for 1 month on Plan Details card
            DashboardHelper.pause_plan(page, 1)           
            framework_logger.info("Paused Instant Ink plan for 1 month")

            # Simulate new billing cycle charge (32 for plan 300)
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)            
            GeminiRAHelper.event_shift(page, event_shift="32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, tally="300")
            framework_logger.info("New billing cycle charged: event shift 32 for page tally 300")

            # Return to Smart Dashboard        
            DashboardHelper.first_access(page, tenant_email)           
            side_menu.click_update_plan()
            framework_logger.info("Navigated to Update Plan page")
            
            # Upgrading to plan 500        
            UpdatePlanHelper.select_plan(page, 500)            
            expect(update_plan_page.upgrade_plan_confirmation).to_be_visible(timeout=30000)  
            update_plan_page.cancel_change_plan_button.click()   
            expect(update_plan_page.upgrade_plan_confirmation).not_to_be_visible(timeout=30000)               
            framework_logger.info("Change plan modal with pause plan cancellation info displayed for plan 500")
            
            # Close modal and test downgrading to plan 50            
            UpdatePlanHelper.select_plan(page, 50)            
            expect(update_plan_page.downgrade_plan_confirmation).to_be_visible(timeout=30000)  
            update_plan_page.cancel_change_plan_button.click()  
            framework_logger.info("Change plan modal with pause plan cancellation info displayed for plan 50")

            framework_logger.info("=== C44481717 - Downgrade/upgrade banner - Upgrade/downgrade plan flow completed successfully ===")
            return tenant_email
            
        except Exception as e:
            framework_logger.error(f"An error occurred during Downgrade/upgrade banner test: {e}\n{traceback.format_exc()}")
            raise e
