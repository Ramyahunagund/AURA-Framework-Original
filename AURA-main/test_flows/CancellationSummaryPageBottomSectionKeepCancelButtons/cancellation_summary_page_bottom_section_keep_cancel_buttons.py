from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.cancellation_page import CancellationPage
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancellation_summary_page_bottom_section_keep_cancel_buttons(stage_callback):
    framework_logger.info("=== C42613640 - Cancellation Summary Page + Bottom Section + Keep/Cancel Buttons flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)
        try:
            # Verify subscription state is subscribed_no_pens
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed_no_pens")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click on Cancel Instant Ink on Overview page
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")
            
            # Verify printer information on Cancellation Summary Page
            expect(cancellation_page.printer_img).to_be_visible(timeout=90000)
            expect(cancellation_page.printer_info_name).to_be_visible()
            expect(cancellation_page.printer_info_serial).to_be_visible()
            framework_logger.info("Verified printer information on Cancellation Summary Page")

            # Sees cancellation image on Cancellation Summary Page
            expect(cancellation_page.cancellation_summary_image).to_be_visible()
            framework_logger.info("Verified cancellation image on Cancellation Summary Page")

            # Doesn't see cancellation summary information on Cancellation Summary Page
            expect(cancellation_page.subscribed_info).not_to_be_visible()
            framework_logger.info("Verified that cancellation summary information is not visible on Cancellation Summary Page")

            # Verify bottom section's title on Cancellation Summary Page
            expect(cancellation_page.bottom_section_title).to_be_visible()
            framework_logger.info("Verified bottom section's title on Cancellation Summary Page")

            # Verify Have your printing needs changed? section on Cancellation Summary Page
            CancellationPlanHelper.verify_bottom_section(page, "Have your printing needs changed?")
            framework_logger.info("Verified 'Have your printing needs changed?' section on Cancellation Summary Page")

            # Verify Did you get a new printer? section on Cancellation Summary Page
            CancellationPlanHelper.verify_bottom_section(page, "Did you get a new printer?")
            framework_logger.info("Verified 'Did you get a new printer?' section on Cancellation Summary Page")

            # Verify Have questions or need help? section on Cancellation Summary Page
            CancellationPlanHelper.verify_bottom_section(page, "Have questions or need help?")
            framework_logger.info("Verified 'Have questions or need help?' section on Cancellation Summary Page")

            # Click to keep the subscription on Cancellation Summary Page
            cancellation_page.keep_enrollment_button.click()
            framework_logger.info("Clicked to keep the subscription on Cancellation Summary Page")

            # Click on Cancel Instant Ink on Overview page
            overview_page.plan_details_card.wait_for(timeout=90000)
            overview_page.cancel_instant_ink.click()
            framework_logger.info("Clicked on Cancel Instant Ink on Overview page")

            # Click to confirm the cancellation on Cancellation Summary Page
            cancellation_page.confirm_cancellation_button.click()
            framework_logger.info("Clicked to confirm the cancellation on Cancellation Summary Page")
            overview_page.plan_details_card.wait_for(timeout=90000)

            # Verify subscription state is obsolete
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "obsolete")

            framework_logger.info("=== C42613640 - Cancellation Summary Page + Bottom Section + Keep/Cancel Buttons flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
