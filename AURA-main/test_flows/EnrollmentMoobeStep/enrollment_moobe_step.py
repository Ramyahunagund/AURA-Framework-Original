import time
import urllib3
import traceback

import test_flows_common.test_flows_common as common
from core.playwright_manager import PlaywrightManager
from helper.enrollment_helper import EnrollmentHelper
from core.settings import framework_logger
from core import utils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"


def enrollment_moobe_step(stage_callback):
    framework_logger.info("=== OOBE Enroll Step ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # Create a new HP ID account
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)
            stage_callback("ii_v2_account", page, screenshot_only=True)

            # Click on Sign Up Now button
            with page.context.expect_page() as new_page_info:
                EnrollmentHelper.signup_now(page)
                framework_logger.info("Sign Up Now button clicked")
            page = new_page_info.value
            stage_callback("signup_now", page, screenshot_only=True)

            # Accept Terms of Service
            EnrollmentHelper.accept_terms_of_service(page)
            framework_logger.info("Terms of Service accepted")

            # Select monthly plan type card
            EnrollmentHelper.select_plan_type(page)
            framework_logger.info("Plan type card selected")
            stage_callback("monthly_plan_type_selected", page, screenshot_only=True)

            framework_logger.info("======== Your Plan: Modal close ========")
            EnrollmentHelper.click_learn_more(page, paper=False, callback=stage_callback)

            framework_logger.info("======== Your Plan: Save button ========")
            EnrollmentHelper.select_plan_v3(page, plan_value='100', paper=False, callback=stage_callback)
            framework_logger.info("Ink only plan selected")
            stage_callback("ink_only_selected", page, screenshot_only=True)

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")


            # Verify billing information text is visible
            #https://hp-testrail.external.hp.com/index.php?/cases/view/27368667
            assert EnrollmentHelper.is_billing_information_text_visible(page, "Please enter your billing information.")

            #verify add shipping is enabled before clicking
            #https://hp-testrail.external.hp.com/index.php?/cases/view/27368679
            #https://hp-testrail.external.hp.com/index.php?/cases/view/27368668
            assert EnrollmentHelper.is_add_shipping_button_enabled(page)

            # verify add billing  is disable before clicking
            #https://hp-testrail.external.hp.com/index.php?/cases/view/27368669
            assert EnrollmentHelper.is_add_billing_button_disabled(page)

        except Exception as e:
            framework_logger.error(
                f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
