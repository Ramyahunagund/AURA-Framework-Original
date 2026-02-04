from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import time
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ii_privacy_experience_flow(stage_callback):
    framework_logger.info("=== C52399937 - II Privacy Experience flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            DashboardHelper.access(page, tenant_email)
            DashboardHelper.accept_banner_and_access_overview_page(page)

            overview_page.continue_setting_preferences.click()

            expect(overview_page.manage_options_button).to_be_visible()
            expect(overview_page.decline_button).to_be_visible()
            expect(overview_page.accept_all_preferences).to_be_visible()

            overview_page.manage_options_button.click()

            assert overview_page.set_personalized_suggestions_button.count() > 0, f"Expected more than 0 but got {overview_page.set_personalized_suggestions_button.count()}"
            assert overview_page.set_advertising_button.count() > 0, f"Expected more than 0 but got {overview_page.set_advertising_button.count()}"
            assert overview_page.set_analytics_button.count() > 0, f"Expected more than 0 but got {overview_page.set_analytics_button.count()}"
            
            expect(overview_page.consent_back_button).to_be_visible()
            expect(overview_page.consent_continue_button).to_be_visible()

            overview_page.privacy_consents_items.nth(0).click()

            common.retry_operation(
                lambda: overview_page.set_analytics_button.get_attribute("value") == 'true',
                operation_name="Wait for analytics button value == true",
                max_attempts=30,
                delay=2
            )
            assert overview_page.set_analytics_button.get_attribute("value") == 'true', f"Expected 'true' but got {overview_page.set_analytics_button.get_attribute('value')}"

            overview_page.consent_continue_button.click()

            if common._stack == "pie":
                overview_page.wait.special_savings_modal_close().click()
            overview_page.wait.skip_tour().click()

            expect(overview_page.privacy_card).to_be_visible()
            expect(overview_page.share_usage_data_link).to_be_visible()

            overview_page.share_usage_data_link.click()

            common.retry_operation(
                lambda: overview_page.set_analytics_button.get_attribute("value") == 'true',
                operation_name="Wait for analytics button value == true",
                max_attempts=30,
                delay=2
            )
            assert overview_page.set_analytics_button.get_attribute("value") == 'true', f"Expected 'true' but got {overview_page.set_analytics_button.get_attribute('value')}"
            assert overview_page.set_advertising_button.get_attribute("value") == 'false', f"Expected 'false' but got {overview_page.set_advertising_button.get_attribute('value')}"
            assert overview_page.set_personalized_suggestions_button.get_attribute("value") == 'false', f"Expected 'false' but got {overview_page.set_personalized_suggestions_button.get_attribute('value')}"

            overview_page.privacy_consents_items.nth(1).click()
            common.retry_operation(
                lambda: overview_page.set_advertising_button.get_attribute("value") == 'true',
                operation_name="Wait for advertising button value == true",
                max_attempts=30,
                delay=2
            )

            overview_page.privacy_consents_items.nth(2).click()
            common.retry_operation(
                lambda: overview_page.set_personalized_suggestions_button.get_attribute("value") == 'true',
                operation_name="Wait for personalized suggestions button value == true",
                max_attempts=30,
                delay=2
            )

            overview_page.consent_continue_button.click()

            common.retry_operation(
                lambda: not overview_page.privacy_card.is_visible(),
                operation_name="Wait for privacy card to disappear",
                max_attempts=30,
                delay=2
            )
            expect(overview_page.privacy_card).not_to_be_visible()
            expect(overview_page.share_usage_data_link).not_to_be_visible()

            framework_logger.info("=== C52399937 - II Privacy Experience flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
