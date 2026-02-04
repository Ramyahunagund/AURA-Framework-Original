from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def payment_issues_banners_cpt606(stage_callback):
    framework_logger.info("=== C44476311 - Payment Issues banners CPT-606 flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status updated to 'subscribed'")

            # Shift subscription and add page tally
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            framework_logger.info(f"Event shift by 32 days and page tally set to 100 pages")

            # Update Pgs override response to payment problem
            GeminiRAHelper.update_to_payment_problem(page)
            framework_logger.info(f"PGS override response updated to 'payment problem'")

            # Submit charge on billing cycle
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Submitted charge")

            # See Status code equals to CPT-201 on Billing cycle page
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", "CPT-201")

            # Then rails admin user sees Payment state equals to problem on subscription page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "problem")

            # Set status code from CPT-201 to CPT-606 on billing cycle page
            GeminiRAHelper.click_billing_cycle_by_status(page, "CPT-201")
            GeminiRAHelper.set_status_code(page, "CPT-606")
            framework_logger.info("Set status code to CPT-606")

            # See Status code equals to CPT-606 on Billing cycle page
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", "CPT-606")

            # Open instant ink dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened instant ink dashboard page")

            # See billing issues banner on Overview page
            expect(overview_page.billing_issues_banner).to_be_visible(timeout=60000)
            framework_logger.info("Billing issues banner is visible on Overview page")

            framework_logger.info("=== C44476311 - Payment Issues banners CPT-606 flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e