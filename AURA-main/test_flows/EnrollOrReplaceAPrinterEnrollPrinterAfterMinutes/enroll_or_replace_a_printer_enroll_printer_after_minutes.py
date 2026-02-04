from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.enrollment_helper import EnrollmentHelper
from pages.overview_page import OverviewPage
from pages.printer_selection_page import PrinterSelectionPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enroll_or_replace_a_printer_enroll_printer_after_minutes(stage_callback):
    framework_logger.info("=== C48992660 - Enroll or replace a printer - Enroll Printer (after 15min) flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Create and claim a new virtual printer
            common.create_and_claim_virtual_printer()
            framework_logger.info(f"Claimed a new virtual printer")

            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")
            
            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")
           
            # Wait more than 15 minutes
            framework_logger.info("Waiting for 15 minutes to let the session expire...")
            time.sleep(930)
            framework_logger.info("Waited for 15 minutes")

            # Click login button in the session expired modal on the Smart Dashboard
            DashboardHelper.login_on_security_session_expired(page, tenant_email)
            framework_logger.info("Logged in the session expired modal")

            # Click on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click(timeout=90000)
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            # Click on Enroll Printer button to open printer selection in a new tab
            with page.expect_popup() as popup_info:
                overview_page.enroll_printer_button.click()
                framework_logger.info("Clicked on Enroll Printer button on Enroll or Replace a Printer modal")

            printer_selection_page = popup_info.value
            printer_selection = PrinterSelectionPage(printer_selection_page)

            # Accept terms of service and sees the printer selection page
            EnrollmentHelper.accept_terms_of_service(printer_selection_page)
            printer_selection.printer_selection_page.wait_for(state="visible", timeout=90000)
            framework_logger.info("Printer selection page is displayed")

            framework_logger.info("=== C48992660 - Enroll or replace a printer - Enroll Printer (after 15min) flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
