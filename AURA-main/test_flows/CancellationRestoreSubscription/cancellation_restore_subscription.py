from pages.cancellation_page import CancellationPage
from pages.cancellation_timeline_page import CancellationTimelinePage
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
from pages.overview_page import OverviewPage

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def cancellation_restore_subscription(stage_callback):
    framework_logger.info("=== C40797086 - Cancellation Timeline page visualization flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        cancellation_page = CancellationPage(page)
        cancellation_timeline_page = CancellationTimelinePage(page)
        overview_page = OverviewPage(page)

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

            # Go to Cancellation Timeline page
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("Navigated to Cancellation Timeline page")

            # Click on 'Restore Your Subscription' link
            CancellationPlanHelper.click_on_link_on_cancellation_page(page, "Restore Your Subscription")
            framework_logger.info("Clicked on 'Restore Your Subscription' link on Cancellation Timeline page")

            #Verify the "Confirm subscription resume" modal is displayed well
            expect(cancellation_page.confirm_subscription_resume_modal).to_be_visible(timeout=30000)

            #Verify the "Back" button and "Resume" button are displayed well.
            expect(cancellation_timeline_page.resume_instant_ink_subscription).to_be_visible(timeout=30000)
            expect(cancellation_timeline_page.back_to_cancel_confirmation).to_be_visible(timeout=30000)

            #Verify the modal should be closed and it stays on the Cancellation Timeline page.
            CancellationPlanHelper.click_on_button_on_resume_modal(page, "Back")
            framework_logger.info("Clicked on 'Back' button on Resume Subscription modal")
            expect(cancellation_timeline_page.header_title).to_be_visible()

            #Click the Restore your Subscription link
            CancellationPlanHelper.click_on_link_on_cancellation_page(page, "Restore Your Subscription")
            CancellationPlanHelper.click_on_button_on_resume_modal(page, "Resume")
            framework_logger.info("Clicked on 'Resume' button on Resume Subscription modal")
            expect(overview_page.page_title).to_be_visible(timeout=70000)
            expect(overview_page.subscription_resumed_banner).to_be_visible(timeout=70000)
            framework_logger.info("Verified subscription resumed banner is displayed on Overview page")


            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed")
            framework_logger.info("Verified subscription state is subscribed")


            framework_logger.info("=== C40797086 - Cancellation Timeline page visualization flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")