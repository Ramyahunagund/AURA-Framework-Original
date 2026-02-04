from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.print_history_page import PrintHistoryPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def view_links_for_subscription_with_subscribed_status_and_free_months(stage_callback):
    framework_logger.info("=== C53671883 - View links for Subscription with subscribed status and free months flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        print_history = PrintHistoryPage(page)
        update_plan = UpdatePlanPage(page)
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to subscribed state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click View Print History link on Status Card
            overview_page.view_print_history_link.click()
            framework_logger.info(f"Clicked on View Print History link on Status Card")

            # Validate Print History page was displayed correctly
            expect(print_history.page_title).to_be_visible(timeout=90000)
            expect(print_history.print_history_card_title).to_be_visible()
            expect(print_history.how_is_calculated_link).to_be_visible()
            expect(print_history.total_printed_pages).to_be_visible()
            expect(print_history.plan_pages_bar).to_be_visible()
            expect(print_history.plan_details_card).to_be_visible()
            framework_logger.info(f"Validated Print History page was displayed correctly")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

            # And the user clicks Print and Payment History link on Smart Dashboard > Update Plan page
            update_plan.print_history_link.click()
            framework_logger.info(f"Clicked on Print and Payment History link on Update Plan page")

            # Validate Print History page was displayed correctly
            expect(print_history.page_title).to_be_visible(timeout=90000)
            expect(print_history.print_history_card_title).to_be_visible()
            expect(print_history.how_is_calculated_link).to_be_visible()
            expect(print_history.total_printed_pages).to_be_visible()
            expect(print_history.plan_pages_bar).to_be_visible()
            expect(print_history.plan_details_card).to_be_visible()
            framework_logger.info(f"Validated Print History page was displayed correctly")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

            # Verify Terms and Service link on Update Plan page
            with page.context.expect_page() as new_page_info:
                update_plan.terms_and_service_link.click()
            new_tab = new_page_info.value
            expect(new_tab).to_have_url("https://instantink-stage1.hpconnectedstage.com/us/en/terms")
            new_tab.close()
            page.bring_to_front()
            framework_logger.info("Verified Terms and Service link on Update Plan page")

            framework_logger.info("=== C53671883 - View links for Subscription with subscribed status and free months flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e