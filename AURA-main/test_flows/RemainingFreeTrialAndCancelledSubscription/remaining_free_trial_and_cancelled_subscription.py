from core.playwright_manager import PlaywrightManager
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.dashboard_helper import DashboardHelper
from pages.update_plan_page import UpdatePlanPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from helper.cancellation_plan_helper import CancellationPlanHelper
from core.settings import framework_logger
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web
from playwright.sync_api import expect

def remaining_free_trial_and_cancelled_subscription(stage_callback):
    tenant_email = enrollment_ink_web(stage_callback)
    framework_logger.info("=== C41928374 - Remaining free trial and cancelled subscription on Update plan page started ===")

    with PlaywrightManager() as page:
        try:
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            update_plan_page = UpdatePlanPage(page)

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Free months removed")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Update Plan page
            dashboard_side_menu_page.click_update_plan()
            expect(update_plan_page.page_title).to_be_visible()

            # Does not see free months in Update Plan page
            UpdatePlanHelper.doesnt_see_free_months(page)
            framework_logger.info(f"Verified free months are not displayed in Update Plan page")

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info(f"Subscription cancellation")

            # Sees the Overview page of cancelled subscription
            DashboardHelper.sees_canceled_subscription_overview_page(page)
            framework_logger.info("Verified Overview page of cancelled subscription")

            # Access subscription on Gemini RA
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info(f"Accessed Subscription page for tenant {tenant_email}")

            # Verify subscription state is obsolete
            GeminiRAHelper.verify_rails_admin_info(page, "State", "obsolete")
            framework_logger.info("Verified subscription state is obsolete")
            framework_logger.info(f"=== C41928374 - Remaining free trial and cancelled subscription on Update plan page finished ===")
        except Exception as e:
            framework_logger.error(f"Error during flow execution: {e}")
            raise e
        finally:
            page.close()
