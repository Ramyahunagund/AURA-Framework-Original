from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pause_plan_on_banner_and_plan_details_card_on_sub_with_paused_plan_on_update_plan_page(stage_callback):
    framework_logger.info("=== C43768665 - Pause plan on banner and Plan details card on sub with paused plan on Update Plan Page flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            update_plan_page = UpdatePlanPage(page)
            side_menu = DashboardSideMenuPage(page)

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

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

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
            framework_logger.info(f"Accessed Dashboard")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

            # Sees Plan pause pending banner on Update Plan page
            DashboardHelper.sees_plan_pause_banner(page)
            framework_logger.info(f"Verified Plan Pause banner on Update Plan page")

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

            # Shift subscription for 62 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "62")
            framework_logger.info("Shifted subscription for 62 days")

            # Access Dashboard
            DashboardHelper.access(page)
            framework_logger.info(f"Accessed Dashboard")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

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
            framework_logger.info(f"Accessed Dashboard")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

            # Sees Plan pause on plan details card on Update Plan page
            expect(update_plan_page.pause_plan_info).to_be_visible(timeout=90000)
            framework_logger.info(f"Verified Plan Pause information on plan details card on Update Plan page")

            # Click on Resume Plan link on plan details card on Update Plan page
            update_plan_page.resume_plan_link.click()
            framework_logger.info(f"Clicked on Resume Plan link on plan details card on Update Plan page")

            # Keeps the plan paused on confirm plan resume modal
            DashboardHelper.click_keep_paused(page)
            framework_logger.info(f"Kept the plan paused on confirm plan resume modal")

            # Click and confirm Resume Plan
            update_plan_page.resume_plan_link.click()
            DashboardHelper.click_resume_plan(page)
            framework_logger.info(f"Clicked on Resume Plan button")

            # Shift subscription for 62 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "62")
            framework_logger.info("Shifted subscription for 62 days")

            # Access Dashboard
            DashboardHelper.access(page)
            framework_logger.info(f"Accessed Dashboard")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

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
            framework_logger.info(f"Accessed Dashboard")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

            # Sees original plan on Update Plan page
            expect(update_plan_page.plan_100_resume_tag).to_be_visible()
            expect(update_plan_page.plan_100_resume_button).to_be_visible()
            framework_logger.info(f"Verified original plan on Update Plan page")

            # Click on Resume
            update_plan_page.plan_100_resume_button.click()
            framework_logger.info(f"Clicked on Resume button on Plan Card on Update Plan page")

            # Keeps the plan paused on confirm plan resume modal
            DashboardHelper.click_keep_paused(page)
            framework_logger.info(f"Kept the plan paused on confirm plan resume modal")

            # Click and confirm Resume Plan
            update_plan_page.plan_100_resume_button.click()
            DashboardHelper.click_resume_plan(page)
            framework_logger.info(f"Clicked on Resume Plan button")

            framework_logger.info("=== C43768665 - Pause plan on banner and Plan details card on sub with paused plan on Update Plan Page flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e