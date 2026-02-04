import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from helper.print_history_helper import PrintHistoryHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.print_history_page import PrintHistoryPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def subscribed_and_redeemed_paper_subscription_print_history_and_shipment_tracking_page(stage_callback):
    framework_logger.info("=== C31622484 / C31749679 - Subscribed and Redeemed Paper Subscription Print History and Shipment Tracking Page flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # HPID signup + UCDE onboarding
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # Claim virtual printer and add address
        printer = common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        try:
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Select ink and paper plan
            EnrollmentHelper.select_plan(page, plan_value="100", plan_type="ink_and_paper")
            framework_logger.info(f"Paper plan selected: 100")

            price = None
            try:
                price = EnrollmentHelper.get_total_price_by_plan_card(page)
            except Exception:
                framework_logger.info(f"Failed to get price from plan card")

            # Add billing
            EnrollmentHelper.add_billing(page, plan_value=price)
            framework_logger.info(f"Billing added")

            # Finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Paper subscription enrollment completed successfully")
        except Exception as e:
            framework_logger.error(f"An error occurred during the paper subscription enrollment: {e}\n{traceback.format_exc()}")
            raise e

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        print_history_page = PrintHistoryPage(page)
        shipment_tracking_page = ShipmentTrackingPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription moved to subscribed state")

            # Verify pilot subscription is redeemed
            RABaseHelper.access_link_by_title(page, "PilotSubscription", "Pilot subscriptions")
            GeminiRAHelper.verify_rails_admin_info(page, "State", "redeemed")
            framework_logger.info("Verified pilot subscription is redeemed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened Instant Ink Dashboard")

            # Access Print and Payment History page
            side_menu.click_print_history()
            framework_logger.info("Navigated to Print and Payment History page")

            # Verify Print and Payment History page
            expect(print_history_page.page_title).to_be_visible(timeout=90000)
            expect(print_history_page.print_history_card).to_be_visible()
            expect(print_history_page.print_history_card_title).to_be_visible()
            expect(print_history_page.how_is_calculated_link).to_be_visible()
            expect(print_history_page.total_printed_pages).to_be_visible()
            expect(print_history_page.plan_pages_bar).to_be_visible()
            expect(print_history_page.trial_pages_bar).to_be_visible()
            expect(print_history_page.rollover_pages_bar).to_be_visible()
            expect(print_history_page.plan_details_card).to_be_visible()
            expect(print_history_page.paper_summary).not_to_be_visible()
            framework_logger.info("Print History page verified")

            # Verify plan information
            PrintHistoryHelper.verify_plan_info(page, "7.99", "100")
            framework_logger.info("Verified plan information in Print History page")

            # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            framework_logger.info("Navigated to Shipment Tracking page")

            # Verify Shipment Tracking page
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=90000)
            expect(shipment_tracking_page.kCartridgeItem).to_be_visible()
            expect(shipment_tracking_page.paper_tracking_item).not_to_be_visible()
            framework_logger.info("Shipment Tracking page verified")

            framework_logger.info("=== C31622484 / C31749679 - Subscribed and Redeemed Paper Subscription Print History and Shipment Tracking Page flow finished successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e