from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from helper.update_plan_helper import UpdatePlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from helper.overview_helper import OverviewHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.cancellation_page import CancellationPage
from pages.shipping_billing_page import ShippingBillingPage
from pages.print_history_page import PrintHistoryPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancellation_flow_elements_with_subscription_unsubscribed(stage_callback):
    framework_logger.info("=== C43803104 - Cancellation flow with unsubscribed subscription flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        print_history_page = PrintHistoryPage(page)
        shipment_tracking_page = ShipmentTrackingPage(page)

        try:
            # Move subscription to subscribed state if needed
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info("Subscription moved to subscribed state if needed")

            # User signs into HP Smart and opens Smart Dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("User signs into HP Smart and opens Smart Dashboard page")
            
            # User cancels subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("User cancelled subscription")

            # Shift subscription by 32 days after cancelled
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            framework_logger.info("Subscription shifted by 32 days after cancelled")

            # Execute SubscriptionUnsubscriberJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionUnsubscriberJob"])
            framework_logger.info("Executed SubscriptionUnsubscriberJob")

            # User opens instant ink dashboard page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("User opens instant ink dashboard page")

            # Verify the Status card on Overview page with unsubscribed subscription
            OverviewHelper.verify_unsubscribed_status_card(page)
            framework_logger.info("Verified the Status card on Overview page with unsubscribed subscription")

            # Verify user does not see cancel link or keep enrollment button in the plan details card
            expect(overview_page.cancel_instant_ink).not_to_be_visible(timeout=5000)                
            expect(cancellation_page.keep_enrollment_button).not_to_be_visible(timeout=5000)
            framework_logger.info("Verified cancel link and keep enrollment button is not visible")           

            # User clicks the Change plan menu but it redirects to Overview page
            side_menu.click_update_plan()
            expect(overview_page.page_title).to_be_visible(timeout=60000)
            framework_logger.info("User clicks the Change plan menu but it redirects to Overview page")

            # User clicks on Print History Menu at UCDE
            side_menu.click_print_history()
            expect(print_history_page.page_title).to_be_visible(timeout=30000)
            framework_logger.info("User clicks on Print History Menu at UCDE")

            # User clicks on Shipment Tracking Menu at UCDE
            side_menu.click_shipment_tracking()
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=30000)
            framework_logger.info("User clicks on Shipment Tracking Menu at UCDE")
            
            # User clicks to expand My Account Menu at UCDE
            side_menu.expand_my_account_menu()
            framework_logger.info("User clicks to expand My Account Menu at UCDE")

            # User clicks on Shipping & Billing Menu at UCDE
            side_menu.click_shipping_billing()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=60000)
            expect(shipping_billing_page.billing_section).to_be_visible(timeout=30000)
            expect(shipping_billing_page.shipping_section).to_be_visible(timeout=30000)
            framework_logger.info("Shipping & Billing page with 'Your Address' and 'Your Billing' info cards")           

            # User clicks on Plan Overview Menu at UCDE
            side_menu.click_overview()
            expect(overview_page.page_title).to_be_visible(timeout=60000)
            framework_logger.info("User clicks on Plan Overview Menu at UCDE")

            # Click enroll printer again button and verify the enroll step page
            OverviewHelper.click_enroll_printer_again_and_verify_enrollment(page)
            framework_logger.info("Clicked enroll printer again button and verified the enroll step page")
           
            # User clicks on close button of the finish enrolling modal if needed          
            overview_page.close_finish_enrollment_button.click()
            expect(overview_page.page_title).to_be_visible(timeout=60000)
            framework_logger.info("User clicks on close button of the finish enrolling modal")
          
            # User clicks on HP Shop Ink button on Status card
            OverviewHelper.click_hp_shop_ink_and_verify_url(page)
            framework_logger.info("User clicks on HP Shop Ink button on Status card")

            # User downloads past invoices on Status card
            OverviewHelper.download_past_invoices_on_status_card(page, "/tmp/downloads")
            framework_logger.info("User downloads past invoices on Status card")

            framework_logger.info("=== C43803104 - Cancellation flow with unsubscribed subscription flow finished successfully ===")
            
        except Exception as e:
            framework_logger.error(f"An error occurred during the Cancellation flow with unsubscribed subscription: {e}\n{traceback.format_exc()}")
            raise e
      