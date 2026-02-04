import re
from pages.overview_page import OverviewPage
from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from playwright.sync_api import expect
from core.settings import framework_logger
import re
import os
import time

class OverviewHelper:
    @staticmethod
    def verify_cartridge_installed_message(page, cartridge):
        overview_page = OverviewPage(page)
        cartridges = cartridge.split(",")

        cartridge_locators = {
            "k": overview_page.get_selector("kCartridgeItem"),
            "c": overview_page.get_selector("cCartridgeItem"),
            "m": overview_page.get_selector("mCartridgeItem"),
            "y": overview_page.get_selector("yCartridgeItem"),
            "cmy": overview_page.get_selector("cmyCartridgeItem")
        }

        for cartridge_type in cartridges:
            cartridge_type = cartridge_type.strip()
            if cartridge_type not in cartridge_locators:
                raise RuntimeError(f"Invalid cartridge type: {cartridge_type}")

            cartridge_element = page.wait_for_selector(cartridge_locators[cartridge_type], timeout=20000)
            assert cartridge_element.is_visible(), f"Cartridge {cartridge_type} is not visible."

    @staticmethod
    def verify_multiple_cartridge_types_installed_message(page, cartridge, cartridge2):
        try:
            OverviewHelper.verify_cartridge_installed_message(page, cartridge)
        except RuntimeError:
            OverviewHelper.verify_cartridge_installed_message(page, cartridge2)

    @staticmethod
    def number_of_printers_in_section(page, group, number):
        overview_page = OverviewPage(page)

        printers_status_section = overview_page.printers_grouped_by_status.all()
        printers_grouped = None

        for element in printers_status_section:
            if group in element.inner_text():
                printers_grouped = element
                break

        assert printers_grouped is not None and printers_grouped.is_visible(), f"Section '{group}' not found or not visible"
        assert group in printers_grouped.inner_text(), f"Section text does not contain '{group}'"

        printer_selected_array = printers_grouped.locator(overview_page.printer_selector_option).all()

        if number == "only one":
            assert len(printer_selected_array) == 1, "Expected only one printer in the section"
        elif number == "more than one":
            assert len(printer_selected_array) > 1, "Expected more than one printer in the section"
        else:
            raise Exception("Invalid number of printers")

    @staticmethod
    def verify_plan_suggestion_banner(page, banner_type="downgrading"):                 
        overview_page = OverviewPage(page)  

        banner_selector = overview_page.get_selector("plan_suggestion_banner")
        banner_locator = page.locator(banner_selector)
        banner_locator.wait_for(state="visible", timeout=30000)
     
        expect(banner_locator).to_be_visible()
    
        banner_text = banner_locator.text_content().lower()
        
        if banner_type.lower() == "downgrading":
            downgrade_keywords = ["downgrading", "lower plan", "reduce", "save money", "smaller plan"]
            assert any(keyword in banner_text for keyword in downgrade_keywords), \
                f"Downgrading banner text not found. Banner content: {banner_text}"
        elif banner_type.lower() == "upgrading":
            upgrading_keywords = ["upgrading", "higher plan", "more pages", "increase", "larger plan"]
            assert any(keyword in banner_text for keyword in upgrading_keywords), \
                f"Upgrading banner text not found. Banner content: {banner_text}"
        else:
            raise ValueError(f"Invalid banner_type: {banner_type}. Must be 'downgrading' or 'upgrading'")

        print(f"✓ Plan suggestion banner ({banner_type}) verified successfully")
        return banner_locator
    
    @staticmethod
    def sees_plan_upgraded_information_on_overview_page(page, plan: str):
        overview_page = OverviewPage(page)

        expect(overview_page.plan_information).to_be_visible(timeout=120000)
        plan_info_text = overview_page.plan_information.inner_text().replace('.', '').replace(',', '')

        plan_info_numbers = re.findall(r'\d+', plan_info_text)
        plan_pages = plan_info_numbers[1]
        assert str(plan_pages) == str(plan)
    
    @staticmethod
    def verify_unsubscribed_status_card(page):      
        overview_page = OverviewPage(page)

        expect(overview_page.unsubscribed_enroll_printer_again_button).to_be_visible(timeout=150000)
        expect(overview_page.unsubscribed_hp_shop_ink_button).to_be_visible(timeout=30000)
        expect(overview_page.unsubscribed_download_past_invoices).to_be_visible(timeout=30000)   

    @staticmethod
    def click_hp_shop_ink_and_verify_url(page):
        overview_page = OverviewPage(page)
   
        expect(overview_page.unsubscribed_hp_shop_ink_button).to_be_visible(timeout=30000)
       
        with page.context.expect_page() as new_page_info:
            overview_page.unsubscribed_hp_shop_ink_button.click()      
        new_tab = new_page_info.value     
        expect(new_tab).to_have_url(re.compile(r'/shop/pdp'), timeout=30000)      
        new_tab.close()      
        
    @staticmethod
    def click_enroll_printer_again_and_verify_enrollment(page):           
        overview_page = OverviewPage(page)      
        overview_page.unsubscribed_enroll_printer_again_button.click()   

        with page.context.expect_page() as new_page_info:            
            enrollment_page = new_page_info.value
            enrollment_page.bring_to_front()       
            try:
                EnrollmentHelper.accept_automatic_printer_updates(enrollment_page)
                framework_logger.info("User clicks on continue button on automatic printer updates page")
            except:
                framework_logger.info("Automatic printer updates page not found or already passed")

        confirmation_page = ConfirmationPage(enrollment_page)        
        expect(confirmation_page.v3_content_area).to_be_visible(timeout=120000)       
        enrollment_page.close()          

    @staticmethod
    def download_past_invoices_on_status_card(page, invoices_directory="/tmp/downloads"):
        overview_page = OverviewPage(page)
        
        expect(overview_page.unsubscribed_download_past_invoices).to_be_visible(timeout=30000)
        os.makedirs(invoices_directory, exist_ok=True)    
                        
        with page.context.expect_page() as new_page_info:
                overview_page.unsubscribed_download_past_invoices.click()            
        pdf_page = new_page_info.value
        pdf_page.bring_to_front()
            
        time.sleep(3)
        pdf_file = os.path.join(invoices_directory, "invoice.pdf")
        pdf_page.pdf(path=pdf_file)
        pdf_page.close()
        
        time.sleep(2)
        assert os.path.exists(pdf_file), f"Invoice PDF file not found at {pdf_file}"
        
        page.screenshot(path=f"{invoices_directory}/invoice_pdf_file_screenshot.png")
        framework_logger.info(f"Invoice PDF downloaded successfully: {pdf_file}")
