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
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def replace_an_existing_printer_one_enrolled_printer_and_one_claimed_printer(stage_callback):
    framework_logger.info("=== C51683208 - Replace an existing printer One enrolled printer and One claimed printer flow started ===")
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

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")

            # Click on enroll or replace a printer link at Update Plan page
            overview_page.enroll_or_replace_button.click()
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

            # Click on enroll or replace a printer link at Overview page
            overview_page.enroll_or_replace_button.click()
            expect(overview_page.enroll_printer_button).to_be_visible(timeout=90000)
            expect(overview_page.replace_printer_button).to_be_visible()
            framework_logger.info("Clicked on enroll or replace a printer link at Overview page")
            
            # Click Replace Printer button on the Enroll or Replace a Printer modal
            overview_page.replace_printer_button.click()
            framework_logger.info("Clicked Replace Printer button on the Enroll or Replace a Printer modal")

            # See the Printer Replacement page
            expect(printer_replacement.printer_not_set_up_button).to_be_visible(timeout=90000)
            expect(printer_replacement.printer_set_up_button).to_be_visible(timeout=90000)
            framework_logger.info("Verified Printer Replacement page is displayed")

            # Access Overview page
            side_menu.click_overview()
            DashboardHelper.sees_status_card(page)
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

            framework_logger.info("=== C51683208 - Replace an existing printer One enrolled printer and One claimed printer flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
