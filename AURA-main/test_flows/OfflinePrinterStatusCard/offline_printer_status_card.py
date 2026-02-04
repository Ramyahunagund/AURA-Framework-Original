import time
from pages.overview_page import OverviewPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def offline_printer_status_card(stage_callback):
    framework_logger.info("=== C42199060 - Offline printer status card started ===")
    tenant_email = create_ii_subscription(stage_callback)
    common.setup()
    
    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)
            side_menu = DashboardSideMenuPage(page)

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Overview page
            side_menu.click_overview()
            expect(overview_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Overview page")
 
            # Click the printer selector
            expect(overview_page.printer_selector).to_be_visible(timeout=30000)
            overview_page.printer_selector.click()
            framework_logger.info(f"Printer selector clicked")
            
            # Get the first printer's serial number
            first_printer = overview_page.printer_selector_first_printer.inner_text().strip()
            first_printer_id = first_printer.replace('S/N: ', '')
            framework_logger.info(f"First printer serial number: {first_printer_id}")

            # Set the printer to offline
            common.remove_printer_webservices(first_printer_id)
            framework_logger.info(f"Removed printer {first_printer_id} via webservice")
            wait_time = 900
            time.sleep(int(wait_time))
            page.reload()
            framework_logger.info(f"Page reloaded after setting printer {first_printer_id} to offline")
            
            # Check if the offline message is displayed
            page.wait_for_load_state("load", timeout=30000)
            DashboardHelper.sees_status_card
            overview_page.printer_offline_message.wait_for(timeout=30000)
            expect(overview_page.printer_offline_message).to_be_visible(timeout=30000)
            framework_logger.info(f"Checked offline message for printer {first_printer_id}")

            # Not ready to print message is seen on the printer status card
            expect(overview_page.status_card).to_contain_text("Not ready to print", timeout=30000)
            framework_logger.info(f"Printer status card shows 'Not ready to print' for printer")

            # Printer status tooltip is shown
            DashboardHelper.printer_status_tooltip
            framework_logger.info(f"Printer status tooltip is shown for printer {first_printer_id}")
            
            # Clicks on Connectivity guide link on Printer Offline Banner
            with page.context.expect_page() as new_page_info:
                overview_page.connectivity_guide_link.click()
            new_tab = new_page_info.value
            new_tab.bring_to_front()
            time.sleep(10)
            expect(page).to_have_url('/us-en/document/ish_2026537-1681507-16')
            framework_logger.info(f"Clicked on Connectivity guide link for printer {first_printer_id}")

            framework_logger.info("=== C42199060 - Offline printer status card started finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
