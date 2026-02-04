from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
from helper.print_history_helper import PrintHistoryHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.print_history_page import PrintHistoryPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TC = "C48415873 | C48543325"
def billing_cycle_with_base_charge_and_overage_charge(stage_callback):
    framework_logger.info("=== Billing Cycle with Base Charge and Overage Charge flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # 1) HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer
        common.create_and_claim_virtual_printer()

    with PlaywrightManager() as page:
        side_menu = DashboardSideMenuPage(page)
        print_history_page = PrintHistoryPage(page)
        try:
            pages_amount = 700
            overage_blocks = 3
            plan_data = common.get_filtered_plan_data(value=pages_amount)[0]
            overage_pages = plan_data["overageBlockSize"] * overage_blocks

             # Start enrollment and sign in
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            framework_logger.info(f"Enrollment started and signed in with email: {tenant_email}")

            # Select printer
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")
            
            # plans
            EnrollmentHelper.select_plan(page, pages_amount)
            framework_logger.info(f"Plan selected: {pages_amount}")

            # Choose hp checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"HP Checkout selected")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Add prepaid with tax paid enabled
            prepaid_code = common.offer_request("12324")
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 20)

            # Add prepaid with tax paid  disabled
            prepaid_code = common.offer_request("12325")
            EnrollmentHelper.apply_and_validate_prepaid_code(page, prepaid_code, 40)

            # Finish enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info(f"Finished enrollment with prepaid")

            # Move to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Charge a new billing cycle with 730 pages
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "32")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, str(pages_amount + overage_pages))
            GeminiRAHelper.submit_charge(page)
            framework_logger.info(f"New billing cycle charged with {pages_amount + overage_pages} pages")

            # Executes the resque jobs: SubscriptionBillingJob, FetchImmutableDataDispatcherJob, PrepareImmutableInvoiceDispatcherJob 
            GeminiRAHelper.complete_jobs(page, 
                                         ["SubscriptionBillingJob", 
                                          "FetchImmutableDataDispatcherJob",
                                          "PrepareImmutableInvoiceDispatcherJob"
                                         ])
            framework_logger.info(f"Executed resque jobs: SubscriptionBillingJob, FetchImmutableDataDispatcherJob, PrepareImmutableInvoiceDispatcherJob")

            # See Charge complete status true on billing cycle page
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.click_billing_cycle_by_status(page, "PEGASUS-SUCCESS")
            GeminiRAHelper.verify_charge_complete(page)

            # See Status code equals to PEGASUS-SUCCESS on Billing cycle page
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", "PEGASUS-SUCCESS")

            # See that the value of Invoice items include BaseChargeInvoiceItem on Billing cycle page
            links = RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "BaseChargeInvoiceItem")
            assert len(links) > 0, "BaseChargeInvoiceItem link not found"
            framework_logger.info("Verified BaseChargeInvoiceItem link on Billing cycle page")

            # See that the value of Invoice items include OverageInvoiceItem on Billing cycle page
            links = RABaseHelper.get_links_with_text_by_title(page, "Invoice items", "OverageInvoiceItem")
            assert len(links) > 0, "OverageInvoiceItem link not found"
            framework_logger.info("Verified OverageInvoiceItem link on Billing cycle page")

            # Click on the first link in the Payment events on the Billing cycle page
            RABaseHelper.get_links_with_text_by_title(page, "Payment events", "PaymentEvent")[0].click()
            framework_logger.info("Accessed first PaymentEvent link from Billing cycle page")

            # See Pretax cents equals to 1199 on Payment events page
            GeminiRAHelper.verify_field_is_positive(page, "Pretax cents")

            # See Tax cents equals to 106 on Payment events page
            GeminiRAHelper.verify_field_is_positive(page, "Tax cents")

            # Click link with text PEGASUS-SUCCESS in the Billing cycle
            RABaseHelper.access_link_by_title(page, "PEGASUS-SUCCESS", "Billing cycle")
            framework_logger.info("Accessed PEGASUS-SUCCESS from Billing cycle")

            # Click on the second link in the Payment events on the Billing cycle page
            RABaseHelper.get_links_with_text_by_title(page, "Payment events", "PaymentEvent")[1].click()
            framework_logger.info("Accessed second PaymentEvent link from Billing cycle page")
            
            # See Pretax cents equals to 2000 on Payment events page
            GeminiRAHelper.verify_field_is_positive(page, "Pretax cents")

            # See Tax cents equals to 0 on Payment events page
            GeminiRAHelper.verify_rails_admin_info(page, "Tax cents", "0")

            # Click link with text PEGASUS-SUCCESS in the Billing cycle
            RABaseHelper.access_link_by_title(page, "PEGASUS-SUCCESS", "Billing cycle")
            framework_logger.info("Accessed PEGASUS-SUCCESS from Billing cycle")

            # Click link with text PEGASUS-SUCCESS in the Request events on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "PEGASUS-SUCCESS", "Request events")
            framework_logger.info("Accessed PEGASUS-SUCCESS from Request events")

            # See Charge amount cents to be positive on request event page
            GeminiRAHelper.verify_field_is_positive(page, "Charge amount cents")

            # Click link with text PEGASUS-SUCCESS in the Billing cycle
            RABaseHelper.access_link_by_title(page, "PEGASUS-SUCCESS", "Billing cycle")
            framework_logger.info("Accessed PEGASUS-SUCCESS from Billing cycle")

            # Click link with text PEGASUS-PARTIAL in the Request events on the Billing cycle page
            RABaseHelper.access_link_by_title(page, "PEGASUS-PARTIAL", "Request events")
            framework_logger.info("Accessed PEGASUS-PARTIAL from Request events")

            # See Charge amount cents to be positive on request event page
            GeminiRAHelper.verify_field_is_positive(page, "Charge amount cents")
            framework_logger.info("Verified Charge amount cents is positive on Request event page")

            # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page for tenant: {tenant_email}")

            # Access Print History Page
            side_menu.click_print_history()
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
            framework_logger.info("Accessed Print History page")

            # Click Download All Invoices button on Print and Payment History page
            PrintHistoryHelper.click_download_all_invoices(page)
            framework_logger.info("Clicked Download All Invoices button on Print and Payment History page")

            framework_logger.info("=== Billing Cycle with Base Charge and Overage Charge flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e