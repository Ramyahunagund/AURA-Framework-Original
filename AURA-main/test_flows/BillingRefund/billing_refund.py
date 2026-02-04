from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.print_history_helper import PrintHistoryHelper
from helper.ra_base_helper import RABaseHelper
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.print_history_page import PrintHistoryPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
import test_flows_common.test_flows_common as common

import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_refund(stage_callback):
    framework_logger.info("=== C44553587 - Refund test flow started ===")

    tenant_email = create_ii_subscription(stage_callback)
    with PlaywrightManager() as page:
        try:
            # Step 1: Identify user and move subscription to subscribed state
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)        
            GeminiRAHelper.subscription_to_subscribed(page)                
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info("Subscription moved to subscribed state and remove free months")
            
            # A new billing cycle is charged for that subscription setting page used as 100
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)

            plan_pages = common.extract_numbers_from_text(RABaseHelper.get_field_text_by_title(page, "Future plan"))[0]
            plan_data = common.get_filtered_plan_data(value=plan_pages)[0]

            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, plan_pages)
            GeminiRAHelper.submit_charge(page) 
            framework_logger.info(f"New billing cycle charged with 31 pages") 

            RABaseHelper.get_links_by_title(page, "Payment events").first.click()
            int_tax_cents = int(RABaseHelper.get_field_text_by_title(page, "Tax cents"))
            page.go_back()
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            GeminiRAHelper.make_refund_option(page, "Full/Remaining Amount")
            
            RABaseHelper.complete_jobs(page, 
                            common._instantink_url, 
                            ["SubscriptionBillingJob", 
                            "FetchImmutableDataDispatcherJob",
                            "PrepareImmutableInvoiceDispatcherJob"])
            
             # Access Overview page
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info(f"Accessed Overview page")
            

            side_menu = DashboardSideMenuPage(page)
            side_menu.click_print_history()

            print_history_page = PrintHistoryPage(page)
            PrintHistoryHelper.click_download_all_invoices(page)

            if not plan_data["taxIncluded"]:
                total_cents = plan_data["priceCents"] + int_tax_cents
            else:
                total_cents = plan_data["priceCents"]
            PrintHistoryHelper.verify_all_billing_cycles_data(page, [
                {
                    "billing_cycle": "2",
                    "total_pages_printed": plan_pages,
                    "pages": plan_pages,
                    "rollover": "0",
                    "additional": "-",
                    "plan_price": plan_data["priceCents"],
                    "overage_price": plan_data["overageBlockPriceCents"],
                    "previous": "0.00",
                    "charges": plan_data["priceCents"],
                    "tax": int_tax_cents,
                    "total": total_cents
                },
            ]) 

            framework_logger.info("=== C44553587 - Refund flow started ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            framework_logger.error(f"Page: #{page.url}")
            raise e
        finally:
            page.close()
