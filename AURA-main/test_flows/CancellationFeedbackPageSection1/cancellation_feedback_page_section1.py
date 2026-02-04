from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.cancellation_page import CancellationPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancellation_feedback_page_section1(stage_callback):
    framework_logger.info("=== C40797111,C40797109,40797103,40797102,40797104,40797107,40797105 - Cancellation feedback page section1 flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)
        try:
            # Move subscription to subscribed state if needed
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription moved to subscribed state if needed")

            # User signs into HP Smart and opens Smart Dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("User signs into HP Smart and opens Smart Dashboard page")

            # Cancel the subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("User cancelled subscription")

            # Verify first section on cancellation feedback page
            CancellationPlanHelper.verify_first_section_on_cancellation_feedback_page(page)
            framework_logger.info("First section on cancellation feedback page verified")

            # Verify radio buttons on cancellation feedback page
            CancellationPlanHelper.verify_radio_buttons_on_cancellation_feedback_page(page)
            framework_logger.info("Radio buttons on cancellation feedback page verified")

            # Verify there is an animation displayed well next to the title.
            stage_callback("context_name", page, screenshot_only=True)

            #Verify there are 6 options with cancellation reasons displayed and none of them is selected
            CancellationPlanHelper.verify_radio_buttons_on_cancellation_feedback_page(page)
            CancellationPlanHelper.verify_feeback_radio_buttons_default_not_selected(page)
            framework_logger.info("Radio buttons on cancellation feedback page verified")

            #Verify there is a text box to the "other" option and the text box is disabled.
            CancellationPlanHelper.verify_feedback_text_box_disabled(page)
            framework_logger.info("Verified the text box to the 'other' option is disabled")

            # Verify the submit feedback button is disabled and click 'Return to Account' button
            CancellationPlanHelper.sees_submit_feedback_button(page, enabled=False)
            cancellation_page.return_to_account_button.click()
            framework_logger.info("Verified submit feedback button is disabled")

            # only one option can be selected at same time.
            CancellationPlanHelper.verify_radio_buttons_exclusive_and_default(page)
            framework_logger.info("Verified only one option can be selected at same time")

            #Select the option "The service is too expensive or I have been charged for additional pages".
            CancellationPlanHelper.select_cancellation_feedback_option(page,feedback_option="The service is too expensive", submit=False)
            framework_logger.info(f"Verified The service is too expensive message")
            CancellationPlanHelper.verify_user_redirected_return_to_overview(page)

            # Keeps the subscription and navigates back to the cancellation feedback page
            DashboardHelper.keep_subscription_and_return_to_feedback_options(page)
            CancellationPlanHelper.select_cancellation_feedback_option(page,feedback_option="I have not received my shipment",submit=False)
            framework_logger.info(f"Verified I have not received my shipment message")
            CancellationPlanHelper.verify_user_redirected_return_to_overview(page)

            # Keeps the subscription and navigates back to the cancellation feedback page
            DashboardHelper.keep_subscription_and_return_to_feedback_options(page)
            CancellationPlanHelper.select_cancellation_feedback_option(page,feedback_option="I have replaced my printer",submit=False)
            framework_logger.info(f"Verified I have not received my shipment message")
            CancellationPlanHelper.verify_user_redirected_return_to_overview(page)

            # Keeps the subscription and navigates back to the cancellation feedback page
            DashboardHelper.keep_subscription_and_return_to_feedback_options(page)
            CancellationPlanHelper.select_cancellation_feedback_option(page,feedback_option="Wi-Fi issues with my printer",submit=False)
            framework_logger.info(f"Verified I have not received my shipment message")
            CancellationPlanHelper.verify_user_redirected_return_to_overview(page)

            # Keeps the subscription and navigates back to the cancellation feedback page
            DashboardHelper.keep_subscription_and_return_to_feedback_options(page)
            CancellationPlanHelper.select_cancellation_feedback_option(page, feedback_option="Other", submit=False)
            framework_logger.info(f"Verified Other option is visible")
            CancellationPlanHelper.verify_user_redirected_return_to_overview(page)

            framework_logger.info("=== C40797111,C40797109,40797103,40797102,40797104,40797107,40797105 - Cancellation feedback page section1 flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e