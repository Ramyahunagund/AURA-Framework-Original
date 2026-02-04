import re
from helper.email_helper import EmailHelper
from pages.hpid_page import HPIDPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from playwright.sync_api import expect
import urllib3
import test_flows_common.test_flows_common as common
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def notifications_extended_invoice(stage_callback):
    framework_logger.info("=== C50559204 - Notifications extended - invoice started ===")
    tenant_email = create_ii_subscription(stage_callback)

    with PlaywrightManager() as page:
        try:
            # Move to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.remove_free_months(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            framework_logger.info(f"Subscription moved to 'Subscribed' state")

            # Access Dashboard
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Pause plan for 2 months on Overview page
            DashboardHelper.pause_plan(page, 2)
            framework_logger.info(f"Paused plan for 2 months on Overview page")

            # First billing cycle
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "32", "100")

            GeminiRAHelper.complete_jobs(page, 
                    ["SubscriptionBillingJob", 
                    "FetchImmutableDataDispatcherJob",
                    "PrepareImmutableInvoiceDispatcherJob",
                    "PrepareIdocsForFinanceDispatcherJob"
                    ])
            framework_logger.info(f"Executed resque jobs: SubscriptionBillingJob, FetchImmutableDataDispatcherJob, PrepareImmutableInvoiceDispatcherJob")

            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "invoice", "Notification events")
            RABaseHelper.wait_page_to_load(page, "Notification event")
            RABaseHelper.access_menu_of_page(page, "Template Data")

            has_pause_plan = GeminiRAHelper.get_template_data(page, "has_pause_plan")
            assert has_pause_plan is True, "Expected 'has_pause_plan' to be True"
            framework_logger.info(f"Verified 'has_pause_plan' is True in Template Data")

            # Second billing cycle
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "32", "100")

            GeminiRAHelper.complete_jobs(page, 
                    ["SubscriptionBillingJob", 
                    "FetchImmutableDataDispatcherJob",
                    "PrepareImmutableInvoiceDispatcherJob",
                    "PrepareIdocsForFinanceDispatcherJob"
                    ])
            framework_logger.info(f"Executed resque jobs: SubscriptionBillingJob, FetchImmutableDataDispatcherJob, PrepareImmutableInvoiceDispatcherJob")

            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            RABaseHelper.access_link_by_title(page, "invoice", "Notification events")
            RABaseHelper.wait_page_to_load(page, "Notification event")
            RABaseHelper.access_menu_of_page(page, "Template Data")
            has_pause_plan = GeminiRAHelper.get_template_data(page, "has_pause_plan")
            assert has_pause_plan is True, "Expected 'has_pause_plan' to be True"
            framework_logger.info(f"Verified 'has_pause_plan' is True in Template Data")

            # Dashboard validation
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Sees the Notification:Invoice
            DashboardHelper.see_notification_on_bell_icon(page, "HP Instant Ink Billing Statement")
            framework_logger.info("Notification: Invoice verified")

            # Verify the email 
            email_details = EmailHelper.extract_email_details(tenant_email, "Review your HP Instant Ink statement.", timeout = 1000)
            framework_logger.info(f"Email subject: {email_details.get('subject', '')}")
            assert email_details['subject'] == "Review your HP Instant Ink statement.", f"Expected subject to be 'Review your HP Instant Ink statement.' but got '{email_details['subject']}'"
            content = email_details['html_body']

            # Validate the email
            assert common.DEFAULT_FIRSTNAME.capitalize() in content, f"Expected first name '{common.DEFAULT_FIRSTNAME}' not found in email body"
            printer_name = common.printer_data()["name"]
            normalized_name = re.search(r"^(.*? \d+\w*)\b", printer_name).group(1)
            assert normalized_name in content, f"Expected printer model '{normalized_name}' not found in email body"
            assert "10 pages" in content, f"Expected '10 pages' not found in email body"

            # Get the link from email
            link = re.search(r'<a[^>]+href="([^"]*instantink.hpsmart[^"]*)"', content).group(1)
            page.goto(link)
            hpid_page = HPIDPage(page)
            hpid_page.wait.username()
            framework_logger.info("Email content verified successfully")

            # Third billing cycle - unpause plan and verify has_pause_plan is False
            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "32", "100")
            GeminiRAHelper.access_subscription(page)
            RABaseHelper.access_link_by_title(page, "invoice", "Notification events")
            RABaseHelper.wait_page_to_load(page, "Notification event")
            RABaseHelper.access_menu_of_page(page, "Template Data")

            has_pause_plan = GeminiRAHelper.get_template_data(page, "has_pause_plan")
            assert has_pause_plan is False, "Expected 'has_pause_plan' to be False"
            framework_logger.info(f"Verified 'has_pause_plan' is False in Template Data")

            # Notification validation on Dashboard and email
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Opened Instant Ink Dashboard")

            # Sees the Notification:Invoice
            DashboardHelper.see_notification_on_bell_icon(page, "HP Instant Ink Billing Statement")
            framework_logger.info("Notification: Invoice verified")

            # Verify the email
            EmailHelper.sees_email_with_subject(tenant_email, "Review your HP Instant Ink statement.")
            framework_logger.info(f"Email with subject 'Review your HP Instant Ink statement.' verified")

            framework_logger.info("=== C50559204 - Notifications extended - invoice finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow C50559204: {e}\n{traceback.format_exc()}")
            raise e
