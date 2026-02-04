from helper.ra_base_helper import RABaseHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def over_monthly_page_amount_notification(stage_callback):
    framework_logger.info("=== C56293015 - Over Monthly Page Amount Notification started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Shift subscription for 32 days and 100 pages charged
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            GeminiRAHelper.manual_retry_until_complete(page=page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            framework_logger.info(f"New billing cycle charged with 100 pages")
            
            # Print 230 additional pages by RTP
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.add_pages_by_rtp(page, "230")
            framework_logger.info(f"Added 230 pages by RTP")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")

            # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")
			
	        # Verify Payment Declined message is displayed on Notification page
            side_menu.click_notifications()
            DashboardHelper.see_notification_on_dashboard(page, "You are over your monthly page")         
            framework_logger.info("Verified Billing update needed message is displayed on Notification page")

            # Click link with text over_availablepages in the Notification events on the Subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "over_availablepages", "Notification events")
            framework_logger.info("Accessed over_availablepages from Notification events")

            # Sees Event variant equals to over_available_pages_not_free_trial_upto_2_times-i_ink and Status equals to complete
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "over_available_pages_not_free_trial_upto_2_times-i_ink")
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Verified Event variant and Status on over_availablepages page")

            framework_logger.info("=== C56293015 - Over Monthly Page Amount Notification finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
