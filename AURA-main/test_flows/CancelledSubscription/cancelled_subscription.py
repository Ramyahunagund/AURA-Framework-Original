from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.cancellation_plan_helper import CancellationPlanHelper
from helper.dashboard_helper import DashboardHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from helper.update_plan_helper import UpdatePlanHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import time
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cancelled_subscription(stage_callback):
    framework_logger.info("=== C38276285 - Cancelled subscription flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        update_plan = UpdatePlanPage(page)
        overview_page = OverviewPage(page)
        try:
            # Send new WK
            trigger_id = GeminiRAHelper.process_new_wk(page, tenant_email)
            framework_logger.info(f"Gemini Rails Admin: New cartridge send by trigger_id: {trigger_id}")

            # Verify Order and send it to Fulfillment Simulator
            fulfillment_service_order_link = FFSRV.receive_and_send_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} received and sent. Order link: {fulfillment_service_order_link}")

            # Update order
            FFSIML.process_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Simulator: Order {trigger_id} processed successfully")

            # Verify Order
            FFSRV.validate_order_received(page, "statusShipped", "standard", trigger_id=trigger_id, order_link=fulfillment_service_order_link)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} updated and verified successfully")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info(f"Accessed Update Plan page")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            CancellationPlanHelper.select_cancellation_feedback_option(page)
            framework_logger.info("Subscription cancellation initiated")

            # Access Overview page
            side_menu.click_overview()
            framework_logger.info(f"Accessed Overview page")

            # Cancellation in progress on overview page
            DashboardHelper.sees_cancellation_in_progress(page)
            framework_logger.info("Verified cancellation in progress on Overview page")

            # Access Update Plan page
            side_menu.click_update_plan()
            expect(update_plan.page_title).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Update Plan page")

            # And the user does not see Cancel Subscription link on Update Plan page
            expect(update_plan.cancel_instant_ink).not_to_be_visible(timeout=90000)
            framework_logger.info("Verified Cancel Subscription link is not visible on Update Plan page")

            # And the user checks if the plans are disabled on Update Plan page
            plan_cards = page.locator("[data-testid^='plans-selector-plan-card-container-']")
            count = plan_cards.count()
            for i in range(count):
                plan_locator = update_plan.get_plan_by_position(i)
                button = plan_locator.locator("button")
                expect(button).to_be_disabled()
            framework_logger.info("Verified all plans are disabled on Update Plan page")

            # Access Overview page
            side_menu.click_overview()
            framework_logger.info(f"Accessed Overview page")

            # Cancellation in progress on overview page
            DashboardHelper.sees_cancellation_in_progress(page)
            framework_logger.info("Verified cancellation in progress on Overview page")

            # Verify subscription state is initiated_unsubscribe
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "State", "initiated_unsubscribe")

            # Shift subscription for 32 days
            GeminiRAHelper.event_shift(page, "32")
            framework_logger.info("Shifted subscription for 32 days")

            # Executes the resque job SubscriptionUnsubscriberJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionUnsubscriberJob"])
            framework_logger.info("Executed SubscriptionUnsubscriberJob")

            # Charge a new billing cycle with 31 pages
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.access_billing_summary_page(page)
            GeminiRAHelper.calculate_and_define_page_tally(page, "31")
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with 31 pages")

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            expect(overview_page.plan_details_card).to_be_visible(timeout=90000)
            framework_logger.info(f"Accessed Overview page")

            # And the user does not see cancel link or keep enrollment button in the plan details card on the Overview page
            expect(overview_page.cancel_instant_ink).not_to_be_visible()
            expect(overview_page.keep_enrollment_button).not_to_be_visible()
            framework_logger.info("Verified cancel link and keep enrollment button are not visible on Overview page")

            # Access Update Plan page
            side_menu.click_update_plan()
            framework_logger.info(f"Accessed Update Plan page")

            # Verify it redirects to Overview page
            expect(overview_page.page_title).to_be_visible(timeout=90000)
            framework_logger.info("Verified Update Plan page redirects to Overview page")

            # Verify not enrolled warning on the Overview page
            expect(overview_page.no_active_plans).to_be_visible(timeout=30000)
            framework_logger.info("Verified not enrolled warning is visible on Overview page")

            # Shift subscription for 40 days
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "40")
            framework_logger.info("Shifted subscription for 40 days")

            # Executes the resque job SubscriptionObsoleteJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SubscriptionObsoleteJob"])
            framework_logger.info("Executed SubscriptionObsoleteJob")

            # And the user verifies the subscription state is Obsolete
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            start_time = time.time()
            while time.time() - start_time < 60:
                try:
                    GeminiRAHelper.verify_rails_admin_info(page, "State", "obsolete")
                    break
                except Exception:
                    page.reload()
                    time.sleep(2)

            # Access Overview page
            DashboardHelper.access(page)
            side_menu.click_overview()
            framework_logger.info(f"Accessed Overview page")

            # Verify no active plans message in the Plan Details card
            expect(overview_page.no_active_plans).to_be_visible(timeout=90000)
            framework_logger.info("Verified no active plans message is visible in the Plan Details card on Overview page")

            framework_logger.info("=== C38276285 - Cancelled subscription flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e