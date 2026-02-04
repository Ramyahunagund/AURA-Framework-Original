import traceback
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage
from pages.sign_in_page import SignInPage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.printer_selection_page import PrinterSelectionPage
from pages.print_history_page import PrintHistoryPage
from pages.update_plan_page import UpdatePlanPage
from pages.shipment_tracking_page import ShipmentTrackingPage
from pages.shipping_billing_page import ShippingBillingPage
from pages.printer_replacement_page import PrinterReplacementPage
from pages.cancellation_page import CancellationPage
from helper.update_plan_helper import UpdatePlanHelper
from helper.dashboard_helper import DashboardHelper

import time
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
import re

def smart_dashboard(stage_callback):
    framework_logger.info("=== Smart Dashboard flow started ===")
    common.setup()

    tenant_email = "hello.instantink+miv48xlz@gmail.com"
    timeout_ms = 120000

    with sync_playwright() as p:
        launch_args = {"headless": GlobalState.headless}
        context_args = {
            "locale": f"{GlobalState.language_code}",
            "viewport": {"width": GlobalState.target_width, "height": GlobalState.target_height}
        }
        if common.PROXY_URL:
            launch_args["proxy"] = {"server": common.PROXY_URL}
            context_args["proxy"] = {"server": common.PROXY_URL}

        browser = p.chromium.launch(**launch_args)
        context = browser.new_context(**context_args)
        framework_logger.info(f"Launching Playwright browser with headless={GlobalState.headless}, locale={GlobalState.language_code}")
        page = context.new_page()
        page.set_default_timeout(timeout_ms)

        try:
            privacy_banner_page = PrivacyBannerPage(page)
            dashboard_side_menu_page = DashboardSideMenuPage(page)
            overview_page = OverviewPage(page)
            landing_page = LandingPage(page)
            sign_in_page = SignInPage(page)
            print_history_page = PrintHistoryPage(page)
            update_plan_page = UpdatePlanPage(page)
            shipment_tracking_page = ShipmentTrackingPage(page)
            shipping_billing_page = ShippingBillingPage(page)
            printer_replacement_page = PrinterReplacementPage(page)
            cancellation_page = CancellationPage(page)

            # Opens Landing page and accept the privacy banner
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()

            # Sign in to the Instant Ink account
            landing_page.sign_in_button.click()
            sign_in_page.email_input.fill(tenant_email)
            sign_in_page.use_password_button.click()
            sign_in_page.password_input.fill(common.DEFAULT_PASSWORD)
            sign_in_page.sign_in_button.click()
            framework_logger.info("Logged in to Instant Ink account")

            # Go to Overview page
            expect(dashboard_side_menu_page.instant_ink_menu_link).to_be_visible(timeout=timeout_ms)
            dashboard_side_menu_page.click_overview()

            # Enroll or replace a printer
            if not overview_page.enroll_or_replace_button.is_visible(timeout=timeout_ms):
                page.reload()
                framework_logger.info("Reloading page to ensure Overview page is displayed")
                expect(overview_page.enroll_or_replace_button).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Overview page loaded successfully")
            overview_page.enroll_or_replace_button.click()
            with context.expect_page() as new_page_info:
                overview_page.enroll_printer_button.click()
            new_tab = new_page_info.value

            printer_selection_page = PrinterSelectionPage(new_tab)
            time.sleep(10)
            expect(printer_selection_page.printer_selection_page).to_be_visible(timeout=timeout_ms)
            new_tab.close()
            page.bring_to_front()

            framework_logger.info("Verified enroll another printer on Overview page")
            overview_page.close_finish_enrollment_button.click()
            overview_page.close_finish_enrollment_button.wait_for(state="detached", timeout=timeout_ms)

            # Verify status card elements
            expect(overview_page.status_card).to_be_visible(timeout=timeout_ms)
            expect(overview_page.status_card_title).to_be_visible(timeout=timeout_ms)
            expect(overview_page.status_card_cloud_kick).to_be_visible(timeout=timeout_ms)
            expect(overview_page.status_card_printer_name).to_be_visible(timeout=timeout_ms)
            expect(overview_page.printer_details_link).to_be_visible(timeout=timeout_ms)
            expect(overview_page.view_print_history_link).to_be_visible(timeout=timeout_ms)
            expect(overview_page.monthly_summary).to_be_visible(timeout=timeout_ms)
            expect(overview_page.plan_pages_bar).to_be_visible(timeout=timeout_ms)
            expect(overview_page.trial_pages_bar).to_be_visible(timeout=timeout_ms)
            expect(overview_page.rollover_pages_bar).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Status card elements on Overview page verified")

            # Verify printer details modal
            overview_page.printer_details_link.click()
            expect(overview_page.printer_details_modal).to_be_visible(timeout=timeout_ms)
            expect(overview_page.printer_details_modal_title).to_be_visible(timeout=timeout_ms)
            expect(overview_page.printer_details_modal_printer_img).to_be_visible(timeout=timeout_ms)
            expect(overview_page.printer_details_modal_printer_info).to_be_visible(timeout=timeout_ms)
            overview_page.printer_details_modal_close_button.click()
            framework_logger.info("Printer details modal verified and closed")

            # Verify View Print History link
            overview_page.view_print_history_link.click()
            expect(print_history_page.page_title).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.print_history_card).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.print_history_card_title).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.how_is_calculated_link).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.total_printed_pages).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.plan_pages_bar).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.trial_pages_bar).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.rollover_pages_bar).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.plan_details_card).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Print History page verified")

            # Verify FAQ card on Print History page
            expect(print_history_page.faq_card).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.faq_question_1).to_be_visible(timeout=timeout_ms)
            print_history_page.faq_question_1.click()
            expect(print_history_page.faq_answer_1).to_be_visible(timeout=timeout_ms)
            with context.expect_page() as new_page_info:
                print_history_page.faq_terms_of_service_link.click()
            new_tab = new_page_info.value
            expect(new_tab).to_have_url("https://instantink-stage1.hpconnectedstage.com/us/en/terms")
            new_tab.close()
            page.bring_to_front()

            expect(print_history_page.faq_question_2).to_be_visible(timeout=timeout_ms)
            print_history_page.faq_question_2.click()
            expect(print_history_page.faq_answer_2).to_be_visible(timeout=timeout_ms)
            print_history_page.faq_overview_link.click()
            expect(overview_page.page_title).to_be_visible(timeout=timeout_ms)
            overview_page.view_print_history_link.click()

            expect(print_history_page.faq_question_2).to_be_visible(timeout=timeout_ms)
            print_history_page.faq_question_2.click()
            print_history_page.faq_update_plan_link.click()
            expect(update_plan_page.page_title).to_be_visible(timeout=timeout_ms)
            dashboard_side_menu_page.click_print_history()

            expect(print_history_page.faq_question_3).to_be_visible(timeout=timeout_ms)
            print_history_page.faq_question_3.click()
            expect(print_history_page.faq_answer_3).to_be_visible(timeout=timeout_ms)

            expect(print_history_page.faq_question_4).to_be_visible(timeout=timeout_ms)
            print_history_page.faq_question_4.click()
            expect(print_history_page.faq_answer_4).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Faq on Print History page verified")

            # Verify Print History table
            expect(print_history_page.print_history_table_button).to_be_visible(timeout=timeout_ms)
            print_history_page.print_history_table_button.click()
            expect(print_history_page.table_date).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.table_description).to_be_visible(timeout=timeout_ms)
            expect(print_history_page.table_invoice).to_be_visible(timeout=timeout_ms)
            print_history_page.table_selector.click()
            expect(print_history_page.table_selector_list).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Print History table verified")

            # Verify Cartridge Status card
            dashboard_side_menu_page.click_overview()
            expect(overview_page.cartridge_status_card).to_be_visible(timeout=timeout_ms)
            expect(overview_page.view_shipments_link).to_be_visible(timeout=timeout_ms)
            overview_page.view_shipments_link.click()
            framework_logger.info("Cartridge Status card on Overview page verified")

            # Verify Cartridge Card on Shipment Tracking page
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=timeout_ms)
            expect(shipment_tracking_page.kCartridgeItem).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Cartridge Card on Shipment Tracking page verified")

            # Verify FAQ card on Shipment Tracking page
            expect(shipment_tracking_page.faq_card).to_be_visible(timeout=timeout_ms)
            expect(shipment_tracking_page.faq_question(0)).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_question(0).click()
            expect(shipment_tracking_page.faq_answer1).to_be_visible(timeout=timeout_ms)

            expect(shipment_tracking_page.faq_question(1)).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_question(1).click()
            expect(shipment_tracking_page.faq_answer2).to_be_visible(timeout=timeout_ms)
            expect(shipment_tracking_page.faq_overview_link).to_be_visible(timeout=timeout_ms)
            expect(shipment_tracking_page.faq_update_plan_link).to_be_visible(timeout=timeout_ms)
    
            expect(shipment_tracking_page.faq_question(2)).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_question(2).click()
            expect(shipment_tracking_page.faq_answer3).to_be_visible(timeout=timeout_ms)

            expect(shipment_tracking_page.faq_question(3)).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.faq_question(3).click()
            expect(shipment_tracking_page.faq_answer4).to_be_visible(timeout=timeout_ms)

            with context.expect_page() as new_page_info:
                shipment_tracking_page.faq_recycle_link.click()
            new_tab = new_page_info.value
            assert "recycling" in new_tab.url, f"Expected 'recycling' in URL, but got {new_tab.url}"
            new_tab.close()
            page.bring_to_front()
            framework_logger.info("Faq on Shipment Tracking page verified")

            # Verify Cartridge Support card
            expect(shipment_tracking_page.cartridge_support_card).to_be_visible(timeout=timeout_ms)
            with context.expect_page() as new_page_info:
                shipment_tracking_page.recycle_your_cartridge_link.click()
            new_tab = new_page_info.value
            assert "recycle" in new_tab.url, f"Expected 'recycle' in URL, but got {new_tab.url}"
            new_tab.close()
            page.bring_to_front()
            expect(shipment_tracking_page.missing_ink_link).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Cartridge Support card on Shipment Tracking page verified")

            # Verify Shipment Tracking table
            expect(shipment_tracking_page.shipment_history_table).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.shipment_history_table.click()
            expect(shipment_tracking_page.table_date).to_be_visible(timeout=timeout_ms)
            expect(shipment_tracking_page.table_description).to_be_visible(timeout=timeout_ms)
            expect(shipment_tracking_page.table_tracking_number).to_be_visible(timeout=timeout_ms)
            shipment_tracking_page.table_selector.click()
            expect(shipment_tracking_page.table_selector_list).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Shipment Tracking table verified")

            # Verify Recycling link on Overview page
            dashboard_side_menu_page.click_overview()
            with context.expect_page() as new_page_info:
                overview_page.recycle_your_cartridge_link.click()
            new_tab = new_page_info.value
            assert "recycle" in new_tab.url, f"Expected 'recycle' in URL, but got {new_tab.url}"
            new_tab.close()
            page.bring_to_front()
            framework_logger.info("Recycling link on Overview page verified")

           # Verify Plan Details card on Overview page
            DashboardHelper.verify_plan_info(page, "7.99", "100")

            free_month_info = overview_page.free_months.text_content()
            numbers = re.findall(r"\d+", free_month_info)
            assert int(numbers[0]) > 0, f"Expected free months to be greater than 0, but got {numbers[0]}"
            framework_logger.info("Plan Details card on Overview page verified")

            # Verify Change Plan link on Overview page
            overview_page.change_plan_link.click()
            expect(update_plan_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Change Plan link on Overview page verified")

            # Verify Change Billing Info link on Overview page
            dashboard_side_menu_page.click_overview()
            overview_page.change_billing_link.click()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Change Billing Info link on Overview page verified")

            # Verify Change Shipping Info link on Overview page
            dashboard_side_menu_page.click_overview()
            overview_page.change_shipping_link.click()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Change Shipping Info link on Overview page verified")

            # Verify Redeem Code link on Overview page
            dashboard_side_menu_page.click_overview()
            overview_page.redeem_code_link.click()
            expect(overview_page.modal_offers).to_be_visible(timeout=timeout_ms)
            overview_page.close_promo_code_modal.click()
            overview_page.modal_offers.wait_for(state="detached", timeout=timeout_ms)
            framework_logger.info("Redeem Code link on Overview page verified")

            # Verify Refer a Friend card on Overview page
            expect(overview_page.raf_card).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Refer a Friend card on Overview page verified")

            # Verify Replace Printer link on Update Plan page
            dashboard_side_menu_page.click_update_plan()
            update_plan_page.replace_printer_link.click()
            expect(printer_replacement_page.printer_replacement_page).to_be_visible(timeout=timeout_ms)
            expect(printer_replacement_page.printer_set_up_button).to_be_visible(timeout=timeout_ms)
            expect(printer_replacement_page.printer_not_set_up_button).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Replace Printer link on Update Plan page verified")

            # Verify Update Plan plans
            dashboard_side_menu_page.click_update_plan()
            UpdatePlanHelper.verify_available_plans(page)
            framework_logger.info("Plans on Update Plan page verified")

            # Verify Update Plan page
            expect(update_plan_page.page_title).to_be_visible(timeout=timeout_ms)
            expect(update_plan_page.free_trial_info_card).to_be_visible(timeout=timeout_ms)
            expect(update_plan_page.plan_card_container).to_be_visible(timeout=timeout_ms)
            expect(update_plan_page.disclaimer_card).to_be_visible(timeout=timeout_ms)
            expect(update_plan_page.plan_details_card).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Update Plan page verified")

            # Verify Print and History link on Update Plan page
            update_plan_page.print_history_link.click()
            expect(print_history_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Print History Link on Update Plan page verified")

            # Verify Terms and Service link on Update Plan page
            dashboard_side_menu_page.click_update_plan()
            with context.expect_page() as new_page_info:
                update_plan_page.terms_and_service_link.click()
            new_tab = new_page_info.value
            expect(new_tab).to_have_url("https://instantink-stage1.hpconnectedstage.com/us/en/terms")
            new_tab.close()
            page.bring_to_front()
            framework_logger.info("Terms and Service link on Update Plan page verified")

            # Verify Change Shipping Info link on Update Plan page
            update_plan_page.change_shipping_link.click()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Change Shipping Link on Update Plan page verified")

            # Verify Change Billing Info link on Update Plan page
            dashboard_side_menu_page.click_update_plan()
            update_plan_page.change_billing_info_link.click()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Change Billing Link on Update Plan page verified")

            # Verify Contact Support link on Update Plan page
            dashboard_side_menu_page.click_update_plan()
            with context.expect_page() as new_page_info:
                update_plan_page.contact_support_link.click()
            new_tab = new_page_info.value
            assert "support" in new_tab.url, f"Expected 'support' in URL, but got {new_tab.url}"
            new_tab.close()
            page.bring_to_front()
            framework_logger.info("Contact Support link on Update Plan page verified")

            # Verify Reedeem Promo Code link on Update Plan page
            update_plan_page.prepaid_code_link.click()
            expect(overview_page.modal_offers).to_be_visible(timeout=timeout_ms)
            overview_page.close_promo_code_modal.click()
            overview_page.modal_offers.wait_for(state="detached", timeout=timeout_ms)
            framework_logger.info("Redeem Code link on Update Plan page verified")

            # Verify Cancel Instant Ink link on Update Plan page
            update_plan_page.cancel_instant_ink_link.click()
            expect(cancellation_page.confirm_cancellation_button).to_be_visible(timeout=timeout_ms)
            expect(cancellation_page.keep_enrollment_button).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Cancel Instant Ink Link on Update Plan page verified")

            # Verify Print History link
            dashboard_side_menu_page.click_print_history()
            expect(print_history_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Print History link on Dashboard Side Menu verified")

            # Verify Shipment Tracking link
            dashboard_side_menu_page.click_shipment_tracking()
            expect(shipment_tracking_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Shipment Tracking link on Dashboard Side Menu verified")

            # Verify Shipping and Billing link
            dashboard_side_menu_page.click_shipping_billing()
            expect(shipping_billing_page.page_title).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Shipping and Billing link on Dashboard Side Menu verified")

            # Verify Manage your shipping address link
            shipping_billing_page.manage_shipping_address.click()
            expect(shipping_billing_page.shipping_form_modal).to_be_visible(timeout=timeout_ms)
            shipping_billing_page.cancel_button.click()
            shipping_billing_page.shipping_form_modal.wait_for(state="detached", timeout=timeout_ms)
            framework_logger.info("Manage your shipping address link on Shipping & Billing page verified")

            # Verify Manage your payment method link
            shipping_billing_page.manage_your_payment_method_link.click()
            expect(shipping_billing_page.billing_form_modal).to_be_visible(timeout=timeout_ms)
            shipping_billing_page.cancel_button.click()
            shipping_billing_page.billing_form_modal.wait_for(state="detached", timeout=timeout_ms)
            framework_logger.info("Manage your payment method link on Shipping & Billing page verified")

            framework_logger.info("=== Smart Dashboard flow ended ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the II Subscription: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            context.close()
            browser.close()
