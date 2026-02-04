from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.confirmation_page import ConfirmationPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.print_history_page import PrintHistoryPage
from pages.overview_page import OverviewPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def printer_selector_reenroll_with_the_obsolete_printer(stage_callback):
    framework_logger.info("=== C42995956 - Printer Selector Reenroll with the obsolete printer flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        side_menu = DashboardSideMenuPage(page)
        print_history_page = PrintHistoryPage(page)
        update_plan = UpdatePlanPage(page)
        shipment_tracking = ShipmentTrackingPage(page)
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

            # Click close button of the finish enrolling modal
            overview_page.close_finish_enrollment_button.click()
            framework_logger.info("Clicked close button of the finish enrolling modal")

            # Verify enrolled printer on printer selector
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)
            DashboardHelper.verify_printer_in_submenu(page, "enrolled")

            # Verify cancelled printer on printer selector
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")

            # Access Print History Page
            side_menu.click_print_history()
            expect(print_history_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Verify enrolled printer on printer selector
            DashboardHelper.verify_printer_in_submenu(page, "enrolled")

            # Verify cancelled printer on printer selector
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

            # Verify enrolled printer on printer selector
            DashboardHelper.verify_printer_in_submenu(page, "enrolled")

            # Verify cancelled printer on printer selector
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")

            # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            expect(shipment_tracking.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Dashboard Shipment Tracking page accessed successfully")

            # Verify enrolled printer on printer selector
            DashboardHelper.verify_printer_in_submenu(page, "enrolled")

            # Verify cancelled printer on printer selector
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")

            framework_logger.info("=== C42995956 - Printer Selector Reenroll with the obsolete printer flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e