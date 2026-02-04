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

def cancellation_summary_page_top_section(stage_callback):
    framework_logger.info("=== C40797070 - Cancellation Summary Page top Section + last day bc flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click on Cancel Instant Ink on Overview page
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            # verify the title  as "Cancel Instant Ink for this printer".
            CancellationPlanHelper.verify_cancellation_summary_page_title(page)
            framework_logger.info(
                "Verified the title as 'Cancel Instant Ink for this printer' on Cancellation Summary Page")

            # # Verify printer information on Cancellation Summary Page
            expect(cancellation_page.printer_img).to_be_visible(timeout=90000)
            expect(cancellation_page.printer_info_name).to_be_visible()
            expect(cancellation_page.printer_info_serial).to_be_visible()
            framework_logger.info("Verified printer information on Cancellation Summary Page")

            # Sees cancellation image on Cancellation Summary Page
            expect(cancellation_page.cancellation_summary_image).to_be_visible()
            framework_logger.info("Verified cancellation image on Cancellation Summary Page")

            # Verify a text with the date for the last day of this billing cycle is displayed well.
            full_text = cancellation_page.last_day_billing_cycle_text.text_content().strip()
            print("full text:", full_text)
            last_day_bc = full_text.split('.')[0] + '.'  # Extract the relevant sentence
            print("Last day of billing cycle text:", last_day_bc)
            date_match = re.search(r"[A-Za-z]{3} \d{2}, \d{4}", last_day_bc)
            if date_match:
                extracted_date = date_match.group()
                print("Extracted date:", extracted_date)
            else:
                raise AssertionError("Date not found in text")
            expected_text = f"If you cancel today, your last day to print with Instant Ink cartridges will be {extracted_date}."
            assert last_day_bc == expected_text, f"Expected: {expected_text}, but got: {last_day_bc}"
            framework_logger.info("Verified the text with the date for the last day of this billing cycle on Cancellation Summary Page")

            # Verify the "Confirm Cancellation" button and "Keep Instant Ink" button are displayed well.
            confirm_cancellation_button = cancellation_page.confirm_cancellation_button
            expect(confirm_cancellation_button).to_be_visible()
            assert confirm_cancellation_button.is_enabled()
            framework_logger.info(
                "Verified 'Confirm Cancellation' button is displayed and enabled on Cancellation Summary Page")
            keep_enrollment_button = cancellation_page.keep_enrollment_button
            expect(keep_enrollment_button).to_be_visible()
            assert keep_enrollment_button.is_enabled()

            "=== C40797116 - Modal close in Cancellation Summary Page flow started ==="
            # Click the "Return to Cancellation" button on change plan modal
            CancellationPlanHelper.clicking_back_button_in_summary(page)
            DashboardHelper.verify_and_close_change_plan_modal(page)
            framework_logger.info(f"Clicked the Return to Cancellation button on change plan modal")

            # Click the "X" button on change plan modal
            DashboardHelper.close_change_plan_modal_x(page)
            framework_logger.info(f"Clicked the X button on change plan modal")

            framework_logger.info("=== C40797070 - Cancellation Summary Page top Section + last day bc flow completed ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e