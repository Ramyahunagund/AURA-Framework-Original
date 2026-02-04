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

def cancellation_feedback_page(stage_callback):
    framework_logger.info("=== C43369722 - Cancellation feedback page flow started ===")
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
            cancellation_page.continue_button.click()
            framework_logger.info("User cancelled subscription")

            # Verify first section on cancellation feedback page
            CancellationPlanHelper.verify_first_section_on_cancellation_feedback_page(page)
            framework_logger.info("First section on cancellation feedback page verified")

            # Verify radio buttons on cancellation feedback page
            CancellationPlanHelper.verify_radio_buttons_on_cancellation_feedback_page(page)
            framework_logger.info("Radio buttons on cancellation feedback page verified")

            # Verify 'Change your mind' section
            CancellationPlanHelper.verify_change_your_mind_section(page)
            framework_logger.info("Verified the 'Change your mind' section on Cancellation Timeline page")

            # Click on 'Restore Your Subscription' link
            CancellationPlanHelper.click_on_link_on_cancellation_page(page, "Keep Subscription")
            framework_logger.info("Clicked on 'Keep Subscription' link on Cancellation Timeline page")

            # Click on 'Back' button on Resume Subscription modal
            CancellationPlanHelper.click_on_button_on_resume_modal(page, "Back")
            framework_logger.info("Clicked on 'Back' button on Resume Subscription modal")

            # Click on 'Restore Your Subscription' link
            CancellationPlanHelper.click_on_link_on_cancellation_page(page, "Keep Subscription")
            framework_logger.info("Clicked on 'Keep Subscription' link on Cancellation Timeline page")

            # Click on 'Resume' button on Resume Subscription modal
            CancellationPlanHelper.click_on_button_on_resume_modal(page, "Resume")
            framework_logger.info("Clicked on 'Resume' button on Resume Subscription modal")

            # Verify the subscription state in Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed")
            framework_logger.info("Verified subscription state is subscribed")

            # Access Overview page
            DashboardHelper.access(page, tenant_email)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page") 

            # Cancel the subscription
            UpdatePlanHelper.cancellation_subscription(page)
            cancellation_page.continue_button.click()
            framework_logger.info("User cancelled subscription")

            # Click on 'Transfer This Subscription' link
            CancellationPlanHelper.click_on_link_on_cancellation_page(page, "Transfer This Subscription")
            framework_logger.info("Clicked on 'Transfer This Subscription' link on Cancellation Timeline page")

            # Click on 'Back' button on Resume Subscription modal
            CancellationPlanHelper.click_on_button_on_resume_modal(page, "Back")
            framework_logger.info("Clicked on 'Back' button on Resume Subscription modal")

            # Click on 'Transfer This Subscription' link
            CancellationPlanHelper.click_on_link_on_cancellation_page(page, "Transfer This Subscription")
            framework_logger.info("Clicked on 'Transfer This Subscription' link on Cancellation Timeline page")

            # Click on 'Resume' button on Transfer This Subscription modal
            with page.context.expect_page() as new_page_info:
                CancellationPlanHelper.click_on_button_on_resume_modal(page, "Resume")
            framework_logger.info("Clicked on 'Resume' button on Transfer This Subscription modal")
            new_page = new_page_info.value

            # Verifies and close the Printer Replacement page
            DashboardHelper.sees_printer_replacement_page(new_page)
            new_page.close()
            framework_logger.info("Verified Printer Replacement page")    

            # Verify the subscription resumed banner
            DashboardHelper.verify_subscription_resumed_banner(page, "Your Instant Ink subscription has resumed.")
            framework_logger.info("Verified subscription resumed banner")

            # Verify the subscription state in Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed")
            framework_logger.info("Verified subscription state is subscribed")

            # Access Overview page
            DashboardHelper.access(page, tenant_email)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")  

            # Cancel the subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("User cancelled subscription") 

            # Select a feedback option for subscription
            CancellationPlanHelper.select_cancellation_feedback_option(page)
            framework_logger.info("Subscription cancellation initiated")

            # See cancellation in progress on overview page
            DashboardHelper.sees_cancellation_in_progress(page)
            framework_logger.info("Verified cancellation in progress on Overview page")

            # Refer a friend card not appear on Overview page
            expect(overview_page.raf_card).not_to_be_visible()
            framework_logger.info(f"Verified that the refer a friend card does not appear on the Overview page")

            # Verify the subscription state in Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "initiated_unsubscribe")
            framework_logger.info("Verified subscription state is initiated_unsubscribe")

            # Access Overview page
            DashboardHelper.access(page, tenant_email)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")   

            # Click on keep enrollment button and confirm on Overview page
            overview_page.keep_enrollment_button.click()
            expect(overview_page.keep_enrollment_confirmation).to_be_visible()
            overview_page.keep_enrollment_confirmation.click()
            framework_logger.info("Clicked on keep enrollment button in the plan details card on Overview page")

            # Cancel the subscription
            UpdatePlanHelper.cancellation_subscription(page)
            cancellation_page.continue_button.click()
            framework_logger.info("User cancelled subscription")

            # Verify the submit feedback button is disabled and click 'Return to Account' button
            CancellationPlanHelper.sees_submit_feedback_button(page, enabled=False)
            cancellation_page.return_to_account_button.click()
            framework_logger.info("Verified submit feedback button is disabled")

            # See cancellation in progress on overview page
            DashboardHelper.sees_cancellation_in_progress(page)
            framework_logger.info("Verified cancellation in progress on Overview page")

            # Refer a friend card not appear on Overview page
            expect(overview_page.raf_card).not_to_be_visible()
            framework_logger.info(f"Verified that the refer a friend card does not appear on the Overview page")

            # Verify the subscription state in Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "initiated_unsubscribe")
            framework_logger.info("Verified subscription state is initiated_unsubscribe")

            framework_logger.info("=== C43369722 - Cancellation feedback page flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e