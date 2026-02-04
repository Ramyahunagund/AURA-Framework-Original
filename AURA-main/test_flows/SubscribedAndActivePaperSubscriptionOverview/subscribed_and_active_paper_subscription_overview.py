import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def subscribed_and_active_paper_subscription_overview(stage_callback):
    framework_logger.info("=== C31446179 - Subscribed and Active Paper Subscription Overview flow started ===")
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
        overview_page = OverviewPage(page)
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

            # Get billing cycle times for validation
            RABaseHelper.access_link_by_title(page, "Subscription", "Subscription")
            GeminiRAHelper.access_second_billing_cycle(page, "-")
            start_time, end_time = GeminiRAHelper.get_billing_cycle_times(page)
            framework_logger.info(f"Retrieved billing cycle times: start_time={start_time}, end_time={end_time}")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened Instant Ink Dashboard")

            # Verify the paper free month disclaimer is displayed on Plan Details Card
            DashboardHelper.sees_plan_details_card(page)
            expect(overview_page.paper_free_months).to_be_visible(timeout=90000)
            framework_logger.info("Verified paper free month disclaimer is displayed on Plan Details Card")

            # Verify plan information is visible
            DashboardHelper.verify_plan_info(page, "12.48", "100")
            framework_logger.info("Verified plan information is displayed")

            # Verify Paper Status Card elements are visible
            expect(overview_page.paper_status).to_be_visible(timeout=90000)
            expect(overview_page.paper_status).to_contain_text("Your paper has been delivered. We'll automatically ship you more when you run low.")
            framework_logger.info("Verified Paper Status Card is displayed")

            # Verify estimated charge and monthly section on status card
            DashboardHelper.verify_paper_monthly_section_on_status_card(page, "0.00", start_time, end_time)
            framework_logger.info("Verified estimated charge is displayed")

            # Step 7: Verify total sheets used is 0
            DashboardHelper.verify_total_sheets_used(page, 0)
            framework_logger.info("Verified total sheets used is 0")

            # Check the progress bars - Verify "Plan sheets" and "Rollover sheets" progress bars are displayed
            DashboardHelper.verify_paper_progress_bars_visible(page, ["plan", "rollover"])
            framework_logger.info("Verified Plan sheets and Rollover sheets progress bars are displayed")

            # Verify the pages on progress bars show 0 usage
            DashboardHelper.verify_pages_used(page, "paper_plan", 0, 100)
            framework_logger.info("Verified Plan sheets progress bar shows 0 of 100 used")

            DashboardHelper.verify_pages_used(page, "paper_rollover", 0, 0)
            framework_logger.info("Verified Rollover sheets progress bar shows 0 of 0 used")

            framework_logger.info("=== C31446179 - Subscribed and Active Paper Subscription Overview flow finished successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e