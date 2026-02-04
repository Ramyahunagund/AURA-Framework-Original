from helper.enrollment_helper import EnrollmentHelper
from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.shipping_billing_page import ShippingBillingPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from playwright.sync_api import expect
import urllib3
import traceback
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from core.settings import GlobalState

def update_info(stage_callback):
    framework_logger.info("=== C38108871 - Update info flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)
            side_menu = DashboardSideMenuPage(page)
            shipping_billing_page = ShippingBillingPage(page)
            
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            
            # Access Smart Dashboard and skip preconditions
            DashboardHelper.first_access(page, tenant_email=tenant_email)
            framework_logger.info("Accessed Smart Dashboard and skipped preconditions")
            
            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info("Accessed Update Plan page")
            
            # Verify the current plan is 100
            DashboardHelper.verify_plan_value(page, 100)
            framework_logger.info("The current plan is 100")
                                  
           # Select plan 300
            UpdatePlanHelper.select_plan(page,300)
            UpdatePlanHelper.select_plan_button(page, 300)
            framework_logger.info("Plan 300 selection completed")

            # Go back to Overview to verify plan change
            side_menu.click_overview()
            framework_logger.info("Navigated back to Overview page")
                           
            # Verify plan value in Overview page
            DashboardHelper.verify_plan_value(page, 300)
            framework_logger.info("Verified plan value 300 in Overview page")

            # Click Change Billing Info link in Overview page
            update_plan_page = UpdatePlanPage(page)
            update_plan_page.change_billing_info_link.click()
            framework_logger.info("Clicked change billing info link")

            # Click Change Billing Info link in Overview page
            shipping_billing_page = ShippingBillingPage(page)
            shipping_billing_page.manage_shipping_address.click()
            framework_logger.info("Clicked Manage your shipping address link")

            # Change shipping info - using second address (index 1)
            DashboardHelper.add_shipping(page, index=1)
            framework_logger.info(f"Changed shipping address to {GlobalState.locale} - Second address (San Francisco)")
                  
            # Change payment method to credit_card_master
            shipping_billing_page.manage_your_payment_method_link.click()
            DashboardHelper.add_billing(page, "credit_card_master_2_series")
            framework_logger.info("Changed payment method to credit_card_master")
            
            # Navigate back to Overview to verify changes
            side_menu.click_overview()
            framework_logger.info("Navigated back to Overview page to verify payment method and change")

            # Verify that shipping address was updated
            DashboardHelper.verify_shipping_address_updated(page, index=1)
            framework_logger.info("Successfully verified shipping address updated in Overview page")

            # Verify that billing updated
            DashboardHelper.verify_credit_card_master_updated(page)
            framework_logger.info("Successfully verified credit_card_master_2_series payment method in Overview page")

            framework_logger.info("=== C38108871 - Update info flow completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the update info flow: {e}\n{traceback.format_exc()}")
            raise e
