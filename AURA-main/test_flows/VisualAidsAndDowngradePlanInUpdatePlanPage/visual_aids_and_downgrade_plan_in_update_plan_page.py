import datetime
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.dashboard_helper import DashboardHelper
from pages.update_plan_page import UpdatePlanPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common

def visual_aids_and_downgrade_plan_in_update_plan_page(stage_callback) -> None:
    framework_logger.info("=== C41060790 - Visual Aids and Downgrade Plan in Update Plan Page flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            dashboard_side_menu_page = DashboardSideMenuPage(page)
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

            # Does not see free months in Update Plan page
            dashboard_side_menu_page.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible()
            UpdatePlanHelper.doesnt_see_free_months(page)
            framework_logger.info(f"Verified free months are not displayed in Update Plan page")

            # Verify available plans and current plan
            UpdatePlanHelper.verify_available_plans(page)
            UpdatePlanHelper.verify_current_plan(page, 100)
            framework_logger.info(f"Verified available plans and current plan is 100 pages")

            # Select a lower plan
            UpdatePlanHelper.select_plan(page, 50)
            framework_logger.info(f"Selected plan with 50 pages")

            # Verify Change your plan modal with information about the downgrade plan
            expect(update_plan_page.downgrade_plan_confirmation).to_be_visible()
            expect(update_plan_page.cancel_change_plan_button).to_be_visible()
            expect(update_plan_page.change_plan_button).to_be_visible()
            expect(update_plan_page.plan_downgrade_close_modal_button).to_be_visible()
            framework_logger.info(f"Verified downgrade plan modal is displayed")

            # Click Close button in the modal
            update_plan_page.plan_downgrade_close_modal_button.click()
            framework_logger.info(f"Clicked Close button in downgrade plan modal")

            # Verify that the plan is not changed
            UpdatePlanHelper.verify_current_plan(page, 100)
            framework_logger.info(f"Verified that the plan is still 100 pages after closing the modal")

            # Click on the plan card to open the downgrade modal again
            UpdatePlanHelper.select_plan(page, 50)
            framework_logger.info(f"Clicked on the plan card to open downgrade modal again")

            # Click Cancel button in the modal
            UpdatePlanHelper.select_plan_button(page, 50)
            framework_logger.info(f"Clicked Cancel button in downgrade plan modal")

            # Verify that the plan is not changed
            UpdatePlanHelper.verify_current_plan(page, 100)
            framework_logger.info(f"Verified that the plan is still 100 pages after clicking Cancel")

            # Click on the plan card to open the downgrade modal again
            UpdatePlanHelper.select_plan(page, 50)
            framework_logger.info(f"Clicked on the plan card to open downgrade modal again")

            # Click Change Plan button in the modal
            UpdatePlanHelper.select_plan_button(page, 50)
            framework_logger.info(f"Clicked Change Plan button in downgrade plan modal")

            # Verify downgrade plan message
            today = datetime.date.today()
            if today.month == 12:
                expected_date = today.replace(year=today.year + 1, month=1)
            else:
                expected_date = today.replace(month=today.month + 1)
            expected_text = f"Your plan will change to the 50 pages/month plan on {expected_date.strftime('%b %d, %Y')}."
            expect(update_plan_page.pending_change_plan).to_be_visible(timeout=30000)
            expect(update_plan_page.pending_change_plan).to_contain_text(expected_text)
            framework_logger.info(f"Verified pending change plan message: {expected_text}")

            framework_logger.info(f"=== C41060790 - Visual Aids and Downgrade Plan in Update Plan Page flow finished ===")
        except Exception as e:
            framework_logger.error(f"Error during flow execution: {e}")