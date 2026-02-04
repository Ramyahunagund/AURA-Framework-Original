from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.update_plan_helper import UpdatePlanHelper
from pages.update_plan_page import UpdatePlanPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.gemini_ra_helper import GeminiRAHelper
from playwright.sync_api import expect

def new_cancellation_flow_sub_initiate_unsubscribed(stage_callback):
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info("=== C44066058 - New cancellation flow - sub with initiated unsubscribe (Update/Overview Page) started ===")
    
    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)
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

            # Verify subscription state is initiated_unsubscribe
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "initiated_unsubscribe")
            framework_logger.info("Verified subscription state is initiated_unsubscribe")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info("Accessed Overview page")

            # Sees the message "Your subscription will end on" on cancellation banner > Overview page
            DashboardHelper.verify_cancellation_banner_message(page, "Your subscription will end on")
            framework_logger.info("Verified cancellation banner message")

            # Sees the message "Replace cartridges by" on Ink Cartridge Status > Overview page
            DashboardHelper.verify_ink_cartridge_status_message(page, "Replace cartridges by")
            framework_logger.info("Verified ink cartridge status message")

            # Verify the Cancellation in Progress message on Plan Details Card > Overview page
            DashboardHelper.sees_cancellation_in_progress(page)
            framework_logger.info("Verified cancellation in progress message")

            # Access the Keep Subscription modal and click on back button
            DashboardHelper.keep_subscription(page, confirm=False)
            framework_logger.info("Clicked on back button in Keep Subscription modal")

            # Sees the message "Your subscription will end on" on cancellation banner > Overview page
            DashboardHelper.verify_cancellation_banner_message(page, "Your subscription will end on")
            framework_logger.info("Verified cancellation banner message")

            # Verify end date on cancellation banner
            DashboardHelper.verify_end_date_on_cancellation_banner(page)
            framework_logger.info("Verified end date on cancellation banner")

            # Access the Keep Subscription modal and click on back button
            DashboardHelper.keep_subscription(page, confirm=False)
            framework_logger.info("Clicked on back button in Keep Subscription modal")

            # Verify the See Cancellation Timeline button is present
            DashboardHelper.validate_see_cancellation_timeline_feature(page)
            framework_logger.info("Validated See Cancellation Timeline button is present")

            # Keep Subscription
            DashboardHelper.keep_subscription(page)
            framework_logger.info("Clicked on Keep Subscription button")

            # Verify the subscription resumed banner
            DashboardHelper.verify_subscription_resumed_banner(page, "Your Instant Ink subscription has resumed.")
            framework_logger.info("Verified subscription resumed banner")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info(f"Subscription cancellation")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

            # Sees the message "Your subscription will end on" on cancellation banner > Update Plan page
            DashboardHelper.verify_cancellation_banner_message(page, "Your subscription will end on")
            framework_logger.info("Verified cancellation banner message on Update Plan page")

            # Verify end date on cancellation banner on Update Plan page
            DashboardHelper.verify_end_date_on_cancellation_banner(page)
            framework_logger.info("Verified end date on cancellation banner on Update Plan page")

            # Verify the See Cancellation Timeline button is present on Update Plan page
            DashboardHelper.validate_see_cancellation_timeline_feature(page)
            framework_logger.info("Validated See Cancellation Timeline button is present on Update Plan page")

            # Access the Keep Subscription modal and click on back button
            DashboardHelper.keep_subscription(page, confirm=False)
            framework_logger.info("Clicked on back button in Keep Subscription modal on Update Plan page")

            # Access the Keep Subscription modal and confirm resume
            DashboardHelper.keep_subscription(page)
            framework_logger.info("Clicked on Keep Subscription button in Keep Subscription modal on Update Plan page")

            # Verify the subscription resumed banner on Update Plan page
            DashboardHelper.verify_subscription_resumed_banner(page, "Your Instant Ink subscription has resumed.")
            framework_logger.info("Verified subscription resumed banner on Update Plan page")
            
            framework_logger.info(f"=== C44066058 - New cancellation flow - sub with initiated unsubscribe (Update/Overview Page) finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred: {e}")
            raise e
        finally:
            page.close()
