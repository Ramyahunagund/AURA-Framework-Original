import time
from pages.overview_page import OverviewPage
from pages.shipping_billing_page import ShippingBillingPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def shipping_elements_subscribed_no_pens(stage_callback):
    framework_logger.info("=== C48935448 - Shipping elements Subscribed no Pens Account started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            side_menu = DashboardSideMenuPage(page)
            overview_page = OverviewPage(page)
            shipping_billing_page = ShippingBillingPage(page)
            
            # Verify subscription state is subscribed_no_pens
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "subscribed_no_pens")
            framework_logger.info(f"Verified subscription state is subscribed_no_pens")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")
            
            # Verify Change Shipping Info link on Overview page
            side_menu.click_overview()
            overview_page.change_shipping_link.click()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=60000)
            framework_logger.info("Change Shipping Info link on Overview page verified")

            # Waits 16 minutes
            time.sleep(960)
            framework_logger.info("Waited 16 minutes")

            # Click on Manage Shipping Address cancelling the Security Session Expired modal and accepting after
            shipping_billing_page.manage_shipping_address.click()
            page.locator("[data-testid='modalCloseButton']").click()
            shipping_billing_page.manage_shipping_address.click()
            DashboardHelper.login_on_security_session_expired(page, tenant_email)
            overview_page.change_shipping_link.click()
            shipping_billing_page.manage_shipping_address.click()
            expect(shipping_billing_page.shipping_form_modal).to_be_visible(timeout=90000)
            framework_logger.info(f"Clicked on Manage Shipping Address")

            # User sets different address 
            DashboardHelper.add_shipping(page, index=0)
            framework_logger.info(f"Changed shipping address successfully")

            # Click on Manage Shipping Address 
            side_menu.click_overview()
            DashboardHelper.verify_shipping_address_updated(page, index=1)
            framework_logger.info(f"Verified shipping address updated successfully")

            # Clicks edit shipping link on Shipping & Billing Page
            overview_page.change_shipping_link.click()
            shipping_billing_page.manage_shipping_address.click()
            framework_logger.info(f"Clicked on Manage Shipping Address")

            # User sets original address without saving
            DashboardHelper.add_shipping_without_saving(page, index=0)
            framework_logger.info(f"Changed shipping address successfully")

            # User sees different address saved previously
            side_menu.click_overview()
            DashboardHelper.verify_shipping_address_updated(page, index=1)
            framework_logger.info(f"Verified shipping address updated successfully")

            framework_logger.info("=== C48935448 - Shipping elements Subscribed no Pens Account finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
            