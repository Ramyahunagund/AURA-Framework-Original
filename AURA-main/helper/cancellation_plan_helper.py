import re
from datetime import datetime, time, timedelta
from pages import cancellation_page
from pages.cancellation_timeline_page import CancellationTimelinePage
from pages.cancellation_page import CancellationPage
from pages.cancellation_banner_page import CancellationBannerPage
from pages.change_plan_cancellation_page import ChangePlanCancellationPage
from playwright.sync_api import expect

from pages.overview_page import OverviewPage
from pages.update_plan_page import UpdatePlanPage
import time


class CancellationPlanHelper:
    @staticmethod
    def select_cancellation_feedback_option(page, feedback_option="I do not print enough", submit: bool = True):
        cancellation_page = CancellationPage(page)
        cancellation_page.continue_button.click(timeout=120000)
        option_map = {
            'I do not print enough': cancellation_page.elements.do_not_print_enough_radio,
            'The service is too expensive': cancellation_page.elements.service_is_too_expensive_radio,
            'I have not received my shipment': cancellation_page.elements.did_not_received_my_shipment_radio,
            'I have replaced my printer': cancellation_page.elements.have_replaced_my_printer_radio,
            'Wi-Fi issues with my printer': cancellation_page.elements.wifi_issues_with_my_printer_radio,
            'Other': cancellation_page.elements.other_option_radio
        }
        selector = option_map.get(feedback_option)
        if not selector:
            raise ValueError(f"Unknown feedback option: {feedback_option}")
        page.click(selector, force=True)
        if feedback_option == "Other":
            page.fill(cancellation_page.elements.feedback_text_box, "Other Reason")
        if submit:
            page.click(cancellation_page.elements.submit_feedback_button)
        else:
            page.click(cancellation_page.elements.return_to_account_button)  

    @staticmethod
    def select_paper_cancellation_feedback_option(page, feedback_option="I'm worried I'm going to run out of paper", submit: bool = True):
        cancellation_page = CancellationPage(page)
        cancellation_page.continue_button.click(timeout=120000)    
        option_map = {
            "I'm worried I'm going to run out of paper": cancellation_page.elements.replenishment_anxiety_radio,
            "I use paper for non-printing purposes": cancellation_page.elements.leakage_radio,
            "I didn't print enough to make it worthwhile": cancellation_page.elements.did_not_print_enough_radio,
            "I ran out of paper": cancellation_page.elements.ran_out_of_paper_radio,
            "I was being charged for additional paper sheets": cancellation_page.elements.paper_overages_radio,
            "I'm cancelling temporarily": cancellation_page.elements.temporary_cancellation_radio,
            "I received too much paper": cancellation_page.elements.stockpiling_radio,
            "Too expensive": cancellation_page.elements.too_expensive_radio,
            "My paper arrived damaged": cancellation_page.elements.damaged_paper_radio,
            "I did not receive shipment": cancellation_page.elements.i_did_not_receive_shipment_radio,
            "I moved to an area where the paper service is not offered": cancellation_page.elements.moved_to_non_paper_service_area_radio,
            "The paper quality was below my expectations": cancellation_page.elements.paper_quality_radio,
            "Other": cancellation_page.elements.other_option_radio
        }
        selector = option_map.get(feedback_option)
        if not selector:
            raise ValueError(f"Unknown feedback option: '{feedback_option}'")
        page.click(selector, force=True)
        if feedback_option == "Other":
            page.fill(cancellation_page.elements.feedback_text_box, "Other Reason")
        if submit:
            page.click(cancellation_page.elements.submit_feedback_button)
        else:
            page.click(cancellation_page.elements.return_to_account_button)

    @staticmethod
    def verify_bottom_section(page, section_title):
        cancellation_page = CancellationPage(page)

        link_selectors = {
            'Have your printing needs changed?': cancellation_page.elements.change_plan_link,
            'Pause your subscription for up to 6 months': cancellation_page.elements.pause_plan_link,
            'Did you get a new printer?': cancellation_page.elements.transfer_subscription_link,
            'Have questions or need help?': cancellation_page.elements.contact_hp_support_link,
            'Only pay when you need to print': cancellation_page.elements.only_pay_when_you_need_to_print_link
        }

        selector = link_selectors.get(section_title)
        if not selector:
            raise ValueError(f"Unknown section title: {section_title}")

        retention_option = page.locator(selector).locator('xpath=../..')
        retention_option_image = retention_option.locator('img')
        retention_option_text = retention_option.locator('p').last
        retention_option_link = retention_option.locator('button')

        expect(retention_option_image).to_be_visible()
        expect(retention_option_text).to_be_visible()
        expect(retention_option_text).to_have_text(section_title)
        expect(retention_option_link).to_be_visible()

    @staticmethod
    def validate_cancellation_links(page, section_title):
        cancellation_page = CancellationPage(page)

        if section_title == "Pause Plan":
            cancellation_page.pause_plan_link.click()
            cancellation_page.close_modal_button.click()
            expect(cancellation_page.close_modal_button).not_to_be_visible

        elif section_title == "Transfer to other printer":
            cancellation_page.transfer_subscription_link.click()

    @staticmethod
    def validate_transfer_subscription_contact_support_link(page, section_title):
        cancellation_page = CancellationPage(page)

        if section_title == "Transfer to other printer":
            expect(cancellation_page.transfer_subscription_link).to_be_visible()
            with page.context.expect_page() as new_page_event:
                cancellation_page.transfer_subscription_link.click()
            new_page = new_page_event.value
            new_page.wait_for_load_state("domcontentloaded")
            expect(new_page).to_have_url(
                re.compile(
                    r"https://consumer\.stage\.portalshell\.int\.hp\.com/us/en/print_plans/printer_replacement\?t1=.*"
                )
            )
        elif section_title == "Contact Support":
            expect(cancellation_page.contact_support_link).to_be_visible()
            with page.context.expect_page() as new_page_event:
                cancellation_page.contact_support_link.click()
            new_page = new_page_event.value
            new_page.wait_for_load_state("domcontentloaded")
            expect(new_page).to_have_url(
                re.compile(
                    r"https://support.hp.com/us-en/service/hp-instant-ink-series/*")
            )
            modal_container = new_page.locator('[class="modal-content"]')
            close_btn = modal_container.locator('[aria-label="close"]')
            close_btn.wait_for(state="visible", timeout=30000)
            close_btn.click(timeout=30000)
        else:
            raise ValueError(f"Unknown section title: {section_title}")
            
    @staticmethod
    def select_change_plan(page, plan_pages: str):
        cancellation_page = CancellationPage(page)
        if not cancellation_page.change_plan_modal.is_visible():
            cancellation_page.change_plan_link.click()

        plan_button = cancellation_page.get_plan_button(plan_pages)
        plan_button.click()

    @staticmethod
    def verify_the_cancellation_timeline_page(page):
        cancellation_timeline_page = CancellationTimelinePage(page)
        expect(cancellation_timeline_page.header_icon).to_be_visible(timeout=90000)
        expect(cancellation_timeline_page.header_title).to_be_visible()
        expect(cancellation_timeline_page.header_subtitle).to_be_visible()
        expect(cancellation_timeline_page.restore_subscription).to_be_visible()
        #expect(cancellation_timeline_page.timeline_img).to_be_visible()
        expect(cancellation_timeline_page.whats_happens_next).to_be_visible()
    
    # @staticmethod
    # def verify_the_steps_on_cancellation_timeline_page(page):
    #     cancellation_timeline_page = CancellationTimelinePage(page)
    #     today = datetime.today()
    #     current_date = today.strftime('%b %d, %Y')
    #
    #     text = cancellation_timeline_page.cancellation_step(1).text_content()
    #     last_day = re.search(r'([A-Za-z]{3} \d{2}, \d{4})', text).group(1)
    #     last_day_date = datetime.strptime(last_day, '%b %d, %Y')
    #
    #     final_bill_first = last_day_date + timedelta(days=1)
    #     final_bill_date = final_bill_first.strftime('%b %d, %Y')
    #
    #     expect(cancellation_timeline_page.first_step_icon).to_be_visible()
    #     expect(cancellation_timeline_page.cancellation_step(0)).to_be_visible()
    #     expect(cancellation_timeline_page.cancellation_step_title(0)).to_contain_text(f"{current_date}: Cancellation submitted")
    #     expect(cancellation_timeline_page.second_step_icon).to_be_visible()
    #     expect(cancellation_timeline_page.cancellation_step(1)).to_be_visible()
    #     expect(cancellation_timeline_page.cancellation_step_title(1)).to_contain_text(f"{last_day}: Last day to print with Instant Ink cartridges")
    #     expect(cancellation_timeline_page.third_step_icon(2)).to_be_visible()
    #     expect(cancellation_timeline_page.cancellation_step(2)).to_be_visible()
    #     expect(cancellation_timeline_page.cancellation_step_title(2)).to_contain_text(f"{final_bill_date}: Instant Ink cartridges deactivated")
    #     expect(cancellation_timeline_page.fourth_step_icon(3)).to_be_visible()
    #     expect(cancellation_timeline_page.cancellation_step(3)).to_be_visible()
    #     expect(cancellation_timeline_page.fifth_step_icon).to_be_visible()
    #     expect(cancellation_timeline_page.cancellation_step(4)).to_be_visible()

    @staticmethod
    def verify_the_steps_on_cancellation_timeline_page(page):
        cancellation_timeline_page = CancellationTimelinePage(page)
        today = datetime.today()
        current_date = today.strftime('%b %d, %Y')

        text = cancellation_timeline_page.cancellation_step(1).text_content()
        last_day = re.search(r'([A-Za-z]{3} \d{2}, \d{4})', text).group(1)
        last_day_date = datetime.strptime(last_day, '%b %d, %Y')

        final_bill_first = last_day_date + timedelta(days=1)
        final_bill_date = final_bill_first.strftime('%b %d, %Y')

        expect(cancellation_timeline_page.first_step_icon).to_be_visible()
        expect(cancellation_timeline_page.cancellation_step(0)).to_be_visible()
        expect(cancellation_timeline_page.cancellation_step_title(0)).to_contain_text(f"{current_date}: Cancellation submitted")
        expect(cancellation_timeline_page.second_step_icon).to_be_visible()
        expect(cancellation_timeline_page.cancellation_step(1)).to_be_visible()
        expect(cancellation_timeline_page.cancellation_step_title(1)).to_contain_text(f"{last_day}: Last day to print with Instant Ink cartridges")
        expect(cancellation_timeline_page.third_step_icon(2)).to_be_visible()
        expect(cancellation_timeline_page.cancellation_step(2)).to_be_visible()
        date_range_pattern = re.compile(rf"{final_bill_first.strftime('%b')} \d{{2}}(?:-\d{{2}})?, \d{{4}}: Instant Ink cartridges deactivated")
        expect(cancellation_timeline_page.cancellation_step_title(2)).to_have_text(date_range_pattern)
        expect(cancellation_timeline_page.fourth_step_icon(3)).to_be_visible()
        expect(cancellation_timeline_page.cancellation_step(3)).to_be_visible()
        expect(cancellation_timeline_page.fifth_step_icon(4)).to_be_visible()
        expect(cancellation_timeline_page.cancellation_step(4)).to_be_visible()


    # @staticmethod
    # def verify_change_your_mind_section(page):
    #     cancellation_timeline_page = CancellationTimelinePage(page)
    #
    #     #expect(cancellation_timeline_page.change_your_mind).to_be_visible()
    #     expect(cancellation_timeline_page.keep_subscription_as_it_was).to_be_visible(timeout=90000)
    #     retention_option = cancellation_timeline_page.keep_subscription_as_it_was.locator("xpath=../..")
    #     retention_option_text = retention_option.locator("p")
    #     retention_option_link = retention_option.locator("span")
    #
    #     expect(retention_option_text).to_be_visible()
    #     assert retention_option_text.inner_text() == "Restore subscription?"
    #     expect(retention_option_link).to_be_visible()
    #
    #     expect(cancellation_timeline_page.transfer_subscription_link).to_be_visible(timeout=90000)
    #     retention_option = cancellation_timeline_page.transfer_subscription_link.locator("xpath=../..")
    #     retention_option_text = retention_option.locator("p")
    #     retention_option_link = retention_option.locator("span")
    #
    #     expect(retention_option_text).to_be_visible()
    #     assert retention_option_text.inner_text() == "Did you get a new printer?"
    #     expect(retention_option_link).to_be_visible()

    @staticmethod
    def verify_change_your_mind_section(page):
        # Keep Subscription Section
        cancellation_timeline_page = CancellationTimelinePage(page)
        expect(cancellation_timeline_page.keep_subscription_as_it_was).to_be_visible(timeout=90000)
        retention_option_text = page.locator(
            '//*[@data-testid="cancellation-alternative-keep-subscription-as-it-was"]/div/div/p[1]')
        retention_option_link = page.locator(
            '//*[@data-testid="cancellation-alternative-keep-subscription-as-it-was"]/div[@class="cancellationCard__button-container___25q-w"]/span')

        expect(retention_option_text).to_be_visible(timeout=90000)
        assert retention_option_text.inner_text().strip() == "Restore subscription?"
        expect(retention_option_link).to_be_visible(timeout=90000)

        # Transfer Subscription Section
        retention_option_text = page.locator(
            '//*[@data-testid="cancellation-alternative-transfer-subscription-to-another-printer"]/div/div/p[1]'
        )
        retention_option_link = page.locator(
            '//*[@data-testid="cancellation-alternative-transfer-subscription-to-another-printer"]/div[@class="cancellationCard__button-container___25q-w"]/span'
        )

        expect(retention_option_text).to_be_visible(timeout=90000)
        assert retention_option_text.inner_text().strip() == "Did you get a new printer?"
        expect(retention_option_link).to_be_visible(timeout=90000)

    @staticmethod
    def validate_buttons_on_cancellation_timeline_page(page, option: str):
        cancellation_timeline_page = CancellationTimelinePage(page)

        if option == "Shop HP Ink":
            expect(cancellation_timeline_page.shop_hp_button.first).to_be_visible()
            with page.expect_popup() as popup_info:
                cancellation_timeline_page.shop_hp_button.first.click()
            new_page = popup_info.value
            expect(new_page).to_have_url(re.compile(r'/shop/cat'))
            new_page.close()
        elif option == "Preview Upcoming Bill":
            expect(cancellation_timeline_page.preview_upcoming_button.first).to_be_visible()
            with page.expect_popup() as popup_info:
                cancellation_timeline_page.preview_upcoming_button.first.click()
            new_page = popup_info.value
            new_page.close()
        elif option == "Request Free Recycling Materials":
            expect(cancellation_timeline_page.request_recycling_button.first).to_be_visible()
            with page.expect_popup() as popup_info:
                cancellation_timeline_page.request_recycling_button.first.click()
            new_page = popup_info.value
            expect(new_page).to_have_url(re.compile(r'/uat-inktoner-recycle'))
            new_page.close()
        elif option == "Close":
            expect(cancellation_timeline_page.cancellation_timeline_close_button).to_be_visible()
            cancellation_timeline_page.cancellation_timeline_close_button.click()
            expect(cancellation_timeline_page.cancellation_timeline_close_button).not_to_be_visible()

    @staticmethod
    def click_on_link_on_cancellation_page(page, option: str):
        cancellation_timeline_page = CancellationTimelinePage(page)

        link_selectors = {
            "Restore Your Subscription": cancellation_timeline_page.restore_subscription,
            "Keep Subscription": cancellation_timeline_page.keep_subscription_as_it_was,
            "Transfer This Subscription": cancellation_timeline_page.transfer_subscription_link
        }

        link = link_selectors[option]
        expect(link).to_be_visible(timeout=90000)
        link.click()

    @staticmethod
    def click_on_button_on_resume_modal(page, button: str):
        cancellation_timeline_page = CancellationTimelinePage(page)
        cancellation_banner = CancellationBannerPage(page)

        if button == "Resume":
            cancellation_timeline_page.resume_instant_ink_subscription.click()
            expect(cancellation_banner.resume_banner).to_be_visible(timeout=90000)
        elif button == "Back":
            cancellation_timeline_page.back_to_cancel_confirmation.click()
    
    @staticmethod
    def verify_the_cancellation_timeline_modal(page):
        cancellation_timeline_page = CancellationTimelinePage(page)
        expect(cancellation_timeline_page.header_title).to_be_visible()
        expect(cancellation_timeline_page.header_subtitle).to_be_visible()
        expect(cancellation_timeline_page.shop_hp_button.first).to_be_visible()
        expect(cancellation_timeline_page.request_recycling_button.first).to_be_visible()

        expect(cancellation_timeline_page.cancellation_timeline_close_button).to_be_visible()
        cancellation_timeline_page.cancellation_timeline_close_button.click()
        expect(cancellation_timeline_page.cancellation_timeline_close_button).not_to_be_visible()

    @staticmethod
    def click_see_cancellation_timeline_button_on_banner(page):
        cancellation_timeline_page = CancellationTimelinePage(page)
        expect(cancellation_timeline_page.see_cancellation_timeline).to_be_visible(timeout=90000)
        cancellation_timeline_page.see_cancellation_timeline.click()

    @staticmethod
    def verify_steps_on_cancellation_timeline_modal(page, step: str):
        cancellation_timeline_page = CancellationTimelinePage(page)

        if step == "First step":
            expect(cancellation_timeline_page.first_step_icon).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step(0)).to_be_visible()
        elif step == "Second step":
            expect(cancellation_timeline_page.second_step_icon).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step(1)).to_be_visible()
        elif step == "Third step":
            expect(cancellation_timeline_page.third_step_icon(2)).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step(2)).to_be_visible()
        elif step == "Fourth step":
            expect(cancellation_timeline_page.fourth_step_icon(3)).to_be_visible()
            expect(cancellation_timeline_page.cancellation_step(3)).to_be_visible()
    
    @staticmethod
    def validate_change_plan_modal(page):
        cancellation_page = CancellationPage(page)
        cancellation_summary_page = ChangePlanCancellationPage(page)

        cancellation_page.change_plan_link.click()
        expect(cancellation_summary_page.change_plan_title).to_be_visible()
        expect(cancellation_summary_page.change_plan_subtitle).to_be_visible()
        expect(cancellation_summary_page.change_plan_icon).to_be_visible()
        expect(cancellation_summary_page.change_plan_shipping_icon).to_be_visible()
        expect(cancellation_summary_page.print_less_message).to_be_visible()

    @staticmethod
    def validate_additional_pages_tooltip_on_change_plan_modal(page, value: str):
        change_plan_modal = ChangePlanCancellationPage(page)

        expect(change_plan_modal.additional_pages_tooltip).to_be_visible()
        change_plan_modal.additional_pages_tooltip.locator("svg").hover()
        expect(change_plan_modal.additional_pages_tooltip_content).to_be_visible()
        
        tooltip_text = change_plan_modal.additional_pages_tooltip_content.inner_text()
        assert value in tooltip_text, f"Expected pages_used {value} but found {tooltip_text} in tooltip"

    @staticmethod
    def select_plan_on_change_plan_modal(page, plan_value: str = "100"):
        change_plan_modal = ChangePlanCancellationPage(page)
        change_plan_modal.select_ink_plan(plan_value)

    @staticmethod
    def validate_the_choose_your_new_plan_start_date_modal(page):
        change_plan_modal = ChangePlanCancellationPage(page)
        date_pattern = r"\b[A-Z][a-z]{2} \d{2}, \d{4}\b"

        expect(change_plan_modal.upgrade_plan_title).to_be_visible()
        expect(change_plan_modal.upgrade_plan_subtitle).to_be_visible()

        expect(change_plan_modal.current_bc_card).to_be_visible()
        expect(change_plan_modal.current_bc_icon).to_be_visible()
        current_bc_text = change_plan_modal.current_bc_card.text_content()
        current_dates = re.findall(date_pattern, current_bc_text)
        assert current_dates, f"No date found in: {current_bc_text}"

        assert change_plan_modal.current_bc_radio.is_checked() is True

        expect(change_plan_modal.next_bc_card).to_be_visible()
        expect(change_plan_modal.next_bc_icon).to_be_visible()
        next_bc_text = change_plan_modal.next_bc_card.text_content()
        next_dates = re.findall(date_pattern, next_bc_text)
        assert next_dates, f"No date found in: {next_bc_text}"

        assert change_plan_modal.next_bc_radio.is_checked() is False
        assert change_plan_modal.back_button_choose_plan().is_visible() is True
        expect(change_plan_modal.confirm_button_choose_plan).to_be_visible()

    @staticmethod
    def click_button_in_the_new_plan_start_date_modal(page, option: str):
        change_plan_modal = ChangePlanCancellationPage(page)

        if option == "back":
            change_plan_modal.back_button_choose_plan().click()
        elif option == "confirm":
            change_plan_modal.confirm_button_choose_plan.click()

        expect(change_plan_modal.upgrade_plan_title).not_to_be_visible()

    @staticmethod
    def select_billing_cycle_on_cancellation_summary_page(page, option: str):
        change_plan_modal = ChangePlanCancellationPage(page)

        if option == "Next": 
            change_plan_modal.next_bc_radio.click()
        elif option == "Current": 
            change_plan_modal.current_bc_radio.click()

        change_plan_modal.confirm_button_choose_plan.click()

    @staticmethod
    def sees_the_pages_and_plan_price_on_change_plan_modal(page, pages: str, plan_price: str):
        change_plan_modal = ChangePlanCancellationPage(page)
        expect(change_plan_modal.change_plan_subtitle).to_be_visible()
        actual_text = change_plan_modal.change_plan_subtitle.inner_text()
        
        numbers = re.findall(r'\d+(?:\.\d+)?', actual_text)
        assert pages in numbers, f"Expected pages '{pages}' not found in '{numbers}'"
        
        price_number = re.search(r'\d+(?:\.\d+)?', plan_price).group()
        assert price_number in numbers, f"Expected price '{plan_price}' not found in '{numbers}'"
        
    @staticmethod
    def verify_ink_plans_on_change_plan_modal(page):
        change_plan_modal = ChangePlanCancellationPage(page)
        plans = [
            {"button": change_plan_modal.change_plan_10_button, "dots": 1, "numbers": ["10", "60.20"]},
            {"button": change_plan_modal.change_plan_25_button, "dots": 2, "numbers": ["25", "58.50"]},
            {"button": change_plan_modal.change_plan_50_button, "dots": 3, "numbers": ["50", "56.50"]},
            {"button": change_plan_modal.change_plan_100_button, "dots": 4, "numbers": ["100", "54.00"]},
            {"button": change_plan_modal.change_plan_300_button, "dots": 5, "numbers": ["300", "46.00"]},
            {"button": change_plan_modal.change_plan_500_button, "dots": 6, "numbers": ["500", "38.00"]},
            {"button": change_plan_modal.change_plan_700_button, "dots": 7, "numbers": ["700", "30.00"]},
        ]

        for plan in plans:
            plan_info = plan["button"].locator("..")
            dots = plan_info.locator(change_plan_modal.dot_icon_ink).count()
            assert dots == plan["dots"], f"Expected {plan['dots']} dots, found {dots}"
            text = plan_info.inner_text()
            numbers = re.findall(r"\d+(?:\.\d+)?", text)
            for num in plan["numbers"]:
                assert num in numbers, f"Expected number '{num}' not found in '{numbers}'"

    @staticmethod
    def verify_first_section_on_cancellation_feedback_page(page):
        cancellation_page = CancellationPage(page)

        expect(cancellation_page.cancellation_feedback_title).to_be_visible()
        expect(cancellation_page.cancellation_feedback_subtitle).to_be_visible()

        assert not page.is_checked(cancellation_page.elements.do_not_print_enough_radio)
        assert not page.is_checked(cancellation_page.elements.wifi_issues_with_my_printer_radio)
        assert not page.is_checked(cancellation_page.elements.service_is_too_expensive_radio)
        assert not page.is_checked(cancellation_page.elements.did_not_received_my_shipment_radio)
        assert not page.is_checked(cancellation_page.elements.have_replaced_my_printer_radio)
        assert not page.is_checked(cancellation_page.elements.other_option_radio)

        expect(cancellation_page.feedback_text_box).to_be_visible()
        assert page.get_attribute(cancellation_page.elements.feedback_text_box, "disabled") is not None

        expect(cancellation_page.submit_feedback_button).to_be_visible()
        assert page.get_attribute(cancellation_page.elements.submit_feedback_button, "disabled") is not None

        expect(cancellation_page.return_to_account_button).to_be_visible()
        assert page.get_attribute(cancellation_page.elements.return_to_account_button, "disabled") is None

    @staticmethod
    def verify_radio_buttons_on_cancellation_feedback_page(page):
        cancellation_page = CancellationPage(page)
        radio_selectors = [
            cancellation_page.elements.do_not_print_enough_radio,
            cancellation_page.elements.wifi_issues_with_my_printer_radio,
            cancellation_page.elements.service_is_too_expensive_radio,
            cancellation_page.elements.did_not_received_my_shipment_radio,
            cancellation_page.elements.have_replaced_my_printer_radio,
            cancellation_page.elements.other_option_radio
        ]
        for idx, selector in enumerate(radio_selectors):
            page.locator(selector).locator("..").click()
            assert page.is_checked(selector), f"Radio {selector} should be checked"
            for jdx, other_selector in enumerate(radio_selectors):
                if idx == jdx:
                    continue
                assert not page.is_checked(other_selector), f"Radio {other_selector} should not be checked"

    @staticmethod
    def verify_paper_radio_buttons_on_cancellation_feedback_page(page):
        cancellation_page = CancellationPage(page)
        paper_radio_selectors = [
            cancellation_page.elements.replenishment_anxiety_radio,
            cancellation_page.elements.leakage_radio,
            cancellation_page.elements.did_not_print_enough_radio,
            cancellation_page.elements.ran_out_of_paper_radio,
            cancellation_page.elements.paper_overages_radio,
            cancellation_page.elements.temporary_cancellation_radio,
            cancellation_page.elements.stockpiling_radio,
            cancellation_page.elements.too_expensive_radio,
            cancellation_page.elements.damaged_paper_radio,
            cancellation_page.elements.i_did_not_receive_shipment_radio,
            cancellation_page.elements.moved_to_non_paper_service_area_radio,
            cancellation_page.elements.paper_quality_radio,
            cancellation_page.elements.other_option_radio
        ]
        for idx, selector in enumerate(paper_radio_selectors):
            page.locator(selector).locator("..").click()
            assert page.is_checked(selector), f"Paper radio button {selector} should be checked"
            for jdx, other_selector in enumerate(paper_radio_selectors):
                if idx == jdx:
                    continue
                assert not page.is_checked(other_selector), f"Paper radio button {other_selector} should not be checked when {selector} is selected"

    @staticmethod
    def sees_submit_feedback_button(page, enabled: bool = False):
        cancellation_page = CancellationPage(page)
        expect(cancellation_page.submit_feedback_button).to_be_visible()
        if enabled:
            assert page.get_attribute(cancellation_page.elements.submit_feedback_button, "disabled") is None
        else:
            assert page.get_attribute(cancellation_page.elements.submit_feedback_button, "disabled") is not None


    def verify_cancellation_summary_page_title(page):
        cancellation_page = CancellationPage(page)
        expect(cancellation_page.cancellation_title).to_be_visible(timeout=90000)


    @staticmethod
    def verify_user_stays_on_loading_page_for_at_least_4s(page):
        cancellation_page = CancellationPage(page)

        # Start timer when loading page is visible
        start_time = datetime.now()
        print("Loading page appeared at:", start_time)

        # Wait for loading page to appear
        expect(cancellation_page.printer_img).to_be_visible(timeout=30000)
        expect(cancellation_page.printer_info_name).to_be_visible(timeout=30000)
        expect(cancellation_page.printer_info_serial).to_be_visible(timeout=30000)

        # Verify the cancellation animation on Cancellation Loading Page
        expect(cancellation_page.cancellation_animation).to_be_visible(timeout=30000)

        # Wait for next page (timeline) header to appear
        cancellation_page.continue_button.wait_for(state="visible", timeout=90000)

        # End timer when timeline page becomes visible
        end_time = datetime.now()
        print("Timeline page appeared at:", end_time)
          # Small delay to ensure accurate timing

        # Calculate duration
        duration = (end_time - start_time).total_seconds()
        print(f" Duration user stayed on loading page: {duration:.2f} seconds")

        assert duration >= 4, (
            f"Expected to stay on loading page for at least 4 seconds, "
            f"but stayed for {duration:.2f} seconds"
        )
        cancellation_page.continue_button.wait_for(state="visible", timeout=90000)




    @staticmethod
    def verify_feeback_radio_buttons_default_not_selected(page):
        cancellation_page = CancellationPage(page)
        radio_selectors = [
            cancellation_page.elements.do_not_print_enough_radio,
            cancellation_page.elements.wifi_issues_with_my_printer_radio,
            cancellation_page.elements.service_is_too_expensive_radio,
            cancellation_page.elements.did_not_received_my_shipment_radio,
            cancellation_page.elements.have_replaced_my_printer_radio,
            cancellation_page.elements.other_option_radio
        ]
        for selector in radio_selectors:
            assert not page.is_checked(selector), f"Radio {selector} should not be checked initially"

    @staticmethod
    def verify_feedback_text_box_disabled(page):
        cancellation_page = CancellationPage(page)
        expect(cancellation_page.feedback_text_box).to_be_visible()
        assert page.get_attribute(cancellation_page.elements.feedback_text_box, "disabled") is not None

    @staticmethod
    def verify_radio_buttons_exclusive_and_default(page):
        cancellation_page = CancellationPage(page)
        radio_selectors = [
            cancellation_page.elements.do_not_print_enough_radio,
            cancellation_page.elements.wifi_issues_with_my_printer_radio,
            cancellation_page.elements.service_is_too_expensive_radio,
            cancellation_page.elements.did_not_received_my_shipment_radio,
            cancellation_page.elements.have_replaced_my_printer_radio,
            cancellation_page.elements.other_option_radio
        ]
        # Check all are unselected by default
        for selector in radio_selectors:
            assert not page.is_checked(selector), f"Radio {selector} should not be checked initially"
        # Check only one can be selected at a time
        for idx, selector in enumerate(radio_selectors):
            page.click(selector)
            for jdx, other_selector in enumerate(radio_selectors):
                if idx == jdx:
                    assert page.is_checked(selector), f"Radio {selector} should be checked"
                else:
                    assert not page.is_checked(other_selector), f"Radio {other_selector} should not be checked"


    @staticmethod
    def verify_user_redirected_return_to_overview(page):
        """
        Clicks on 'Return to Account', waits for Overview page,
        and reopens the cancellation flow.
        """
        cancellation_page = CancellationPage(page)
        overview_page = OverviewPage(page)
        expect(cancellation_page.return_to_account_button).to_be_visible()
        cancellation_page.return_to_account_button.click()

        # Verify the Overview page loads
        expect(overview_page.page_title).to_be_visible(timeout=70000)

    @staticmethod
    def clicking_back_button_in_summary(page):
        cancellation_page = CancellationPage(page)
        expect(cancellation_page.summary_page_back_button).to_be_visible(timeout=10000)  # Reduced timeout
        cancellation_page.summary_page_back_button.click()
