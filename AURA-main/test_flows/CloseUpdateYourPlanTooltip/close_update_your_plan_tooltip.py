from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.privacy_banner_page import PrivacyBannerPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def close_update_your_plan_tooltip(stage_callback):
    framework_logger.info("=== C41445730 - Close update your plan tooltip flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        overview_page = OverviewPage(page)
        privacy_banner_page = PrivacyBannerPage(page)
        side_menu = DashboardSideMenuPage(page)
        update_plan = UpdatePlanPage(page)

        try:
            # Access Overview page
            DashboardHelper.access(page, tenant_email)
            privacy_banner_page.accept_privacy_banner()
            side_menu.click_overview()
            framework_logger.info(f"Accessed Overview page with tenant email: {tenant_email}")

            # Click continue in the modal setting your preferences
            overview_page.continue_setting_preferences.click()
            overview_page.accept_all_preferences.click()
            framework_logger.info("Clicked continue in the modal setting your preferences")
            
            # Click start tour button and closed update your plan tooltip on Overview page
            overview_page.start_tour.click(timeout=90000)
            expect(overview_page.next_button_update_your_plan_tooltip).to_be_visible()
            overview_page.tour_tooltip_close_button.click()
            overview_page.tour_tooltip_close_button.wait_for(state="detached")
            framework_logger.info("Clicked start tour button and closed Update your plan tooltip on Overvie page")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

            # Access Overview page
            side_menu.click_overview()
            expect(overview_page.plan_details_card).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Overview page")

            # Verify tour modal does not appear on Overview page
            expect(overview_page.start_tour).not_to_be_visible()
            framework_logger.info(f"Verified that the tour modal does not appear on the Overview page")

            # And gemini user closes the browser
            page.close()
            framework_logger.info(f"Closed the browser")

            # Access Overview page with new page
            new_page = page.context.new_page()
            new_overview_page = OverviewPage(new_page)
            new_privacy_banner_page = PrivacyBannerPage(new_page)
            new_side_menu = DashboardSideMenuPage(new_page)

            DashboardHelper.access(new_page, tenant_email)
            new_privacy_banner_page.accept_privacy_banner()
            new_side_menu.click_overview()
            expect(new_overview_page.plan_details_card).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Overview page")

            # Verify tour modal does not appear on Overview page
            expect(new_overview_page.start_tour).not_to_be_visible()
            framework_logger.info(f"Verified that the tour modal does not appear on the Overview page")

            framework_logger.info("=== C41445730 - Close update your plan tooltip flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e