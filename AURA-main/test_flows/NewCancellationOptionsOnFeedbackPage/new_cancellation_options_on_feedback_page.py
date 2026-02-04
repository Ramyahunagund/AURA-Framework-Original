from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.update_plan_page import UpdatePlanPage
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.gemini_ra_helper import GeminiRAHelper
from playwright.sync_api import expect

def new_cancellation_options_on_feedback_page(stage_callback):
    tenant_email = enrollment_ink_web(stage_callback)
    framework_logger.info("=== C44210558 - New cancellation options on feedback page flow started ===")
    
    with PlaywrightManager() as page:
        try:
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            update_plan_page = UpdatePlanPage(page)

            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info(f"Subscription cancellation")
            
            CancellationPlanHelper.select_cancellation_feedback_option(page, feedback_option="I do not print enough", submit= False)
            framework_logger.info(f"Verified I do not print enough message")

            # Keeps the subscription and navigates back to the cancellation feedback page
            DashboardHelper.keep_subscription_and_return_to_feedback_options(page)

            CancellationPlanHelper.select_cancellation_feedback_option(page, feedback_option="The service is too expensive", submit= False)
            framework_logger.info(f"Verified The service is too expensive message")

            # Keeps the subscription and navigates back to the cancellation feedback page
            DashboardHelper.keep_subscription_and_return_to_feedback_options(page)
            
            CancellationPlanHelper.select_cancellation_feedback_option(page, feedback_option="I have not received my shipment", submit= False)
            framework_logger.info(f"Verified I have not received my shipment message")
            
            # Keeps the subscription and navigates back to the cancellation feedback page
            DashboardHelper.keep_subscription_and_return_to_feedback_options(page)

            CancellationPlanHelper.select_cancellation_feedback_option(page, feedback_option="I have replaced my printer", submit= False)
            framework_logger.info(f"Verified I have replaced my printer message")

            # Keeps the subscription and navigates back to the cancellation feedback page
            DashboardHelper.keep_subscription_and_return_to_feedback_options(page)

            CancellationPlanHelper.select_cancellation_feedback_option(page, feedback_option="Wi-Fi issues with my printer", submit= False)
            framework_logger.info(f"Verified Wi-Fi issues with my printer message")

            # Keeps the subscription and navigates back to the cancellation feedback page
            DashboardHelper.keep_subscription_and_return_to_feedback_options(page)

            CancellationPlanHelper.select_cancellation_feedback_option(page, feedback_option="Other", submit= False)
            framework_logger.info(f"Verified Other option is visible")
            
            # Cancellation in progress on overview page
            DashboardHelper.sees_cancellation_in_progress(page)
            framework_logger.info(f"Verified Cancellation in progress on overview page")
            framework_logger.info(f"=== C44210558 - New cancellation options on feedback page flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred: {e}")
            raise e
        finally:
            page.close()
            