from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pause_plan_cards(stage_callback):
    framework_logger.info("=== C43244656 - II Account eligible for pause plan - pause plan cards flow started ===")
    tenant_email = enrollment_ink_web(stage_callback)

    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)
            update_plan_page = UpdatePlanPage(page)
            side_menu = DashboardSideMenuPage(page)

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info("Subscription moved to subscribed state and free months removed")

            # Access Smart Dashboard and skip preconditions
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")

            # Click Pause Instant Ink link then close the modal on Plan Details card > Overview page
            DashboardHelper.click_pause_plan_link_and_close_modal(page)
            framework_logger.info("Clicked Pause Instant Ink link then closed the modal on Plan Details card > Overview page")

            # Click on Update Plan Menu
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Clicked on Change Plan Menu")

            # Click Pause Instant Ink link then close the modal on Plan Details card > Update Plan page
            DashboardHelper.click_pause_plan_link_and_close_modal(page)
            framework_logger.info("Clicked Pause Instant Ink link then closed the modal on Plan Details card > Update Plan page")

            framework_logger.info("=== C43244656 - II Account eligible for pause plan - pause plan cards flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the pause plan cards flow: {e}\n{traceback.format_exc()}")
            raise e
