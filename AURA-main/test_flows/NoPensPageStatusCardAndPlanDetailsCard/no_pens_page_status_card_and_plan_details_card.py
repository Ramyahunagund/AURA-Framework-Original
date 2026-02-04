from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.dashboard_helper import DashboardHelper
from pages.overview_page import OverviewPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.print_history_helper import PrintHistoryHelper
from playwright.sync_api import expect


def no_pens_page_status_card_and_plan_details_card(stage_callback) -> None:
    framework_logger.info("=== C41854607 - No Pens Page status card and plan details card flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)
            dashboard_side_menu_page = DashboardSideMenuPage(page)

            # Remove free months from tenant
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Free months removed from tenant")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Verify the Status card
            DashboardHelper.sees_status_card(page)
            framework_logger.info(f"Verified Status card is visible")

            # Verify that no billing cycle information is displayed in status card
            expect(overview_page.view_print_history_link).not_to_be_visible()
            expect(overview_page.plan_pages_bar).not_to_be_visible()
            expect(overview_page.rollover_pages_bar).not_to_be_visible()
            framework_logger.info(f"Verified that no billing cycle information is displayed in status card")

            # Verify a green icon with information about subscription cartridges on status card
            expect(overview_page.notification_status_card).to_be_visible()
            framework_logger.info(f"Verified a green icon with information about subscription cartridges on status card")

            # Verify Plan Details card
            DashboardHelper.sees_plan_details_card(page)
            expect(overview_page.subscription_id).to_be_visible()
            expect(overview_page.cancel_instant_ink).to_be_visible()
            expect(overview_page.redeem_code_link).to_be_visible()
            expect(overview_page.billing_section_plan_details).to_be_visible()
            expect(overview_page.shipping_section_plan_details).to_be_visible()
            framework_logger.info(f"Verified Plan Details card is visible")

            # Verify free months are not displayed in Plan Details card
            DashboardHelper.doesnt_see_free_months(page)
            framework_logger.info(f"Verified free months are not displayed in Plan Details card")

            # Verify free months are not displayed in Print History
            dashboard_side_menu_page.click_print_history()
            PrintHistoryHelper.doesnt_see_free_months(page)
            framework_logger.info(f"Verified free months are not displayed in Print History")

            framework_logger.info(f"=== C41854607 - No Pens Page status card and plan details card flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred: {e}")
