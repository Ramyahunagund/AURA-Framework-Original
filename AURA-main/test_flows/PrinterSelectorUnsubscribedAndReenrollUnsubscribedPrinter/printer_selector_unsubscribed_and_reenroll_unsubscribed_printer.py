from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from helper.ra_base_helper import RABaseHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from helper.overview_helper import OverviewHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.cancellation_plan_helper import CancellationPlanHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from core.settings import framework_logger
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def printer_selector_unsubscribed_and_reenroll_unsubscribed_printer(stage_callback):
    framework_logger.info("=== C43554029 - Printer Selector (Unsubscribed) & re-enroll the unsubscribed printer flow started ===")
    tenant_email = create_ii_subscription(stage_callback)
    common.setup()
    
    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)
            side_menu = DashboardSideMenuPage(page)

            # Move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            CancellationPlanHelper.select_cancellation_feedback_option(page)
            framework_logger.info("Subscription cancelled")

            # Verify the subscription state in Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "initiated_unsubscribe")
            framework_logger.info("Verified subscription state is initiated_unsubscribe")

            # Billing cycle charged for that subscription setting page used as 100
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "80")
            GeminiRAHelper.submit_charge(page) 
            GeminiRAHelper.manual_retry_until_complete(page=page)  
            framework_logger.info(f"Billing cycle charged with 32 pages")  

            # Executes the resque job: SubscriptionUnsubscriberJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionUnsubscriberJob"])
            framework_logger.info("SubscriptionUnsubscriberJob executed")

            # Verify the subscription state in Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "unsubscribed")
            framework_logger.info("Verified subscription state is unsubscribed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Verify cancelled printer on printer selector - Overview page
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")
            framework_logger.info("Cancelled printer is displayed on printer selector - Overview page")

            # Verify cancelled printer on printer selector - Print History page
            side_menu.click_print_history()
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")
            framework_logger.info("Cancelled printer is displayed on printer selector - Print History page")

            # Verify cancelled printer on printer selector - Shipment Tracking page
            side_menu.click_shipment_tracking()
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")
            framework_logger.info("Cancelled printer is displayed on printer selector - Shipment Tracking page")

            # Get the first printer's serial number
            first_printer = overview_page.printer_selector_first_printer.inner_text().strip()
            first_printer_id = first_printer.replace('S/N: ', '')
            framework_logger.info(f"First printer serial number: {first_printer_id}")

            # Set the printer to offline
            printer_id = common._printer_created[0].entity_id
            common.remove_printer_webservices(printer_id)
            framework_logger.info(f"Removed printer {printer_id} via webservice")

            # Verify there is only one printer on Overview page
            side_menu.click_overview()
            expect(overview_page.printer_selector).to_be_visible(timeout=50000)
            overview_page.printer_selector.click()
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK CANCELLED SUBSCRIPTIONS", "only one")
            framework_logger.info(f"Number of printers in INSTANT INK CANCELLED SUBSCRIPTIONS was confirmed to be more than one")

            # Set the printer online
            printer_id = common._printer_created[0].entity_id
            common.enable_printer_webservices(printer_id)
            page.reload()
            time.sleep(10)
            framework_logger.info(f"Enabled printer {printer_id} via webservice")

            # Enroll printer again with 100 pages plan
            with page.context.expect_page() as new_page_info:
                overview_page.enroll_or_replace_button.click()
            new_page = new_page_info.value
            EnrollmentHelper.accept_terms_of_service(new_page)
            EnrollmentHelper.select_printer(new_page)
            EnrollmentHelper.select_plan(new_page, 100)
            EnrollmentHelper.finish_enrollment(new_page)
            new_page.close()
            framework_logger.info(f"Re-enrolled printer with 100 pages plan")

            # Set printed pages to 50
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            GeminiRAHelper.set_printed_pages(page, "50")
            framework_logger.info("Set printed pages to 50")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Sees the plan pages as 50 of 100 used on Overview page
            DashboardHelper.verify_pages_used(page, "plan", 50, 100)
            framework_logger.info(f"Verified plan pages as 50 of 100 used on Print History Page")

            # Sees the plan pages as 50 of 100 used on Print History Page
            side_menu.click_print_history()
            DashboardHelper.verify_pages_used(page, "plan", 50, 100)
            framework_logger.info(f"Verified plan pages as 50 of 100 used on Print History Page")

            # Verify cancelled printer on printer selector - Overview page
            side_menu.click_overview()
            expect(overview_page.printer_selector).to_be_visible(timeout=90000)
            DashboardHelper.verify_printer_in_submenu(page, "cancelled")
            framework_logger.info("Cancelled printer is displayed on printer selector - Overview page")

            # Verify the subscription state in Rails Admin
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page, index=1)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "obsolete")
            framework_logger.info("Verified subscription state is obsolete")

            framework_logger.info("=== C43554029 - Printer Selector (Unsubscribed) & re-enroll the unsubscribed printer flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
