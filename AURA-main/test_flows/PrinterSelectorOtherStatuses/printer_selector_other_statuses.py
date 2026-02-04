# test_flows/PrinterSelectorOtherStatusesCucumber/printer_selector_cucumber_c42810629.py

import traceback
from playwright.sync_api import sync_playwright, expect
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
from pages.print_history_page import PrintHistoryPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from helper.update_plan_helper import UpdatePlanHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def printer_selector_other_statuses(stage_callback):
    framework_logger.info("=== C42810629 Printer Selector Other Statuses flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)
            update_plan = UpdatePlanPage(page)
            print_history_page = PrintHistoryPage(page)
            shipment_tracking_page = ShipmentTrackingPage(page)
            overview_page = OverviewPage(page)
    
            # Verify subscription state is subscribed_no_pens
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed_no_pens")
            framework_logger.info(f"Verified subscription state is subscribed_no_pens")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Check the enrolled printer on Overview page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

             # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Update Plan page is displayed")

            # Check the enrolled printer on Update plan page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

            # Access Print History page
            side_menu.click_print_history()
            expect(print_history_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Print and Payment History page is displayed")

            # Check the enrolled printer on Print History page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

             # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Shipment Tracking page")

            # Check the enrolled printer on Shipment Tracking page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed")
            framework_logger.info(f"Subscription status updated to 'subscribed'")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Check the enrolled printer on Overview page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

             # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Update Plan page is displayed")

            # Check the enrolled printer on Update plan page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

            # Access Print History page
            side_menu.click_print_history()
            expect(print_history_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Print and Payment History page is displayed")

            # Check the enrolled printer on Print History page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

             # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Shipment Tracking page")

            # Check the enrolled printer on Shipment Tracking page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

            # Access Overview page
            side_menu.click_overview()
            expect(overview_page.plan_details_card).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Overview page")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info(f"Subscription cancellation")

            # Verify subscription state is initiated_unsubscribe
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "initiated_unsubscribe")
            framework_logger.info(f"Verified subscription state is initiated_unsubscribe")

                # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Check the enrolled printer on Overview page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

             # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Update Plan page is displayed")

            # Check the enrolled printer on Update plan page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

            # Access Print History page
            side_menu.click_print_history()
            expect(print_history_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Print and Payment History page is displayed")

            # Check the enrolled printer on Print History page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

             # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Shipment Tracking page")

            # Check the enrolled printer on Shipment Tracking page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

                # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Check the enrolled printer on Overview page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

             # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Update Plan page is displayed")

            # Check the enrolled printer on Update plan page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

            # Access Print History page
            side_menu.click_print_history()
            expect(print_history_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Print and Payment History page is displayed")

            # Check the enrolled printer on Print History page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

            # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Shipment Tracking page")

            # Check the enrolled printer on Shipment Tracking page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

            # Access Shipment Tracking page
            side_menu.click_overview()
            expect(overview_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Shipment Tracking page")

            # Keep the subscription
            DashboardHelper.keep_subscription(page)
            framework_logger.info("Kept subscription")

            # Check the enrolled printer on Overview page
            DashboardHelper.verify_instant_ink_enrolled_printer_visible(page, "INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("Successfully verified enrolled subscription printer")

            framework_logger.info("=== C42810629 - Printer Selector Other Statuses completed successfully")
            return tenant_email

        except Exception as e:
            framework_logger.error(f"An error occurred during Cucumber scenario execution: {e}\n{traceback.format_exc()}")
            raise
