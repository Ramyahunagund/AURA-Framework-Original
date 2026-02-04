import re
import time
from pages.dashboard_side_menu_page import DashboardSideMenuPage
from pages.overview_page import OverviewPage
from pages.print_history_page import PrintHistoryPage
from playwright.sync_api import expect
from core.settings import framework_logger
import test_flows_common.test_flows_common as common

from pages.update_plan_page import UpdatePlanPage

class PrintHistoryHelper:
      
    @staticmethod
    def verify_previous_billing_cycle_period(page):
        print_history_page = PrintHistoryPage(page)
        print_history_page.billing_cycle_option.click()
        print_history_page.select_1_option.click()
        expect(print_history_page.billing_cycle_period_title).not_to_contain_text('Current')
        
    @staticmethod
    def get_billing_cycle_option(page, period_index: int):
        print_history_page = PrintHistoryPage(page)
        print_history_page.billing_cycle_option.click()
        framework_logger.info("Opened billing cycle dropdown")
        
        # Select the specified period
        if period_index == 1:
            print_history_page.select_1_option.click()
        elif period_index == 2:
            print_history_page.select_2_option.click()
        elif period_index == 3:
            print_history_page.select_3_option.click()
        else:
            raise ValueError(f"Invalid period_index: {period_index}. Must be 1, 2, or 3.")
        
        framework_logger.info(f"Selected billing cycle period option {period_index}")
        
        # Wait for table to update
        expect(print_history_page.print_history_table_button).to_be_visible(timeout=10000)
        framework_logger.info("Billing table updated after period selection")

    @staticmethod
    def verify_billing_table_data(page, total_pages_printed):     
        framework_logger.info("Starting billing table data validation")
        print_history_page = PrintHistoryPage(page)
        
        # Validate total pages printed
        total_pages_text = print_history_page.total_pages_printed.inner_text()
        numbers = common.extract_numbers_from_text(total_pages_text)

        if len(numbers) == 0:
            raise ValueError(f"Expected total pages printed to be {total_pages_printed}, but found no numbers in text: '{total_pages_text}'")

        assert numbers[0] == total_pages_printed, \
            f"Expected total pages printed to be {total_pages_printed}, but found {numbers[0]} in text: '{total_pages_text}'"

    @staticmethod
    def get_text_from_selector(page, selector):
        """Helper method to get text from a page element"""
        if hasattr(selector, 'inner_text'):
            # If it's already a locator object, use it directly
            return selector.inner_text()
        else:
            # If it's a string selector, create a locator and get the first element
            return page.locator(selector).first.inner_text()
    
    @staticmethod
    def normalize_currency_value(value):
        if not value:
            return "0.00"
        normalized = str(value).strip().replace(',', '.').replace('$', '').replace('€', '').replace('£', '')
        normalized = normalized.replace('\xa0', '').replace(' ', '')
        if normalized in ['-', '', '—', 'N/A', 'n/a']:
            return "0.00"
        try:
            float_val = float(normalized)
            return f"{float_val:.2f}"
        except:
            return normalized

    @staticmethod
    def validate_currency_field(page, selector, expected, partial_match=False):
        actual_text = PrintHistoryHelper.get_text_from_selector(page, selector)
        if isinstance(expected, int):
            expected = expected / 100
        expected_norm = PrintHistoryHelper.normalize_currency_value(expected)
        if partial_match:
            assert expected_norm in actual_text.replace(',', '.'), \
                f"Expected value '{expected_norm}' not found in actual text '{actual_text}'"
        else:
            actual_norm = PrintHistoryHelper.normalize_currency_value(actual_text)
            assert actual_norm == expected_norm, \
                f"Expected value '{expected_norm}', but got '{actual_norm}' (raw: '{actual_text}')"

    @staticmethod
    def verify_correct_billing_section(page, expected_values: dict):
        print_history = PrintHistoryPage(page)

        # Total pages printed
        if "total_pages_printed" in expected_values:
            actual = common.extract_numbers_from_text(
                print_history.total_pages_printed.inner_text()
            )[0]
            expected = expected_values["total_pages_printed"]
            assert str(actual) == str(expected), f"Expected 'total_pages_printed' to be '{expected}', but got '{actual}'"

        # Plan pages
        if "pages" in expected_values:
            actual = common.extract_numbers_from_text(
                PrintHistoryHelper.get_text_from_selector(page, print_history.elements.plan_pages_text)
            )[0]
            expected = expected_values["pages"]
            assert str(actual) == str(expected), f"Expected 'pages' to be '{expected}', but got '{actual}'"

        # Rollover
        if "rollover" in expected_values and str(expected_values["rollover"]).strip() != "-":
            actual = common.extract_numbers_from_text(
                PrintHistoryHelper.get_text_from_selector(page, print_history.elements.rollover_pages_text)
            )[0]
            expected = expected_values["rollover"]
            assert str(actual) == str(expected), f"Expected 'rollover' to be '{expected}', but got '{actual}'"

        # Additional
        if "additional" in expected_values and str(expected_values["additional"]).strip() != "-":
            actual = common.extract_numbers_from_text(
                PrintHistoryHelper.get_text_from_selector(page, print_history.elements.additional_pages_text)
            )[0]
            expected = expected_values["additional"]
            assert str(actual) == str(expected), f"Expected 'additional' to be '{expected}', but got '{actual}'"

        # Plan price
        if "plan_price" in expected_values:
            PrintHistoryHelper.validate_currency_field(
                page,
                print_history.elements.plan_price_text,
                expected_values["plan_price"],
                partial_match=True
            )

        # Overage price
        if "overage_price" in expected_values:
            PrintHistoryHelper.validate_currency_field(
                page,
                print_history.elements.overage_description_text,
                expected_values["overage_price"],
                partial_match=True
            )

        # Previous billing
        if "previous" in expected_values:
            PrintHistoryHelper.validate_currency_field(
                page,
                print_history.elements.previous_billing_text,
                expected_values["previous"]
            )

        # Charges
        if "charges" in expected_values:
            PrintHistoryHelper.validate_currency_field(
                page,
                print_history.elements.current_billing_text,
                expected_values["charges"]
            )

        # Tax (if element exists)
        if "tax" in expected_values and str(expected_values["tax"]).strip() != "-":
            try:
                PrintHistoryHelper.validate_currency_field(
                    page,
                    '[data-testid="tax-amount"]',  # Update selector if needed
                    expected_values["tax"]
                )
            except Exception:
                framework_logger.warning("Tax element not found, skipping tax validation")

        # Total
        if "total" in expected_values:
            PrintHistoryHelper.validate_currency_field(
                page,
                print_history.elements.current_total_text,
                expected_values["total"]
            )

    @staticmethod
    def verify_all_billing_cycles_data(page, expected_data: list):
        print_history = PrintHistoryPage(page)

        for row in expected_data:
            billing_cycle_index = int(row["billing_cycle"]) - 1  # Convert to 0-based index
            framework_logger.info(f"Validating billing cycle {row['billing_cycle']}")
            
            print_history.billing_cycle_option.click()
            framework_logger.info("Opened billing cycle dropdown")      
            billing_options = page.locator(print_history.elements.billing_cycle_options)
            billing_options.nth(billing_cycle_index).click()
            framework_logger.info(f"Selected billing cycle option {billing_cycle_index + 1}")
            page.wait_for_timeout(1000)    
            PrintHistoryHelper.verify_correct_billing_section(page, row)


    @staticmethod
    def validate_faq_on_print_and_payment_history(page):
        print_history_page = PrintHistoryPage(page)
        overview_page = OverviewPage(page)
        update_plan_page = UpdatePlanPage(page)
        side_menu = DashboardSideMenuPage(page)

        print_history_page.faq_question_1.click()
        expect(print_history_page.faq_answer_1).to_be_visible(timeout=30000)

        # Validate FAQ [1] and Terms of Service page
        with page.expect_popup(timeout=30000) as popup_info:
            print_history_page.faq_terms_of_service_link.click()
        popup = popup_info.value
        expect(popup).to_have_url(re.compile(r'/terms'), timeout=30000)
        popup.close()

        # Validate FAQ [2], Overview and Update Plan pages
        print_history_page.faq_question_2.click()
        expect(print_history_page.faq_answer_2).to_be_visible(timeout=30000)
        print_history_page.faq_overview_link.click()
        expect(overview_page.status_card_title).to_be_visible(timeout=30000)
        side_menu.print_history_menu_link.click()

        print_history_page.faq_question_2.click()
        expect(print_history_page.faq_answer_2).to_be_visible(timeout=30000)
        print_history_page.update_plan_link.first.click()
        expect(update_plan_page.page_title).to_be_visible(timeout=30000)
        side_menu.print_history_menu_link.click()

        # Validate FAQ [3]
        print_history_page.faq_question_3.click()
        expect(print_history_page.faq_answer_3).to_be_visible(timeout=30000)

        # Validate FAQ [4] and Update Plan page
        print_history_page.faq_question_4.click()
        expect(print_history_page.faq_answer_4).to_be_visible(timeout=30000)
        print_history_page.update_plan_link.last.click()
        expect(update_plan_page.page_title).to_be_visible(timeout=30000)
        side_menu.print_history_menu_link.click()

    @staticmethod
    def validate_no_pens_print_history_page(page):
        print_history_page = PrintHistoryPage(page)
        # Check visible elements
        expect(print_history_page.print_history_section).to_be_visible(timeout=30000)
        expect(print_history_page.page_title).to_be_visible(timeout=30000)

        # Check elements are not visible
        expect(print_history_page.print_history_card_title).not_to_be_visible(timeout=30000)
        expect(print_history_page.how_is_calculated_link).not_to_be_visible(timeout=30000)
        expect(print_history_page.total_printed_pages).not_to_be_visible(timeout=30000)
        expect(print_history_page.plan_pages_bar).not_to_be_visible(timeout=30000)
        expect(print_history_page.plan_details_card).not_to_be_visible(timeout=30000)

    @staticmethod
    def click_download_all_invoices(page):
        print_history_page = PrintHistoryPage(page)
        for attempt in range(60):
            try:
                print_history_page.print_history_table_button.click()
                expect(print_history_page.download_all_invoices_button).to_be_visible(timeout=5000)
                break
            except Exception:
                if attempt == 59:
                    raise Exception("Download All Invoices button is not visible after maximum retries")
                framework_logger.info(f"Download All Invoices button not visible, retry {attempt + 1}/60")
                time.sleep(60)
                page.reload()
                expect(print_history_page.print_history_card_title).to_be_visible(timeout=90000)
                                
        with page.context.expect_page() as new_page_info:
            print_history_page.download_all_invoices_button.click()
        new_tab = new_page_info.value
        assert "invoices" in new_tab.url, f"Expected 'invoices' in URL, but got {new_tab.url}"

    @staticmethod
    def see_notification_on_print_history(page, notifications_text: str):
        print_history_page = PrintHistoryPage(page)
        if print_history_page.print_history_table.is_hidden():
            print_history_page.print_history_table_button.click()
        expect(print_history_page.print_history_table).to_be_visible(timeout=30000)
        time.sleep(3)
        table_content = print_history_page.print_history_table.inner_text()
        assert notifications_text in table_content, f"Expected notification text '{notifications_text}' not found in print history table. \nActual table content: '{table_content}'"

    @staticmethod
    def verify_plan_info(page, plan_value: str, plan_pages: str):
        print_history_page = PrintHistoryPage(page)
        expect(print_history_page.print_history_card).to_be_visible(timeout=90000)
        plan_info = print_history_page.plan_price_text.text_content()
        numbers = common.extract_numbers_from_text(plan_info)
        assert numbers[0] == plan_value, f"Expected plan value to be {plan_value}, but got {numbers[0]}"
        assert numbers[1] == plan_pages, f"Expected plan pages to be {plan_pages}, but got {numbers[1]}"

    @staticmethod
    def verify_current_total(page, total_value: str):
        print_history_page = PrintHistoryPage(page)
        expect(print_history_page.print_history_card).to_be_visible(timeout=90000)
        current_total = print_history_page.current_total_text.first.text_content()
        numbers = common.extract_numbers_from_text(current_total)
        assert numbers[0] == total_value, f"Expected total value to be {total_value}, but got {numbers[0]}"
        