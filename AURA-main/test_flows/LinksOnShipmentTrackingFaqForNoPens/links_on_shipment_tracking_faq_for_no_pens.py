from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def links_on_shipment_tracking_faq_for_no_pens(stage_callback):
    framework_logger.info("=== C35624091 - Links on Shipment Tracking FAQ for no pens flow started ===")
    tenant_email = create_ii_subscription(stage_callback)
    timeout_ms = 120000

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        shipment_tracking_page = ShipmentTrackingPage(page)
        try:
            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Shipment Tracking Menu at UCDE
            side_menu.click_shipment_tracking()
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info(f"Accessed Shipment Tracking page")

            # Verify FAQ card on Shipment Tracking page
            expect(shipment_tracking_page.faq_card).to_be_visible(timeout=timeout_ms)
            expect(shipment_tracking_page.faq_question(0)).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_question(0).click()
            expect(shipment_tracking_page.faq_answer1).to_be_visible(timeout=timeout_ms)
            print(f"FAQ answer 1 is visible")

            expect(shipment_tracking_page.faq_question(1)).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_question(1).click()
            expect(shipment_tracking_page.faq_answer2).to_be_visible(timeout=timeout_ms)
            expect(shipment_tracking_page.faq_overview_link).to_be_visible(timeout=timeout_ms)
            expect(shipment_tracking_page.faq_update_plan_link).to_be_visible(timeout=timeout_ms)
            print(f"FAQ answer 2 is visible")

            expect(shipment_tracking_page.faq_question(2)).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_question(2).click()
            expect(shipment_tracking_page.faq_answer3).to_be_visible(timeout=timeout_ms)
            print(f"FAQ answer 3 is visible")
            framework_logger.info(f"Faq on Shipment Tracking page verified")

            framework_logger.info("=== C35624091 - Links on Shipment Tracking FAQ for no pens flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
