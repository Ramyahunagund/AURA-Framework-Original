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

def cancellation_timeline_page(stage_callback):
    framework_logger.info("=== C43197789 - Cancellation Timeline page flow started ===")
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

            # Verify Cancellation Timeline page
            CancellationPlanHelper.verify_the_cancellation_timeline_page(page)
            framework_logger.info("Verified the Cancellation Timeline page")

            # Verify the steps on Cancellation Timeline page
            CancellationPlanHelper.verify_the_steps_on_cancellation_timeline_page(page)
            framework_logger.info("Verified the steps on Cancellation Timeline page")

            # Verify 'Change your mind' section
            CancellationPlanHelper.verify_change_your_mind_section(page)
            framework_logger.info("Verified the 'Change your mind' section on Cancellation Timeline page")

            # Validate Shop HP Ink button on Cancellation Timeline page
            CancellationPlanHelper.validate_buttons_on_cancellation_timeline_page(page, "Shop HP Ink")
            framework_logger.info("Verified the 'Shop HP Ink' button on Cancellation Timeline page")

            # Validate Request Free Recycling Materials button on Cancellation Timeline page
            CancellationPlanHelper.validate_buttons_on_cancellation_timeline_page(page, "Request Free Recycling Materials")
            framework_logger.info("Verified the 'Request Free Recycling Materials' button on Cancellation Timeline page")

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

            # Go to Cancellation Timeline page
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("Navigated to Cancellation Timeline page")

            # Click on 'Restore Your Subscription' link
            CancellationPlanHelper.click_on_link_on_cancellation_page(page, "Restore Your Subscription")
            framework_logger.info("Clicked on 'Restore Your Subscription' link on Cancellation Timeline page")

            # Click on 'Back' button on Resume Subscription modal
            CancellationPlanHelper.click_on_button_on_resume_modal(page, "Back")
            framework_logger.info("Clicked on 'Back' button on Resume Subscription modal")

            # Click on 'Restore Your Subscription' link
            CancellationPlanHelper.click_on_link_on_cancellation_page(page, "Restore Your Subscription")
            framework_logger.info("Clicked on 'Restore Your Subscription' link on Cancellation Timeline page")

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

            # Go to Cancellation Timeline page
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("Navigated to Cancellation Timeline page")

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

            # Go to Cancellation Timeline page and cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("Navigated to Cancellation Timeline page and cancelled subscription")
            framework_logger.info("=== C43197789 - Cancellation Timeline page flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
