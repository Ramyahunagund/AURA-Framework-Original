from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.printers_page import PrintersPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def remove_printer_from_printer_page(stage_callback):
    framework_logger.info("=== C38097833 - Remove Printer from Printer page flow started ===")
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"Tenant email: {tenant_email}")

    with PlaywrightManager() as page:
        printers_page = PrintersPage(page)
        side_menu = DashboardSideMenuPage(page)
        try:
            # Claim virtual printer
            common.create_and_claim_virtual_printer()

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Printers page
            side_menu.printers_menu_link.click(timeout=90000)
            framework_logger.info(f"Clicked on Printers menu link")

            # Remove non-enrolled printer
            printer_box = printers_page.non_enrolled_printer_box
            expect(printer_box).to_be_visible(timeout=90000)
            printer_box.locator(printers_page.elements.printer_options).click()
            printer_box.locator(printers_page.elements.remove_printer_button).click()
            printers_page.confirm_remove_printer_button.click()
            printers_page.close_remove_printer_button.click()
            framework_logger.info(f"Removed non-enrolled printer")

            # Do not see non-enrolled printer on my Printers page
            page.reload()
            printers_page.printer_options.wait_for(timeout=90000)
            expect(printers_page.non_enrolled_printer_box).not_to_be_visible()
            framework_logger.info(f"Verified that non-enrolled printer is not visible")

            # Try to remove enrolled printer
            printers_page.printer_options.click()
            printers_page.remove_printer_button.click()
            printers_page.confirm_remove_printer_button.click()
            expect(printers_page.manage_subscription_button).to_be_visible(timeout=90000)
            printers_page.close_remove_printer_button.click()
            framework_logger.info(f"Tried to remove enrolled printer")

            # See enrolled printer on my Printers page
            page.reload()
            expect(printers_page.enrolled_printer_box).to_be_visible(timeout=90000)
            framework_logger.info(f"Verified that enrolled printer is visible")

            framework_logger.info("=== C38097833 - Remove Printer from Printer page flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
