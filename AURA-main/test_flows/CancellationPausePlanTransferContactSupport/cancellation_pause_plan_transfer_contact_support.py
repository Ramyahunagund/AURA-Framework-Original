from helper.cancellation_plan_helper import CancellationPlanHelper
from pages.cancellation_page import CancellationPage
from pages.overview_page import OverviewPage
from pages.printer_replacement_page import PrinterReplacementPage
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

def cancellation_pause_plan_transfer_contact_support(stage_callback):
    framework_logger.info("=== C42996363 - Cancellation - Pause plan , Transfer and contact support started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            overview_page = OverviewPage(page)
            side_menu = DashboardSideMenuPage(page)
            cancellation_page = CancellationPage(page)


            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Clicks on Cancel Instant Ink on Plan Details Card
            overview_page.cancel_instant_ink.click()
            framework_logger.info(f"Clicked on Cancel Instant Ink button")

            # Click to contact our expert support on Cancellation Summary page
            with page.context.expect_page() as new_page_info:
                cancellation_page.contact_hp_support_link.click()
            new_tab = new_page_info.value
            new_tab.locator('[class="close-btn"]').click()
            assert "HP Instant Ink support" in new_tab.content(), "HP Instant Ink support is not present on the page"
            new_tab.close()
            framework_logger.info("Clicked to contact our expert support on Cancellation Summary page")

            #  Access the Overview page and clicks on Cancel Instant INk
            page.bring_to_front()
            side_menu.click_overview()
            overview_page.cancel_instant_ink.click()
            framework_logger.info(f"Clicked on Cancel Instant Ink button again")

            # Validates Pause Plan link on Cancellation Summary Page
            CancellationPlanHelper.validate_cancellation_links(page, "Pause Plan")
            framework_logger.info(f"Validated Pause Plan link on Cancellation Summary Page")

            #  Access the Overview page and clicks on Cancel Instant INk
            side_menu.click_overview()
            overview_page.cancel_instant_ink.click()
            framework_logger.info(f"Clicked on Cancel Instant Ink button again")

            # Validates Transfer Subscription link on Cancellation Summary Page
            CancellationPlanHelper.validate_cancellation_links(page, "Transfer to other printer")
            with page.context.expect_page() as new_page_info:
                new_tab = new_page_info.value
            printer_replacement_page =  PrinterReplacementPage(new_tab)
            expect(printer_replacement_page.printer_not_set_up_button).to_be_visible(timeout=600000)
            framework_logger.info(f"Validated Transfer Subscription link on Cancellation Summary Page")

            framework_logger.info("=== C42996363 - Cancellation - Pause plan , Transfer and contact support finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()