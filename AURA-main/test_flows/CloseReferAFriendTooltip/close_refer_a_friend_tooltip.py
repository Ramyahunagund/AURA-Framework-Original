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

def close_refer_a_friend_tooltip(stage_callback):
    framework_logger.info("=== C41447878 - Close Refer a Friend tooltip flow started ===")
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

            # Scroll down the page
            page.mouse.wheel(0, 600)
            # Scroll up the page
            page.mouse.wheel(0, -600)
            framework_logger.info("Scrolled down and up the page")

            # Clicks start tour button on Overview page
            overview_page.start_tour.click()
            expect(overview_page.next_button_update_your_plan_tooltip).to_be_visible()
            framework_logger.info("Clicked start tour button on Overview page")

            # Scroll down the page
            page.mouse.wheel(0, 600)
            # Scroll up the page
            page.mouse.wheel(0, -600)
            framework_logger.info("Scrolled down and up the page")

            # Clicks next button on the Update your Plan tooltip
            overview_page.next_button_update_your_plan_tooltip.click()
            expect(overview_page.next_button_billing_shipping_tooltip).to_be_visible()
            framework_logger.info("Clicked next button on the Update your Plan tooltip")

            # Scroll down the page
            page.mouse.wheel(0, 600)
            # Scroll up the page
            page.mouse.wheel(0, -600)
            framework_logger.info("Scrolled down and up the page")

            # Click next button on the Billing and Shipping tooltip
            overview_page.next_button_billing_shipping_tooltip.click()
            expect(overview_page.last_button_raf_tooltip).to_be_visible()
            framework_logger.info("Clicked next button on the Billing and Shipping tooltip")

            # Scroll down the page
            page.mouse.wheel(0, 600)
            # Scroll up the page
            page.mouse.wheel(0, -600)
            framework_logger.info("Scrolled down and up the page")

            # See the Refer a Friend tooltip and close it
            overview_page.last_button_raf_tooltip.click()
            overview_page.last_button_raf_tooltip.wait_for(state="detached")
            framework_logger.info("Closed the Refer a Friend tooltip")

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

            framework_logger.info("=== C41447878 - Close Refer a Friend tooltip flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e