from helper.update_plan_helper import UpdatePlanHelper
from pages.overview_page import OverviewPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.email_helper import EmailHelper
from pages.update_plan_page import UpdatePlanPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pause_plan_pending_and_subscription_with_plan_paused(stage_callback):
    framework_logger.info("=== C43554400 - Pause plan pending cases + Subscription with plan paused flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)
            overview_page = OverviewPage(page)
            update_plan_page = UpdatePlanPage(page)

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Pause plan for 2 months on Overview page
            DashboardHelper.pause_plan(page, 2)
            framework_logger.info(f"Paused plan for 2 months on Overview page")

            # Sees Plan pause pending banner on Overview page
            DashboardHelper.sees_plan_pause_banner(page)
            framework_logger.info(f"Verified Plan Pause banner on Overview page")

            # Click on Resume Plan link on pause plan banner
            DashboardHelper.click_resume_plan_banner(page)
            framework_logger.info(f"Clicked on Resume Plan link on pause plan banner")

            # Keeps the plan paused on confirm plan resume modal
            DashboardHelper.click_keep_paused(page)
            framework_logger.info(f"Kept the plan paused on confirm plan resume modal")

            # Click and confirm Resume Plan
            DashboardHelper.click_resume_plan_banner(page)
            DashboardHelper.click_resume_plan(page)
            framework_logger.info(f"Clicked on Resume Plan button")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info(f"Accessed Update Plan page")

            # Pause plan for 2 months on Update Plan page
            DashboardHelper.pause_plan(page, 2)
            framework_logger.info(f"Paused plan for 2 months on Update Plan page")

            # Click on Resume Plan link on pause plan banner
            DashboardHelper.click_resume_plan_banner(page)
            framework_logger.info(f"Clicked on Resume Plan link on pause plan banner")

            # Keeps the plan paused on confirm plan resume modal
            DashboardHelper.click_keep_paused(page)
            framework_logger.info(f"Kept the plan paused on confirm plan resume modal")

            # Click and confirm Resume Plan
            DashboardHelper.click_resume_plan_banner(page)
            DashboardHelper.click_resume_plan(page)
            framework_logger.info(f"Clicked on Resume Plan button")

            # Access Overview page
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")
            
            # Pause plan for 2 months on Update Plan page
            DashboardHelper.pause_plan(page, 2)
            framework_logger.info(f"Paused plan for 2 months on Update Plan page")

            # Shift subscription for 32 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            framework_logger.info("Shifted subscription for 32 days")

            # Access Dashboard
            DashboardHelper.access(page)
            side_menu.click_overview()
            expect(overview_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Overview page")

            # Click on Cancel Instant Ink link on Overview page
            update_plan_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink link on Overview page")
            
            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info(f"Accessed Update Plan page")
            
            # Click on Cancel Instant Ink link on Update Plan page
            update_plan_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink link on Update Plan page")

            # Access Overview page
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Verify pause plan information
            DashboardHelper.verify_pause_plan_information(page)
            framework_logger.info("Verified pause plan information on Overview page")

            # And the user clicks on Cancel Instant Ink link on Overview page
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("Clicked on Cancel Instant Ink link on Overview page")
                        
            # And the user sees the confirmation email with subject "Confirmation: Cancellation Request Received"
            EmailHelper.sees_email_with_subject(tenant_email, subject="Confirmation: Cancellation Request Received")
            framework_logger.info(f"Received email with subject 'Confirmation: Cancellation Request Received'")
            framework_logger.info("=== C43554400 - Pause plan pending cases + Subscription with plan paused flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
