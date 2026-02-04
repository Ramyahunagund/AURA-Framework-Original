from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def temp_cancel_rollover_during_vacation_months_with_overages(stage_callback):
    framework_logger.info("=== C44253168 - Temp Cancel - Rollover during Vacation months with overages flow started ===")

    tenant_email = create_ii_subscription(stage_callback)
    with PlaywrightManager() as page:
        try:
            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)        
            GeminiRAHelper.remove_free_months(page)
            GeminiRAHelper.subscription_to_subscribed(page)                
            framework_logger.info("Subscription moved to subscribed state and remove free months")
            
            # Set pages used to 80
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page) 
            GeminiRAHelper.add_pages_by_rtp(page, "80")

            # Pause plan for 3 months on Overview page
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.pause_plan(page, 3)
            framework_logger.info(f"Paused plan for 3 months on Overview page")

            # Charge a new billing cycle with page tally 80
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "32", "80")
            framework_logger.info("New billing cycle charged with page tally 80")

            # Verify the rollover pages
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            rollover_pages = RABaseHelper.get_field_text_by_title(page, 'Initial rollover pages')
            assert rollover_pages == '20', f"Expected rollover pages to be 20, but got {rollover_pages}"

            # Verify the rollover pages on Overview page
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 20)
            framework_logger.info("Verified rollover pages as 0 of 20 on Overview page")

            # Charge a new billing cycle with page tally 15
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "31", "15")
            framework_logger.info("New billing cycle charged with page tally 15")

            # Sees the starting rollover pages and status code
            rollover = RABaseHelper.get_field_text_by_title(page, "Starting rollover pages")
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            assert rollover == "20", f"Expected rollover to be 20, but got {rollover}"
            assert status_code == "NO-CHARGE", f"Expected status code to be NO-CHARGE, but got {status_code}"

            # Verify the rollover pages on Overview page
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 15)
            framework_logger.info("Verified rollover pages as 0 of 15 on Overview page")

            # Charge a new billing cycle with page tally 40
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "31", "40")
            framework_logger.info("New billing cycle charged with page tally 40")

            # Sees the starting rollover pages and status code
            rollover = RABaseHelper.get_field_text_by_title(page, "Starting rollover pages")
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            assert rollover == "15", f"Expected rollover to be 15, but got {rollover}"
            assert status_code != "NO-CHARGE", f"Expected status code to be different from NO-CHARGE, but got {status_code}"

            # Verify the rollover pages on Overview page
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 5)
            framework_logger.info("Verified rollover pages as 0 of 5 on Overview page")

            # Charge a new billing cycle with page tally 20
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "31", "20")
            framework_logger.info("New billing cycle charged with page tally 20")

            # Sees the starting rollover pages and status code
            rollover = RABaseHelper.get_field_text_by_title(page, "Starting rollover pages")
            status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
            assert rollover == "5", f"Expected rollover to be 5, but got {rollover}"
            assert status_code != "NO-CHARGE", f"Expected status code to be different from NO-CHARGE, but got {status_code}"

            # Verify the rollover pages on Overview page
            DashboardHelper.first_access(page, tenant_email)
            DashboardHelper.verify_pages_used(page, "rollover", 0, 5)
            framework_logger.info("Verified rollover pages as 0 of 5 on Overview page")

            # Charge a new billing cycle with page tally 120
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "32", "120")
            framework_logger.info("New billing cycle charged with page tally 120")

            # Access Print History page
            DashboardHelper.first_access(page, tenant_email)
            side_menu = DashboardSideMenuPage(page)
            side_menu.print_history_menu_link.click()

            # Sees the plan pages as 10 of 10 used
            PrintHistoryHelper.get_billing_cycle_option(page, 2)
            DashboardHelper.verify_pages_used(page, "plan", 10, 10)
            framework_logger.info("Plan pages verified as 10 of 10 used on Print History page")

            # Sees the additional pages as 5 of 10 used on Print History page
            DashboardHelper.verify_pages_used(page, "additional", 5, 10)
            framework_logger.info("Additional pages verified as 5 of 10 used on Print History page")

            # Sees the rollover pages as 5 of 5 used on Print History page
            DashboardHelper.verify_pages_used(page, "rollover", 5, 5)
            framework_logger.info("Rollover pages verified as 5 of 5 used on Print History page")

            framework_logger.info("=== C44253168 - Temp Cancel - Rollover during Vacation months with overages flow completed ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
