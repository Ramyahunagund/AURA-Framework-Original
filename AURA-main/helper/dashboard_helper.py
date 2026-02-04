from inspect import ismethod
import time
import re
from pages.cancellation_page import CancellationPage
from pages.change_plan_cancellation_page import ChangePlanCancellationPage
from pages.notifications_page import NotificationsPage
from pages.printer_replacement_page import PrinterReplacementPage
import test_flows_common.test_flows_common as common
from core.settings import framework_logger
from helper.hpid_helper import HPIDHelper
from helper.update_plan_helper import UpdatePlanHelper
from helper.enrollment_helper import EnrollmentHelper
from pages.cancellation_banner_page import CancellationBannerPage
from pages.cancellation_timeline_page import CancellationTimelinePage
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.shipping_billing_page import ShippingBillingPage
from pages.update_plan_page import UpdatePlanPage
from pages.print_history_page import PrintHistoryPage
from pages.overview_page import OverviewPage
from pages.privacy_banner_page import PrivacyBannerPage
from playwright.sync_api import expect
from core.settings import framework_logger, GlobalState
from pages.confirmation_page import ConfirmationPage
from datetime import datetime, timedelta
from pages.printer_selection_page import PrinterSelectionPage
from pages.tos_hp_smart_page import TermsOfServiceHPSmartPage
from pages.dashboard_hp_smart_page import DashboardHPSmartPage

class DashboardHelper:
    @staticmethod
    def access(page, tenant_email: str = None):
        page.wait_for_load_state("load", timeout=15000)
        page.goto(common._portalshell_url, timeout=45000)
        page.wait_for_load_state("load")
        try:
            page.wait_for_load_state("networkidle")
        except Exception:
            pass

        if "login" in page.url:
            if not tenant_email:
                raise ValueError("tenant_email is required for sign-in.")
            HPIDHelper.sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
        
        dashboard_side_menu_page = DashboardSideMenuPage(page)
        element = dashboard_side_menu_page.visible_instant_ink_menu_link()
        assert element.is_visible(), "Instant Ink menu link is not visible"

    @staticmethod
    def first_access(page, tenant_email: str):
        DashboardHelper.access(page, tenant_email)
        overview_page = OverviewPage(page)
        DashboardHelper.accept_banner_and_access_overview_page(page)
        
        # Dashboard first access
        elements = [
            lambda: overview_page.special_savings_modal_close,
            lambda: overview_page.flip_modal_not_now_button,
            lambda: overview_page.continue_setting_preferences,
            lambda: overview_page.accept_all_preferences,
            lambda: overview_page.no_paper_offer_modal,
            lambda: overview_page.skip_tour,
            lambda: overview_page.special_savings_modal_close
        ]

        if common._stack in ["pie", "stage"]:
            elements.append(lambda: overview_page.special_savings_modal_close)

        for attempt in range(6):
            if not elements:
                break

            remaining_elements = elements[:]
            for element_func in remaining_elements:
                try:
                    element = element_func()
                    if element.is_visible():
                        element.click()
                        element_name = element_func.__code__.co_names[0] if element_func.__code__.co_names else "unknown"
                        print(f"Clicked on element: {element_name}")
                        elements.remove(element_func)
                except Exception:
                    pass
            time.sleep(2)

    @staticmethod
    def sees_status_card(page):
        overview_page = OverviewPage(page)
        expect(overview_page.status_card_title).to_be_visible(timeout=90000)
        expect(overview_page.printer_details_link).to_be_visible()
        expect(overview_page.monthly_summary).to_be_visible()

    @staticmethod
    def sees_plan_details_card(page):
        overview_page = OverviewPage(page)
        expect(overview_page.plan_details_card).to_be_visible()

    @staticmethod
    def doesnt_see_free_months(page):
        overview_page = OverviewPage(page)
        expect(overview_page.free_months).not_to_be_visible()

    @staticmethod
    def get_plan_value_from_plan_details(page):
        overview_page = OverviewPage(page)
        plan_info_text = overview_page.plan_information.inner_text()
        plan_value = common.extract_numbers_from_text(plan_info_text)[-1]
        return plan_value

    @staticmethod
    def verify_free_months_value(page, free_months):
        overview_page = OverviewPage(page)
        free_months_text = overview_page.free_months.inner_text()
        free_months_numbers = common.extract_numbers_from_text(free_months_text)
        if not free_months_numbers:
            raise ValueError(f"No numbers found in free months text: '{free_months_text}'")
        free_months_from_page = int(free_months_numbers[0])
        assert free_months == free_months_from_page, \
            f"Expected free months {free_months}, but got {free_months_from_page} from overview page"

    @staticmethod
    def verify_special_offer_value(page, prepaid):
        overview_page = OverviewPage(page)
        offer_value = float(common.extract_numbers_from_text(overview_page.special_offers_balance.inner_text())[0])
        assert offer_value == float(prepaid), \
            f"Expected offer value '{prepaid}', but got '{offer_value}' from overview page"

    @staticmethod
    def verify_plan_value(page, plan_value):
        plan_value_from_page = DashboardHelper.get_plan_value_from_plan_details(page)
        assert plan_value_from_page == plan_value, \
            f"Expected plan value '{plan_value}', but got '{plan_value_from_page}' from overview page"

    @staticmethod
    def verify_progress_bars_visible(page, progress_bars=None):
        overview_page = OverviewPage(page)

        if progress_bars is None:
            progress_bars = ["plan", "trial", "rollover", "credited", "complimentary"]

        progress_bar_map = {
            "plan": overview_page.plan_pages_bar,
            "trial": overview_page.trial_pages_bar,
            "rollover": overview_page.rollover_pages_bar,
            "credited": overview_page.credited_pages_bar,
            "complimentary": overview_page.complimentary_pages_bar
        }

        for i, progress_bar in enumerate(progress_bars):
            if progress_bar not in progress_bar_map:
                raise ValueError(f"Invalid progress_bar '{progress_bar}'. Valid options: {list(progress_bar_map.keys())}")

            timeout = 90000 if i == 0 else None
            if timeout:
                expect(progress_bar_map[progress_bar]).to_be_visible(timeout=timeout)
            else:
                expect(progress_bar_map[progress_bar]).to_be_visible()

    @staticmethod
    def verify_paper_progress_bars_visible(page, progress_bars=None):
        overview_page = OverviewPage(page)

        if progress_bars is None:
            progress_bars = ["plan", "trial", "rollover"]

        progress_bar_map = {
            "plan": overview_page.paper_plan_pages_bar,
            "trial": overview_page.paper_trial_pages_bar,
            "rollover": overview_page.paper_rollover_pages_bar
        }

        for i, progress_bar in enumerate(progress_bars):
            if progress_bar not in progress_bar_map:
                raise ValueError(f"Invalid progress_bar '{progress_bar}'. Valid options: {list(progress_bar_map.keys())}")

            timeout = 90000 if i == 0 else None
            if timeout:
                expect(progress_bar_map[progress_bar]).to_be_visible(timeout=timeout)
            else:
                expect(progress_bar_map[progress_bar]).to_be_visible()

    @staticmethod
    def verify_pages_used(page, progress_bar, pages_used: str, total_pages: str):
        overview_page = OverviewPage(page)

        progress_bar_map = {
            "plan": overview_page.plan_pages_bar,
            "trial": overview_page.trial_pages_bar,
            "rollover": overview_page.rollover_pages_bar,
            "credited": overview_page.credited_pages_bar,
            "additional": overview_page.additional_pages_bar,
            "complimentary": overview_page.complimentary_pages_bar,
            "paper_plan": overview_page.paper_plan_pages_bar,
            "paper_trial": overview_page.paper_trial_pages_bar,
            "paper_rollover": overview_page.paper_rollover_pages_bar
        }

        if progress_bar not in progress_bar_map:
            raise ValueError(f"Invalid progress_bar '{progress_bar}'. Valid options: {list(progress_bar_map.keys())}")

        progress_bar_element = progress_bar_map[progress_bar]
        numbers = common.extract_numbers_from_text(progress_bar_element.text_content())

        assert str(pages_used) == numbers[0], f"Expected {pages_used} pages used in {progress_bar} bar, but found {numbers[0]}"
        assert str(total_pages) == numbers[1], f"Expected {total_pages} total pages in {progress_bar} bar, but found {numbers[1]}"

    @staticmethod
    def pause_plan(page, months, page_view="Dashboard"):
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)

        if page_view == "Dashboard":
            overview_page.pause_plan_link.click()
        elif page_view == "Cancellation":
            cancellation_page.pause_plan_link.click()

        overview_page.pause_plan_modal.last.wait_for()
        overview_page.pause_plan_dropdown.last.click()
        months_option = page.locator(f"[data-value='{months}']")
        months_option.click()
        overview_page.confirm_pause_plan.last.click()
        overview_page.pause_plan_modal.last.wait_for(state="hidden")

    @staticmethod
    def sees_plan_pause_banner(page):
        overview_page = OverviewPage(page)
        expect(overview_page.plan_paused_banner).to_be_visible(timeout=90000)

    @staticmethod
    def click_resume_plan_banner(page):
        overview_page = OverviewPage(page)
        overview_page.resume_plan_link.click()
        overview_page.confirm_resume_plan_modal.wait_for(state="visible")

    @staticmethod
    def click_keep_paused(page):
        overview_page = OverviewPage(page)
        overview_page.keep_paused_button.click()
        overview_page.confirm_resume_plan_modal.wait_for(state="detached")

    @staticmethod
    def click_resume_plan(page):
        overview_page = OverviewPage(page)
        overview_page.resume_plan_button.click()
        overview_page.confirm_resume_plan_modal.wait_for(state="detached")

    @staticmethod
    def click_pause_plan_link_and_close_modal(page, page_view="Overview"):
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)

        if page_view == "Overview":
            overview_page.pause_plan_link.click()
            overview_page.pause_plan_modal.last.wait_for(state="visible")
            framework_logger.info("Opened pause plan modal")

        if page_view == "Cancellation":
            cancellation_page = CancellationPage(page)
            cancellation_page.pause_plan_link.click()
            cancellation_page.pause_plan_modal.last.wait_for(state="visible")
            framework_logger.info("Opened pause plan modal")

        try:          
            if overview_page.close_pause_plan_button.is_visible():
                overview_page.close_pause_plan_button.click()
            else:
                page.keyboard.press("Escape")
        except:
            page.keyboard.press("Escape")
        
        overview_page.pause_plan_modal.last.wait_for(state="hidden")
        framework_logger.info("Closed pause plan modal")

    @staticmethod
    def sees_canceled_subscription_overview_page(page, expected_text="There are no active plans for this printer."):
        overview_page = OverviewPage(page)
        expect(overview_page.status_card_title).to_be_visible(timeout=120000)
        expect(overview_page.printer_details_link).to_be_visible()
        expect(overview_page.plan_details_card).to_be_visible()

        assert not overview_page.cartridge_status_card.is_visible()
        assert not overview_page.special_offer_card.is_visible()

        expect(overview_page.no_active_plans).to_be_visible(timeout=30000)
        expect(overview_page.no_active_plans).to_have_text(expected_text)
        expect(overview_page.plan_details_card).not_to_have_text('Enroll Printer Again')

    @staticmethod
    def verify_tooltip(page, tooltip):
        overview_page = OverviewPage(page)
        tooltip_map = {
            "plan": overview_page.plan_pages_bar,
            "trial": overview_page.trial_pages_bar,
            "rollover": overview_page.rollover_pages_bar,
            "credited": overview_page.credited_pages_bar,
            "additional": overview_page.additional_pages_bar,
            "complimentary": overview_page.complimentary_pages_bar
        }

        if tooltip not in tooltip_map:
            raise ValueError(f"Invalid tooltip '{tooltip}'. Valid options: {list(tooltip_map.keys())}")

        progress_bar_element = tooltip_map[tooltip]
        tooltip_icon = progress_bar_element.locator('[class^="progressBar__tooltip-icon"]')
        tooltip_icon.hover()

        tooltip_text = progress_bar_element.locator('div[role="tooltip"]')
        expect(tooltip_text).to_be_visible()
        page.mouse.move(0, 0)
        tooltip_text.wait_for(state="hidden")


    @staticmethod
    def verify_pages_on_tooltip(page, tooltip, pages_used=None, total_pages=None):
        overview_page = OverviewPage(page)
        tooltip_map = {
            "plan": overview_page.plan_pages_bar,
            "trial": overview_page.trial_pages_bar,
            "rollover": overview_page.rollover_pages_bar,
            "credited": overview_page.credited_pages_bar,
            "additional": overview_page.additional_pages_bar,
            "complimentary": overview_page.complimentary_pages_bar
        }

        if tooltip not in tooltip_map:
            raise ValueError(f"Invalid tooltip '{tooltip}'. Valid options: {list(tooltip_map.keys())}")

        progress_bar_element = tooltip_map[tooltip]
        tooltip_icon = progress_bar_element.locator('[class^="progressBar__tooltip-icon"]')
        tooltip_icon.hover()

        tooltip_text = progress_bar_element.locator('div[role="tooltip"]').inner_text()
        numbers_list = common.extract_numbers_from_text(tooltip_text)

        assert str(total_pages) == numbers_list[0], f"Expected total_pages {total_pages}, but found {numbers_list[0]} in tooltip"
        if pages_used is not None:
            assert str(pages_used) == numbers_list[1], f"Expected pages_used {pages_used}, but found {numbers_list[1]} in tooltip"
            assert str(total_pages) == numbers_list[2], f"Expected total_pages {total_pages}, but found {numbers_list[2]} in tooltip"

    @staticmethod
    def verify_total_pages_printed(page, expected_pages: int):
        overview_page = OverviewPage(page)
        total_pages_text = overview_page.total_pages_printed.inner_text()
        numbers = common.extract_numbers_from_text(total_pages_text)

        if len(numbers) == 0:
            raise ValueError(f"Expected total pages printed to be {expected_pages}, but found no numbers in text: '{total_pages_text}'")

        assert numbers[0] == str(expected_pages), \
            f"Expected total pages printed to be {expected_pages}, but found {numbers[0]} in text: '{total_pages_text}'"
    
    @staticmethod
    def verify_total_sheets_used(page, expected_sheets: int):
        overview_page = OverviewPage(page)
        total_sheets_text = overview_page.paper_sheets_used.inner_text()
        numbers = common.extract_numbers_from_text(total_sheets_text)

        if len(numbers) == 0:
            raise ValueError(f"Expected total sheets used to be {expected_sheets}, but found no numbers in text: '{total_sheets_text}'")

        assert numbers[0] == str(expected_sheets), \
            f"Expected total sheets used to be {expected_sheets}, but found {numbers[0]} in text: '{total_sheets_text}'"

    @staticmethod
    def verify_monthly_section_on_status_card(page, expected_charge, start_time: str, end_time: str):
        overview_page = OverviewPage(page)
        overview_page.wait.monthly_summary(state="visible", timeout=120000)
        expect(overview_page.monthly_summary).to_be_visible()
        expect(overview_page.estimated_charge).to_be_visible()
        expect(overview_page.total_pages_printed).to_be_visible()

        estimated_charge_text = overview_page.estimated_charge.inner_text()
        estimated_charge = common.extract_numbers_from_text(estimated_charge_text)

        if len(estimated_charge) == 0:
            raise ValueError(f"Expected estimated charge to be {expected_charge}, but found no numbers in text: '{estimated_charge_text}'")

        assert float(estimated_charge[0]) == float(expected_charge), \
            f"Expected estimated charge to be {expected_charge}, but found {estimated_charge[0]} in text: '{estimated_charge_text}'"

        billing_period = overview_page.date_range_container.inner_text()
        DashboardHelper.compare_billing_period_with_tolerance(billing_period, start_time, end_time)

    @staticmethod
    def verify_paper_monthly_section_on_status_card(page, expected_charge, start_time: str, end_time: str):
        overview_page = OverviewPage(page)
        expect(overview_page.paper_billing_cycle).to_be_visible(timeout=120000)
        expect(overview_page.paper_estimated_charge).to_be_visible()
        expect(overview_page.paper_sheets_used).to_be_visible()

        estimated_charge_text = overview_page.paper_estimated_charge.inner_text()
        estimated_charge = common.extract_numbers_from_text(estimated_charge_text)

        if len(estimated_charge) == 0:
            raise ValueError(f"Expected estimated charge to be {expected_charge}, but found no numbers in text: '{estimated_charge_text}'")

        assert float(estimated_charge[0]) == float(expected_charge), \
            f"Expected estimated charge to be {expected_charge}, but found {estimated_charge[0]} in text: '{estimated_charge_text}'"

        billing_period = overview_page.paper_billing_cycle.inner_text()
        DashboardHelper.compare_billing_period_with_tolerance(billing_period, start_time, end_time)

    @staticmethod
    def compare_billing_period_with_tolerance(billing_period_str, start_time_str, end_time_str):
        start_dt = datetime.strptime(start_time_str, "%Y/%m/%d %I:%M:%S %p")
        end_dt = datetime.strptime(end_time_str, "%Y/%m/%d %I:%M:%S %p")

        start_fmt = start_dt.strftime("%b %d")
        end_dates = [
            end_dt - timedelta(days=1),
            end_dt,
            end_dt + timedelta(days=1)
        ]
        end_fmts = [d.strftime("%b %d") for d in end_dates]
        matches = [f"{start_fmt} - {end_fmt}" for end_fmt in end_fmts]

        if billing_period_str not in matches:
            raise AssertionError(
                f"Billing period '{billing_period_str}' does not match any of the allowed periods: {matches}"
            )

    @staticmethod
    def keep_subscription_and_return_to_feedback_options(page):
        DashboardHelper.keep_subscription(page)
        UpdatePlanHelper.cancellation_subscription(page)
        framework_logger.info("Navigated back to the subscription cancellation feedback page")

    @staticmethod
    def sees_cancellation_in_progress(page):
        cancellation_banner = CancellationBannerPage(page)
        overview_page = OverviewPage(page)
        assert overview_page.overview_page_title.is_visible()
        assert overview_page.keep_enrollment_button.is_visible()
        assert cancellation_banner.see_cancellation_timeline.is_visible()

    @staticmethod
    def keep_subscription(page, confirm=True):
        overview_page = OverviewPage(page)
        overview_page.keep_enrollment_button.click()
        if confirm:
            overview_page.resume_button.click()
        else:
            overview_page.back_button.click()

    @staticmethod
    def verify_cancellation_banner(page, end_date: list):
        cancellation_banner = CancellationBannerPage(page)
        expect(cancellation_banner.keep_subscription_button).to_be_visible(timeout=60000)
        expect(cancellation_banner.see_cancellation_timeline).to_be_visible(timeout=60000)
        expect(cancellation_banner.cancellation_banner).to_be_visible(timeout=60000)
        cancel_date_text = cancellation_banner.cancellation_banner.inner_text()
        cancel_date_list = common.extract_numbers_from_text(cancel_date_text)
        assert end_date == cancel_date_list, \
            f"Expected cancellation end date {end_date}, but got {cancel_date_list} from cancellation banner"

    @staticmethod
    def get_list_with_end_date_from_cancellation_timeline(page):
        cancellation_timeline = CancellationTimelinePage(page)
        cancel_date_text = cancellation_timeline.timeline_stepper_header(1).inner_text()
        cancel_date_list = common.extract_numbers_from_text(cancel_date_text)
        return cancel_date_list

    @staticmethod
    def validate_see_cancellation_timeline_feature(page):
        cancellation_banner = CancellationBannerPage(page)
        cancellation_banner.see_cancellation_timeline.click()
        cancellation_timeline = CancellationTimelinePage(page)
        cancellation_timeline.timeline_modal.is_visible()
        cancellation_timeline.close_button.click()

    @staticmethod
    def validate_keep_enrollment_feature(page):
        cancellation_banner = CancellationBannerPage(page)
        cancellation_banner.keep_subscription_button.click()
        cancellation_banner.back_button.click()
        cancellation_banner.keep_subscription_button.click()
        cancellation_banner.resume_button.click()
        cancellation_banner.wait.resume_banner

    @staticmethod
    def verify_trial_pages_used(page, pages_used: int):
        overview_page = OverviewPage(page)
        trial_bar = overview_page.trial_pages_bar
        numbers = common.extract_numbers_from_text(trial_bar.text_content())
        assert int(numbers[0]) == pages_used, f"Expected {pages_used} trial pages used, but found {numbers[0]}"
        
    @staticmethod
    def verify_cancellation_banner_message(page, message: str):
        cancellation_banner = CancellationBannerPage(page)
        cancellation_banner.cancellation_banner.wait_for(state="visible", timeout=120000)
        assert cancellation_banner.cancellation_banner.is_visible()
        assert message in cancellation_banner.cancellation_banner.inner_text()

    @staticmethod
    def verify_ink_cartridge_status_message(page, message: str):
        overview_page = OverviewPage(page)
        overview_page.ink_cartridge_status_card.wait_for(state="visible", timeout=90000)
        assert overview_page.ink_cartridge_status_card.is_visible()
        assert message in overview_page.ink_cartridge_status_card.inner_text()
        
    @staticmethod
    def verify_subscription_resumed_banner(page, message):
        overview_page = OverviewPage(page)
        overview_page.subscription_resumed_banner.wait_for(state="visible", timeout=90000)
        assert message in overview_page.subscription_resumed_banner.inner_text()

    @staticmethod
    def verify_end_date_on_cancellation_banner(page):
        cancellation_banner = CancellationBannerPage(page)
        cancellation_banner.cancellation_banner.wait_for(state="visible", timeout=90000)
        text = cancellation_banner.cancellation_banner.inner_text()
        match = re.search(r'([A-Za-z]{3} \d{2}, \d{4})', text)
        assert match, "End date not found in cancellation banner text"
        last_day = match.group(1)
        assert cancellation_banner.cancellation_banner.is_visible()
        assert f"Your subscription will end on {last_day}" in text
        assert f"Your subscription will end on {last_day}" in text

    @staticmethod
    def printer_status_tooltip(page, tooltip):
        overview_page = OverviewPage(page)
        expect(overview_page.printer_status_tooltip).to_be_visible(timeout=30000)

        tooltip_icon = overview_page.locator('[id^="printerStatusRow__printer-status-row"] [class^="printerStatus__printer-status"]')
        tooltip_icon.hover()

        tooltip_text = overview_page.locator('div[role="tooltip"]')
        expect(tooltip_text).to_be_visible()
        page.mouse.move(0, 0)
        tooltip_text.wait_for(state="hidden")

    @staticmethod
    def verify_pause_plan_information(page):
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)
        assert overview_page.pause_plan_info.is_visible()
        assert not cancellation_page.whats_happens_next.is_visible()
		
    @staticmethod
    def verify_no_payment_method_added_on_plan_details_card(page):
        overview_page = OverviewPage(page)
        expect(overview_page.plan_details_card).to_be_visible()
        expect(overview_page.message_add_billing_info).to_have_text("No payment method has been added.")
        
    @staticmethod
    def verify_add_payment_method_message_on_plan_details_card(page, message_type="alert"):    
        overview_page = OverviewPage(page)
        expect(overview_page.plan_details_card).to_be_visible()
        
        if message_type == "alert":
            expect(overview_page.alert_message).to_be_visible()
        elif message_type == "critical":
            expect(overview_page.critical_message).to_be_visible()
        else:
            raise ValueError(f"Invalid message_type '{message_type}'. Valid options: 'alert', 'critical'")

        expect(overview_page.message_add_billing_info).to_be_visible()

    @staticmethod
    def verify_this_PIN_or_promo_code_requires_an_additional_payment_method_message(page):
        overview_page = OverviewPage(page)
        expect(overview_page.modal_offers).to_be_visible()
        expect(overview_page.promo_code_helper_text).to_be_visible()

    @staticmethod
    def access_shipping_billing_page(page):
        overview_page = OverviewPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        overview_page.change_billing_link.click()
        expect(shipping_billing_page.page_title).to_be_visible(timeout=120000)

    @staticmethod
    def verify_and_close_change_plan_modal(page):
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)
        change_plan_modal = ChangePlanCancellationPage(page)

        expect(overview_page.cancel_instant_ink).to_be_visible()
        overview_page.cancel_instant_ink.click()

        expect(cancellation_page.change_plan_link).to_be_visible()
        cancellation_page.change_plan_link.click()

        expect(change_plan_modal.return_to_cancellation_button).to_be_visible(timeout=60000)
        change_plan_modal.return_to_cancellation_button.click()

    @staticmethod
    def close_change_plan_modal_x(page):
        overview_page = OverviewPage(page)
        cancellation_page = CancellationPage(page)

        expect(cancellation_page.change_plan_link).to_be_visible(timeout=60000)
        cancellation_page.change_plan_link.click()

        expect(cancellation_page.close_modal).to_be_visible(timeout=60000)
        cancellation_page.close_modal.click()

    @staticmethod
    def apply_promo_code_on_overview_page(page, promo_code: str):
        overview_page = OverviewPage(page)
        overview_page.redeem_code_link.click()
        expect(overview_page.modal_offers).to_be_visible()
        overview_page.promo_code_input_box.fill(promo_code)
        
        if overview_page.accept_promo_code_checkbox.is_visible():
            overview_page.accept_promo_code_checkbox.click()
        else:
            print("\tWARNING: Accept Promo Code checkbox not displayed!")

        overview_page.apply_promo_code_button.click()
        overview_page.promo_code_success_message.wait_for(state="visible")
        overview_page.close_promo_code_modal.click()

    @staticmethod
    def add_shipping(page, index=0, company_name=None):
        confirmation_page = ConfirmationPage(page)
        address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
        state_name = address.get("fullState", address.get(f"fullState_{GlobalState.language_code}"))
        if company_name:
            confirmation_page.company_name_input.fill(company_name)
        confirmation_page.street1_input.fill(address.get("street1", ""))
        confirmation_page.street2_input.fill(address.get("street2", ""))
        countries_without_city_mandate = ["Hong Kong", "Singapore"]
        if GlobalState.country not in countries_without_city_mandate:
            confirmation_page.city_input.fill(address.get("city", ""))
        countries_without_states_mandate = ["Austria", "Belgium", "Denmark", "Finland", "France", "Germany", "Luxembourg", "Netherlands", "New Zealand", "Norway", "Portugal", "Puerto Rico", "Singapore", "Sweden", "Switzerland"]
        if GlobalState.country not in countries_without_states_mandate and state_name:
            DashboardHelper.select_state(page, state_name)
        countries_without_zip_mandate = ["Hong Kong"]
        if GlobalState.country not in countries_without_zip_mandate:
            confirmation_page.zip_code_input.fill(address.get("zipCode", ""))
        confirmation_page.phone_number_input.fill(address.get("phoneNumber1", ""))
        confirmation_page.save_button.click()
        try:
            page.wait_for_selector(confirmation_page.elements.suggested_address_modal, state="visible", timeout=60000)
            if page.wait_for_selector(confirmation_page.elements.suggested_address_modal).is_enabled():
                confirmation_page.ship_to_address_button.click()
        except Exception as e:
            print("Suggested address modal not displayed or button not available")

    @staticmethod
    def select_state(page, state_name, avoid_state=False):
        confirmation_page = ConfirmationPage(page)
        confirmation_page.state_dropdown.click()
        element_id = confirmation_page.state_dropdown.get_attribute("id")
        select_list_option = f"#{element_id}-listbox li"
        
        if avoid_state:
            selector = f"{select_list_option}:not(:has-text('{state_name}'))"
            select_state = page.locator(selector).first
        else:
            selector = f"{select_list_option}:has-text('{state_name}')"
            select_state = page.locator(selector)
        
        select_state.wait_for(state="visible", timeout=2000)
        value = None
        try:
            value = select_state.get_attribute('data-value') #'[data-value="NC"]'
        except Exception:
            pass
        select_state.click()
        return value or state_name

    @staticmethod
    def add_billing(page, payment_method=None):
        if payment_method is None:
            payment_method = getattr(GlobalState, "payment_method", None)
        if payment_method:
            if "paypal" in payment_method:
                DashboardHelper.add_paypal_billing(page, payment_method)
                return
            elif payment_method == "google_pay":
                DashboardHelper.add_google_pay_billing(page)
                return
            elif payment_method == "apple_pay":
                DashboardHelper.add_apple_pay_billing(page)
                return
            elif "direct_debit" in payment_method:
                DashboardHelper.add_direct_debit_billing(page, payment_method)
                return  
        card_payment_gateway = getattr(GlobalState, "card_payment_gateway")
        if card_payment_gateway == "PGS":
            DashboardHelper.add_pgs_billing(page, payment_method)
        elif card_payment_gateway == "2CO":
            DashboardHelper.add_2co_billing(page, payment_method)
        else:
            raise ValueError(f"Unsupported payment provider: {card_payment_gateway}")

    @staticmethod
    def add_pgs_billing(page, card_type=None):
        confirmation_page = ConfirmationPage(page)
        shipping_billing_page = ShippingBillingPage(page)
        payment_data = common.get_payment_method_data(card_type)
        framework_logger.info(f"Using card type: {card_type}")
       
        if GlobalState.country_code == "IT":
            page.fill(confirmation_page.elements.tax_id_input, "MRTMTT91D08F205J")

        # Fix: check if enabled, then click
        page.locator(confirmation_page.elements.billing_continue_button).is_enabled()
        page.locator(confirmation_page.elements.billing_continue_button).click()
        page.locator(confirmation_page.elements.iframe_pgs).wait_for(state="visible", timeout=120000)
        frame = page.frame_locator(confirmation_page.elements.iframe_pgs)
        card_input = frame.locator(confirmation_page.elements.card_number)
        card_input.fill(payment_data["credit_card_number"])
        frame.locator(confirmation_page.elements.exp_month).select_option(payment_data.get("expiration_month"))
        frame.locator(confirmation_page.elements.exp_year).select_option(payment_data.get("expiration_year"))
        frame.locator(confirmation_page.elements.cvv_input).type(payment_data["cvv"])        
        if frame.locator(confirmation_page.elements.billing_next_button).count() > 0:
            frame.locator(confirmation_page.elements.billing_next_button).click()
        else:
            frame.locator(confirmation_page.elements.sca_save_button).click()
            try:
                frame.locator("iframe#redirectTo3ds1Frame").wait_for(state="visible", timeout=5000)
                challenge_frame = frame.frame_locator("#redirectTo3ds1Frame")
                submit_selector = 'input[type="submit"][value="Submit"]'
            except:
                frame.locator("iframe" + confirmation_page.elements.iframe_2fa).wait_for(state="visible", timeout=5000)
                challenge_frame = frame.frame_locator(confirmation_page.elements.iframe_2fa)
                submit_selector = confirmation_page.elements.acs_submit
            challenge_frame.locator(confirmation_page.elements.authentication_result_2fa).wait_for(state="visible", timeout=10000)
            challenge_frame.locator(confirmation_page.elements.authentication_result_2fa).select_option(payment_data.get("3ds_auth_result", "AUTHENTICATED"))
            challenge_frame.locator(submit_selector).wait_for(state="visible")
            challenge_frame.locator(submit_selector).click()
        shipping_billing_page.update_shipping_billing_message.first.wait_for(state="visible", timeout=60000)

    @staticmethod
    def add_company_and_tax_account_type_business(page, company_name=None, tax_id=None):
        shipping_billing_page = ShippingBillingPage(page)
        confirmation_page = ConfirmationPage(page)
        shipping_billing_page.manage_your_payment_method_link.click()
        ShippingBillingPage.select_business_account_type(page)
        if company_name:
            confirmation_page.billing_company_input.fill(company_name)
        if tax_id:
            confirmation_page.tax_id_input.fill(tax_id)
       
    @staticmethod
    def add_paypal_billing(page, payment_type="paypal"):
        confirmation_page = ConfirmationPage(page)
        page.wait_for_timeout(5000)
        confirmation_page.billing_continue_button.click()
        try:
            confirmation_page.paypal_button.wait_for(timeout=60000)
        except Exception as e:
            if page.locator(confirmation_page.elements.billing_continue_button).is_enabled():
                confirmation_page.billing_continue_button.click()
                confirmation_page.paypal_button.wait_for(timeout=60000)
            else:
                raise Exception(f"Payment iframe not found: {e}")

        with page.context.expect_page() as new_page_info:
            page.wait_for_timeout(2000)
            confirmation_page.paypal_button.click()
            print("Waiting for PayPal page to open...")

        paypal_page = new_page_info.value

        payment_data = common.get_payment_method_data(payment_type)
        paypal_email = payment_data["email"]
        paypal_password = payment_data["password"]
            
        EnrollmentHelper._paypal_login_popup(paypal_page, confirmation_page, paypal_email, paypal_password)

    @staticmethod
    def verify_shipping_address_updated(page, index=0):
        overview_page = OverviewPage(page)
        address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
        expect(overview_page.shipping_information).to_be_visible(timeout=30000)
        framework_logger.info("Shipping information section is visible")

        expect(overview_page.shipping_address_street).to_be_visible(timeout=10000)
        street_text = overview_page.shipping_address_street.inner_text()
        framework_logger.info(f"Street address displayed: {street_text}")
        
        assert address['street1'] in street_text, \
        f"Expected street address '{address['street1']}' not found in '{street_text}'"

        expect(overview_page.shipping_address_city_state_zip).to_be_visible(timeout=10000)
        city_state_zip_text = overview_page.shipping_address_city_state_zip.inner_text()
        framework_logger.info(f"City, state, zip displayed: {city_state_zip_text}")

        assert address['city'] in city_state_zip_text, \
            f"Expected city '{address['city']}' not found in '{city_state_zip_text}'"

        assert address['zipCode'] in city_state_zip_text, \
            f"Expected zip code '{address['zipCode']}' not found in '{city_state_zip_text}'"

        framework_logger.info(f"Successfully verified that shipping address was updated to {address}")

    @staticmethod
    def verify_credit_card_master_updated(page):
        overview_page = OverviewPage(page)
        expect(overview_page.credit_card_payment_info).to_be_visible(timeout=30000)
        framework_logger.info("MasterCard payment information is visible")
        expect(overview_page.credit_card_expiration_info).to_be_visible(timeout=10000)
        expiration_text = overview_page.credit_card_expiration_info.inner_text()
        framework_logger.info(f"Credit card expiration info: {expiration_text}")
        assert "Expires:" in expiration_text, \
            f"Expected expiration information, but found: {expiration_text}"

        framework_logger.info("Successfully verified that payment method was updated to credit_card_master (MasterCard)")

    @staticmethod
    def verify_footer_section(page):    
        overview_page = OverviewPage(page)
        # HP.com
        with page.expect_popup(timeout=30000) as popup_info:
            overview_page.footer_hp_com.click()
        popup = popup_info.value
        expect(popup).to_have_url(re.compile(r'/home.html'), timeout=30000)
        popup.close()

        # Wireless Print Center
        with page.expect_popup(timeout=30000) as popup_info:
            overview_page.footer_wireless_print_center.click()
        popup = popup_info.value
        expect(popup).to_have_url(re.compile(r'/wireless-printing'), timeout=30000)
        popup.close()

        # Help Center
        overview_page.footer_help_center.click()
        expect(page).to_have_url(re.compile(r'/help/about-hp-smart'))
        page.go_back()

        # Terms of Use
        with page.expect_popup(timeout=30000) as popup_info:
            overview_page.footer_terms_of_use.click()
        popup = popup_info.value
        expect(popup).to_have_url(re.compile(r'/tou'), timeout=30000)
        popup.close()

        # HP Privacy
        with page.expect_popup(timeout=30000) as popup_info:
            overview_page.footer_hp_privacy.click()
        popup = popup_info.value
        expect(popup).to_have_url(re.compile(r'/privacy-central.html'), timeout=30000)
        popup.close()

        # HP Privacy Choices
        with page.expect_popup(timeout=30000) as popup_info:
            overview_page.footer_hp_your_privacy_choices.click()
        popup = popup_info.value
        expect(popup).to_have_url(re.compile(r'/your-privacy-choices.html'), timeout=30000)
        popup.close()

    @staticmethod
    def accept_banner_and_access_overview_page(page):
        dashboard_side_menu_page = DashboardSideMenuPage(page)
        overview_page = OverviewPage(page)
        privacy_banner_page = PrivacyBannerPage(page)
        privacy_banner_page.accept_privacy_banner()
        
        dashboard_side_menu_page.expand_instant_ink_menu()
        dashboard_side_menu_page.click_overview()
        overview_page.get_page_title(220000)

    @staticmethod
    def skips_all_but_tour_precondition(page):
        overview_page = OverviewPage(page)
        
        elements = [
            lambda: overview_page.continue_setting_preferences,
            lambda: overview_page.accept_all_preferences,
            lambda: overview_page.no_paper_offer_modal,
        ]

        for attempt in range(6):
            if not elements:
                break

            remaining_elements = elements[:]
            for element_func in remaining_elements:
                try:
                    element = element_func()
                    if element.is_visible():
                        element.click(timeout=60000)
                        element_name = element_func.__code__.co_names[0] if element_func.__code__.co_names else "unknown"
                        print(f"Clicked on element: {element_name}")
                        elements.remove(element_func)
                except Exception:
                    pass
            time.sleep(2)

    @staticmethod
    def skip_tour_modal(page):
        overview_page = OverviewPage(page)
        expect(overview_page.skip_tour).to_be_visible(timeout=30000)
        overview_page.skip_tour.click()

    @staticmethod
    def verify_tour_modal_not_appears(page):
        overview_page = OverviewPage(page)
        expect(overview_page.page_title).to_be_visible(timeout=30000)
        assert not overview_page.skip_tour.is_visible()

    @staticmethod
    def sign_out(page):
        overview_page = OverviewPage(page)
        overview_page.avatar_menu.click()
        expect(overview_page.sign_out_button).to_be_visible(timeout=30000)
        overview_page.sign_out_button.click()

    @staticmethod
    def see_notification_on_dashboard(page, notifications_text: str):
        notifications_page = NotificationsPage(page)
        notifications_page.wait.table(timeout=600000)
        expect(notifications_page.table).to_be_visible(timeout=30000)
        notification_content = notifications_page.table.inner_text()
        assert notifications_text in notification_content

    @staticmethod
    def click_enroll_printer_again_and_validate_new_tab(page):       
        overview_page = OverviewPage(page)        
        
        initial_pages_count = len(page.context.pages)
        overview_page.enroll_printer_again_button.click()
       
        page.wait_for_timeout(3000)
        new_pages_count = len(page.context.pages)
        
        if new_pages_count > initial_pages_count:
            # Validate Printer Selection page in new tab
            new_tab = page.context.pages[-1]
            new_tab.wait_for_load_state("networkidle", timeout=120000)
            
            # Accept TOS if present
            try:
                EnrollmentHelper.accept_terms_of_service(new_tab)
                framework_logger.info(f"Terms of Services accepted")
            except Exception as e:
                framework_logger.info(f"Terms of Service not present or already accepted: {e}")
        
            printer_selection = PrinterSelectionPage(new_tab)
            new_tab.wait_for_selector(printer_selection.elements.printer_selection_page, state="visible", timeout=120000)
            
            new_tab.close()
            page.bring_to_front()
            
            overview_page.close_finish_enrollment_button.click()
            
        else:
            raise AssertionError("Expected new tab to open but none was found")

    @staticmethod
    def click_enroll_printer_again_button(page):       
        try:
            overview_page = OverviewPage(page)     
            
            initial_pages_count = len(page.context.pages)
            overview_page.enroll_printer_again_button.click()
            
            page.wait_for_timeout(3000)
            new_pages_count = len(page.context.pages)
            
            if new_pages_count > initial_pages_count:
                new_tab = page.context.pages[-1]
                new_tab.wait_for_load_state("networkidle", timeout=120000)
                
                # Accept TOS if present
                try:
                    EnrollmentHelper.accept_terms_of_service(new_tab)
                    framework_logger.info("Terms of Services accepted")
                except Exception as e:
                    framework_logger.info(f"Terms of Service not present or already accepted: {e}")
                
                framework_logger.info("Successfully opened new enrollment tab")
                return True, new_tab
            else:
                framework_logger.warning("Expected new tab to open but none was found")
                return False, None
                
        except Exception as e:
            framework_logger.error(f"Error clicking 'Enroll Printer Again' button: {e}")
            return False, None
        
    @staticmethod
    def select_printer_from_selector(page, option_name: str):    
        framework_logger.info(f"Trying to select printer: {option_name}")   

        overview_page = OverviewPage(page)
        overview_page.printer_selector.click()      
        framework_logger.info("Printer dropdown opened successfully")
               
        dropdown_option = page.locator('[class^="selectablePrinters__selectable-printers-container-"]', has_text=option_name)
        dropdown_option.click()
        framework_logger.info(f"Selected printer: {option_name}")

    @staticmethod
    def verify_instant_ink_enrolled_printer_visible(page, option_name: str):
        overview_page = OverviewPage(page)
        overview_page.printer_selector.click() 
        dropdown_option = page.locator('[class^="selectablePrinters__selectable-printers-container-"]', has_text=option_name)
        dropdown_option.is_visible()       

    @staticmethod
    def click_on_all_available_links_on_the_smart_dashboard_page(page):       
        hp_smart_dashboard = DashboardHPSmartPage(page)       
           
        expect(hp_smart_dashboard.keypoint_intelligence_link).to_be_visible()  
        expect(hp_smart_dashboard.footer_hp_com_link).to_be_visible()
        expect(hp_smart_dashboard.footer_wireless_print_center_link).to_be_visible()
        expect(hp_smart_dashboard.footer_help_center_link).to_be_visible()
        expect(hp_smart_dashboard.footer_terms_of_use_link).to_be_visible()
        expect(hp_smart_dashboard.footer_hp_privacy_link).to_be_visible()
        expect(hp_smart_dashboard.footer_hp_your_privacy_choices_link).to_be_visible()
        framework_logger.info("Verified promotional page elements are visible")    
               
        with page.context.expect_page() as popup_info:
            hp_smart_dashboard.keypoint_intelligence_link.click()             
        popup = popup_info.value 
        expect(popup).to_have_url(re.compile(r'/HPInstantInk'), timeout=30000)            
        popup.close()  
        DashboardHelper.verify_footer_section(page)        

    @staticmethod
    def verify_plan_info(page, plan_value: str, plan_pages: str):
        overview_page = OverviewPage(page)
        expect(overview_page.plan_details_card).to_be_visible(timeout=90000)
        plan_info = overview_page.plan_information.text_content()
        numbers = common.extract_numbers_from_text(plan_info)
        assert numbers[0] == plan_value, f"Expected plan value to be {plan_value}, but got {numbers[0]}"
        assert numbers[1] == plan_pages, f"Expected plan pages to be {plan_pages}, but got {numbers[1]}"

    @staticmethod
    def set_invalid_billing_address(page, type: str):
        shipping_and_billing_page = ShippingBillingPage(page)
        shipping_and_billing_page.manage_your_payment_method_link.click()

        if type == "address with special characters":
            shipping_and_billing_page.input_first_address.clear()
            shipping_and_billing_page.input_first_address.fill('149 New Montgomery St!@#')
            shipping_and_billing_page.input_second_address.clear()
            shipping_and_billing_page.input_second_address.fill('10300 ENERGY DR!@#$')
            expect(shipping_and_billing_page.continue_button).to_be_disabled()
            expect(shipping_and_billing_page.billing_address_error_message).to_be_visible()

        elif type == "address with incomplete information":
            shipping_and_billing_page.input_first_address.clear()
            shipping_and_billing_page.input_second_address.clear()
            expect(shipping_and_billing_page.continue_button).to_be_disabled()
            expect(shipping_and_billing_page.billing_address_error_message).to_be_visible()

        elif type == "credit card invalid":
            shipping_and_billing_page.continue_button.click()
            page.locator(shipping_and_billing_page.elements.billing_modal_iframe).wait_for(state="visible", timeout=10000)
            frame = page.frame_locator(shipping_and_billing_page.elements.billing_modal_iframe)
            credit_card_input = frame.locator(shipping_and_billing_page.input_card_number)
            credit_card_input.fill('345678901234123')
            frame.locator(shipping_and_billing_page.elements.billing_next_button).click()
            frame.locator(shipping_and_billing_page.elements.credit_card_invalid_error_message).wait_for(state="visible", timeout=10000)
        else:
            raise ValueError(f"Unknown invalid billing address type: {type}")
        
        shipping_and_billing_page.close_modal_button.first.click()
        
    @staticmethod
    def sees_printer_replacement_page(page):
        printer_replacement = PrinterReplacementPage(page)
        expect(page.locator(printer_replacement.elements.printer_set_up_button)).to_be_visible(timeout=90000)
        expect(page.locator(printer_replacement.elements.printer_not_set_up_button)).to_be_visible()
       

    @staticmethod
    def click_printer_options_for_enrolled_printer(page):   
        dashboard_hp_smart = DashboardHPSmartPage (page)        
        subscription_selector = dashboard_hp_smart.subscription_state    

        printer_options_selector = dashboard_hp_smart.printer_options
        my_printer_element = subscription_selector.locator('xpath=../../../..').locator(printer_options_selector)

        if my_printer_element.get_attribute('aria-expanded') == 'false':
            my_printer_element.click()

    @staticmethod
    def check_savings_calculator_on_overview(page, data):
        overview_page = OverviewPage(page)
        
        expect(overview_page.savings_calculator_card).to_be_visible()
        
        if data.get('annual_savings'):
            annual_savings_text = overview_page.savings_calculator_card_annual_savings.inner_text()
            extracted = common.extract_numbers_from_text(annual_savings_text)
            expected = common.extract_numbers_from_text(data['annual_savings'])
            assert extracted == expected, \
                f"Expected annual savings {expected}, got {extracted} from text '{annual_savings_text}'"

        if data.get('printing_average') or data.get('traditional_cartridge_cost'):
            overview_page.savings_calculator_tooltip_icon.hover()
        
        if data.get('printing_average'):
            printing_average_text = overview_page.savings_calculator_tooltip_printing_average.inner_text()
            extracted = common.extract_numbers_from_text(printing_average_text)
            expected = common.extract_numbers_from_text(data['printing_average'])
            assert extracted == expected, \
                f"Expected printing average {expected}, got {extracted} from text '{printing_average_text}'"
        
        if data.get('traditional_cartridge_cost'):
            traditional_cost_text = overview_page.savings_calculator_tooltip_traditional_cartridge_cost.inner_text()
            extracted = common.extract_numbers_from_text(traditional_cost_text)
            expected = common.extract_numbers_from_text(data['traditional_cartridge_cost'])
            assert extracted == expected, \
                f"Expected traditional cartridge cost {expected}, got {extracted} from text '{traditional_cost_text}'"

    @staticmethod
    def login_on_security_session_expired(page, tenant_email: str):
        overview_page = OverviewPage(page)
 
        overview_page.expired_session_login.click()
        page.wait_for_load_state("load", timeout=12000)
        if "login" in page.url:
            if not tenant_email:
                raise ValueError("tenant_email is required for sign-in.")
            HPIDHelper.sign_in(page, tenant_email, common.DEFAULT_PASSWORD)
        
        dashboard_side_menu_page = DashboardSideMenuPage(page)
        element = dashboard_side_menu_page.visible_instant_ink_menu_link()
        assert element.is_visible(), "Instant Ink menu link is not visible"

    @staticmethod
    def add_direct_debit_billing(page, payment_method):
        confirmation_page = ConfirmationPage(page)
        payment_data = common.get_payment_method_data(payment_method)

        confirmation_page.add_billing_button.click()

        # Select Direct Debit option
        page.locator("[data-testid='direct-debit-radio-button'], [data-testid='direct-debit-radio-option']").click(force=True, timeout=60000)
        confirmation_page.billing_continue_button.click()

        # Fill IBAN and bank details
        frame = page.frame_locator(confirmation_page.elements.iframe_pgs)
        frame.locator("[id='txtIBAN']").fill(payment_data["iban"])
        frame.locator("[id='txtAccountHolderName']").fill(payment_data["bank_name"])

        # Accept SEPA mandate
        frame.locator("[id='btn_pgs_directdebit_add']").click()
        framework_logger.info("Direct Debit billing successfully added")

    @staticmethod
    def select_printer_by_serial_number(page, serial_number):
        overview_page = OverviewPage(page)
        overview_page.printer_selector.click()      
        framework_logger.info("Printer dropdown opened successfully")
               
        dropdown_option = page.locator('[class^="selectablePrinters__selectable-printers-container-"]')
        printer_option = dropdown_option.locator(f'[data-testid^="printer-option-{serial_number}-id"]').first
        printer_option.click()
        framework_logger.info(f"Selected printer with serial number: {serial_number}")

    @staticmethod
    def verify_printer_in_submenu(page, printer_type):
        overview_page = OverviewPage(page)
        if printer_type.lower() == "enrolled":
            submenu_title = "INSTANT INK ENROLLED PRINTERS"
        elif printer_type.lower() == "cancelled":
            submenu_title = "INSTANT INK CANCELLED SUBSCRIPTIONS"
        else:
            framework_logger.error(f"Invalid printer_type: {printer_type}. Use 'enrolled' or 'cancelled'")

        submenu_container = page.locator('[class^="selectablePrinters__selectable-printers-container-"]', has_text=submenu_title)
        try:
            expect(submenu_container).to_be_visible()
        except Exception as e:
            overview_page.printer_selector.click()
            expect(submenu_container).to_be_visible(timeout=10000)

        printer_name_element = submenu_container.locator('[class^="option__printer-name"]')
        expect(printer_name_element).to_be_visible()

        serial_number_element = submenu_container.locator('[class*="option__printer-serial-number"]')
        expect(serial_number_element).to_be_visible()

        printer_name = printer_name_element.text_content().strip()
        serial_number = serial_number_element.text_content().strip()

        framework_logger.info(f"Found printer in {printer_type} submenu - Name: {printer_name}, {serial_number}")

    @staticmethod
    def click_printer_submenu(page, printer_type):
        overview_page = OverviewPage(page)
        if printer_type.lower() == "enrolled":
                submenu_title = "INSTANT INK ENROLLED PRINTERS"
        elif printer_type.lower() == "cancelled":
                submenu_title = "INSTANT INK CANCELLED SUBSCRIPTIONS"
        submenu_container = page.locator('[class^="selectablePrinters__selectable-printers-container-"]', has_text=submenu_title)
        try:
            expect(submenu_container).to_be_visible()
        except Exception:
            overview_page = OverviewPage(page)
            overview_page.printer_selector.click()
            expect(submenu_container).to_be_visible(timeout=10000)
        submenu_container.click()   

    @staticmethod
    def see_notification_on_bell_icon(page, title):
        notifications_page = NotificationsPage(page)
        notifications_page.notifications_icon.click()
        notifications_text = notifications_page.notifications_table.text_content()
        assert title in notifications_text, f"Expected notification title '{title}' not found in notifications"
        notifications_page.notifications_icon.click()  

    @staticmethod
    def add_shipping_without_saving(page, index=0):
        confirmation_page = ConfirmationPage(page)
        address = GlobalState.address_payload[index] if isinstance(GlobalState.address_payload, list) else GlobalState.address_payload
        state_name = address.get("fullState", address.get(f"fullState_{GlobalState.language_code}"))
        
        confirmation_page.street1_input.fill(address.get("street1", ""))
        confirmation_page.street2_input.fill(address.get("street2", ""))
        countries_without_city_mandate = ["Hong Kong", "Singapore"]
        if GlobalState.country not in countries_without_city_mandate:
            confirmation_page.city_input.fill(address.get("city", ""))
        countries_without_states_mandate = ["Austria", "Belgium", "Denmark", "Finland", "France", "Germany", "Luxembourg", "Netherlands", "New Zealand", "Norway", "Portugal", "Puerto Rico", "Singapore", "Sweden", "Switzerland"]
        if GlobalState.country not in countries_without_states_mandate and state_name:
            DashboardHelper.select_state(page, state_name)
        countries_without_zip_mandate = ["Hong Kong"]
        if GlobalState.country not in countries_without_zip_mandate:
            confirmation_page.zip_code_input.fill(address.get("zipCode", ""))
        confirmation_page.phone_number_input.fill(address.get("phoneNumber1", ""))
        framework_logger.info(f"Filled shipping address form with address: {address} but did not save")
        time.sleep(960)
        confirmation_page.save_button.click()

    @staticmethod
    def verify_plan_pages_on_plan_details_card(page, plan_pages: str, dashboard_page: str):
        overview_page = OverviewPage(page)
        update_plan_page = UpdatePlanPage(page)
        print_history_page = PrintHistoryPage(page)

        if dashboard_page == "Overview":
            expect(overview_page.plan_details_card).to_be_visible(timeout=90000)
            plan_info = overview_page.plan_information.text_content()
        elif dashboard_page == "Update Plan":
            expect(update_plan_page.plan_details_card).to_be_visible(timeout=90000)
            plan_info = update_plan_page.plan_information.text_content()
        elif dashboard_page == "Print History":
            plan_info = print_history_page.plan_price_text.first.text_content()
        else:
            raise ValueError(f"Unknown dashboard_page: {dashboard_page}")

        numbers = common.extract_numbers_from_text(plan_info)
        assert numbers[1] == plan_pages, f"Expected plan pages to be {plan_pages}, but got {numbers[1]}"

    @staticmethod
    def pass_validation(page):
        overview_page = OverviewPage(page)
        expect(overview_page.paas_banner).to_be_visible()
        expect(overview_page.paas_image).to_be_visible()
        expect(overview_page.pass_title).to_be_visible()
        expect(overview_page.pass_description).to_be_visible()
        expect(overview_page.pass_link).to_be_visible()

        with page.context.expect_page() as new_page_info:
            overview_page.pass_link.click()
            new_tab = new_page_info.value

        assert "hp-all-in-plan-enroll" in new_tab.url, "Support link did not navigate to the expected URL"
        framework_logger.info("Support link navigates to the expected URL")
        new_tab.close()
        page.bring_to_front()

    @staticmethod
    def add_2co_billing(page, card_type=None):
        """Handle 2Checkout payment method for billing page"""
        shipping_billing_page = ShippingBillingPage(page)
        payment_data = common.get_payment_method_data(card_type)
        confirmation_page = ConfirmationPage(page)
        framework_logger.info(f"Using card type: {card_type}")

        # Click continue button to proceed to 2checkout iframe
        page.locator(confirmation_page.elements.billing_continue_button).is_enabled()
        page.locator(confirmation_page.elements.billing_continue_button).click()

        # Wait for 2checkout iframe and interact with it
        page.wait_for_selector(confirmation_page.elements.iframe_2co, state="visible", timeout=120000)
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.continue_to_billing).wait_for(state="visible", timeout=60000)
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.continue_to_billing).click()
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.continue_to_payment).wait_for(state="visible", timeout=60000)
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.continue_to_payment).click()
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.card_name_2co).wait_for(state="attached", timeout=3000)

        # Fill in cardholder name
        if page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.card_name_2co).is_visible():
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.card_name_2co).fill("John Doe")
        else:
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.first_name_2co).wait_for(state="visible")
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.first_name_2co).type("John")
            page.keyboard.press("Tab")
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.last_name_2co).wait_for(state="visible")
            page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.last_name_2co).type("Doe")

        # Fill in card details
        page.keyboard.press("Tab")
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.card_number_2co).type(payment_data["credit_card_number"])
        page.keyboard.press("Tab")
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.exp_date_2co).type(f"{payment_data.get('expiration_month')}/{payment_data.get('expiration_year')[-2:]}")
        page.keyboard.press("Tab")
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.cvv_2co).type(payment_data["cvv"])
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.place_order_button).wait_for(state="visible", timeout=60000)
        page.frame_locator(confirmation_page.elements.iframe_2co).locator(confirmation_page.elements.place_order_button).click()

        # Wait for billing update confirmation
        shipping_billing_page.update_shipping_billing_message.first.wait_for(state="visible", timeout=60000)
        framework_logger.info("2Checkout billing successfully added")

    def flip_conversion_enroll_now(page):
        overview_page = OverviewPage(page)
        overview_page.enroll_now.wait_for(state="visible", timeout=100000)
        overview_page.enroll_now.click()
    

    @staticmethod
    def flip_conversion_enter_address(page):
        overview_page = OverviewPage(page)
        overview_page.enter_address.wait_for(state="visible", timeout=100000)
        overview_page.enter_address.click()

    @staticmethod
    def flip_conversion_modal_enter_address(page):
        overview_page = OverviewPage(page)
        page.reload()
        expect(overview_page.flip_modal_enter_address_button).to_be_visible(timeout=30000)
        overview_page.flip_modal_enter_address_button.click()

    @staticmethod
    def add_paper(page):
        overview_page = OverviewPage(page)
        expect(overview_page.paper_modal_claim_button).to_be_visible(timeout=30000)
        overview_page.paper_modal_claim_button.click()
        overview_page.paper_hero_banner_button.wait_for(state="visible", timeout=100000)
        overview_page.paper_hero_banner_button.click()
        expect(overview_page.paper_pre_enroll_content_continue_button).to_be_visible(timeout=30000)
        overview_page.paper_pre_enroll_content_continue_button.click()
        expect(overview_page.paper_plan_review_confirm_button).to_be_visible(timeout=30000)
        overview_page.paper_plan_review_confirm_button.click()
        expect(overview_page.paper_checkbox_redeem).to_be_visible(timeout=30000)
        overview_page.paper_checkbox_redeem.click()
        overview_page.paper_redeem_button.click()

    @staticmethod
    def cancel_instant_paper(page):    
        overview_page = OverviewPage(page)
        expect(overview_page.paper_remove_link).to_be_visible(timeout=30000)
        overview_page.paper_remove_link.click()
        expect(overview_page.keep_subscription_button).to_be_visible(timeout=30000)
        expect(overview_page.confirm_cancellation_button).to_be_visible(timeout=30000)
        overview_page.confirm_cancellation_button.click()
       
    @staticmethod
    def add_paper_from_update_plan(page):
        overview_page = OverviewPage(page)
        dashboard_side_menu = DashboardSideMenuPage(page)
        dashboard_side_menu.click_update_plan()
        update_plan_page = UpdatePlanPage(page)
        expect(update_plan_page.plan_selector_paper_card_button).to_be_visible(timeout=30000)
        update_plan_page.plan_selector_paper_card_button.click()
        overview_page.paper_hero_banner_button.wait_for(state="visible", timeout=100000)
        overview_page.paper_hero_banner_button.click()
        expect(overview_page.paper_pre_enroll_content_continue_button).to_be_visible(timeout=30000)
        overview_page.paper_pre_enroll_content_continue_button.click()
        expect(overview_page.paper_plan_review_confirm_button).to_be_visible(timeout=30000)
        overview_page.paper_plan_review_confirm_button.click()
        expect(overview_page.paper_checkbox_redeem).to_be_visible(timeout=30000)
        overview_page.paper_checkbox_redeem.click()
        overview_page.paper_redeem_button.click()
          
