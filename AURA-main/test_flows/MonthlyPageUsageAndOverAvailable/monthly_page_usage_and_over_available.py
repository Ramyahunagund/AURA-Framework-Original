from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from helper.ra_base_helper import RABaseHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from core.settings import framework_logger 
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def monthly_page_usage_and_over_available(stage_callback):
    framework_logger.info("=== C50492630 - Monthly page usage and over available flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page: 
        side_menu = DashboardSideMenuPage(page)     
        try:
            # Move subscription to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")
			
            # Pause plan for 2 months on Overview page
            DashboardHelper.pause_plan(page, 2)
            framework_logger.info(f"Paused plan for 2 months on Overview page")	       

 	        # Billing cycle charge (shift 31 and page tally 100)
            GeminiRAHelper.access(page)            
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            GeminiRAHelper.manual_retry_until_complete(page=page)
            framework_logger.info(f"Billing cycle charged")

            # Print 9 additional pages by RTP           
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.add_pages_by_rtp(page, "9")
            framework_logger.info(f"Added 9 pages by RTP")

            # Access Dashboard
            DashboardHelper.access(page)
            framework_logger.info(f"Accessed Dashboard")
			
	        # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")
			
	        # Verify "Monthly Page usage update" message displayed on Notification page
            side_menu.click_notifications()
            DashboardHelper.see_notification_on_dashboard(page, "Monthly Page usage update")         
            framework_logger.info("Verified Monthly Page usage update message displayed on Notification page")

            # Click link with text near_availablepages in the Notification events
            GeminiRAHelper.access(page)            
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "near_availablepages", "Notification events")
            framework_logger.info(f"Accessed near_availablepages in Notification events")

            # Sees Event variant equals to near_pages_pause-i_ink on Details for Notification event page
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "near_pages_pause-i_ink")
            framework_logger.info("Verified Event variant equals to near_pages_pause-i_ink on Details for Notification event page")

            # Sees Status equals to complete on near_availablepages page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Verified Status equals to complete on near_availablepages page")

            # Print 6 additional pages by RTP           
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.add_pages_by_rtp(page, "6")
            framework_logger.info(f"Added 6 pages by RTP")
		
            # Access Dashboard
            DashboardHelper.access(page)
            framework_logger.info(f"Accessed Dashboard")
			
	        # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")
			
	        # Verify "Over Available Pages" message displayed on Notification page
            side_menu.click_notifications()
            DashboardHelper.see_notification_on_dashboard(page, "Over Available Pages")         
            framework_logger.info("Verified Over Available Pages message displayed on Notification page")

            # Click link with text over_availablepages in the Notification events
            GeminiRAHelper.access(page)            
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "over_availablepages", "Notification events")
            framework_logger.info(f"Accessed near_availablepages")

            # Sees Event variant equals to over_pages_pause-i_ink on Details for Notification event page
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "over_pages_pause-i_ink")
            framework_logger.info("Verified Event variant equals to over_pages_pause-i_ink on Details for Notification event page")

            # Sees Status equals to complete on near_availablepages page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")
            framework_logger.info("Verified Status equals to complete on over_availablepages page")

            framework_logger.info("=== C50492630 - Monthly page usage and over available flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close
        