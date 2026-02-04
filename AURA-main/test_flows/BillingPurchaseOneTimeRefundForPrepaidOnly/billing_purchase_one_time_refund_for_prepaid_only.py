from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_purchase_one_time_refund_for_prepaid_only(stage_callback):
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"=== C46057785 - Billing Purchase(onetime) Refund - Prepaid Only flow started ===")

    with PlaywrightManager() as page:
        try:
            # Move subscription to subscribed state and remove free months
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Click on One Time Charge button and set 10 as amount on Subscription page
            GeminiRAHelper.one_time_charge(page, "10")
            framework_logger.info(f"One Time Charge of 10 set on Subscription page")

            # Charge a Billing Cycle with 100 pages used
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.event_shift(page, "31")
            GeminiRAHelper.click_billing_cycle_by_status(page, "-")
            GeminiRAHelper.calculate_and_define_page_tally(page, "100")
            GeminiRAHelper.submit_charge(page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            framework_logger.info(f"Billing cycle charged with 100 pages")
           
            # Charge comple status is true 
            GeminiRAHelper.verify_charge_complete(page)
            framework_logger.info("Charge complete status is true on billing cycle page")
            
            # Verify Status code on Billing cycle page
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", "PEGASUS-SUCCESS")      
            framework_logger.info(f"Status code on Billing cycle page is PEGASUS-SUCCESS")   
            
            # Full/Remaining refund for current billing cycle
            GeminiRAHelper.make_refund_option(page, "Full/Remaining Amount")
            framework_logger.info("Full/Remaining refund made for current billing cycle")
                        
            # Verify Status code on Billing purchase page is REFUNDED       
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", "REFUNDED")  
            framework_logger.info(f"Status code on Billing cycle page is REFUNDED")
            
            # See Refund complete status true on billing cycle page
            GeminiRAHelper.verify_refund_complete(page)
            framework_logger.info("Refund complete status is true on billing cycle page")
           
            # Click in the link with text Billing::PaymentEvent and confirm details on Payment events page        
            RABaseHelper.access_link_by_title(page, "Billing::PaymentEvent", "Payment events")               
            GeminiRAHelper.verify_rails_admin_info(page, "Event type", "refund")                 
            expected_payment_engine = common.payment_engine()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)
            GeminiRAHelper.verify_field_is_negative(page, "Pretax cents")          
            GeminiRAHelper.verify_field_is_negative(page, "Tax cents")
            framework_logger.info(f"Clicked link with text Billing::PaymentEvent and verified details")

            # Click in the link with text PEGASUS-REFUNDED and confirm details on Request events page
            page.go_back()
            RABaseHelper.access_link_by_title(page, "PEGASUS-REFUNDED", "Request events")               
            GeminiRAHelper.verify_rails_admin_info(page, "Response status", "PEGASUS-REFUNDED")                 
            expected_payment_engine = common.payment_engine()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)
            GeminiRAHelper.verify_field_is_negative(page, "Charge amount cents")          
            framework_logger.info(f"Clicked link with text PEGASUS-REFUNDED and verified details")

            # Click in the link with text BillingTransaction and confirm details on Billing transactions page
            page.go_back()
            RABaseHelper.access_link_by_title(page, "BillingTransaction", "Billing transactions")          
            GeminiRAHelper.verify_rails_admin_info(page, "Transaction type", "refund")
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "succeeded")
            GeminiRAHelper.verify_rails_admin_info(page, "Invoice status", "ready_to_invoice")
            GeminiRAHelper.verify_field_is_negative(page, "Pretax cents")
            GeminiRAHelper.verify_field_is_negative(page, "Tax cents")
            framework_logger.info(f"Clicked link with text BillingTransaction and verified details")
                     
            framework_logger.info(f"=== C46057785 - Billing Purchase(onetime) Refund - Prepaid Only flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        