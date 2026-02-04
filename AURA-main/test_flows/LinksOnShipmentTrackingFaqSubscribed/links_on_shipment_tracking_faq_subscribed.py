from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def links_on_shipment_tracking_faq_subscribed(stage_callback):
    framework_logger.info("=== C44606960 - Links on Shipment Tracking FAQ for subscribed state flow started ===")
    tenant_email = create_ii_subscription(stage_callback)
    timeout_ms = 120000

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        shipment_tracking_page = ShipmentTrackingPage(page)
        overview_page = OverviewPage(page)
        update_plan_page = UpdatePlanPage(page)
        
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription moved to subscribed state")

            # Access Smart Dashboard and skip preconditions
            DashboardHelper.first_access(page, tenant_email=tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")

            # Click Shipment Tracking page
            side_menu.click_shipment_tracking()
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Accessed Shipment Tracking page")
            
            # Click on "What does my payment include" question (index 1)
            expect(shipment_tracking_page.faq_question(1)).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_question(1).click()
            expect(shipment_tracking_page.faq_answer2).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Clicked on 'What does my payment include' question")

            # Click the Overview link
            expect(shipment_tracking_page.faq_overview_link).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_overview_link.click()
            
            # Verify redirection to Overview page
            expect(overview_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Step 1 completed: Successfully redirected to Overview page")

            # Click Shipment Tracking page again
            side_menu.click_shipment_tracking()
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Navigated back to Shipment Tracking page")

            # Click on "What does my payment include" question again
            expect(shipment_tracking_page.faq_question(1)).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_question(1).click()
            expect(shipment_tracking_page.faq_answer2).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Clicked on 'What does my payment include' question again")

            # Click the Update Plan link
            expect(shipment_tracking_page.faq_update_plan_link).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_update_plan_link.click()
            
            # Verify redirection to Update Plan page
            expect(update_plan_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Step 2 completed: Successfully redirected to Update Plan page")

            framework_logger.info("=== C44606960 - Links on Shipment Tracking FAQ for subscribed state flow finished successfully ===")
            
        except Exception as e:
            framework_logger.error(f"An error occurred during the subscribed state flow: {e}\n{traceback.format_exc()}")
            raise e
