from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def enrollment_oobe_extended_visual(stage_callback) -> None:
    framework_logger.info("=== Enrollment OOBE flow started ===")
    common.setup()
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

            try:
                page.wait_for_selector(f"div.option[id='{common._tenant_country_short}']", timeout=10000)
                page.locator(f"div.option[id='{common._tenant_country_short}']").click()
                page.locator('[class="footer-2"] button').click()
            except Exception as e:
                framework_logger.info(f"Don't need to select country")

            # Decline
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

            # Add Shipping
            framework_logger.info("======== Add Shipping ========")
            EnrollmentHelper.add_shipping(page, additional_check=True)
            framework_logger.info(f"Shipping added successfully")

            # Add Billing
            framework_logger.info("======== Add Billing ========")
            EnrollmentHelper.add_billing(page,payment_method="paypal")
            framework_logger.info("Billing added successfully.")

            # Review page plan info: https://hp-testrail.external.hp.com/index.php?/cases/view/27368531
            framework_logger.info("======== C27368531-Your Plan card-Review plan info ========")
            monthly_plan_review, monthly_pages_review, monthly_charges_review = EnrollmentHelper.selected_plan_info(page,onboarded=False) # If running test post onboarding, change to "Yes"
            assert monthly_plan_name == monthly_plan_review, f"Expected plan name '{monthly_plan_name}', but got '{monthly_plan_review}'"
            assert monthly_plan_pages == monthly_pages_review, f"Expected plan pages '{monthly_plan_pages}', but got '{monthly_pages_review}'"
            assert monthly_plan_charges == monthly_charges_review, f"Expected charges '{monthly_plan_charges}', but got '{monthly_charges_review}'"
            framework_logger.info("Plan info validated on Review page")
            stage_callback("ReviewPage_PlanInfo", page, screenshot_only=True)

            # Review page plan edit option: https://hp-testrail.external.hp.com/index.php?/cases/view/27368532
            framework_logger.info("======== C27368532-Edit icon-Review plan edit option ========")
            EnrollmentHelper.selected_plan_edit_validate(page)
            framework_logger.info("Plan edit validated on Review page")
            stage_callback("ReviewPage_PlanEdit", page, screenshot_only=True)

            # Plan modal recommended plan: https://hp-testrail.external.hp.com/index.php?/cases/view/27368533
            framework_logger.info("======== C27368533-Most Popular plan-Plan modal recommended plan ========")
            EnrollmentHelper.plan_recommended_validate(page)
            framework_logger.info("Plan edit recommended plan checked")
            stage_callback("PlanEdit_RecommendedPlan", page, screenshot_only=True)

            # Plan modal pages & pricing list validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368534
            framework_logger.info("======== C27368534-Agena Plans-Plan modal pages & pricing list validation ========")
            EnrollmentHelper.plan_pagesprice_modal_list_validate(page, callback=stage_callback)
            framework_logger.info("Plan pages & pricing list validated")
            stage_callback("PlanEdit_PagesPriceList", page, screenshot_only=True)

            # # Plan Review modal validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368536
            # framework_logger.info("======== C27368536-Modal Close-Plan Review modal validation ========")
            # EnrollmentHelper.plan_review_modal_validate(page)
            # framework_logger.info("Plan review modal validated")
            # stage_callback("PlanReview_Modal", page, screenshot_only=True)

            # Enroll Summary validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368537
            framework_logger.info("======== C27368537-27368537-Enroll Summary validation ========")
            # Enroll Summary all plans validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368538
            framework_logger.info("======== C27368538-Different Plans-Enroll Summary all plans validation ========")
            EnrollmentHelper.enroll_summary_validate_all_plans(page, callback=stage_callback)
            framework_logger.info("Enroll summary validated for all plans")
            stage_callback("EnrollSummary_Validation", page, screenshot_only=True)

            # Review page Shipping details validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368539
            framework_logger.info("======== C27368539-Saved shipping-Review page Shipping details validation ========")
            EnrollmentHelper.selected_shipping_info_validate(page)
            framework_logger.info("Shipping details validated on Review page")
            stage_callback("ReviewPage_ShippingInfo", page, screenshot_only=True)

            # Shipping Review modal messages validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368540
            framework_logger.info("======== C27368540-Shipping Modal-Shipping Review modal messages validation ========")
            EnrollmentHelper.shipping_review_modal_msgs_validate(page, callback=stage_callback)
            framework_logger.info("Shipping review modal messages validated")
            stage_callback("ShippingReview_ModalMsg", page, screenshot_only=True)

            # Shipping Review modal PBL validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368542
            framework_logger.info("======== C27368542-04 PBL-Shipping Review modal PBL validation ========")
            # Shipping Review modal close button boundary check: https://hp-testrail.external.hp.com/index.php?/cases/view/27368544
            framework_logger.info("======== C27368544-06 Modal Close-Shipping Review modal close button boundary check ========")
            # Shipping Review modal update address: https://hp-testrail.external.hp.com/index.php?/cases/view/27368545
            framework_logger.info("======== C27368545-07 Modify shipping address-Shipping Review modal update address ========")
            # Shipping Review modal blank mandatory field: https://hp-testrail.external.hp.com/index.php?/cases/view/27368546
            framework_logger.info("======== C27368546-08 Mandatory Fields-Shipping Review modal blank mandatory field ========")
            EnrollmentHelper.shipping_review_modal_modify_validate(page, callback=stage_callback)
            framework_logger.info("Shipping review modal modify details validated")
            stage_callback("ShippingReview_ModalModify", page, screenshot_only=True)

            # Billing Card validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368549
            framework_logger.info("======== C27368549-Billing card-Billing Card validation ========")
            EnrollmentHelper.billing_card_validate(page, callback=stage_callback)
            framework_logger.info("Billing card validated on Review page")
            stage_callback("ReviewPage_BillingInfo", page, screenshot_only=True)

            # Post edit billing validations: https://hp-testrail.external.hp.com/index.php?/cases/view/27368550
            framework_logger.info("======== C27368550-Billing modal(Step 1 of 2)-Post edit billing validations ========")
            EnrollmentHelper.post_edit_billing_validate(page, callback=stage_callback)
            framework_logger.info("Post edit billing validated on Review page")
            stage_callback("PostEdit_BillingInfo", page, screenshot_only=True)

            # Billing Review modal validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368553
            framework_logger.info("======== C27368553-Modal Close-Billing Review modal validation ========")
            EnrollmentHelper.billing_review_modal_validate(page, callback=stage_callback)
            framework_logger.info("Billing review modal validated")
            stage_callback("BillingReview_Modal", page, screenshot_only=True)

            # Billing Review modal credit card modification: https://hp-testrail.external.hp.com/index.php?/cases/view/27368554
            framework_logger.info("======== C27368554-06 Modify billing details-Billing Review modal credit card modification ========")
            # Billing Review modal credit card mandatory validation: https://hp-testrail.external.hp.com/index.php?/cases/view/27368555
            framework_logger.info("======== C27368555-04 PBL-07 Mandatory-Billing Review credit card modal validation ========")
            EnrollmentHelper.billing_review_modal_creditcard_modify(page, callback=stage_callback)
            framework_logger.info("Billing review modal modified credit card details validated")
            stage_callback("BillingReview_ModifiedCard", page, screenshot_only=True)

            # Billing Review modal paypal modification: https://hp-testrail.external.hp.com/index.php?/cases/view/27368557
            framework_logger.info("======== C27368557-09 Modify billing details-Billing Review modal paypal modification ========")
            EnrollmentHelper.billing_review_modal_paypal_modify(page, callback=stage_callback)
            framework_logger.info("Billing review modal modified paypal details validated")
            stage_callback("BillingReview_ModifiedPaypal", page, screenshot_only=True)

        #     # Select plan
        #     EnrollmentHelper.select_plan(page, 100)
        #     framework_logger.info(f"Selected plan 100")

        #     price = None
        #     try:
        #         price = EnrollmentHelper.get_total_price_by_plan_card(page)
        #     except Exception:
        #         framework_logger.info(f"Failed to get price from plan card")

        #     # Add Shipping
        #     EnrollmentHelper.add_shipping(page)
        #     framework_logger.info(f"Added shipping info")

        #     # Add Billing
        #     EnrollmentHelper.add_billing(page, plan_value=price)
        #     framework_logger.info(f"Billing Added successfully")

        #     # Skip Paper Offer
        #     EnrollmentHelper.skip_paper_offer(page)
        #     framework_logger.info(f"Skipped paper offer")

        #     # Finish Enrollment
        #     EnrollmentHelper.finish_enrollment(page)
        #     framework_logger.info("=== OOBE Enrollment completed successfully ===")

        #     return tenant_email
        # except Exception as e:
        #     framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
        #     raise e
        finally:
            page.close()
