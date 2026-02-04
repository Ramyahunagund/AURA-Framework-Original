from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.print_history_helper import PrintHistoryHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.printer_selection_page import PrinterSelectionPage
from pages.print_history_page import PrintHistoryPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def re_enroll_obsolete_printer_same_account(stage_callback):
    framework_logger.info("=== C62141869 - Re-enroll the obsolete printer with same account - Online flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        printer_selection_page = PrinterSelectionPage(page)
        print_history_page = PrintHistoryPage(page)
        update_plan_page = UpdatePlanPage(page)
        
        try:               
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.force_subscription_to_obsolete(page)
            framework_logger.info("Subscription moved to obsolete state")

            # Access Smart Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Accessed Smart Dashboard")

            # click enroll printer again button
            DashboardHelper.click_enroll_printer_again_button(page)
            framework_logger.info("Clicked enroll printer again button")      
                    
            new_tab = page.context.pages[-1]
            new_tab.bring_to_front()
            new_tab.wait_for_load_state("networkidle", timeout=120000)
            framework_logger.info("Switched to last tab")

             # Printer selector method
            EnrollmentHelper.select_printer(new_tab)
            framework_logger.info("Printer selected")

            # Plans
            EnrollmentHelper.select_plan(new_tab, 100)
            framework_logger.info(f"Plan selected")
                
            # Validate free trial on the enrollment tab
            EnrollmentHelper.validate_benefits_header(new_tab, 3)
            framework_logger.info(f"Free months verified")

            # Finish enrollment  
            EnrollmentHelper.finish_enrollment(new_tab)
            framework_logger.info("Enrollment completed successfully")
            
            # Close the enrollment tab and return to main page
            new_tab.close()            
            page.bring_to_front()
            framework_logger.info("Closed the enrollment tab and return to main page")
                   
            # Page tally
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.define_page_tally(page, "100")
            framework_logger.info("Page Tally updated")

            # Go to Dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Dashboard accessed")

            # Verify the total pages printed
            DashboardHelper.verify_total_pages_printed(page, 100)
            framework_logger.info("Verified total pages printed")
            
           # Access Print History Page
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify the total pages printed
            DashboardHelper.verify_total_pages_printed(page, 100)
            framework_logger.info("Verified total pages printed")

            # FAQ "What does my monthly payment include?" - Overview link
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            print_history_page.faq_question_2.click()
            expect(print_history_page.faq_answer_2).to_be_visible(timeout=30000)
            print_history_page.faq_overview_link.click()
            expect(overview_page.status_card_title).to_be_visible(timeout=30000)
            framework_logger.info("FAQ Overview link redirects correctly to enrolled printer Overview page")

            # FAQ "What does my monthly payment include?" - Update Plan link
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            print_history_page.faq_question_2.click()
            expect(print_history_page.faq_answer_2).to_be_visible(timeout=30000)
            print_history_page.update_plan_link.first.click()
            expect(update_plan_page.page_title).to_be_visible(timeout=30000)
            framework_logger.info("FAQ Update Plan link redirects correctly to enrolled printer Update Plan page")

            # Go to Overview page
            side_menu.click_overview()
            expect(overview_page.status_card_title).to_be_visible(timeout=30000)
            framework_logger.info("Navigated to Overview page")

            # Select cancelled subscription printer'
            DashboardHelper.select_printer_from_selector(page, "INSTANT INK CANCELLED SUBSCRIPTIONS")
            framework_logger.info("Successfully selected cancelled subscription printer")
   
            # FAQ "What does my monthly payment include?" - Overview link
            side_menu.click_print_history()            
            expect(print_history_page.page_title).to_be_visible(timeout=90000)
            print_history_page.faq_question_2.click()
            expect(print_history_page.faq_answer_2).to_be_visible(timeout=30000)
            print_history_page.faq_overview_link.click()
            expect(overview_page.status_card_title).to_be_visible(timeout=30000)
            framework_logger.info("FAQ Overview link works for cancelled subscription printer")
            
            # FAQ "What does my monthly payment include?" - Update Plan link
            side_menu.click_print_history()
            expect(print_history_page.page_title).to_be_visible(timeout=90000)
            print_history_page.faq_question_2.click()
            expect(print_history_page.faq_answer_2).to_be_visible(timeout=30000)
            print_history_page.update_plan_link.first.click()
            # For cancelled printer, this should redirect to Overview instead of Update Plan
            expect(overview_page.status_card_title).to_be_visible(timeout=30000)
            framework_logger.info("FAQ Update Plan link redirects to Overview for cancelled subscription printer")

            # FAQ "What are Additional Pages and Rollover Pages?" - Update Plan link
            side_menu.click_print_history()  
            expect(print_history_page.page_title).to_be_visible(timeout=90000)          
            print_history_page.faq_question_4.click()
            expect(print_history_page.faq_answer_4).to_be_visible(timeout=30000)
            print_history_page.update_plan_link.last.click()
            # For cancelled printer, this should redirect to Overview instead of Update Plan
            expect(overview_page.status_card_title).to_be_visible(timeout=30000)
            framework_logger.info("Additional Pages FAQ Update Plan link redirects to Overview for cancelled subscription printer")    

            framework_logger.info("=== C62141869 - Re-enroll the obsolete printer with same account - Online flow completed successfully ===")
            
        except Exception as e:
            framework_logger.error(f"An error occurred during the re-enroll flow: {e}\n{traceback.format_exc()}")
            raise e
