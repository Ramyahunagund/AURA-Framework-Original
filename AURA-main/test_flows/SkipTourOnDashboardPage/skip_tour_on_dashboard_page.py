from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def skip_tour_on_dashboard_page(stage_callback):
    framework_logger.info("=== C41186609 - Skip Tour on Dashboard page flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)

            # Access Dashboard for the first time
            DashboardHelper.access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # access Overview page
            DashboardHelper.accept_banner_and_access_overview_page(page)

            # Skip all but tour precondition
            DashboardHelper.skips_all_but_tour_precondition(page)
            framework_logger.info("Skipped all but tour modal")

            # Skip Tour modal on Overview page
            DashboardHelper.skip_tour_modal(page)
            framework_logger.info("Skipped tour modal")

            # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            framework_logger.info("Dashboard Shipment Tracking page accessed successfully")

            # Access Overview page
            side_menu.overview_menu_link.click()
            framework_logger.info("Accessed Overview page")

            # Verify Tour modal is not visible
            DashboardHelper.verify_tour_modal_not_appears(page)
            framework_logger.info("Verified Tour modal is not visible on Overview page")
            framework_logger.info("=== C41186609 - Skip Tour on Dashboard page flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()