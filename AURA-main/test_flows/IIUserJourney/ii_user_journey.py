from time import time
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from helper.fulfillment_service_ra_helper import FulfillmentServiceRAHelper as FFSRV
from helper.fulfillment_simulator_ra_helper import FulfillmentSimulatorRAHelper as FFSIML
import test_flows_common.test_flows_common as common
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def ii_user_journey(stage_callback) -> None:
    framework_logger.info("=== Enrollment OOBE flow started ===")
    common.setup()
    test_requirements = GlobalState.requirements
    plan_pages = test_requirements.get("plan_pages")
    hpplus_action = test_requirements.get("hpplus")
    flip_shipping = test_requirements.get("flip_shipping")
    flip_billing = test_requirements.get("flip_billing")
    paper_option = test_requirements.get("paper_option")
    flip_flow = test_requirements.get("flip_flow")

    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    # Create virtual printer
    printer = common.create_virtual_printer()

    # Create new HPID account and setup OSS Emulator
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)

            # Setup OSS Emulator for OOBE
            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info(f"OSS Emulator setup completed")

            # Accept connected printing services
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info(f"Accepted connected printing services")
            #select country
            OssEmulatorHelper.country_select(page)
            framework_logger.info("Selected country")
            #if flex DEcline HP+, if flex and want HP+ activate it
            if GlobalState.biz_model == "Flex" and hpplus_action == "decline":
                OssEmulatorHelper.decline_hp_plus(page)
                framework_logger.info(f"Declined HP+")
                
                # Continue on dynamic security notice
                OssEmulatorHelper.continue_dynamic_security_notice(page)
                framework_logger.info(f"Continued on dynamic security notice")
            
            elif(GlobalState.biz_model == "Flex" and hpplus_action == "activate"):
                OssEmulatorHelper.activate_hp_plus(page)
                framework_logger.info(f"Activated HP+")
            elif(GlobalState.biz_model == "E2E" and hpplus_action == "ignore"):
                framework_logger.info(f"Continued flow")
            else:
                   # Continue with the next steps if neither condition is met
                    framework_logger.info("No HP+ action required, continuing enrollment flow.")   

            if flip_flow == "yes":
                framework_logger.debug(f"Easy enroll flow started")
                if flip_shipping == "no shipping" and flip_billing =="no billing":
                    EnrollmentHelper.flip_skip_free_months(page)
                    framework_logger.info(f"skip clicked")
                    framework_logger.info(f"No shipping and no billing selected")
                elif flip_shipping == "autofill":
                    EnrollmentHelper.add_shipping_flip_auto_fill(page)
                    framework_logger.info(f"Added shipping info")
                elif flip_shipping == "manual":
                    EnrollmentHelper.enter_address_manually_flip(page)
                    framework_logger.info("Clicked Enter address manually")
                    EnrollmentHelper.add_shipping(page)
                    framework_logger.info("Added shipping info")
                elif flip_shipping == "skip":
                    EnrollmentHelper.flip_skip_free_months(page)
                    framework_logger.info(f"skip clicked")
                    EnrollmentHelper.add_shipping(page)
                    framework_logger.info("Added shipping info")
                elif flip_shipping == "next":
                    EnrollmentHelper.flip_continue(page)
                    framework_logger.info(f"Continued on Flip page")
                    EnrollmentHelper.add_shipping(page)
                    framework_logger.info("Added shipping info")
                if flip_billing == "add":
                    EnrollmentHelper.add_billing(page)
                    framework_logger.info(f"Billing Added successfully")
                elif flip_billing == "no billing" and flip_shipping != "no shipping":
                    EnrollmentHelper.close_billing_or_shipping_modal(page)
                    framework_logger.info(f"No billing selected")
                if paper_option == "add":
                    EnrollmentHelper.add_paper_to_your_plan_flip(page)
                    framework_logger.info(f"Added paper to your plan")
                if flip_shipping != "no shipping":
                    #Edit Shipping and closing modal
                    EnrollmentHelper.edit_shipping(page)
                    EnrollmentHelper.close_billing_or_shipping_modal(page)
                    framework_logger.info(f"Closed shipping modal")
                    #Edit Shipping and save changes
                    EnrollmentHelper.edit_shipping(page)
                    EnrollmentHelper.add_shipping(page)
                    framework_logger.info(f"Edited shipping info")
                if flip_billing != "no billing":
                    #Edit Billing and closing modal
                    EnrollmentHelper.edit_billing(page)
                    EnrollmentHelper.close_billing_or_shipping_modal(page)
                    framework_logger.info(f"Closed billing modal")
                    #Edit Billing and save changes
                    EnrollmentHelper.edit_billing(page)
                    EnrollmentHelper.add_billing(page)
                    framework_logger.info(f"Edited billing info")       

            elif flip_flow == "no":
                    OssEmulatorHelper.continue_value_proposition(page)
                    framework_logger.info(f"Continued on value proposition page")
                    # Accept automatic printer updates
                    EnrollmentHelper.accept_automatic_printer_updates(page)
                    framework_logger.info(f"Accepted automatic printer updates")

                    # Choose HP Checkout
                    EnrollmentHelper.choose_hp_checkout(page)
                    framework_logger.info(f"Chose HP Checkout")

                    EnrollmentHelper.add_shipping(page)
                    framework_logger.info("Added shipping info")

                    EnrollmentHelper.add_billing(page)
                    framework_logger.info("Added billing info")

                    if paper_option=="add":
                        EnrollmentHelper.add_paper_offer(page)
                        framework_logger.info(f"Added paper to your plan")
                    elif paper_option=="skip":
                        EnrollmentHelper.skip_paper_offer(page)
                        framework_logger.info(f"Skipped paper to your plan")

                    #Edit Billing and closing modal
                    EnrollmentHelper.edit_billing(page)
                    EnrollmentHelper.close_billing_or_shipping_modal(page)
                    framework_logger.info(f"Closed billing modal")

                    #Edit Shipping and closing modal
                    EnrollmentHelper.edit_shipping(page)
                    EnrollmentHelper.close_billing_or_shipping_modal(page)
                    framework_logger.info(f"Closed shipping modal")

                    #Edit Shipping and save changes
                    EnrollmentHelper.edit_shipping(page)
                    EnrollmentHelper.add_shipping(page)
                    framework_logger.info(f"Edited shipping info")

                    #Edit Billing and save changes
                    EnrollmentHelper.edit_billing(page)
                    EnrollmentHelper.add_billing(page)
                    framework_logger.info(f"Edited billing info")    

            # Edit Plan
            EnrollmentHelper.edit_plan(page,plan_pages)
            framework_logger.info(f"Edited plan")
           
            EnrollmentHelper.see_details_special_offer(page)
            framework_logger.info(f"See details special offer")       
        
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== Enrollment completed successfully ===")

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info("=== Gemini RA accessed successfully ===")
            GeminiRAHelper.run_ship_supplies_job(page)
            framework_logger.info("=== Ship Supplies Job triggered ===")  

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info("=== Gemini RA accessed successfully ===")          
            
            trigger_id = GeminiRAHelper.click_on_welcome_kit_and_fetch_trigger_id(page)
            framework_logger.info(f"Gemini Rails Admin: Welcome kit trigger_id: {trigger_id}")

            # Verify Order and send it to Fulfillment Simulator
            fulfillment_service_order_link = FFSRV.receive_and_send_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} received and sent. Order link: {fulfillment_service_order_link}")

            # Update order
            FFSIML.process_order(page, trigger_id)
            framework_logger.info(f"Fulfillment Simulator: Order {trigger_id} processed successfully")

            # Verify Order
            FFSRV.validate_order_received(page, "statusShipped", "standard", trigger_id=trigger_id, order_link=fulfillment_service_order_link)
            framework_logger.info(f"Fulfillment Service: Order {trigger_id} updated and verified successfully")

            # GRA subscription verify Notification events
            GeminiRAHelper.verify_notification_events(page,"welcome_std-i_ink", tenant_email)
            framework_logger.info(f"Gemini Rails Admin: Notification events verified for tenant {tenant_email}")

        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()