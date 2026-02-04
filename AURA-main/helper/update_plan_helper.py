import time
from pages.cancellation_page import CancellationPage
from pages.update_plan_page import UpdatePlanPage
import test_flows_common.test_flows_common as common
from pages.overview_page import OverviewPage
from playwright.sync_api import expect
import re

class UpdatePlanHelper:
    @staticmethod
    def doesnt_see_free_months(page):
        update_plan_page = UpdatePlanPage(page)
        expect(update_plan_page.free_trial_info_card).not_to_be_visible()
        expect(update_plan_page.free_trial_plan_details).not_to_be_visible()

    @staticmethod
    def verify_available_plans(page, expectedPlans = [10, 25, 50, 100, 300, 500, 700, 1500], plan_type: str = None):
        update_plan_page = UpdatePlanPage(page)
        expect(update_plan_page.plan_card_container).to_be_visible(timeout=120000)
        plan_elements = update_plan_page.plan_card_container.locator("[data-testid^='plans-selector-plan-card-container']").all()
        plan_count = len(plan_elements)
        assert plan_count == len(expectedPlans), f"Expected {len(expectedPlans)} plan cards, but found {plan_count} cards"

        for i in range(plan_count):
            card_text = update_plan_page.get_plan_by_position(i).text_content()
            card_text_numbers = re.findall(r"\d+\.\d+|\d+", card_text)
            actual_plan = int(card_text_numbers[0])
            expected_plan = expectedPlans[i]
            assert actual_plan == expected_plan, f"Expected plan {expected_plan} pages, but got {actual_plan} pages"
            if plan_type == "ink_and_paper":
                assert "Includes ink and paper" in card_text, f"Expected 'Includes ink and paper' in plan card text, but got '{card_text}'"
            elif plan_type is None:
                assert "Includes ink and paper" not in card_text, f"Expected 'Includes ink and paper' not to be in plan card text, but got '{card_text}'"

    @staticmethod
    def verify_current_plan(page, expectedPlan: int):
        update_plan_page = UpdatePlanPage(page)
        plan_card = update_plan_page.get_plan_by_pages(expectedPlan)
        expect(plan_card.locator('[data-testid$="plan-tag-container"]')).to_be_visible()        
        
    @staticmethod
    def select_plan(page, plan_pages: int):
        update_plan_page = UpdatePlanPage(page)
        plan_card = update_plan_page.get_plan_by_pages(plan_pages)
        plan_button = plan_card.locator("button")
        plan_button.click()

    @staticmethod
    def select_plan_button(page, plan_button: int):
        update_plan_page = UpdatePlanPage(page)
        plan_button = update_plan_page.get_select_plan_button(plan_button) 
        plan_button.wait_for(state="visible", timeout=90000)
        plan_button.click()
        plan_button.wait_for(state="detached", timeout=90000)

    @staticmethod
    def select_plan_by_position(page, position: int):
        update_plan_page = UpdatePlanPage(page)
        plan_locator = update_plan_page.get_plan_by_position(position-1)
        plan_locator.locator("button").click()
       
    @staticmethod
    def cancellation_subscription(page,callback=None):
        dashboard_page = UpdatePlanPage(page)
        cancellation_page = CancellationPage(page)
        dashboard_page.cancel_instant_ink.wait_for(state="visible", timeout=90000)
        dashboard_page.cancel_instant_ink.click()
        cancellation_page.confirm_cancellation_button.wait_for(state="visible", timeout=120000)
        cancellation_page.confirm_cancellation_button.click()
        try:
            cancellation_page.continue_button.wait_for(state="visible", timeout=90000)
            print("Continue button is visible on Cancellation Feedback Page")
            time.sleep(5)
            if callback: callback("Returned_Confirmation_Page", page, screenshot_only=True)
        except Exception:
            cancellation_page.confirm_cancellation_button.click()


    @staticmethod
    def validate_terms_of_service_page(page):
        update_plan_page = UpdatePlanPage(page)
        with page.expect_popup(timeout=30000) as popup_info:
            update_plan_page.terms_and_service_link.click()
        terms_page = popup_info.value
        expect(terms_page).to_have_url(re.compile(r'/terms'), timeout=90000)
        terms_page.close()

    @staticmethod
    def sees_plan_upgraded_or_downgraded_message_on_banner(page, plan: str):
        update_plan_page = UpdatePlanPage(page)
        expect(update_plan_page.pending_change_plan).to_be_visible(timeout=90000)
        actual_text = update_plan_page.pending_change_plan.inner_text()
        numbers = re.findall(r'\d+', actual_text)
        assert plan in numbers, f"Expected plan '{plan}' not found in '{numbers}'"    

    @staticmethod
    def click_button_on_undo_your_plan_modal(page, button: str):
        update_plan_page = UpdatePlanPage(page)
        update_plan_page.cancel_change_plan_link.click()

        if button == "Cancel":
            update_plan_page.undo_plan_change_cancel_button.click(timeout=90000)
            expect(update_plan_page.undo_plan_change_cancel_button).not_to_be_visible() 
        elif button == "Undo Upgrade":
            update_plan_page.undo_plan_change_confirmation.click(timeout=90000)   
            expect(update_plan_page.undo_plan_change_confirmation).not_to_be_visible() 

    @staticmethod
    def verify_plan_info(page, plan_value: str, plan_pages: str):
        update_plan_page = UpdatePlanPage(page)
        expect(update_plan_page.plan_details_card).to_be_visible(timeout=90000)
        plan_info = update_plan_page.plan_information.text_content()
        numbers = common.extract_numbers_from_text(plan_info)
        assert numbers[0] == plan_value, f"Expected plan value to be {plan_value}, but got {numbers[0]}"
        assert numbers[1] == plan_pages, f"Expected plan pages to be {plan_pages}, but got {numbers[1]}"
