from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.overview_page import OverviewPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.printer_replacement_page import PrinterReplacementPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def replace_an_existing_printer_one_enrolled_printer_offline_and_one_claimed_printer(stage_callback):
    framework_logger.info("=== C51683209 - Replace an existing printer One enrolled printer offline and One claimed printer flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        printer_replacement = PrinterReplacementPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status updated to 'subscribed'")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            # Set the printer to offline
            printer_id = common._printer_created[0].entity_id
            common.remove_printer_webservices(printer_id)
            framework_logger.info(f"Removed printer {printer_id} via webservice")
            framework_logger.info("Waiting 15 minutes for the system to recognize the printer is offline...")
            time.sleep(900)
            page.reload()
            framework_logger.info(f"Page reloaded after setting printer {printer_id} to offline")

            # See Printer Offline message on Overview page
            expect(overview_page.printer_offline_message).to_be_visible(timeout=90000)
            framework_logger.info(f"Checked offline message for printer: {printer_id}")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")

            # Click login button in the session expired modal on the Smart Dashboard
            overview_page.enroll_or_replace_button.click()
            DashboardHelper.login_on_security_session_expired(page, tenant_email)
            framework_logger.info("Logged in the session expired modal")

            # Click on enroll or replace a printer link at Update Plan page
            overview_page.enroll_or_replace_button.click(timeout=90000)
            expect(overview_page.enroll_printer_button).to_be_visible(timeout=90000)
            expect(overview_page.replace_printer_button).to_be_visible()
            overview_page.enroll_modal_close.click()
            framework_logger.info("Clicked on enroll or replace a printer link at Update Plan page")

            # Access Print History Page
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Click on enroll or replace a printer link at Print History page
            overview_page.enroll_or_replace_button.click()
            expect(overview_page.enroll_printer_button).to_be_visible(timeout=90000)
            expect(overview_page.replace_printer_button).to_be_visible()
            overview_page.enroll_modal_close.click()
            framework_logger.info("Clicked on enroll or replace a printer link at Print History page")

            # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            framework_logger.info("Accessed Shipment Tracking page")

            # Click on enroll or replace a printer link at Shipment Tracking page
            overview_page.enroll_or_replace_button.click()
            expect(overview_page.enroll_printer_button).to_be_visible(timeout=90000)
            expect(overview_page.replace_printer_button).to_be_visible()
            overview_page.enroll_modal_close.click()
            framework_logger.info("Clicked on enroll or replace a printer link at Shipment Tracking page")

            # Access Overview page
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Create and claim a new virtual printer
            common.create_and_claim_virtual_printer()
            framework_logger.info(f"Claimed a new virtual printer")

            # Click on enroll or replace a printer link at Overview page
            overview_page.enroll_or_replace_button.click()
            expect(overview_page.enroll_printer_button).to_be_visible(timeout=90000)
            expect(overview_page.replace_printer_button).to_be_visible()
            framework_logger.info("Clicked on enroll or replace a printer link at Overview page")

            # Click Replace Printer button on the Enroll or Replace a Printer modal
            overview_page.replace_printer_button.click()
            framework_logger.info("Clicked Replace Printer button on the Enroll or Replace a Printer modal")

            # See Review your Instant Ink subscription transfer page
            expect(printer_replacement.current_printer_card).to_be_visible(timeout=90000)
            expect(printer_replacement.new_printer_card).to_be_visible(timeout=90000)
            framework_logger.info("Verified Review your Instant Ink subscription transfer page is displayed")

            framework_logger.info("=== C51683209 - Replace an existing printer One enrolled printer offline and One claimed printer flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
