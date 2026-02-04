from multiprocessing import context
from helper.enrollment_helper import EnrollmentHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def printer_selector_obsolete_not_eligible_for_reenroll(stage_callback):
    framework_logger.info("=== C43173802 - Printer Selector obsolete (not eligible for re-enroll) started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        side_menu = DashboardSideMenuPage(page)

        try:
            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Force subscription to obsolete state
            GeminiRAHelper.force_subscription_to_obsolete(page)
            framework_logger.info(f"Subscription moved to obsolete state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click enroll printer again button
            DashboardHelper.click_enroll_printer_again_button(page)
            framework_logger.info("Clicked enroll printer again button")

            new_tab = page.context.pages[-1]
            new_tab.bring_to_front()
            new_tab.wait_for_load_state("networkidle", timeout=120000)
            framework_logger.info("Switched to last tab")

            # Select printer
            EnrollmentHelper.select_printer(new_tab)
            framework_logger.info("Printer selected")

            # Select plan
            EnrollmentHelper.select_plan(new_tab, 100)
            framework_logger.info(f"Plan selected")

            # Finish enrollment
            EnrollmentHelper.finish_enrollment(new_tab)
            framework_logger.info("Enrollment completed successfully")

            # Close the enrollment tab and return to main page
            new_tab.close()
            page.bring_to_front()
            framework_logger.info("Closed the enrollment tab and return to main page")

            # Refreshes the page
            page.reload()
            framework_logger.info("Page refreshed")

            # Verify enrolled printer on printer selector
            DashboardHelper.verify_printer_in_submenu(page, "enrolled")
            framework_logger.info("Enrolled printer is displayed on printer selector")

            # Verify cancelled printer on printer selector
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")
            framework_logger.info("Cancelled printer is displayed on printer selector") 

            # First printer is selected on INSTANT INK CANCELLED SUBSCRIPTIONS printers on Overview page
            DashboardHelper.click_printer_submenu(page, "cancelled")
            framework_logger.info("Clicked on INSTANT INK CANCELLED SUBSCRIPTIONS printers on Overview page")   

            # Verifies there is only the Status card and Plan Details card
            DashboardHelper.sees_plan_details_card(page)
            framework_logger.info("Plan details card is displayed")

            # Sees the There are no active plans for this printer text and enroll printer again button is not visible
            assert "There are no active plans for this printer" in page.content(timeout=5000)
            expect(overview_page.enroll_printer_again_button).not_to_be_visible()
            framework_logger.info("There are no active plans for this printer text is displayed")

            # Doesn't see the Enroll this printer again to resume your service text on Status card
            assert "Enroll this printer again to resume your service" not in page.content()
            framework_logger.info("Doesn't see the Enroll this printer again to resume your service text on Status card")

            # Verify printer details modal
            overview_page.printer_details_link.click()
            expect(overview_page.printer_details_modal).to_be_visible(timeout=5000)
            overview_page.printer_details_modal_close_button.click()
            framework_logger.info("Printer details modal verified and closed")

            # Clicks on Download past invoices link on Status card
            overview_page.unsubscribed_download_past_invoices.click()
            framework_logger.info("Download past invoices modal verified and closed")

            # CLicks on Update Plan Menu
            side_menu.update_plan_menu_link.click()
            framework_logger.info("Clicked on Update Plan Menu")

            # Sees printer selector with Enroll or Replace Printer link
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)
            
            # Clicks on Print History Menu
            side_menu.print_history_menu_link.click()
            framework_logger.info("Clicked on Print History Menu")

            # Sees printer selector with Enroll or Replace Printer link
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)

            # Clicks on Shipment Tracking Menu
            side_menu.shipment_tracking_menu_link.click()
            framework_logger.info("Clicked on Shipment Tracking Menu")

            # Sees printer selector with Enroll or Replace Printer link
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)

            framework_logger.info("=== C43173802 - Printer Selector obsolete (not eligible for re-enroll) finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
