from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.print_history_page import PrintHistoryPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from test_flows.EnrollmentOOBE.enrollment_oobe import enrollment_oobe
import test_flows_common.test_flows_common as common

import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def temp_cancel_rollover_during_vacation_months_without_overages(stage_callback):
    framework_logger.info("=== C43504782 - Temp Cancel - Rollover during Vacation months without overages ===")

    tenant_email = create_ii_subscription(stage_callback)
    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        try:
            # Step 1: Identify user and move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)        
            GeminiRAHelper.remove_free_months(page)
            GeminiRAHelper.subscription_to_subscribed(page)                
            framework_logger.info("Subscription moved to subscribed state and remove free months")
            # set pages used to 80
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page) 
            GeminiRAHelper.add_pages_by_rtp(page, "80")
            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Pause plan for 2 months on Overview page
            DashboardHelper.pause_plan(page, 2)
            framework_logger.info(f"Paused plan for 2 months on Overview page")

             # Charge the first billing cycle without page tally
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "32", "80")
            GeminiRAHelper.complete_jobs(page, ["SubscriptionBillingJob"])

            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page) 
            GeminiRAHelper.access_first_billing_cycle(page)
            rollover_pages = RABaseHelper.get_field_text_by_title(page, 'Initial rollover pages')
            assert rollover_pages == '20', f"Expected rollover pages to be 20, but got {rollover_pages}"

            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 20)
            framework_logger.info("Verified rollover pages as 0 of 20 on Overview page")

            # Charge the seccond billing cycle with page tally 5
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "31", "5")

            rollover = RABaseHelper.get_field_text_by_title(page, "Starting rollover pages")
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            assert rollover == "20", f"Expected rollover to be 20, but got {rollover}"
            assert status_code == "NO-CHARGE", f"Expected status code to be NO-CHARGE, but got {status_code}"

            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 20)
            framework_logger.info("Verified rollover pages as 0 of 20 on Overview page")

            # Charge the third billing cycle with page tally 8
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "31", "8")

            rollover = RABaseHelper.get_field_text_by_title(page, "Starting rollover pages")
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")

            assert rollover == "20", f"Expected rollover to be 20, but got {rollover}"
            assert status_code == "NO-CHARGE", f"Expected status code to be NO-CHARGE, but got {status_code}"

            # access dashboard
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 20)
            framework_logger.info("Verified rollover pages as 0 of 20 on Overview page")

            # print history verification
            side_menu = DashboardSideMenuPage(page)
            side_menu.print_history_menu_link.click()

            PrintHistoryHelper.get_billing_cycle_option(page, 1)

            # Sees the plan pages as 8 of 100 used
            DashboardHelper.verify_pages_used(page, "plan", 8, 10)
            framework_logger.info("Plan pages verified as 8 of 10 used on Overview page")

            # Sees the rollover pages as 0 of 0 used on Overview page
            DashboardHelper.verify_pages_used(page, "rollover", 0, 20)
            framework_logger.info("Rollover pages verified as 0 of 20 used on Overview page")

            framework_logger.info("=== C43504782 - Temp Cancel - Rollover during Vacation months without overages ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
