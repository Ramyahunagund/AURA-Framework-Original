from time import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.cancellation_banner_page import CancellationBannerPage
from pages.cancellation_timeline_page import CancellationTimelinePage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from pages.update_plan_page import UpdatePlanPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


TC="C38323929"
def extra_ink_when_upgrading_the_plan(stage_callback):
    framework_logger.info("=== Test C38323929 Extra Ink when upgrading to the 700 page plan started ===")
    common.setup()
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"Generated tenant_email={tenant_email}")
    with PlaywrightManager() as page:
        try:
            # Move subscription to subscribed state
            GeminiRAHelper.access(page)           
            GeminiRAHelper.access_tenant_page(page, tenant_email)           
            GeminiRAHelper.access_subscription_by_tenant(page)            
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription status updated")          

            # Go to Smart Dashboard and change to a higher plan
            DashboardHelper.first_access(page, tenant_email=tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")

            # Access Update Plan page
            side_menu = DashboardSideMenuPage(page)
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")

            # Select plan 700
            UpdatePlanHelper.select_plan(page, 700)
            update_plan_page = UpdatePlanPage(page)
            update_plan_page.change_plan_upgrade_button.click(timeout=60000)
            framework_logger.info("Plan 700 selection completed")

            # validate new cartridges
            side_menu.click_shipment_tracking()
            shipment_tracking_page = ShipmentTrackingPage(page)
            shipment_tracking_page.shipment_history_table.click()

            first_descriptions = shipment_tracking_page.shipment_history_description

            first_description = first_descriptions.first.inner_text()
            cartridges = common.extract_numbers_from_text(first_description)
            assert len(cartridges) > 1 , f"Expected at least 2 cartridges in the description, but found {cartridges.count()}"
            assert cartridges[0] == 1, f"Expected 1 cartridge, but found {cartridges[0]}"
            assert cartridges[1] == 1, f"Expected 1 cartridges, but found {cartridges[1]}"

            # validate new shipment
            GeminiRAHelper.access(page)           
            GeminiRAHelper.access_tenant_page(page, tenant_email)           
            GeminiRAHelper.access_subscription_by_tenant(page)  
            framework_logger.info("Accessed subscription page in GRA")

            first_shipments_link = RABaseHelper.get_links_by_title(page, "Printer shipments")
            first_shipments_link.first.click()
            framework_logger.info("Accessed Printer shipments page in GRA")

            source_text = RABaseHelper.get_field_text_by_title(page, "Source")
            assert source_text == "extraKitForPlanUpgrade", f"Expected 'extraKitForPlanUpgrade' as Source but found '{source_text}'"
            framework_logger.info("Source field verification completed")

            # Go to Smart Dashboard and change to a higher plan
            DashboardHelper.access(page)
            framework_logger.info("Accessed Smart Dashboard")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")

            # Select plan 1500
            UpdatePlanHelper.select_plan(page, 1500)
            update_plan_page = UpdatePlanPage(page)
            update_plan_page.change_plan_upgrade_button.click(timeout=60000)
            framework_logger.info("Plan 1500 selection completed")

            # validate new cartridges
            side_menu.click_shipment_tracking()
            shipment_tracking_page = ShipmentTrackingPage(page)
            shipment_tracking_page.shipment_history_table.click()

            seccond_descriptions = shipment_tracking_page.shipment_history_description
            seccond_description = seccond_descriptions.first.inner_text()
            cartridges = common.extract_numbers_from_text(seccond_description)

            assert first_descriptions.count() == seccond_descriptions.count(), f"Expected the same number of descriptions, but found {first_descriptions.count()} and {seccond_descriptions.count()}"
            assert len(cartridges) > 1 , f"Expected at least 2 cartridges in the description, but found {cartridges.count()}"
            assert cartridges[0] == 1, f"Expected 1 cartridge, but found {cartridges[0]}"
            assert cartridges[1] == 1, f"Expected 1 cartridges, but found {cartridges[1]}"

            # validate new shipment
            GeminiRAHelper.access(page)           
            GeminiRAHelper.access_tenant_page(page, tenant_email)           
            GeminiRAHelper.access_subscription_by_tenant(page)  
            framework_logger.info("Accessed subscription page in GRA")

            seccond_shipments_link = RABaseHelper.get_links_by_title(page, "Printer shipments")
            assert first_shipments_link.count() == seccond_shipments_link.count(), f"Expected the same number of Printer shipments links, but found {first_shipments_link.count()} and {seccond_shipments_link.count()}"
            seccond_shipments_link.first.click()
            framework_logger.info("Accessed Printer shipments page in GRA")

            source_text = RABaseHelper.get_field_text_by_title(page, "Source")
            assert source_text == "extraKitForPlanUpgrade", f"Expected 'extraKitForPlanUpgrade' as Source but found '{source_text}'"
            framework_logger.info("Source field verification completed")
            
            DashboardHelper.access(page)
            framework_logger.info("Accessed Smart Dashboard")

            # Access Update Plan page
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            DashboardHelper.verify_plan_value(page, 1500)

            framework_logger.info("Test completed successfully")
        except Exception as e:
            framework_logger.error(f"Test with Error: {e}\n{traceback.format_exc()}")
            raise e
