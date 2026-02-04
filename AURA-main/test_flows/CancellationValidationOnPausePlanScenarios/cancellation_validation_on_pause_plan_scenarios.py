from pages.dashboard_side_menu_page import DashboardSideMenuPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancellation_validation_on_pause_plan_scenarios(stage_callback):
    framework_logger.info("=== C43597102 - Cancellation validation on pause plan scenarios started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        side_menu = DashboardSideMenuPage(page)
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click on Cancel Instant Ink on Overview page 
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            # Validates Pause Plan link on Cancellation Summary Page
            DashboardHelper.click_pause_plan_link_and_close_modal(page, "Cancellation")
            framework_logger.info(f"Validated Pause Plan link on Cancellation Summary Page")

            # Pause Instant Ink for 1 month
            DashboardHelper.pause_plan(page, 1, "Cancellation")
            framework_logger.info("Paused Instant Ink for 1 month")

            # Go to overview and validate pause plan pending message
            side_menu.open_overview_page()
            framework_logger.info("Opened Overview page")
            expect(overview_page.plan_paused_banner).to_be_visible()
            framework_logger.info("Validated pause plan pending message on Overview page")

            # Cancel Plan Pause
            overview_page.resume_plan_link.click()
            expect(overview_page.resume_plan_button).to_be_visible(timeout=30000)
            overview_page.resume_plan_button.click()
            framework_logger.info("Validated Resume Plan button on Overview page")

            # Click on Cancel Instant Ink on Overview page
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            # Validates Pause Plan link on Cancellation Summary Page
            DashboardHelper.click_pause_plan_link_and_close_modal(page, "Cancellation")
            framework_logger.info(f"Validated Pause Plan link on Cancellation Summary Page")

            # Pause Instant Ink for 2 months
            DashboardHelper.pause_plan(page, 2, "Cancellation")
            framework_logger.info("Paused Instant Ink for 2 months")

            # Go to overview and validate pause plan pending message
            side_menu.open_overview_page()
            framework_logger.info("Opened Overview page")
            expect(overview_page.plan_paused_banner).to_be_visible()
            framework_logger.info("Validated pause plan pending message on Overview page")

            # Cancel Plan Pause
            overview_page.resume_plan_link.click()
            expect(overview_page.resume_plan_button).to_be_visible(timeout=30000)
            overview_page.resume_plan_button.click()
            framework_logger.info("Validated Resume Plan button on Overview page")

            # Click on Cancel Instant Ink on Overview page
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            # Validates Pause Plan link on Cancellation Summary Page
            DashboardHelper.click_pause_plan_link_and_close_modal(page, "Cancellation")
            framework_logger.info(f"Validated Pause Plan link on Cancellation Summary Page")

            # Pause Instant Ink for 3 months
            DashboardHelper.pause_plan(page, 3, "Cancellation")
            framework_logger.info("Paused Instant Ink for 3 months")

            # Go to overview and validate pause plan pending message
            side_menu.open_overview_page()
            framework_logger.info("Opened Overview page")
            expect(overview_page.plan_paused_banner).to_be_visible()
            framework_logger.info("Validated pause plan pending message on Overview page")

            # Cancel Plan Pause
            overview_page.resume_plan_link.click()
            expect(overview_page.resume_plan_button).to_be_visible(timeout=30000)
            overview_page.resume_plan_button.click()
            framework_logger.info("Validated Resume Plan button on Overview page")

            # Click on Cancel Instant Ink on Overview page
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            # Validates Pause Plan link on Cancellation Summary Page
            DashboardHelper.click_pause_plan_link_and_close_modal(page, "Cancellation")
            framework_logger.info(f"Validated Pause Plan link on Cancellation Summary Page")

            # Pause Instant Ink for 4 months
            DashboardHelper.pause_plan(page, 4, "Cancellation")
            framework_logger.info("Paused Instant Ink for 4 months")

            # Go to overview and validate pause plan pending message
            side_menu.open_overview_page()
            framework_logger.info("Opened Overview page")
            expect(overview_page.plan_paused_banner).to_be_visible()
            framework_logger.info("Validated pause plan pending message on Overview page")

            # Cancel Plan Pause
            overview_page.resume_plan_link.click()
            expect(overview_page.resume_plan_button).to_be_visible(timeout=30000)
            overview_page.resume_plan_button.click()
            framework_logger.info("Validated Resume Plan button on Overview page")

            # Click on Cancel Instant Ink on Overview page
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            # Validates Pause Plan link on Cancellation Summary Page
            DashboardHelper.click_pause_plan_link_and_close_modal(page, "Cancellation")
            framework_logger.info(f"Validated Pause Plan link on Cancellation Summary Page")

            # Pause Instant Ink for 5 months
            DashboardHelper.pause_plan(page, 5, "Cancellation")
            framework_logger.info("Paused Instant Ink for 5 months")

            # Go to overview and validate pause plan pending message
            side_menu.open_overview_page()
            framework_logger.info("Opened Overview page")
            expect(overview_page.plan_paused_banner).to_be_visible()
            framework_logger.info("Validated pause plan pending message on Overview page")

            # Cancel Plan Pause
            overview_page.resume_plan_link.click()
            expect(overview_page.resume_plan_button).to_be_visible(timeout=30000)
            overview_page.resume_plan_button.click()
            framework_logger.info("Validated Resume Plan button on Overview page")

            # Click on Cancel Instant Ink on Overview page
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            # Validates Pause Plan link on Cancellation Summary Page
            DashboardHelper.click_pause_plan_link_and_close_modal(page, "Cancellation")
            framework_logger.info(f"Validated Pause Plan link on Cancellation Summary Page")

            # Pause Instant Ink for 6 months
            DashboardHelper.pause_plan(page, 6, "Cancellation")
            framework_logger.info("Paused Instant Ink for 6 months")

            # Go to overview and validate pause plan pending message
            side_menu.open_overview_page()
            framework_logger.info("Opened Overview page")
            expect(overview_page.plan_paused_banner).to_be_visible()
            framework_logger.info("Validated pause plan pending message on Overview page")

            # Cancel Plan Pause
            overview_page.resume_plan_link.click()
            expect(overview_page.resume_plan_button).to_be_visible(timeout=30000)
            overview_page.resume_plan_button.click()
            framework_logger.info("Validated Resume Plan button on Overview page")

            framework_logger.info("=== C43597102 - Cancellation validation on pause plan scenarios started finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e