from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from pages.printer_replacement_page import PrinterReplacementPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from datetime import datetime, timedelta
from helper.ra_base_helper import RABaseHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.update_plan_helper import UpdatePlanHelper
from core.playwright_manager import PlaywrightManager
from pages.overview_page import OverviewPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage  
from pages.cancellation_timeline_page import CancellationTimelinePage 
from core.settings import framework_logger
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common 
import urllib3
import traceback
import time
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enroll_or_replace_printer_subscribed_no_pens(stage_callback):
    framework_logger.info("=== C48992920 - Enroll Or Replace Printer Subscribed No Pens flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:  
        cancellation_timeline_page = CancellationTimelinePage(page)      
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        try:
            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            expect(overview_page.plan_pages_bar).not_to_be_visible()
            framework_logger.info("Verified that Plan and Pages bar is not visible for Subscribed_No_Pens account")

            framework_logger.info("Waiting for 15 minutes to verify session expired modal")
            time.sleep(901)
            framework_logger.info("Waited for 15 minutes for the session expired modal")

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            # Click cancel button in the session expired modal on the Smart Dashboard
            overview_page.expired_session_cancel.click()
            framework_logger.info("Clicked on cancel button in the session expired modal")

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click(timeout=90000)
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            # Click login button in the session expired modal on the Smart Dashboard
            DashboardHelper.login_on_security_session_expired(page, tenant_email)
            framework_logger.info("Logged in the session expired modal")

            # See the Overview page
            DashboardHelper.sees_status_card(page)
            framework_logger.info("Verified the Overview page")

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            framework_logger.info("Waiting for 15 minutes to verify session expired modal")
            time.sleep(901)
            framework_logger.info("Waited for 15 minutes for the session expired modal")

            expect(overview_page.expired_session_cancel).to_be_visible()
            # Click login button in the session expired modal on the Smart Dashboard
            DashboardHelper.login_on_security_session_expired(page, tenant_email)
            framework_logger.info("Logged in the session expired modal")

            # See the Overview page
            DashboardHelper.sees_status_card(page)
            framework_logger.info("Verified the Overview page")

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            initial_pages_count = len(page.context.pages)
            overview_page.enroll_printer_button.click()
            framework_logger.info("Clicked on enroll printer button")

            page.wait_for_timeout(3000)
            new_pages_count = len(page.context.pages)
            
            if new_pages_count > initial_pages_count:
                # Validate Printer Selection page in new tab
                new_tab = page.context.pages[-1]
                new_tab.wait_for_load_state("networkidle", timeout=120000)
                
                EnrollmentHelper.accept_terms_of_service(new_tab)

                confirmation_page = ConfirmationPage(new_tab)

                confirmation_page.wait.monthly_plan(timeout=90000)
                new_tab.close()
                page.bring_to_front()

            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # See the Overview page
            DashboardHelper.sees_status_card(page)
            framework_logger.info("Verified the Overview page")

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            framework_logger.info("Waiting for 15 minutes to verify session expired modal")
            time.sleep(901)
            framework_logger.info("Waited for 15 minutes for the session expired modal")

            expect(overview_page.expired_session_cancel).to_be_visible()
            # Click login button in the session expired modal on the Smart Dashboard
            DashboardHelper.login_on_security_session_expired(page, tenant_email)
            framework_logger.info("Logged in the session expired modal")

            # See the Overview page
            DashboardHelper.sees_status_card(page)
            framework_logger.info("Verified the Overview page")

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            overview_page.replace_printer_button.click()

            printer_replacement_page = PrinterReplacementPage(page)
            printer_replacement_page.wait.printer_replacement_page(timeout=90000)
            framework_logger.info("Verified the Printer Replacement page")

            framework_logger.info("=== C48992920 - Enroll Or Replace Printer Subscribed No Pens flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
