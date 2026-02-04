from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from core.playwright_manager import PlaywrightManager
from pages.overview_page import OverviewPage
from core.settings import framework_logger
from playwright.sync_api import expect
import urllib3
import traceback
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pages.cancellation_page import CancellationPage

def cancellation_summary_flow_validation(stage_callback):
    framework_logger.info("=== C40797059,40797116 - Cancellation Summary Page + no text below printer info flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)


        try:
            #Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed_no_pens")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click on Cancel Instant Ink on Overview page
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            #verify the title  as "Cancel Instant Ink for this printer".
            CancellationPlanHelper.verify_cancellation_summary_page_title(page)
            framework_logger.info("Verified the title as 'Cancel Instant Ink for this printer' on Cancellation Summary Page")

            # # Verify printer information on Cancellation Summary Page
            expect(cancellation_page.printer_img).to_be_visible(timeout=90000)
            expect(cancellation_page.printer_info_name).to_be_visible()
            expect(cancellation_page.printer_info_serial).to_be_visible()
            framework_logger.info("Verified printer information on Cancellation Summary Page")

            # Sees cancellation image on Cancellation Summary Page
            expect(cancellation_page.cancellation_summary_image).to_be_visible()
            framework_logger.info("Verified cancellation image on Cancellation Summary Page")

            #Verify there is no text displayed below the subscription information section
            empty_section=cancellation_page.below_subscription_info
            expect(empty_section).to_have_text("")
            framework_logger.info("Verified that there is no text below the subscription information.")

            #Verify the "Confirm Cancellation" button and "Keep Instant Ink" button are displayed well.
            confirm_cancellation_button = cancellation_page.confirm_cancellation_button
            expect(confirm_cancellation_button).to_be_visible()
            assert confirm_cancellation_button.is_enabled()
            framework_logger.info("Verified 'Confirm Cancellation' button is displayed and enabled on Cancellation Summary Page")
            keep_enrollment_button = cancellation_page.keep_enrollment_button
            expect(keep_enrollment_button).to_be_visible()
            assert keep_enrollment_button.is_enabled()




            framework_logger.info("=== C40797059,40797116 - Cancellation Summary Page + no text below printer info modal close in change plan flow completed ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e