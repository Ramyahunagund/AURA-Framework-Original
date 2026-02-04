from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from pages.confirmation_page import ConfirmationPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"


def ii_flip_conversion_with_prepaid_ca(stage_callback) -> None:
    framework_logger.info("=== Enrollment OOBE flow started ===")
    common.setup()
    test_requirements = GlobalState.requirements
    plan_pages = test_requirements.get("plan_pages")
    hpplus_action = test_requirements.get("hpplus")
    amount_greater = test_requirements.get("amount_greater")
    plan_change = test_requirements.get("plan_change")

    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    printer = common.create_virtual_printer()

    with PlaywrightManager() as page:
        new_tab = None
        try:
            page = common.create_ii_v2_account(page)
            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info("OSS Emulator setup completed")
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info("Accepted connected printing services")
            OssEmulatorHelper.country_select(page)
            framework_logger.info("Selected country")

            if GlobalState.biz_model == "Flex" and hpplus_action == "decline":
                OssEmulatorHelper.decline_hp_plus(page)
                framework_logger.info("Declined HP+")
                OssEmulatorHelper.continue_dynamic_security_notice(page)
                framework_logger.info("Continued on dynamic security notice")
            elif GlobalState.biz_model == "Flex" and hpplus_action == "activate":
                OssEmulatorHelper.activate_hp_plus(page)
                framework_logger.info("Activated HP+")
            elif GlobalState.biz_model == "E2E" and hpplus_action == "ignore":
                framework_logger.info("Continued flow")
            else:
                framework_logger.info("No HP+ action required, continuing enrollment flow.")

            EnrollmentHelper.flip_skip_free_months(page)
            framework_logger.info("Closed billing or shipping modal if it appeared")
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== Enrollment completed successfully ===")

            DashboardHelper.access(page)
            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("=== Dashboard launched successfully ===")
            
            with page.expect_popup() as popup_info:
                DashboardHelper.flip_conversion_enroll_now(page)
                framework_logger.info("Clicked on Enroll Now button")
                new_tab = popup_info.value  # Assign after the with block

            new_tab.wait_for_load_state()
            framework_logger.info("Switched to new tab after Enroll Now")
            confirmation_page = ConfirmationPage(new_tab)
            EnrollmentHelper.add_shipping(new_tab, index=1)
            framework_logger.info("Added shipping info")
            EnrollmentHelper.close_billing_or_shipping_modal(new_tab)
            framework_logger.info("Closed billing or shipping modal if it appeared")
            
            if plan_change == "False" and amount_greater == "True":
                EnrollmentHelper.add_prepaid_by_value(new_tab,300,True)
                framework_logger.info("Added prepaid card by value") 

                EnrollmentHelper.optional_payment_method(new_tab)
                framework_logger.info("Payment method is optional as expected")
                assert confirmation_page.enroll_step_skip_button.is_enabled(), "Skip Now button is not enabled"
                assert confirmation_page.shipping_card.is_visible(), "Shipping card is not visible"
                assert confirmation_page.billing_card.is_visible(), "Billing card is not visible"
                assert confirmation_page.flip_paper_addon_container.is_visible(timeout=100000), "Flip paper addon container is not visible"
                framework_logger.info("Flip paper addon container is visible")
            elif plan_change == "False" and amount_greater == "False":
                EnrollmentHelper.add_prepaid_by_value(new_tab,1500,False)
                framework_logger.info("Added prepaid card by value")
                EnrollmentHelper.prepaid_funds_do_not_cover(new_tab)
                framework_logger.info("Payment method is required as expected")
                assert confirmation_page.enroll_step_skip_button.is_enabled(), "Skip Now button is not enabled"
                assert confirmation_page.shipping_card.is_visible(), "Shipping card is not visible"
                assert confirmation_page.billing_card.is_visible(), "Billing card is not visible"
                EnrollmentHelper.add_billing(new_tab)
                framework_logger.info("Added billing info")
                assert confirmation_page.flip_paper_addon_container.is_visible(timeout=100000) 
            elif plan_change == "True" and amount_greater == "False":
                EnrollmentHelper.add_prepaid_by_value(new_tab,1500,False)
                framework_logger.info("Added prepaid card by value")
                EnrollmentHelper.prepaid_funds_do_not_cover(new_tab)
                framework_logger.info("Payment method is required as expected")
                assert confirmation_page.enroll_step_skip_button.is_enabled(), "Skip Now button is not enabled"
                assert confirmation_page.shipping_card.is_visible(), "Shipping card is not visible"
                assert confirmation_page.billing_card.is_visible(), "Billing card is not visible"
                EnrollmentHelper.edit_plan(new_tab, 10)
                framework_logger.info("Changed plan to 10 pages")

            EnrollmentHelper.finish_enrollment(new_tab)
            framework_logger.info("=== Enrollment completed successfully ===")

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            framework_logger.info("=== Gemini RA accessed successfully ===")

            approval_date = GeminiRAHelper.flip_approval_date(page)
            assert approval_date != "-", "Approval date is empty"
            framework_logger.info(f"Approval date is {approval_date}")
             
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
