import os
import time
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
from core.playwright_manager import PlaywrightManager
from helper.enrollment_helper import EnrollmentHelper
from helper.dashboard_helper import DashboardHelper
import test_flows_common.test_flows_common as common
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.dashboard_hp_smart_page import DashboardHPSmartPage
from pages.plan_selector_v3_page import PlanSelectorV3Page
from pages.overview_page import OverviewPage
from pages.printer_selection_page import PrinterSelectionPage
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def user_without_subscription(stage_callback):
    """
    Test flow for user without subscription but with printer registered
    """
    framework_logger.info("=== C42568108 User Without Subscription (with and without printer registered)) flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    with PlaywrightManager() as page:
        dashboard_hp_smart = DashboardHPSmartPage(page) 
        side_menu = DashboardSideMenuPage(page)
        plan_selector_v3 = PlanSelectorV3Page(page)
        overview_page = OverviewPage(page)
        try:         
            # Create a new HPID account
            page = common.create_ii_v2_account(page)        
            
            # Validate HP Instant Ink submenu at UCDE Dashboard                   
            expect(side_menu.instant_ink_menu_link).to_be_visible(timeout=60000)
            framework_logger.info("HP Print Plans menu link is visible")
            
            # Verify HP Instant Ink submenu items are NOT present (user has no subscription)
            expect(side_menu.overview_menu_link).not_to_be_visible()
            expect(side_menu.update_plan_menu_link).not_to_be_visible()
            expect(side_menu.print_history_menu_link).not_to_be_visible()
            expect(side_menu.shipment_tracking_menu_link).not_to_be_visible()
            framework_logger.info("Verified submenu items are not visible for user without subscription")
            
            # The Smart Dashboard page is displayed with:   
            expect(dashboard_hp_smart.signup_now_button).to_be_visible(timeout=600000)  
            expect(dashboard_hp_smart.promotional_page_background).to_be_visible()
            expect(dashboard_hp_smart.promotional_page_disclaimer).to_be_visible()
            expect(dashboard_hp_smart.keypoint_intelligence_link).to_be_visible()
            framework_logger.info("Verified promotional page elements are visible")         
           
            # Validate promotional page elements and test keypoint intelligence link
            DashboardHelper.click_on_all_available_links_on_the_smart_dashboard_page(page)
            framework_logger.info("Validated all links redirect to the correct page when clicked")
            
            # Click on Account in the side menu
            side_menu.expand_my_account_menu()
            expect(side_menu.shipping_billing_submenu_link).to_be_visible(timeout=30000)
            side_menu.click_shipping_billing()          
            expect(dashboard_hp_smart.shipping_billing_page).to_be_visible(timeout=30000)       
            framework_logger.info("Verified 'Shipping & Billing' page is displayed")

            # Click HP Instant Ink menu
            side_menu.instant_ink_menu_link.click()
            
            # Click the "Sign Up Now" button and switch to new tab
            with page.context.expect_page() as new_page_info:
                dashboard_hp_smart.signup_now_button.click()                          
            new_page = new_page_info.value
            new_page.bring_to_front()                   
            EnrollmentHelper.accept_terms_of_service(new_page)
            EnrollmentHelper.select_plan_type(new_page)                  
            plan_selector_v3 = PlanSelectorV3Page(new_page)
            expect(plan_selector_v3.content_area_v3).to_be_visible(timeout=30000) 
            new_page.close()        
            framework_logger.info("Verified the V3 enroll step page is displayed") 
            
            # Verify Are you finished modal and close
            expect(overview_page.close_finish_enrollment_button).to_be_visible(timeout=30000)
            overview_page.close_finish_enrollment_button.click()
            framework_logger.info("Verified Are you finished modal is displayed and closed")
            
            # Create and Claim virtual printer (but don't enroll in subscription)
            common.create_and_claim_virtual_printer()
            framework_logger.info("Virtual printer created and claimed")

            page.reload()
            framework_logger.info("Page refreshed")

             # Validate HP Instant Ink submenu at UCDE Dashboard                   
            expect(side_menu.instant_ink_menu_link).to_be_visible(timeout=60000)
            framework_logger.info("HP Print Plans menu link is visible")
            
            # Verify HP Instant Ink submenu items are NOT present (user has no subscription)
            expect(side_menu.overview_menu_link).not_to_be_visible()
            expect(side_menu.update_plan_menu_link).not_to_be_visible()
            expect(side_menu.print_history_menu_link).not_to_be_visible()
            expect(side_menu.shipment_tracking_menu_link).not_to_be_visible()
            framework_logger.info("Verified submenu items are not visible for user without subscription")
            
            # The Smart Dashboard page is displayed with:   
            expect(dashboard_hp_smart.signup_now_button).to_be_visible(timeout=600000)  
            expect(dashboard_hp_smart.promotional_page_background).to_be_visible()
            expect(dashboard_hp_smart.promotional_page_disclaimer).to_be_visible()
            expect(dashboard_hp_smart.keypoint_intelligence_link).to_be_visible()
            framework_logger.info("Verified promotional page elements are visible")         
           
            # Validate promotional page elements and test keypoint intelligence link
            DashboardHelper.click_on_all_available_links_on_the_smart_dashboard_page(page)
            framework_logger.info("Validated all links redirect to the correct page when clicked")
            
            # Click on Account in the side menu
            side_menu.expand_my_account_menu()
            expect(side_menu.shipping_billing_submenu_link).to_be_visible(timeout=30000)
            side_menu.click_shipping_billing()          
            expect(dashboard_hp_smart.shipping_billing_page).to_be_visible(timeout=30000)       
            framework_logger.info("Verified 'Shipping & Billing' page is displayed")

            # Click HP Instant Ink menu
            side_menu.instant_ink_menu_link.click()

            # Click the "Sign Up Now" button and verify printer selection page displayed in a new tab
            with page.context.expect_page() as new_page_info:
                dashboard_hp_smart.signup_now_button.click()             
            new_page = new_page_info.value
            new_page.bring_to_front()
            printer_selection = PrinterSelectionPage(new_page)
            new_page.wait_for_selector(printer_selection.elements.printer_selection_page, state="visible", timeout=120000)
            framework_logger.info("Verified  Printer Selection page is displayed") 

            new_page.close()
            page.bring_to_front()
            
            # Verify Are you finished modal and close
            expect(overview_page.close_finish_enrollment_button).to_be_visible(timeout=30000)
            overview_page.close_finish_enrollment_button.click()     
            framework_logger.info("Verified Are you finished modal is displayed and closed")

            framework_logger.info("== C42568108 - User without subscription (with and without printer registered)) test completed successfully")
            return tenant_email
            
        except Exception as e:
            framework_logger.error(f"An error occurred during User Without Subscription (With Printer) test: {e}\n{traceback.format_exc()}")
            raise e

