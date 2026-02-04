from datetime import datetime, timedelta
import re
from helper.ra_base_helper import RABaseHelper
from pages.cancellation_timeline_page import CancellationTimelinePage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.notifications_page import NotificationsPage
from pages.print_history_page import PrintHistoryPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.update_plan_helper import UpdatePlanHelper
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def initiated_unsubscription(stage_callback):
    framework_logger.info("=== C57415728 - Initiated Unsubscription started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        notifications_page = NotificationsPage(page)
        print_history_page = PrintHistoryPage(page)

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

            # Cancel subscription
            UpdatePlanHelper.cancellation_subscription(page)
            framework_logger.info("Subscription cancellation initiated")

            # Verifies the First and Third steps section on Cancellation Timeline Page
            cancellation_timeline_page = CancellationTimelinePage(page)
            today = datetime.today()
            
            # Time definition
            text = cancellation_timeline_page.cancellation_step(1).text_content()
            last_day = re.search(r'([A-Za-z]{3} \d{2}, \d{4})', text).group(1)
            last_day_date = datetime.strptime(last_day, '%b %d, %Y')
            current_date = today.strftime('%b %d, %Y')
            final_bill_first = last_day_date + timedelta(days=1)
            final_bill_date = final_bill_first.strftime('%b %d, %Y')

           
            expect(cancellation_timeline_page.first_step_icon).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step(0)).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step_title(0)).to_contain_text(f"{current_date}: Cancellation submitted")

            expect(cancellation_timeline_page.third_step_icon(2)).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step(2)).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step_title(2)).to_contain_text(f"{final_bill_date}: Instant Ink cartridges deactivated")
            framework_logger.info("Verified the First and Third steps section on Cancellation Timeline Page")

            # Go to overview and validate pause plan pending message
            side_menu.click_overview()
            DashboardHelper.sees_cancellation_in_progress(page)
            framework_logger.info("Verified cancellation in progress on Overview page")

            # Clicks link with text cancellation in the Notification events on the Subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_link_by_text_on_rails_admin(page, "cancellation", "Notification events")
            assert RABaseHelper.get_field_text_by_title(page, "Event variant") == "initiate_cancel_flex-i_ink"
            framework_logger.info("Verified cancellation initiated on Rails Admin")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Click notification icon
            notifications_page.notifications_icon.click()
            framework_logger.info(f"Clicked on notifications icon")

            # Sees "Your request to cancel your HP Instant Ink subscription" notification
            notifications_text = notifications_page.notifications_table.text_content()            
            assert "Your request to cancel your HP Instant Ink subscription" in notifications_text
            framework_logger.info(f"Verified cancellation notification")

            # Access Notifications Menu
            side_menu.expand_my_account_menu()
            side_menu.click_notifications()
            framework_logger.info(f"Opened Notifications page")

            # Sees "Your cancellation will be final on" notification
            assert "Your cancellation will be final on" in page.content(), "Expected cancellation final notification not found"
            framework_logger.info(f"Verified cancellation final notification")

            # Access Print History
            side_menu.click_print_history()
            framework_logger.info(f"Opened Print History page")

            # Sees "HP Instant Ink Service Cancellation Requested" message on Print and Payment History page
            print_history_page.print_history_table_button.click()
            assert "HP Instant Ink Service Cancellation Requested" in print_history_page.print_history_table.text_content(timeout=5000)
            framework_logger.info(f"Verified cancellation message on Print and Payment History page")

            # Clicks link with text cancellation in the Notification events on the Subscription page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_link_by_text_on_rails_admin(page, "cancellation", "Notification events")
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "sent")
            framework_logger.info("Verified cancellation completed on Rails Admin")

            # Clicks on Template Data menu
            RABaseHelper.access_menu_of_page(page, "Template Data")
            framework_logger.info("Accessed Template Data menu on Rails Admin")

            # Validates final charge and cancel initiate date in notifications events is equal to the cancellation timeline page with 0 days to add
            RABaseHelper.validate_template_data(page, current_date, final_bill_date)
            framework_logger.info("Validated Template Data final charge and cancel initiate date")

            framework_logger.info("=== C57415728 - Initiated Unsubscription finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
