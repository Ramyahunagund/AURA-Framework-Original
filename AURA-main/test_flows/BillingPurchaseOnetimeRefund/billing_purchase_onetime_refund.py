from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from helper.ra_base_helper import RABaseHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def billing_purchase_onetime_refund(stage_callback):

    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info(f"=== C48567451, C48636196 - Billing Purchase (onetime) Refund - {common._payment_method} flow started ===")

    with PlaywrightManager() as page:
        try:
            # Test 1 and 2 Billing Purchase(onetime) Refund
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)
            GeminiRAHelper.remove_free_months(page)
            framework_logger.info(f"Subscription moved to subscribed state and free months removed")

            # Charge a new billing purchase with value 100
            GeminiRAHelper.one_time_charge(page, "100")
            framework_logger.info(f"New billing purchase charged with 100")  
           
            # Verify Status code on Billing cycle page
            expected_status_code = common.billing_status_code()
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", expected_status_code)    
            framework_logger.info(f"Status code on Billing cycle page is {expected_status_code}")   
            GeminiRAHelper.verify_charge_complete(page)           
            
            # Gemini Rails Admin user Refund total payment for current billing purchase
            GeminiRAHelper.billing_purchase_refund_total_payment(page)
            framework_logger.info(f"Refunded total payment for current billing purchase")
            
            # See Refund complete status true on billing cycle page
            GeminiRAHelper.verify_refund_complete(page)
            framework_logger.info("Refund complete status is true on billing cycle page")

            # Verify Status code on Billing purchase page is REFUNDED       
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", "REFUNDED")  
            framework_logger.info(f"Status code on Billing cycle page is REFUNDED")
           
            # Test 3:  Refund Payment Events          
            RABaseHelper.access_link_by_title(page, "Billing::PaymentEvent", "Payment events")               
            GeminiRAHelper.verify_rails_admin_info(page, "Event type", "refund")                 
            expected_payment_engine = common.payment_engine()
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)
            GeminiRAHelper.verify_field_is_negative(page, "Pretax cents")          
            GeminiRAHelper.verify_field_is_negative(page, "Tax cents")
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Billing transaction", "BillingTransaction")
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded payment event invoice items", "RefundedPaymentEventInvoiceItem")
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded invoice items", "RefundedInvoiceItem")
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Reversed Transaction Payment Events", "Payment Event")
            RABaseHelper.access_link_by_title(page, "RefundedPaymentEventInvoiceItem", "Refunded payment event invoice items")   
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Payment event", "Billing::PaymentEvent") 
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded invoice item", "RefundedInvoiceItem") 
            framework_logger.info("Refund Payment Events validated")

            # Test 4: Refund Request Events
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            framework_logger.info("Accessed Billing purchase page")

            # Verify if PAY-PAL-REFUNDED is visible, if not use PAYMENT-GATEWAY-REFUNDED
            try:
                # Try to find and click the PAY-PAL-REFUNDED link
                paypal_link = page.locator('a:has-text("PAY-PAL-REFUNDED")')
                if paypal_link.is_visible(timeout=2000):
                    request_event = "PAY-PAL-REFUNDED"
                    framework_logger.info("PAY-PAL-REFUNDED link found and visible")
                else:
                    raise Exception("PAY-PAL-REFUNDED not visible")
            except:
                # if PAY-PAL-REFUNDED is not visible, use PAYMENT-GATEWAY-REFUNDED
                request_event = "PAYMENT-GATEWAY-REFUNDED"
                framework_logger.info("PAY-PAL-REFUNDED not found, using PAYMENT-GATEWAY-REFUNDED")
            
            RABaseHelper.access_link_by_title(page, request_event, "Request events")
            GeminiRAHelper.verify_field_is_negative(page, "Charge amount cents")
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)
            framework_logger.info(f"Clicked link with text {request_event} and verified details")

            # Test 5: Refund Billing Transactions
            page.go_back()
            RABaseHelper.access_link_by_title(page, "BillingTransaction", "Billing transactions")          
            GeminiRAHelper.verify_rails_admin_info(page, "Transaction type", "refund")
            GeminiRAHelper.verify_rails_admin_info(page, "Status", "succeeded")
            GeminiRAHelper.verify_rails_admin_info(page, "Invoice status", "ready_to_invoice")
            GeminiRAHelper.verify_field_is_negative(page, "Pretax cents")
            GeminiRAHelper.verify_field_is_negative(page, "Tax cents")
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Payment events", "Billing::PaymentEvent") 
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded invoice items", "RefundedInvoiceItem") 
            framework_logger.info("Refund Billing Transactions validated")

            # Test 6: Reversed Transaction Payment Events
            page.go_back()
            RABaseHelper.access_link_by_title(page, "Billing::PaymentEvent", "Payment events") 
            RABaseHelper.access_link_by_title(page, "Payment Event", "Reversed Transaction Payment Events") 
            GeminiRAHelper.verify_rails_admin_info(page, " Event type", "charge")
            GeminiRAHelper.verify_rails_admin_info(page, "Payment engine", expected_payment_engine)
            GeminiRAHelper.verify_field_is_positive(page, "Pretax cents")
            GeminiRAHelper.verify_field_is_positive(page, "Tax cents")
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Billing transaction", "BillingTransaction") 
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Reversed Transaction Payment Events", "Payment Event")
            framework_logger.info("Reversed Transaction Payment Events validated")

            # Test 7: Refunded Invoice Items           
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.access_first_billing_cycle(page)
            framework_logger.info("Accessed Billing purchase page")
           
            RABaseHelper.access_link_by_title(page, "RefundedInvoiceItem", "Refunded invoice items")
            GeminiRAHelper.verify_rails_admin_info(page, "Quantity", "1")
            GeminiRAHelper.verify_field_is_positive(page, "Amount in cents")
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Invoice item", "1 * OneTimeChargeInvoiceItem") 
            RABaseHelper.access_link_by_title(page, "RefundedPaymentEventInvoiceItem", "Refunded payment event invoice items")
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Payment event", "Billing::PaymentEvent") 
            GeminiRAHelper.verify_rails_admin_info_contains(page, "Refunded invoice item", "RefundedInvoiceItem") 
            framework_logger.info("Refunded Invoice Items validated")     
                     
            framework_logger.info(f"=== C48567451, C48636196 - Billing Purchase (onetime) Refund - {common._payment_method} flow finished ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
        