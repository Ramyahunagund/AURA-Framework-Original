from multiprocessing import context
import time
from helper.enrollment_helper import EnrollmentHelper
from helper.overview_helper import OverviewHelper
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def re_enroll_with_obsolete_printer_more_than_once(stage_callback):
    framework_logger.info("=== C44065035 - Re-enroll with the obsolete printer more than once started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status updated to 'subscribed'")

            # Force Subscription to Obsolete
            GeminiRAHelper.force_subscription_to_obsolete(page)
            framework_logger.info("Subscription forced to obsolete state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Enroll Printer Again
            overview_page.enroll_printer_again_button.click()
            original_page = page
            with page.context.expect_page() as new_page_info:
                page = new_page_info.value
            EnrollmentHelper.accept_terms_of_service(page)
            original_page.close()

            overview_page = OverviewPage(page)
            side_menu = DashboardSideMenuPage(page)
       
            # Selects the printer on printer selection page
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Selects the Plan 100
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            # Force Subscription to Obsolete
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.force_subscription_to_obsolete(page)
            framework_logger.info("Subscription forced to obsolete state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Wait for 5 minutes and refresh page
            time.sleep(300)
            page.reload()
            framework_logger.info("Page refreshed after 5 minutes")

            # Checks if the INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector on Overview Page
            expect(overview_page.printer_selector).to_be_visible(timeout=50000)
            overview_page.printer_selector.click()
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK CANCELLED SUBSCRIPTIONS")
            framework_logger.info("INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector")

            # Verify there is more than One Printer on Overview Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK CANCELLED SUBSCRIPTIONS","more than one")
            framework_logger.info(f"Number of printers in INSTANT INK CANCELLED SUBSCRIPTIONS was confirmed to be more than one")

            # Checks if the INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector on Print History Page
            side_menu.print_history_menu_link.click()
            expect(overview_page.printer_selector).to_be_visible(timeout=30000)
            overview_page.printer_selector.click() 
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK CANCELLED SUBSCRIPTIONS", timeout=10000)
            framework_logger.info("INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector")

            # Verify there is more than One Printer on Print History Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK CANCELLED SUBSCRIPTIONS","more than one")
            framework_logger.info(f"Number of printers in INSTANT INK CANCELLED SUBSCRIPTIONS was confirmed to be more than one")

            # Access Overview Page
            side_menu.overview_menu_link.click()
            expect(overview_page.printer_selector).to_be_visible(timeout=10000)
            framework_logger.info(f"Opened Overview Page")

            # Enroll Printer Again
            overview_page.re_enroll_printer_button.click()
            original_page = page
            with page.context.expect_page() as new_page_info:
                page = new_page_info.value
            EnrollmentHelper.accept_terms_of_service(page)

            expect(overview_page.printer_selector).to_be_visible(timeout=30000)
            framework_logger.info(f"Opened Overview Page")

            # Enroll Printer Again
            overview_page.enroll_printer_again_button.click()
            original_page = page
            with page.context.expect_page() as new_page_info:
                page = new_page_info.value
            EnrollmentHelper.accept_terms_of_service(page)
            original_page.close()

            overview_page = OverviewPage(page)
            side_menu = DashboardSideMenuPage(page)
       
            # Selects the printer on printer selection page
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Selects the Plan 100
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # Finish enrollment  
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment completed successfully")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")
            
            # Checks if the INSTANT INK ENROLLED PRINTERS section is visible on printer selector on Overview Page
            expect(overview_page.printer_selector).to_be_visible(timeout=50000)
            overview_page.printer_selector.click()
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("INSTANT INK ENROLLED PRINTERS section is visible on printer selector")

            # Verify there is only One Printer on Overview Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK ENROLLED PRINTERS","only one")
            framework_logger.info(f"Number of printers in INSTANT INK ENROLLED PRINTERS was confirmed to be only one")

            # Checks if the INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector on Overview Page
            expect(overview_page.printer_selector).to_be_visible(timeout=30000)
            overview_page.printer_selector.click()
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK CANCELLED SUBSCRIPTIONS")
            framework_logger.info("INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector")

            # Verify there is more than One Printer on Overview Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK CANCELLED SUBSCRIPTIONS","more than one")
            framework_logger.info(f"Number of printers in INSTANT INK CANCELLED SUBSCRIPTIONS was confirmed to be more than one")

            # Checks if the INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector on Update Plan Page
            side_menu.click_update_plan.click()
            expect(overview_page.printer_selector).to_be_visible(timeout=30000)
            overview_page.printer_selector.click() 
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK CANCELLED SUBSCRIPTIONS", timeout=10000)
            framework_logger.info("INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector")

            # Verify there is more than One Printer on Update Plan Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK CANCELLED SUBSCRIPTIONS","more than one")
            framework_logger.info(f"Number of printers in INSTANT INK CANCELLED SUBSCRIPTIONS was confirmed to be more than one")

            # Checks if the INSTANT INK ENROLLED PRINTERS section is visible on printer selector on Update Plan Page
            expect(overview_page.printer_selector).to_be_visible(timeout=30000)
            overview_page.printer_selector.click()
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("INSTANT INK ENROLLED PRINTERS section is visible on printer selector")

            # Verify there is only One Printer on Update Plan Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK ENROLLED PRINTERS","only one")
            framework_logger.info(f"Number of printers in INSTANT INK ENROLLED PRINTERS was confirmed to be only one")

            # Checks if the INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector on Print History Page
            side_menu.click_print_history.click()
            expect(overview_page.printer_selector).to_be_visible(timeout=30000)
            overview_page.printer_selector.click() 
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK CANCELLED SUBSCRIPTIONS", timeout=10000)
            framework_logger.info("INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector")

            # Verify there is more than One Printer on Print History Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK CANCELLED SUBSCRIPTIONS","more than one")
            framework_logger.info(f"Number of printers in INSTANT INK CANCELLED SUBSCRIPTIONS was confirmed to be more than one")

            # Checks if the INSTANT INK ENROLLED PRINTERS section is visible on printer selector on Print History Page
            expect(overview_page.printer_selector).to_be_visible(timeout=10000)
            overview_page.printer_selector.click()
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("INSTANT INK ENROLLED PRINTERS section is visible on printer selector")

            # Verify there is only One Printer on Print History Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK ENROLLED PRINTERS","only one")
            framework_logger.info(f"Number of printers in INSTANT INK ENROLLED PRINTERS was confirmed to be only one")

            # Checks if the INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector on Shipment Tracking Page
            side_menu.click_shipment_tracking.click()
            expect(overview_page.printer_selector).to_be_visible(timeout=30000)
            overview_page.printer_selector.click() 
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK CANCELLED SUBSCRIPTIONS", timeout=10000)
            framework_logger.info("INSTANT INK CANCELLED SUBSCRIPTIONS section is visible on printer selector")

            # Verify there is more than One Printer on Shipment Tracking Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK CANCELLED SUBSCRIPTIONS","more than one")
            framework_logger.info(f"Number of printers in INSTANT INK CANCELLED SUBSCRIPTIONS was confirmed to be more than one")

            # Checks if the INSTANT INK ENROLLED PRINTERS section is visible on printer selector on Shipment Tracking Page
            expect(overview_page.printer_selector).to_be_visible(timeout=10000)
            overview_page.printer_selector.click()
            expect(overview_page.printers_grouped_by_status).to_contain_text("INSTANT INK ENROLLED PRINTERS")
            framework_logger.info("INSTANT INK ENROLLED PRINTERS section is visible on printer selector")

            # Verify there is only One Printer on Shipment Tracking Page
            OverviewHelper.number_of_printers_in_section(page, "INSTANT INK ENROLLED PRINTERS","only one")
            framework_logger.info(f"Number of printers in INSTANT INK ENROLLED PRINTERS was confirmed to be only one")

            framework_logger.info("=== C44065035 - Re-enroll with the obsolete printer more than once finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
