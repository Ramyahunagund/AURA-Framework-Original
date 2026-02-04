from pages.printer_replacement_page import PrinterReplacementPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.overview_page import OverviewPage
from pages.printer_selection_page import PrinterSelectionPage
from playwright.sync_api import expect
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def initiated_unsubscribed_enroll_or_replace_a_printer_enroll_printer_after15_min(stage_callback):
    framework_logger.info("=== C49012097 - Initiated Unsubscribed Enroll or replace a printer Enroll Printer after 15 min flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            CancellationPlanHelper.select_cancellation_feedback_option(page)
            framework_logger.info("Subscription cancellation initiated")

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

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click(timeout=90000)
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            # Click on enroll printer button on the Enroll or Replace Printer modal at UCDE
            with page.context.expect_page() as new_page_info:
                overview_page.enroll_printer_button.click()
                new_tab = new_page_info.value
            framework_logger.info("Clicked on enroll printer button on the Enroll or Replace Printer modal at UCDE")

            # Sees the Printer Selection page on the Smart Dashboard
            EnrollmentHelper.accept_terms_of_service(new_tab)
            printer_selection_page = PrinterSelectionPage(new_tab)
            expect(printer_selection_page.printer_selection_page).to_be_visible(timeout=90000)
            
            new_tab.close()
            page.bring_to_front()

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

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click(timeout=90000)
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            # Click on replace printer button on the Enroll or Replace Printer modal at UCDE
            overview_page.replace_printer_button.click()
            printer_replacement_page = PrinterReplacementPage(page)
            printer_replacement_page.wait.printer_replacement_page(timeout=90000)
            framework_logger.info("Verified the Printer Replacement page")

            framework_logger.info("Clicked on replace printer button on the Enroll or Replace Printer modal at UCDE")

            framework_logger.info("=== C49012097 - Initiated Unsubscribed Enroll or replace a printer Enroll Printer after 15 min flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
