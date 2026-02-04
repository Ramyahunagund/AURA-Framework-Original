from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def you_just_got_free_months(stage_callback):
    framework_logger.info("=== C57368161 - You just got free months flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Get raf code at Special offers card
            raf_code = overview_page.raf_code.inner_text()
            framework_logger.info(f"RAF code: {raf_code}")

        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e

    common.setup()
    tenant_email2 = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email2}")

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
        try:
            # Start enrollment and sign in
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email2)
            framework_logger.info(f"Enrollment started and signed in with email: {tenant_email2}")

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

            # Apply RaF code
            EnrollmentHelper.apply_and_validate_raf_code(page, raf_code)
            framework_logger.info(f"RaF code applied and validated successfully")

            # Add billing method
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing method added successfully")
            
            # Finish enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info(f"Finished enrollment with prepaid")

        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        try:
            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Notifications
            side_menu.click_notifications()
            framework_logger.info(f"Accessed Notifications page")

            # See "Free month for referring a friend" on Notification page
            DashboardHelper.see_notification_on_dashboard(page, "Free month for referring a friend")
            framework_logger.info(f"Verified 'Free month for referring a friend' notification is present")

            # Access Print History
            side_menu.click_print_history()
            framework_logger.info(f"Accessed Print History page")

            # See "Refer-a-Friend Program (One of your friends enrolled and you got 1 month free) Applied" notification on Print History card
            PrintHistoryHelper.see_notification_on_print_history(page, "Refer-a-Friend Program (One of your friends enrolled and you got 1 month free) Applied")
            framework_logger.info(f"Verified 'Refer-a-Friend Program (One of your friends enrolled and you got 1 month free) Applied' notification is present")

            # Access Subscription page on Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info(f"Accessed Subscription page on Rails Admin for tenant: {tenant_email}")

            # Click link with text purl_shared_enroll in the Notification events on the Subscription page
            RABaseHelper.access_link_by_title(page, "purl_shared_enroll", "Notification events")
            framework_logger.info(f"Clicked link with text 'purl_shared_enroll' in the Notification events")

            # See Status equals to complete on Notification Event page
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "complete")

            framework_logger.info("=== C57368161 - You just got free months flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
