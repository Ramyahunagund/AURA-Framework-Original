from helper.enrollment_helper import EnrollmentHelper
from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from test_flows.EnrollmentOOBE.enrollment_oobe import enrollment_oobe
import test_flows_common.test_flows_common as common
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def paas_cards_on_overview_page(stage_callback):
    framework_logger.info("=== C44513493 - PaaS cards on Overview Page flow started ===")
    tenant_email = create_ii_subscription(stage_callback)
    common.setup()
    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.event_shift(page, "732", force_billing=False)
            framework_logger.info("Subscription moved to subscribed state and free months removed")

            # Access Smart Dashboard and skip preconditions
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")

            subscription_id = overview_page.wait.subscription_id().text_content().strip().split()[-1]
            framework_logger.info(f"Subscription ID: {subscription_id}")

            expect(overview_page.support_card).to_be_visible()
            expect(overview_page.support_card_icon).to_be_visible()
            expect(overview_page.support_card_title).to_be_visible()
            expect(overview_page.support_card_description).to_be_visible()
            expect(overview_page.support_card_link).to_be_visible()

            with page.context.expect_page() as new_page_info:
                overview_page.support_card_link.click()
                new_tab = new_page_info.value

            assert "support.hp.com" in new_tab.url, "Support link did not navigate to the expected URL"
            framework_logger.info("Support link navigates to the expected URL")
            new_tab.close()
            page.bring_to_front()
            
            DashboardHelper.pass_validation(page)

            common.create_and_claim_virtual_printer()
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            
            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)

            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")

            # Change the subscription
            DashboardHelper.select_printer_by_serial_number(page, common._printer_created[0].entity_id)

            # assert that the subscription is the same as before
            new_subscription_id = overview_page.subscription_id.text_content().strip().split()[-1]
            assert new_subscription_id == subscription_id, "Subscription ID changed after switching printers"
            framework_logger.info(f"Subscription ID: {new_subscription_id}")

            DashboardHelper.pass_validation(page)

            # Change the subscription
            DashboardHelper.select_printer_by_serial_number(page, common._printer_created[-1].entity_id)

            expect(overview_page.paas_banner).not_to_be_visible()
            expect(overview_page.paas_image).not_to_be_visible()
            expect(overview_page.pass_title).not_to_be_visible()
            expect(overview_page.pass_description).not_to_be_visible()
            expect(overview_page.pass_link).not_to_be_visible()

            DashboardHelper.select_printer_by_serial_number(page, common._printer_created[0].entity_id)
            DashboardHelper.pass_validation(page)
            framework_logger.info("=== C44513493 - PaaS cards on Overview Page flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during PaaS cards on Overview Page flow: {e}\n{traceback.format_exc()}")
            raise e
