from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.overview_helper import OverviewHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.update_plan_page import UpdatePlanPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancellation_change_plan_modal(stage_callback):
    framework_logger.info("=== C43390350 - Cancellation - Change Plan modal flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        dashboard_page = UpdatePlanPage(page)
        
        try:
            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Verify the Change Plan modal and close it
            DashboardHelper.verify_and_close_change_plan_modal(page)
            framework_logger.info(f"Change Plan modal verified and closed")

            # Validate the Change Plan modal on Cancellation Summary page
            CancellationPlanHelper.validate_change_plan_modal(page)
            framework_logger.info("Change Plan modal validated")

            # Validate the additional pages tooltip on Change Plan modal
            CancellationPlanHelper.validate_additional_pages_tooltip_on_change_plan_modal(page, "$1.50")
            framework_logger.info("Additional pages tooltip validated")

            # Select plan on the Change Plan modal on Cancellation Summary page
            CancellationPlanHelper.select_plan_on_change_plan_modal(page, "1500")
            framework_logger.info("Change Plan modal validated")

            # Validate the choose your new plan start date modal
            CancellationPlanHelper.validate_the_choose_your_new_plan_start_date_modal(page)
            framework_logger.info("Choose your new plan start date modal validated")

            # Click on back button in the new plan start date modal
            CancellationPlanHelper.click_button_in_the_new_plan_start_date_modal(page, "back")
            framework_logger.info("Choose your new plan start date modal validated")

            # Select plan on the Change Plan modal on Cancellation Summary page
            CancellationPlanHelper.select_plan_on_change_plan_modal(page, "1500")
            framework_logger.info("Change Plan modal validated")

            # Select next billing cycle on cancellation summary page
            CancellationPlanHelper.select_billing_cycle_on_cancellation_summary_page(page, "Next")
            framework_logger.info("Next billing cycle on cancellation summary page selected")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")

            # Verify the plan upgraded or downgraded message on Update Plan page
            UpdatePlanHelper.sees_plan_upgraded_or_downgraded_message_on_banner(page, "1500")
            framework_logger.info("Plan upgraded or downgraded message on Update Plan page verified")

            # Click on Cancel button on Undo your plan modal on Update Plan page
            UpdatePlanHelper.click_button_on_undo_your_plan_modal(page, "Cancel")           
            framework_logger.info("Cancel button on Undo your plan modal on Update Plan page clicked")

            # Access Overview page
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Validate the Change Plan modal on Cancellation Summary page
            dashboard_page.cancel_instant_ink.click()
            CancellationPlanHelper.validate_change_plan_modal(page)
            framework_logger.info("Change Plan modal validated")

            # Select plan on the Change Plan modal on Cancellation Summary page
            CancellationPlanHelper.select_plan_on_change_plan_modal(page, "1500")
            framework_logger.info("Change Plan modal validated")

            # Select current billing cycle on cancellation summary page
            CancellationPlanHelper.select_billing_cycle_on_cancellation_summary_page(page, "Current")
            framework_logger.info("Current billing cycle on cancellation summary page selected")

            # Verify the plan upgraded info on Overview page
            OverviewHelper.sees_plan_upgraded_information_on_overview_page(page, "1500")
            framework_logger.info("Plan upgraded info on Overview page verified")

            # Validate the Change Plan modal on Cancellation Summary page
            dashboard_page.cancel_instant_ink.click()
            CancellationPlanHelper.validate_change_plan_modal(page)
            framework_logger.info("Change Plan modal validated")

            # Verify the pages and plan price on Change Plan modal
            CancellationPlanHelper.sees_the_pages_and_plan_price_on_change_plan_modal(page, "1500", "$61.99")
            framework_logger.info("Pages and plan price on Change Plan modal verified")

            # Verify all the ink plans on Change Plan modal
            CancellationPlanHelper.verify_ink_plans_on_change_plan_modal(page)
            framework_logger.info("All the ink plans on Change Plan modal verified")

            # Select plan on the Change Plan modal on Cancellation Summary page
            CancellationPlanHelper.select_plan_on_change_plan_modal(page, "10")
            framework_logger.info("Change Plan modal validated")

            # Click on back button in the new plan start date modal
            CancellationPlanHelper.click_button_in_the_new_plan_start_date_modal(page, "back")
            framework_logger.info("Choose your new plan start date modal validated")

            # Select plan on the Change Plan modal on Cancellation Summary page
            CancellationPlanHelper.select_plan_on_change_plan_modal(page, "10")
            framework_logger.info("Change Plan modal validated")

            # Click on back button in the new plan start date modal
            CancellationPlanHelper.click_button_in_the_new_plan_start_date_modal(page, "confirm")
            framework_logger.info("Choose your new plan start date modal validated")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")

            # Verify the plan upgraded or downgraded message on Update Plan page
            UpdatePlanHelper.sees_plan_upgraded_or_downgraded_message_on_banner(page, "10")
            framework_logger.info("Plan upgraded or downgraded message on Update Plan page verified")

            framework_logger.info("=== C43390350 - Cancellation - Change Plan modal flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
