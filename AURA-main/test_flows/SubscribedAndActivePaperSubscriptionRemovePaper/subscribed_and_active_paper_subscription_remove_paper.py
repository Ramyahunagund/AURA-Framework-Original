import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.ra_base_helper import RABaseHelper
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.cancellation_page import CancellationPage
from pages.cancellation_timeline_page import CancellationTimelinePage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def subscribed_and_active_paper_subscription_remove_paper(stage_callback):
    framework_logger.info("=== C30340504 - Subscribed and Active Paper Subscription Remove Paper flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # HPID signup + UCDE onboarding
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # Claim virtual printer and add address
        printer = common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        try:
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Select ink and paper plan
            EnrollmentHelper.select_plan(page, plan_value="100", plan_type="ink_and_paper")
            framework_logger.info(f"Paper plan selected: 100")

            price = None
            try:
                price = EnrollmentHelper.get_total_price_by_plan_card(page)
            except Exception:
                framework_logger.info(f"Failed to get price from plan card")

            # Add billing
            EnrollmentHelper.add_billing(page, plan_value=price)
            framework_logger.info(f"Billing added")

            # Finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Paper subscription enrollment completed successfully")
        except Exception as e:
            framework_logger.error(f"An error occurred during the paper subscription enrollment: {e}\n{traceback.format_exc()}")
            raise e

    with PlaywrightManager() as page:
        cancellation_page = CancellationPage(page)
        cancellation_timeline = CancellationTimelinePage(page)
        overview_page = OverviewPage(page)
        side_menu = DashboardSideMenuPage(page)
        update_plan = UpdatePlanPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription moved to subscribed state")
            
            # Activate pilot subscription
            RABaseHelper.access_link_by_title(page, "PilotSubscription", "Pilot subscriptions")
            GeminiRAHelper.activate_pilot(page)
            framework_logger.info("Activated pilot subscription")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened Instant Ink Dashboard")

            # Remove paper on overview page
            overview_page.cancel_paper_add_on.click()
            framework_logger.info("Clicked on Remove Paper button on Overview Page")

            # Verify Cancellation Summary Page is displayed
            expect(cancellation_page.confirm_paper_cancellation_button).to_be_visible(timeout=90000)
            expect(cancellation_page.keep_paper_button).to_be_visible()
            framework_logger.info("Cancellation Summary Page is displayed")

            # Keep paper subscription
            cancellation_page.keep_paper_button.click()
            expect(overview_page.status_card).to_be_visible(timeout=90000)
            framework_logger.info("Clicked on Keep Paper button")

            # Verify paper subscription is still active
            DashboardHelper.verify_plan_info(page, "12.48", "100")
            framework_logger.info("Verified paper subscription is still active after keeping paper")

            # Access Update Page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Page")

            # Click remove paper subscription on header of Update Plan Page
            update_plan.header_remove_paper_link.click()
            framework_logger.info("Clicked on Remove Paper link on Update Plan Page header")

            # Verify Cancellation Summary Page is displayed
            expect(cancellation_page.confirm_paper_cancellation_button).to_be_visible(timeout=90000)
            expect(cancellation_page.keep_paper_button).to_be_visible()
            framework_logger.info("Cancellation Summary Page is displayed")

            # Access Update Page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Page")

            # Click remove paper subscription on plan details of Update Plan Page
            update_plan.cancel_paper_add_on.click(timeout=90000)
            framework_logger.info("Clicked on Remove Paper link on Update Plan Page plan details")

            # Verify Cancellation Summary Page is displayed
            expect(cancellation_page.confirm_paper_cancellation_button).to_be_visible(timeout=90000)
            expect(cancellation_page.keep_paper_button).to_be_visible()
            framework_logger.info("Cancellation Summary Page is displayed")

            # Confirm paper cancellation
            cancellation_page.confirm_paper_cancellation_button.click()
            framework_logger.info("Clicked on Confirm Remove Paper button")

            # Verify Cancellation Timeline is displayed
            expect(cancellation_timeline.header_icon).to_be_visible(timeout=90000)
            expect(cancellation_timeline.header_title).to_be_visible()
            expect(cancellation_timeline.timeline_img).to_be_visible()
            expect(cancellation_timeline.whats_happens_next).to_be_visible()
            framework_logger.info("Cancellation Timeline is displayed")

            # Verify feedback options 
            cancellation_page.continue_button.click()
            CancellationPlanHelper.verify_paper_radio_buttons_on_cancellation_feedback_page(page)
            cancellation_page.return_to_account_button.click()
            framework_logger.info("Verified paper cancellation feedback options")

            # Verify Plan Details Card
            expect(overview_page.paper_cancellation_in_progress).to_be_visible(timeout=90000)
            expect(overview_page.keep_paper_button).to_be_visible()
            DashboardHelper.verify_plan_info(page, "7.99", "100")
            framework_logger.info("Verified Plan Details Card after paper cancellation")

            # Verify Status Card
            expect(overview_page.paper_billing_cycle).to_be_visible()
            expect(overview_page.paper_estimated_charge).to_be_visible()
            expect(overview_page.paper_sheets_used).to_be_visible()
            DashboardHelper.verify_paper_progress_bars_visible(page, ["plan", "rollover"])
            framework_logger.info("Verified Status Card after paper cancellation")

            # Verify Paper Status Card
            expect(overview_page.paper_status).to_be_visible()
            expect(overview_page.paper_status).to_contain_text("Your paper subscription will end")
            framework_logger.info("Verified Paper Status Card after paper cancellation")

            # Access Update Page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Page")

            # Verify Plan cards do not include paper
            UpdatePlanHelper.verify_available_plans(page)
            framework_logger.info("Verified available plans do not include paper")

            # Access Print and Payment History page
            side_menu.click_print_history()
            framework_logger.info("Navigated to Print and Payment History page")

            # Verify plan information
            PrintHistoryHelper.verify_plan_info(page, "7.99", "100")
            framework_logger.info("Verified plan information in Print History page")

            framework_logger.info("=== C30340504 - Subscribed and Active Paper Subscription Remove Paper flow finished successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e