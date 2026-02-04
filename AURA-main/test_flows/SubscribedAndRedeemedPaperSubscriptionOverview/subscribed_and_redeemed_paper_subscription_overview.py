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

def subscribed_and_redeemed_paper_subscription_overview(stage_callback):
    framework_logger.info("=== C31446185 - Subscribed and Redeemed Paper Subscription Overview flow started ===")
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

            # Verify pilot subscription is redeemed
            RABaseHelper.access_link_by_title(page, "PilotSubscription", "Pilot subscriptions")
            GeminiRAHelper.verify_rails_admin_info(page, "State", "redeemed")
            framework_logger.info("Verified pilot subscription is redeemed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Opened Instant Ink Dashboard")

            # Verify message
            expect(overview_page.paper_redeemed_message).to_be_visible(timeout=90000)
            framework_logger.info("Verified paper redeemed message is displayed")

            # Verify the paper free month disclaimer is displayed on Plan Details Card
            DashboardHelper.sees_plan_details_card(page)
            expect(overview_page.paper_free_months).to_be_visible()
            framework_logger.info("Verified paper free month disclaimer is displayed on Plan Details Card")

            # Verify links on Plan Details Card
            expect(overview_page.redeem_code_link).to_be_visible()
            expect(overview_page.transfer_subscription_link).to_be_visible()
            expect(overview_page.cancel_instant_ink).to_be_visible()
            expect(overview_page.cancel_paper_add_on).to_be_visible()
            framework_logger.info("Verified links on Plan Details Card are displayed")

            # Verify Paper Status Card elements are visible
            expect(overview_page.paper_status).to_be_visible()
            expect(overview_page.paper_status).to_contain_text("Congratulations, you are enrolled in HP Paper Add-On Service! Your paper order is being processed.")
            framework_logger.info("Verified Paper Status Card is displayed")

            framework_logger.info("=== C31446185 - Subscribed and Redeemed Paper Subscription Overview flow finished successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e