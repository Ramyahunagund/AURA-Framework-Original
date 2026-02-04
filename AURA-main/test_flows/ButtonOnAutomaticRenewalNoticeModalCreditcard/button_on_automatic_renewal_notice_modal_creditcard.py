import time
from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from pages.overview_page import OverviewPage
from pages.thank_you_page import ThankYouPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def button_on_automatic_renewal_notice_modal_creditcard(stage_callback):
    framework_logger.info("=== C44874599 - Button on Automatic renewal notice modal - with subscription - Credit card started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)

            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Clicks the Enroll Another Printer link on the dashboard
            overview_page.enroll_or_replace_button.click()

            page.wait_for_timeout(3000)
            with page.context.expect_page() as new_page_info:
                overview_page.enroll_printer_button.click()
            new_tab = new_page_info.value
            new_tab.bring_to_front()
            new_tab.wait_for_load_state("networkidle", timeout=120000)
            framework_logger.info("Switched to last tab")

            EnrollmentHelper.accept_terms_of_service(new_tab)

            # Selects the Plan 100
            EnrollmentHelper.select_plan_v3(new_tab, plan_value=100)
            framework_logger.info(f"Plan selected: 100")

            # Clicks continue button and waits more than 15 minutes than confirm terms of service
            confirmation_page = ConfirmationPage(new_tab)
            thank_you_page = ThankYouPage(new_tab)
            confirmation_page.wait.continue_enrollment_button().click(timeout=120000)
            
            time.sleep(920) 
            framework_logger.info(f"Waited for 15 minutes and 20 seconds to trigger the automatic renewal notice modal")
            confirmation_page.terms_agreement_checkbox.wait_for(state="visible", timeout=60000)
            confirmation_page.terms_agreement_checkbox.check(force=True)
            confirmation_page.enroll_button.click()
            thank_you_page.continue_button.wait_for(state="visible", timeout=60000)
            framework_logger.info(f"Clicked on Continue button on Thank You page")

            framework_logger.info("=== C44874599 - Button on Automatic renewal notice modal - with subscription - Credit card finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
