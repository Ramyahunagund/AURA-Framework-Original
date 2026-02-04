import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from helper.hpid_helper import HPIDHelper
from pages.confirmation_page import ConfirmationPage
from pages.overview_page import OverviewPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def moobe_order_review(stage_callback) -> None:
    framework_logger.info("=== MOOBE order review flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    # Create virtual printer
    printer = common.create_virtual_printer()
    
    # Create new HPID account and setup OSS Emulator
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)
            framework_logger.info(f"HPID account created successfully with email={tenant_email}")
            
            # Setup OSS Emulator for MOOBE
            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info(f"OSS Emulator setup completed")

            # Resize the window resolution
            page.set_viewport_size({"width": 400, "height": 740})
            framework_logger.info(f"Set viewport size to 400x740")

            # # Accept connected printing services
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info(f"Accepted connected printing services")

            # # Decline HP+ offer
            OssEmulatorHelper.decline_hp_plus(page)
            framework_logger.info(f"Declined HP+")
            
            # Continue on dynamic security notice
            OssEmulatorHelper.continue_dynamic_security_notice(page)
            framework_logger.info(f"Continued on dynamic security notice")
           
            # # Continue on value proposition
            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")
            
            # Select plan
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Selected plan 100")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Added shipping info")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            offer = common.get_offer(GlobalState.country_code)
            identifier = offer.get("identifier")
            if not identifier:
                raise ValueError(f"No identifier found for region: {GlobalState.country_code}")

            ek_code = common.offer_request(identifier)
            EnrollmentHelper.apply_and_validate_ek_code(page, ek_code)

            EnrollmentHelper.apply_and_validate_promo_code(page, "freeinkautonew2025")

            EnrollmentHelper.apply_and_validate_raf_code(page, "2nbdy7")

            # Special Offer Benefits(SOB) model : https://hp-testrail.external.hp.com/index.php?/cases/view/29549325
            # Special Offers section : https://hp-testrail.external.hp.com/index.php?/cases/view/29549322
            framework_logger.info("=== Tcs C29549322 & C29549325 started ===")
            EnrollmentHelper.validate_special_offer_benefits(page)
            framework_logger.info("Validated special offer benefits successfully")

            EnrollmentHelper.validate_breakdown_credits_section(page)
            framework_logger.info("Validated breakdown credits section successfully")
            framework_logger.info("=== Tcs C29549322 & C29549325 Ended ===")

            # Order Summary section : https://hp-testrail.external.hp.com/index.php?/cases/view/31438552
            framework_logger.info("=== Tc C31438552 started ===")
            EnrollmentHelper.validate_order_summary_section(page)
            framework_logger.info("Validated order summary section successfully")
            framework_logger.info("=== Tc C31438552 Ended ===")

            # Content and Layout : https://hp-testrail.external.hp.com/index.php?/cases/view/29595560
            # Disclaimer : https://hp-testrail.external.hp.com/index.php?/cases/view/29595564
            framework_logger.info("=== Tcs C29595560 & C29595564 started ===")
            EnrollmentHelper.validate_automatic_renewal_notice_modal(page, callback=stage_callback)
            framework_logger.info("Validated automatic renewal notice modal successfully")
            stage_callback("AutomaticRenewalNoticeModal", page, screenshot_only=True)
            framework_logger.info("=== Tcs C29595560 & C29595564 ended ===")

            # Model Close : https://hp-testrail.external.hp.com/index.php?/cases/view/29595561
            framework_logger.info("=== Tcs C29595561 started ===")
            EnrollmentHelper.validate_arn_modal_close(page, callback=stage_callback)
            framework_logger.info("Validated links on automatic renewal notice modal successfully")
            stage_callback("AutomaticRenewalNoticeModalLinks", page, screenshot_only=True)
            framework_logger.info("=== Tcs C29595561 ended ===")

            # Links : https://hp-testrail.external.hp.com/index.php?/cases/view/29595562
            framework_logger.info("=== Tcs C29595562 started ===")
            EnrollmentHelper.validate_links_on_automatic_renewal_notice_modal(page, callback=stage_callback)
            framework_logger.info("Validated links on automatic renewal notice modal successfully")
            stage_callback("AutomaticRenewalNoticeModalLinks", page, screenshot_only=True)
            framework_logger.info("=== Tcs C29595562 ended ===")

            # Button : https://hp-testrail.external.hp.com/index.php?/cases/view/29595563
            framework_logger.info("=== Tc C29595563 started ===")
            EnrollmentHelper.validate_enroll_button_on_automatic_renewal_notice_modal(page, callback=stage_callback)
            framework_logger.info("Validated Enroll button on automatic renewal notice modal successfully")
            stage_callback("AutomaticRenewalNoticeModalEnrollButton", page, screenshot_only=True)
            framework_logger.info("=== Tc C29595563 ended ===")

            #Content and Layout 01 : https://hp-testrail.external.hp.com/index.php?/cases/view/27368729
            # Email id : https://hp-testrail.external.hp.com/index.php?/cases/view/27599058
            # Buttons : https://hp-testrail.external.hp.com/index.php?/cases/view/27850014
            framework_logger.info("=== Tcs C27368729, C27599058 & C27850014 started ===")
            EnrollmentHelper.validate_thank_you_page_for_moobe(page, additional_check=True, continue_flow=True, callback=stage_callback)
            framework_logger.info("Validated Thank You page")
            stage_callback("ThankYouPage", page, screenshot_only=True)
            framework_logger.info("=== Tcs C27368729, C27599058 & C27850014 ended ===")

            # # Skip Paper Offer
            # EnrollmentHelper.skip_paper_offer(page)
            # framework_logger.info(f"Skipped paper offer")
            
            # # Finish Enrollment
            # EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== MOOBE Enrollment completed successfully ===") 
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
