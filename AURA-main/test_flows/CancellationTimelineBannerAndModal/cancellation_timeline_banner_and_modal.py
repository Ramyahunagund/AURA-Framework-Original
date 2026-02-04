from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancellation_timeline_banner_and_modal(stage_callback):
    framework_logger.info("=== C43932771 - Cancellation timeline banner and modal flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Go to Cancellation Timeline page
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("Navigated to Cancellation Timeline page")

            # Access Overview page
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")    

            # Verify the Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.verify_the_cancellation_timeline_modal(page)
            framework_logger.info("Verified the Cancellation Timeline modal on Overview page")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")

            # Verify the Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.verify_the_cancellation_timeline_modal(page)
            framework_logger.info("Verified the Cancellation Timeline modal on Update Plan page")

            # Access Print History page
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Verify the Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.verify_the_cancellation_timeline_modal(page)
            framework_logger.info("Verified the Cancellation Timeline modal on Print History page")

            # Access Shipment Tracking page
            side_menu.click_shipment_tracking()
            framework_logger.info("Accessed Shipment Tracking page")

            # Verify the Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.verify_the_cancellation_timeline_modal(page)
            framework_logger.info("Verified the Cancellation Timeline modal on Shipment Tracking page")

            # Validate Shop HP Ink button on Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.validate_buttons_on_cancellation_timeline_page(page, "Shop HP Ink")
            framework_logger.info("Verified the 'Shop HP Ink' button on Cancellation Timeline modal")

            # Validate Request Free Recycling Materials button on Cancellation Timeline modal
            CancellationPlanHelper.validate_buttons_on_cancellation_timeline_page(page, "Request Free Recycling Materials")
            framework_logger.info("Verified the 'Request Free Recycling Materials' button on Cancellation Timeline modal")

            # Validate Close button on Cancellation Timeline modal
            CancellationPlanHelper.validate_buttons_on_cancellation_timeline_page(page, "Close")
            framework_logger.info("Verified the 'Close' button on Cancellation Timeline modal")

            # Verify the first step on Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.verify_steps_on_cancellation_timeline_modal(page, "First step")
            framework_logger.info("Verified the first step on Cancellation Timeline modal")

            # Shift subscription for 2 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "2")
            framework_logger.info("Shifted subscription for 2 days")

            # Access Overview page
            DashboardHelper.access(page, tenant_email)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page") 

            # Verify the Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.verify_the_cancellation_timeline_modal(page)
            framework_logger.info("Verified the Cancellation Timeline modal on Overview page")

            # Verify the first step on Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.verify_steps_on_cancellation_timeline_modal(page, "First step")
            framework_logger.info("Verified the first step on Cancellation Timeline modal")

            # Verify the second step on Cancellation Timeline modal
            CancellationPlanHelper.verify_steps_on_cancellation_timeline_modal(page, "Second step")
            framework_logger.info("Verified the second step on Cancellation Timeline modal")
            
            # Shift subscription for 28 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "28")
            framework_logger.info("Shifted subscription for 28 days")

            # Access Overview page
            DashboardHelper.access(page, tenant_email)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page") 

            # Verify the Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.verify_the_cancellation_timeline_modal(page)
            framework_logger.info("Verified the Cancellation Timeline modal on Overview page")

            # Verify the second step on Cancellation Timeline modal
            CancellationPlanHelper.click_see_cancellation_timeline_button_on_banner(page)
            CancellationPlanHelper.verify_steps_on_cancellation_timeline_modal(page, "Second step")
            framework_logger.info("Verified the second step on Cancellation Timeline modal")

            # Verify the third step on Cancellation Timeline modal
            CancellationPlanHelper.verify_steps_on_cancellation_timeline_modal(page, "Third step")
            framework_logger.info("Verified the third step on Cancellation Timeline modal")

            # Verify the fourth step on Cancellation Timeline modal
            CancellationPlanHelper.verify_steps_on_cancellation_timeline_modal(page, "Fourth step")
            framework_logger.info("Verified the fourth step on Cancellation Timeline modal")
            
            framework_logger.info("=== C43932771 - Cancellation timeline banner and modal flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
