from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from core.utils import extract_styles
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from pages.confirmation_page import ConfirmationPage
from playwright.sync_api import expect
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def oobe_enroll_step_layout_validation(stage_callback):
    framework_logger.info("=== C27368497 - OOBE Enroll Step Layout Validation flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

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

            # Select country if needed
            try:
                page.wait_for_selector(f"div.option[id='{common._tenant_country_short}']", timeout=10000)
                page.locator(f"div.option[id='{common._tenant_country_short}']").click()
                page.locator('[class="footer-2"] button').click()
            except Exception:
                framework_logger.info(f"Country selection not required")

            # Decline HP+
            OssEmulatorHelper.decline_hp_plus(page)
            framework_logger.info(f"Declined HP+")

            # Continue on dynamic security notice
            OssEmulatorHelper.continue_dynamic_security_notice(page)
            framework_logger.info(f"Continued on dynamic security notice")

            # Continue on value proposition
            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")

            # Accept automatic printer updates
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Accepted automatic printer updates")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Select plan
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Selected plan 100")

            # Initialize confirmation page object
            confirmation_page = ConfirmationPage(page)
                           
            # Check font on plan card
            confirmation_page.edit_plan_button.click()
            plan_card = page.locator(confirmation_page.elements.plans_consumer_plan_content_container)            
            plan_elem = plan_card.element_handle()
            plan_styles = extract_styles(plan_elem)
            framework_logger.info(f"Plan card font: {plan_styles}")
            page.keyboard.press('Escape')
            framework_logger.info(f"Verified font in plan card")
            
            # Check font on shipping card
            confirmation_page.add_shipping_button.click(timeout=30000)            
            shipping_card = page.locator(confirmation_page.elements.shipping_form_container)
            shipping_elem = shipping_card.element_handle()
            shipping_styles = extract_styles(shipping_elem)
            framework_logger.info(f"Shipping card font: {shipping_styles}")
            confirmation_page.close_shipping_modal_button.click()   
            framework_logger.info(f"Verified font in shipping modal")             
            
            # Check font in skip trial modal
            confirmation_page.skip_trial_button.click()

            skip_modal_content = page.locator(confirmation_page.elements.skip_trial_modal)            
            skip_modal_elem = skip_modal_content.element_handle()
            skip_modal_styles = extract_styles(skip_modal_elem)
            framework_logger.info(f"Skip trial modal content font: {skip_modal_styles}")       
            page.keyboard.press('Escape')
            framework_logger.info(f"Verified font in skip trial modal")
              
            # Hover over 'i' icon on Plans card and check tooltip font
            confirmation_page.plan_tooltip_icon.hover()                             
            tooltip_content = page.locator('[role="tooltip"]').first           
            tooltip_elem = tooltip_content.element_handle()
            tooltip_styles = extract_styles(tooltip_elem)
            framework_logger.info(f"Plans card tooltip font: {tooltip_styles}")
            framework_logger.info(f"Verified font in plan tooltip")                        

            # Hover over 'i' icon on Billing card and check tooltip font
            confirmation_page.billing_tooltip_icon.hover()                              
            tooltip_content = page.locator('[role="tooltip"]').last        
            tooltip_elem = tooltip_content.element_handle()
            tooltip_styles = extract_styles(tooltip_elem)
            framework_logger.info(f"Billing card tooltip font: {tooltip_styles}")
            framework_logger.info(f"Verified font in billing tooltip")   

            framework_logger.info("=== C27368497 -OOBE Enroll Step Layout Validation flow completed successfully ===")
            
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e
    