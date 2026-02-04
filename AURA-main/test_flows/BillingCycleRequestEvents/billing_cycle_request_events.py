from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_cycle_request_events(stage_callback):
    framework_logger.info("=== C40643673 - Billing Cycle Request Events flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Charge a new billing cycle with 100 pages
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 100 pages")

            # Click link with text PEGASUS-SUCCESS in the Request events on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "PEGASUS-SUCCESS", "Request events")
            framework_logger.info(f"Clicked link with text PEGASUS-SUCCESS in the Request events on the Billing cycle page")

            # See Response status equals to PEGASUS-SUCCESS on request event page
            GeminiRAHelper.verify_rails_admin_info(page, "Response status", "PEGASUS-SUCCESS")

            # See Charge amount cents to be positive on request event page
            GeminiRAHelper.verify_field_is_positive(page, "Charge amount cents")
            framework_logger.info(f"Verified field Charge amount cents is positive")

            # See Payment engine equals to pegasus on request event page
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", "pegasus")

            framework_logger.info("=== C40643673 - Billing Cycle Request Events flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
