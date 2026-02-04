from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from pages.notifications_page import NotificationsPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def near_monthly_page_amount_prepaid_only(stage_callback):
    framework_logger.info("=== C51820858 - Near Monthly Page Amount Prepaid Only flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # 1) HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer
        common.create_and_claim_virtual_printer()

    with PlaywrightManager() as page:
        notifications_page = NotificationsPage(page)
        try:
             # Start enrollment and sign in
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            framework_logger.info(f"Enrollment started and signed in with email: {tenant_email}")

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")
            
            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Choose hp checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Apply a prepaid
            prepaid_code = common.get_offer_code("prepaid", amount_equal=3000)
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 30)
            framework_logger.info(f"Prepaid code applied and validated")
            
            # Finish enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info(f"Finished enrollment with prepaid")

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Print 96 additional pages by RTP
            GeminiRAHelper.add_pages_by_rtp(page, "96")
            framework_logger.info(f"Added 96 pages by RTP")

            # Access subscription
            links = RABaseHelper.get_links_by_title(page, "Current subscription")
            links.first.click()
            framework_logger.info(f"Accessed current subscription")

            # Click link with text near_availablepages in the Notification events
            RABaseHelper.access_link_by_title(page, "near_availablepages", "Notification events")
            framework_logger.info(f"Accessed near_availablepages")

            # Sees Status equals to complete on near_availablepages page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click notification icon
            notifications_page.notifications_icon.click()
            framework_logger.info(f"Clicked on notifications icon")

            # See notification on Smart Dashboard
            expect(notifications_page.notifications_box).to_be_visible()
            framework_logger.info(f"Notifications box is visible")

            framework_logger.info("=== C51820858 - Near Monthly Page Amount Prepaid Only flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e