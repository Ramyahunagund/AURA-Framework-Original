from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.printer_selection_page import PrinterSelectionPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def unsubscribed_enroll_another_printer_link_after15_min(stage_callback):
    framework_logger.info("=== C56291746 - Unsubscribed Enroll Another Printer link after 15 min flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
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
            CancellationPlanHelper.select_cancellation_feedback_option(page)
            framework_logger.info("Subscription cancellation initiated")

            # Shift 32 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            framework_logger.info("Shifted 32 days")

            # Execute SubscriptionUnsubscriberJob
            GeminiRAHelper.complete_jobs(page, ["SubscriptionUnsubscriberJob"])
            framework_logger.info("Executed SubscriptionUnsubscriberJob")

            # Verify the subscription state is unsubscribed
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            for attempt in range(10):
                try:
                    GeminiRAHelper.verify_rails_admin_info(page, "State", "unsubscribed")
                    break
                except Exception as e:
                    if attempt == 9: 
                        raise e
                    page.reload()

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Wait more than 15 minutes
            framework_logger.info("Waiting for 15 minutes to let the session expire...")
            time.sleep(930)
            framework_logger.info("Waited for 15 minutes")

            # Click on enroll another printer button at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll another printer button at UCDE")

            # Click login button in the session expired modal on the Smart Dashboard
            DashboardHelper.login_on_security_session_expired(page, tenant_email)
            framework_logger.info("Logged in the session expired modal")

            # See the Overview page
            expect(overview_page.plan_details_card).to_be_visible(timeout=90000)
            framework_logger.info("Verified the Overview page")

            # Click on enroll another printer button at UCDE
            with page.context.expect_page() as new_page_info:
                overview_page.enroll_or_replace_button.click()
                new_tab = new_page_info.value
            framework_logger.info("Clicked on enroll another printer button at UCDE")

            # Sees the Printer Selection page on the Smart Dashboard
            EnrollmentHelper.accept_terms_of_service(new_tab)
            printer_selection_page = PrinterSelectionPage(new_tab)
            expect(printer_selection_page.printer_selection_page).to_be_visible(timeout=90000)

            framework_logger.info("=== C56291746 - Unsubscribed Enroll Another Printer link after 15 min flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
