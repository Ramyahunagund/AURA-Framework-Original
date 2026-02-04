from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.print_history_page import PrintHistoryPage
from pages.update_plan_page import UpdatePlanPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from pages.shipping_billing_page import ShippingBillingPage
from pages.printer_selection_page import PrinterSelectionPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obsolete_eligible_re_enroll_simplified(stage_callback):
    framework_logger.info("=== C43381507 - Obsolete (eligible for re-enroll) simplified flow started ===")
    
    # Pre-condition 1: Enroll the printer to dashboard page
    tenant_email = create_ii_subscription(stage_callback)
    timeout_ms = 120000

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        print_history_page = PrintHistoryPage(page)
        update_plan_page = UpdatePlanPage(page)
        shipment_tracking_page = ShipmentTrackingPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        printer_selection_page = PrinterSelectionPage(page)
        
        try:
            # Pre-condition 2: Make sure the subscription is "obsolete" status
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription moved to subscribed state")

            # Force subscription to obsolete
            GeminiRAHelper.force_subscription_to_obsolete(page)
            framework_logger.info("Pre-condition completed: Subscription forced to obsolete state")

            # Access Smart Dashboard and skip preconditions
            DashboardHelper.first_access(page, tenant_email=tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")

            # Go to Overview page and verify Status card and Plan Details card
            expect(overview_page.status_card).to_be_visible(timeout=timeout_ms)
            expect(overview_page.plan_details_card).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified Status card and Plan Details card are displayed")

            # Check the header - verify Printer Selector with "Enroll Another Printer" link
            expect(overview_page.printer_selector).to_be_visible(timeout=timeout_ms)
            expect(overview_page.enroll_or_replace_button).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified Printer Selector with 'Enroll Another Printer' link")
            
            # Check Plan Details card - verify "There are no active plans" text
            expect(overview_page.no_active_plans).to_be_visible(timeout=timeout_ms)           
            expect(overview_page.no_active_plans).to_have_text("There are no active plans for this printer.")

            # Verify "re-enroll to select a plan" link is NOT displayed           
            expect(overview_page.plan_details_card).not_to_have_text('Enroll Printer Again')
            framework_logger.info("Verified Enroll Printer Again is NOT displayed")
                       
            # verify 'Printer Details' link
            expect(overview_page.printer_details_link).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified 'Printer Details' link is displayed")

            # Click 'Printer Details' link and verify modal
            overview_page.printer_details_link.click()
            expect(overview_page.printer_details_modal).to_be_visible(timeout=timeout_ms)
            expect(overview_page.printer_details_modal_title).to_be_visible(timeout=timeout_ms)
            expect(overview_page.printer_details_modal_printer_img).to_be_visible(timeout=timeout_ms)
            expect(overview_page.printer_details_modal_printer_info).to_be_visible(timeout=timeout_ms)
            overview_page.printer_details_modal_close_button.click()
            expect(overview_page.printer_details_modal).not_to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified printer details modal is displayed with printer information")        
                       
            # Check Enroll Printer Again button
            expect(overview_page.enroll_printer_again_button).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified 'Enroll Printer Again' button is displayed")

            # Click 'Download past invoices' link and verify redirection to Print History
            expect(overview_page.download_past_invoices).to_be_visible(timeout=timeout_ms)          
            overview_page.download_past_invoices.click()
            expect(print_history_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Successfully navigated to Print and Payment History page")

            # Click Update Plan tab and verify redirection to Overview
            side_menu.click_update_plan()
            expect(overview_page.overview_page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Step 11: Update Plan tab redirected to Overview page")

            # Click Print and Payment History
            side_menu.click_print_history()
            expect(print_history_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Print and Payment History page is displayed")

            # Check header in Print History - verify Printer Selector
            expect(overview_page.printer_selector).to_be_visible(timeout=timeout_ms)
            expect(overview_page.enroll_or_replace_button).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified Printer Selector with 'Enroll Another Printer' link in Print History")

            # Click Shipment Tracking tab and verify redirection to Overview
            side_menu.click_shipment_tracking()
            expect(overview_page.overview_page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Shipment Tracking tab redirected to Overview page")

            # Click 'Enroll Printer Again' button and verify new tab
            DashboardHelper.click_enroll_printer_again_and_validate_new_tab(page)
            framework_logger.info("Verified redirected to the Printer Selection page in a new tab.")
                       
            # Go back to dashboard and click Shipping & Billing
            side_menu.click_shipping_billing()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Successfully navigated to Shipping & Billing page")

            # Check Shipping & Billing page cards
            expect(shipping_billing_page.billing_section).to_be_visible(timeout=timeout_ms)         
            expect(shipping_billing_page.shipping_section).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified shipping and billing info cards for II subscription")

            framework_logger.info("=== C43381507 - Obsolete (eligible for re-enroll) simplified flow completed successfully ===")
            
        except Exception as e:
            framework_logger.error(f"An error occurred during the obsolete re-enroll simplified flow: {e}\n{traceback.format_exc()}")
            raise e
