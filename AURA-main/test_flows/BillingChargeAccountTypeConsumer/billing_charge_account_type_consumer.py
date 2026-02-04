from helper.ra_base_helper import RABaseHelper
from pages import print_history_page
from pages.cancellation_page import CancellationPage
from pages.overview_page import OverviewPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.dashboard_helper import DashboardHelper
from pages.overview_page import OverviewPage
from pages.shipping_billing_page import ShippingBillingPage
from pages.print_history_page import PrintHistoryPage
from pages.overview_page import OverviewPage
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_charge_account_type_consumer(stage_callback):
    framework_logger.info("=== C39510046 - Billing cycle charge account type consumer Started ===")
    tenant_email = create_ii_subscription(stage_callback)
    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        print_history_page = PrintHistoryPage(page)

        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.remove_free_months(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription status changed to 'subscribed'")

            # Charge a billing cycle
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            GeminiRAHelper.manual_retry_until_complete(page=page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Dashboard")

            # Click change billing link
            overview_page.change_billing_link.click()
            framework_logger.info("Accessed Shipping & Billing page")

            # Click business option and fill company and tax id
            DashboardHelper.add_company_and_tax_account_type_business(page, company_name="Business", tax_id="12-3456789")
            framework_logger.info("Clicked business option and filled company and tax id")

            # Change payment method
            DashboardHelper.add_billing(page, "credit_card_master_2_series")
            framework_logger.info("Changed payment method to credit_card_master")

            # Charge a billing cycle
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "80")
            GeminiRAHelper.submit_charge(page)
            GeminiRAHelper.manual_retry_until_complete(page=page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            framework_logger.info(f"New billing cycle charged with 80 pages")

            # Verify Charge complete status true
            GeminiRAHelper.verify_charge_complete(page)
            framework_logger.info(f"Verified Charge complete status true")

            # Clicks link with text BaseChargeInvoiceItem in the Invoice item page
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "BaseChargeInvoiceItem")[0].click()
            framework_logger.info("Accessed BaseChargeInvoiceItem page")

            # Charge a billing cycle
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "600")
            GeminiRAHelper.submit_charge(page)
            GeminiRAHelper.manual_retry_until_complete(page=page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            framework_logger.info(f"New billing cycle charged with 600 pages")

            # Verify Charge complete status true
            GeminiRAHelper.verify_charge_complete(page)
            framework_logger.info(f"Verified Charge complete status true")

            # Clicks link with text OverageInvoiceItem in the Invoice item page
            RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "OverageInvoiceItem")[0].click()
            framework_logger.info("Accessed OverageInvoiceItem page")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Dashboard")

            # Click Printy History menu
            side_menu.click_print_history()
            framework_logger.info("Accessed Printy History page")

            # validates if the Print History page was displayed correctly
            expect(print_history_page.page_title).to_be_visible()
            expect(print_history_page.print_history_card).to_be_visible()
            expect(print_history_page.print_history_card_title).to_be_visible()
            expect(print_history_page.how_is_calculated_link).to_be_visible()
            expect(print_history_page.total_printed_pages).to_be_visible()
            expect(print_history_page.plan_details_card).to_be_visible()
            expect(print_history_page.print_history_section).to_be_visible()
            framework_logger.info("Print History page displayed correctly")

            framework_logger.info("=== C39510046 - Billing cycle charge account type consumer Finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
       