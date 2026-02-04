from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.cancellation_page import CancellationPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enroll_additional_printer(stage_callback):
    framework_logger.info("=== C38215330 - Enroll Additional Printer started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Make subscription state to subscribed
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status updated to 'subscribed'")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Clicks on enroll or replace a printer link at UCDE
            overview_page.enroll_or_replace_button.click()
            framework_logger.info("Clicked on enroll or replace a printer link at UCDE")

            # Clicks on enroll printer button on the Enroll or Replace Printer modal
            expect(overview_page.enroll_printer_button).to_be_visible(timeout=90000)
            overview_page.enroll_printer_button.click()
            original_page = page
            with page.context.expect_page() as new_page_info:
                page = new_page_info.value
            EnrollmentHelper.accept_terms_of_service(page)

            overview_page = OverviewPage(page)
            framework_logger.info("Clicked on enroll  additional printer button on the Enroll or Replace Printer modal")

            # Selects the Plan 100
            EnrollmentHelper.select_plan_v3(page, 100)
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Plan selected: 100")

            # Sees Connect Printer Later button on pre-enroll page 
            connect_page = ConfirmationPage(page)
            page.wait_for_selector(connect_page.elements.preenroll_continue_button, state="visible", timeout=9000)
            connect_page.preenroll_continue_button.click()
            page.wait_for_load_state("load")
            page.wait_for_selector(connect_page.elements.connect_later_button, timeout=30000)
            connect_page.connect_later_button.click()
            framework_logger.info("Clicked on Connect Printer Later button")

            # Closes finished replacing your printer modal on dashboard
            original_page.bring_to_front()
            page = original_page
            overview_page = OverviewPage(page)

            expect(overview_page.finished_replacing_printer_modal).to_be_visible( timeout=30000)
            overview_page.finished_replacing_printer_modal.click()
            framework_logger.info("Closed finished replacing printer modal")

            # Clicks on Complete Enrollment button
            expect(overview_page.complete_enrollment_button).to_be_visible( timeout=500000)
            overview_page.complete_enrollment_button.click()
            framework_logger.info("Clicked on Complete Enrollment button")

            # Clicks Manage Instant Ink Account button on Consumer Dashboard
            expect(overview_page.connect_later_button).to_be_visible( timeout=30000)
            overview_page.connect_later_button.click()
            expect(overview_page.status_card).to_be_visible(timeout=30000)
            framework_logger.info("Clicked on Manage Instant Ink Account button")

            framework_logger.info("=== C38215330 - Enroll Additional Printer finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
