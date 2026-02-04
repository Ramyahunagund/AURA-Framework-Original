from time import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.cancellation_banner_page import CancellationBannerPage
from pages.cancellation_timeline_page import CancellationTimelinePage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


TC="C44199184"
def cancellation_sub_initiated_unsubscribe_print_and_payment_shipment_tracking(stage_callback):
    framework_logger.info("=== Test started ===")
    common.setup()
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"Generated tenant_email={tenant_email}")
    with PlaywrightManager() as page:
        try:
            # Move to subscribed and get user data
            GeminiRAHelper.access(page)
            tenant_id = GeminiRAHelper.access_tenant_page(page, tenant_email)
            subscription_id = GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Dashboard first access completed successfully")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info(f"Subscription cancellation")

            cancel_date_list = DashboardHelper.get_list_with_end_date_from_cancellation_timeline(page)
            # Validations on print history
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            dashboard_side_menu_page.click_print_history()

            # get subscription data
            common.validate_subscription_state(subscription_id, "initiated-unsubscribe")

            DashboardHelper.verify_cancellation_banner(page, cancel_date_list)
            framework_logger.info("Cancellation banner verified successfully")

            DashboardHelper.validate_see_cancellation_timeline_feature(page)
            framework_logger.info("See cancellation timeline feature validated successfully")

            DashboardHelper.validate_keep_enrollment_feature(page)
            framework_logger.info("Keep enrollment feature validated successfully")

            common.validate_subscription_state(subscription_id, "subscribed")
            framework_logger.info("Print history validations completed successfully")

            dashboard_side_menu_page.click_update_plan()
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info(f"Subscription cancellation")

            cancel_date_list = DashboardHelper.get_list_with_end_date_from_cancellation_timeline(page)

            # Validations on shipment tracking
            dashboard_side_menu_page.click_shipment_tracking()

            # get subscription data
            common.validate_subscription_state_by_me(page, "initiated-unsubscribe")

            DashboardHelper.verify_cancellation_banner(page, cancel_date_list)
            framework_logger.info("Cancellation banner verified successfully")

            DashboardHelper.validate_see_cancellation_timeline_feature(page)
            framework_logger.info("See cancellation timeline feature validated successfully")

            DashboardHelper.validate_keep_enrollment_feature(page)
            framework_logger.info("Keep enrollment feature validated successfully")

            # get subscription data
            common.validate_subscription_state(subscription_id, "subscribed")

            framework_logger.info("Test completed successfully")
        except Exception as e:
            framework_logger.error(f"Test with Error: {e}\n{traceback.format_exc()}")
            raise e
