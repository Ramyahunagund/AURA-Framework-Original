import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from helper.print_history_helper import PrintHistoryHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.print_history_page import PrintHistoryPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def subscribed_and_active_paper_subscription_print_history_page(stage_callback):
    framework_logger.info("=== C30340468 - Subscribed and Active Paper Subscription Print History Page flow started ===")
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
        side_menu = DashboardSideMenuPage(page)
        print_history_page = PrintHistoryPage(page)
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

            # Access Print and Payment History page
            side_menu.click_print_history()
            framework_logger.info("Navigated to Print and Payment History page")

            # Verify Print and Payment History page
            expect(print_history_page.page_title).to_be_visible(timeout=90000)
            expect(print_history_page.print_history_card).to_be_visible()
            expect(print_history_page.print_history_card_title).to_be_visible()
            expect(print_history_page.how_is_calculated_link).to_be_visible()
            expect(print_history_page.total_printed_pages).to_be_visible()
            expect(print_history_page.plan_pages_bar).to_be_visible()
            expect(print_history_page.trial_pages_bar).to_be_visible()
            expect(print_history_page.rollover_pages_bar).to_be_visible()
            expect(print_history_page.plan_details_card).to_be_visible()
            expect(print_history_page.paper_summary).not_to_be_visible()
            framework_logger.info("Print History page verified")

            # Verify plan information
            PrintHistoryHelper.verify_plan_info(page, "12.48", "100")
            framework_logger.info("Verified plan information in Print History page")

            # Trigger Paper base billing charge
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.remove_free_months(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 100 pages")

            # Access Print History page 
            DashboardHelper.access(page)
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Verify Paper plan monthly charge info displayed
            PrintHistoryHelper.see_notification_on_print_history(page, "HP Instant Ink Service 100 Page Plan\n(+ applicable tax) Billed")
            framework_logger.info("Verified Paper plan monthly charge info displayed in Print History page")

            # Trigger Paper overage billing charge
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "130")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 130 pages")

            # Access Print History page
            DashboardHelper.access(page)
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")

            # Verify Paper plan monthly charge plus overage info displayed 
            PrintHistoryHelper.see_notification_on_print_history(page, "HP Instant Ink Service 100 Page Plan\n3 Additional page sets of 10 pages")
            framework_logger.info("Verified Paper plan monthly charge plus overage info displayed in Print History page")

            framework_logger.info("=== C30340468 - Subscribed and Active Paper Subscription Print History Page flow finished successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e