from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from helper.ra_base_helper import RABaseHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def expiring_credit_card(stage_callback):
    framework_logger.info("=== C56951781 - Expiring Credit Card flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Set the credit card to expire in the current month and year
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            RABaseHelper.access_link_by_title(page, "Charger::Models::PgsCredential", "Pgs credential")
            GeminiRAHelper.set_almost_expired_credit_card(page)
            framework_logger.info("Credit card expiration date set to current month and year")

            # Event shift - 1 day
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "1")
            framework_logger.info("Event shifted by 1 day")

            # Executes the resque job: CreditCardExpirationCheckJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["CreditCardExpirationCheckJob"])
            framework_logger.info("CreditCardExpirationCheckJob executed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Expand My Account Menu
            side_menu = DashboardSideMenuPage(page)
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")

	        # Verify "Credit card nearing expiration" message displayed on Notification page
            side_menu.click_notifications()
            DashboardHelper.see_notification_on_dashboard(page, "Credit card nearing expiration")         
            framework_logger.info("Verified Credit card nearing expiration message is displayed on Notification page")

	        # Click on the payment_issue link in the Notification events
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "payment_issue", "Notification events")
            framework_logger.info("Accessed payment_issue from Notification events")

            # Sees Event variant equals to payment_credit_card_nearing_expiration-i_ink on Details for Notification event page
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "payment_credit_card_nearing_expiration-i_ink")
            framework_logger.info("Verified Event variant equals to payment_credit_card_nearing_expiration-i_ink on Details for Notification event page")

            framework_logger.info("=== C56951781 - Expiring Credit Card flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
