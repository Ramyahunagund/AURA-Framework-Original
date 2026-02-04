from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.email_helper import EmailHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def payment_suspension_multi_series(stage_callback):
    framework_logger.info("=== C51743301 - Payment Suspension Multi Series flow started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        try:
            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Add the Page Tally 100 and Shifts for 32 days and update to Payment Problem
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.update_to_payment_problem(page)
            GeminiRAHelper.submit_charge(page)
            framework_logger.info("Charge submited for payment problem")

            # Sees Payment state equals to problem on subscription page
            subscription = RABaseHelper.get_links_by_title(page, "Subscription")
            subscription.click()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "problem")
                        
            # Shift subscription for 14 days
            GeminiRAHelper.event_shift(page, "14")
            framework_logger.info("Event shifted by 14 days")

            # Run the resque job: SuspensionNotificationJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SuspensionNotificationJob",
                                                                      "SubscriptionSuspenderJob"])
            framework_logger.info("SuspensionNotificationJob executed")

            # Sees Payment state equals to suspended on subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.verify_rails_admin_info(page, "Payment state", "suspended")

            # See link with text payment_issue in the Notification events on the Subscription page
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Notification events", "payment_issue")
            
            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Access Notifications Menu
            side_menu.click_notifications()
            framework_logger.info(f"Accessed Notifications in side menu")

            # See "Account suspended" notification on Notification page
            DashboardHelper.see_notification_on_dashboard(page, "Account suspended")
            framework_logger.info(f"Verified 'Account suspended' notification on Notification page")

            # Access Print History page
            side_menu.click_print_history()
            framework_logger.info("Accessed Print History page")
            
            # See "HP Instant Ink Service Suspended" notification on Print History page
            PrintHistoryHelper.see_notification_on_print_history(page, "HP Instant Ink Service Suspended")
            framework_logger.info(f"Verified 'HP Instant Ink Service Suspended' notification on Print History page")

            # Run the resque job: EmailCallSchedulerEventsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["EmailCallSchedulerEventsJob"])
            framework_logger.info("EmailCallSchedulerEventsJob executed")

            # Verify email with subject "account has been suspended"
            EmailHelper.sees_email_with_subject(tenant_email, "account has been suspended")
            framework_logger.info("Verified email with subject 'account has been suspended'")

            # Shift subscription for 14 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "14")
            framework_logger.info("Event shifted by 14 days")

            # Run the resque job: SuspensionNotificationJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SuspensionNotificationJob",
                                                                      "SubscriptionSuspenderJob"])
            framework_logger.info("SuspensionNotificationJob executed")

            # Click link with text payment_suspension in the Notification events on the Subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            time.sleep(10)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "payment_suspension", "Notification events")
            framework_logger.info("Accessed payment_suspension from Notification events")

            # See Event variant equals to day_14-i_ink on Notification events page
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "day_14-i_ink")

            # Run the resque job: EmailCallSchedulerEventsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["EmailCallSchedulerEventsJob"])
            framework_logger.info("EmailCallSchedulerEventsJob executed")

            # Verify email with subject "service has been disabled"
            EmailHelper.sees_email_with_subject(tenant_email, "service has been disabled")
            framework_logger.info("Verified email with subject 'service has been disabled'")

            # Shift subscription for 14 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "14")
            framework_logger.info("Event shifted by 14 days")

            # Run the resque job: SuspensionNotificationJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SuspensionNotificationJob",
                                                                      "SubscriptionSuspenderJob"])
            framework_logger.info("SuspensionNotificationJob executed")

            # Click link with text payment_suspension in the Notification events on the Subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            time.sleep(10)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "payment_suspension", "Notification events")
            framework_logger.info("Accessed payment_suspension from Notification events")

            # See Event variant equals to day_28-i_ink on Notification events page
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "day_28-i_ink")
            
            # Run the resque job: EmailCallSchedulerEventsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["EmailCallSchedulerEventsJob"])
            framework_logger.info("EmailCallSchedulerEventsJob executed")

            # Verify email with subject "service has been disabled"
            EmailHelper.sees_email_with_subject(tenant_email, "service has been disabled")
            framework_logger.info("Verified email with subject 'service has been disabled'")

            # Shift subscription for 28 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "28")
            framework_logger.info("Event shifted by 28 days")

            # Run the resque job: SuspensionNotificationJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SuspensionNotificationJob",
                                                                      "SubscriptionSuspenderJob"])
            framework_logger.info("SuspensionNotificationJob executed")

            # Click link with text payment_suspension in the Notification events on the Subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            time.sleep(10)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "payment_suspension", "Notification events")
            framework_logger.info("Accessed payment_suspension from Notification events")

            # See Event variant equals to day_56-i_ink on Notification events page
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "day_56-i_ink")
            
            # Run the resque job: EmailCallSchedulerEventsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["EmailCallSchedulerEventsJob"])
            framework_logger.info("EmailCallSchedulerEventsJob executed")

            # Verify email with subject "service has been disabled"
            EmailHelper.sees_email_with_subject(tenant_email, "service has been disabled")
            framework_logger.info("Verified email with subject 'service has been disabled'")

            # Shift subscription for 56 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "56")
            framework_logger.info("Event shifted by 56 days")

            # Run the resque job: SuspensionNotificationJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SuspensionNotificationJob",
                                                                      "SubscriptionSuspenderJob"])
            framework_logger.info("SuspensionNotificationJob executed")

            # Click link with text payment_suspension in the Notification events on the Subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            time.sleep(10)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "payment_suspension", "Notification events")
            framework_logger.info("Accessed payment_suspension from Notification events")

            # See Event variant equals to day_112-i_ink on Notification events page
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "day_112-i_ink")
            
            # Run the resque job: EmailCallSchedulerEventsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["EmailCallSchedulerEventsJob"])
            framework_logger.info("EmailCallSchedulerEventsJob executed")

            # Verify email with subject "service has been disabled"
            EmailHelper.sees_email_with_subject(tenant_email, "service has been disabled")
            framework_logger.info("Verified email with subject 'service has been disabled'")

            # Shift subscription for 56 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "56")
            framework_logger.info("Event shifted by 56 days")

            # Run the resque job: SuspensionNotificationJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SuspensionNotificationJob",
                                                                      "SubscriptionSuspenderJob"])
            framework_logger.info("SuspensionNotificationJob executed")

            # Click link with text payment_suspension in the Notification events on the Subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            time.sleep(10)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "payment_suspension", "Notification events")
            framework_logger.info("Accessed payment_suspension from Notification events")

            # See Event variant equals to day_168-i_ink on Notification events page
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "day_168-i_ink")
            
            # Run the resque job: EmailCallSchedulerEventsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["EmailCallSchedulerEventsJob"])
            framework_logger.info("EmailCallSchedulerEventsJob executed")

            # Verify email with subject "service has been disabled"
            EmailHelper.sees_email_with_subject(tenant_email, "service has been disabled")
            framework_logger.info("Verified email with subject 'service has been disabled'")
            
            # Shift subscription for 56 days
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "56")
            framework_logger.info("Event shifted by 56 days")

            # Run the resque job: SuspensionNotificationJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["SuspensionNotificationJob",
                                                                      "SubscriptionSuspenderJob"])
            framework_logger.info("SuspensionNotificationJob executed")

            # Click link with text payment_suspension in the Notification events on the Subscription page
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            time.sleep(10)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "payment_suspension", "Notification events")
            framework_logger.info("Accessed payment_suspension from Notification events")

            # See Event variant equals to day_224-i_ink on Notification events page
            GeminiRAHelper.verify_rails_admin_info(page, "Event variant", "day_224-i_ink")
            
            # Run the resque job: EmailCallSchedulerEventsJob
            RABaseHelper.complete_jobs(page, common._instantink_url, ["EmailCallSchedulerEventsJob"])
            framework_logger.info("EmailCallSchedulerEventsJob executed")

            # Verify email with subject "service has been disabled"
            EmailHelper.sees_email_with_subject(tenant_email, "service has been disabled")
            framework_logger.info("Verified email with subject 'service has been disabled'")

            framework_logger.info("=== C51743301 - Payment Suspension Multi Series flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
