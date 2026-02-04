import re
import time

from core.utils import load_locale_data
from pages.landing_page import LandingPage
from pages.privacy_banner_page import PrivacyBannerPage
from pages.printer_selection_page import PrinterSelectionPage
from pages.printer_updates_page import PrinterUpdatesPage
from pages.confirmation_page import ConfirmationPage
from pages.thank_you_page import ThankYouPage
from pages.tos_hp_smart_page import TermsOfServiceHPSmartPage
from playwright.sync_api import expect
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
from test_flows.LandingPage.landing_page import landing_page


class LandingPageHelper:

    @staticmethod
    def open(page):
        page.goto(common._instantink_url, timeout=120000)
        page.wait_for_load_state("load")

    @staticmethod
    def access(page):
        LandingPageHelper.open(page)
        privacy_banner_page = PrivacyBannerPage(page)
        privacy_banner_page.accept_privacy_banner()

        landing_page = LandingPage(page)
        try:
            landing_page.close_banner.click()
        except Exception as e:
            print(f"Close banner not found or could not be clicked: {e}")

    @staticmethod
    def verify_raf_banner_with_free_months(page, expected_months=1):    
        landing_page = LandingPage(page)            
        raf_banner = page.locator(landing_page.elements.raf_banner)
        expect(raf_banner).to_be_visible(timeout=30000)        
 
        banner_text = raf_banner.text_content()
        expected_text = f"You have {expected_months} free month of HP Instant Ink"
        
        assert expected_text in banner_text, f"RaF banner text does not include expected text. Found: '{banner_text}', Expected to include: '{expected_text}'"
        framework_logger.info(f"✓ RaF banner is visible and contains expected text: '{expected_text}'")
        return True
          
    @staticmethod
    def verify_raf_footnote_on_landing_page(page):   
        landing_page = LandingPage(page)
        raf_footnote = page.locator(landing_page.elements.raf_footnote)
        expect(raf_footnote).to_be_visible(timeout=30000)

    @staticmethod
    def verify_section_is_in_viewport(page, section_selector):
        # Verify FAQs section is in the viewport after click
        is_in_viewport = page.evaluate("""
            (selector) => {
                const el = document.querySelector(selector);
                if (!el) return false;
                const rect = el.getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight)
                );
            }
        """, section_selector)
        return is_in_viewport

    @staticmethod
    def consumer_landing_page_oobe(page, callback=None):
        landing_page = LandingPage(page)
        try:
            # Sign Up Now button
            page.goto("https://instantink-stage1.hpconnectedstage.com/us/en/l/v2", timeout=120000)
            try:
                page.wait_for_selector("#onetrust-accept-btn-handler", timeout=10000).click()
                framework_logger.info("Privacy banner accepted")
            except Exception as e:
                framework_logger.debug(f"Privacy banner not found or already accepted: {e}")
            landing_page.sign_up_header_button.wait_for(state='visible', timeout=200000)
            landing_page.sign_up_header_button.click()
            try:
                page.wait_for_selector("#onetrust-accept-btn-handler", timeout=10000).click()
                framework_logger.info("Privacy banner accepted")
            except Exception as e:
                framework_logger.debug(f"Privacy banner not found or already accepted: {e}")
            landing_page.hpid_page.wait_for(state='visible', timeout=50000)
            if callback: callback("signup_function", page, screenshot_only=True)
            framework_logger.info("Sign Up Now Function is working fine on Landing Page")

            # Return to Customer Landing Page
            page.goto("https://instantink-stage1.hpconnectedstage.com/us/en/l/v2", timeout=120000)
            try:
                page.wait_for_selector("#onetrust-accept-btn-handler", timeout=10000).click()
                framework_logger.debug("Privacy banner accepted")
            except Exception as e:
                framework_logger.debug(f"Privacy banner not found or already accepted: {e}")
            landing_page.sign_up_header_button.wait_for(state='visible', timeout=50000)

            # How It Works section
            landing_page.how_it_works_tab.wait_for(state='visible', timeout=50000)
            landing_page.how_it_works_tab.click()
            time.sleep(5) # Wait for scroll to the section
            landing_page.how_it_works_section.wait_for(state='visible', timeout=50000)
            if LandingPageHelper.verify_section_is_in_viewport(page,landing_page.elements.how_it_works_section):
                framework_logger.info("How It Works Function is working fine on Landing Page and is in the viewport after click")
            else:
                framework_logger.error("How It Works section is not in the viewport after clicking How It Works link")
            if callback: callback("howitworks", page, screenshot_only=True)

            # Instant Paper Plan section
            landing_page.instant_paper_tab.wait_for(state='visible', timeout=50000)
            landing_page.instant_paper_tab.click()
            time.sleep(5) # Wait for scroll to the section
            landing_page.instant_paper_section.wait_for(state='visible', timeout=50000)
            if LandingPageHelper.verify_section_is_in_viewport(page, landing_page.elements.instant_paper_section):
                framework_logger.info("Instant Paper Plan Function is working fine on Landing Page and is in the viewport after click")
            else:
                framework_logger.error("Instant Paper Plan section is not in the viewport after clicking Instant Paper Plan link")
            if callback: callback("instant_paper", page, screenshot_only=True)

            # Plans section
            landing_page.plans_tab.wait_for(state='visible', timeout=50000)
            landing_page.plans_tab.click()
            time.sleep(5) # Wait for scroll to the section
            landing_page.plans_section.wait_for(state='visible', timeout=50000)
            if LandingPageHelper.verify_section_is_in_viewport(page, landing_page.elements.plans_section):
                framework_logger.info("Plans Function is working fine on Landing Page and is in the viewport after click")
            else:
                framework_logger.error("Plans section is not in the viewport after clicking Plans section")
            if callback: callback("plans", page, screenshot_only=True)

            # FAQs section
            landing_page.faqs_tab.wait_for(state='visible', timeout=50000)
            landing_page.faqs_tab.click()
            time.sleep(5) # Wait for scroll to the section
            landing_page.faqs_section.wait_for(state='visible', timeout=50000)
            if LandingPageHelper.verify_section_is_in_viewport(page, landing_page.elements.faqs_section):
                framework_logger.info("FAQs Function is working fine on Landing Page and is in the viewport after click")
            else:
                framework_logger.error("FAQs section is not in the viewport after clicking FAQs section")
            if callback: callback("faqs", page, screenshot_only=True)
        except Exception as e:
            framework_logger.error(f'ERROR in consumer_landing_page method: {e}')

    @staticmethod
    def consumer_landing_page_mobe(page, callback=None):
        landing_page = LandingPage(page)
        try:
            # Sign Up Now button
            page.goto("https://instantink-stage1.hpconnectedstage.com/us/en/l/v2", timeout=120000)
            try:
                page.wait_for_selector("#onetrust-accept-btn-handler", timeout=10000).click()
                framework_logger.info("Privacy banner accepted")
            except Exception as e:
                framework_logger.debug(f"Privacy banner not found or already accepted: {e}")
            landing_page.mobe_menu_button.wait_for(state='visible', timeout=200000)
            landing_page.mobe_menu_button.click()
            landing_page.mobe_sign_up_button.wait_for(state='visible', timeout=200000)
            landing_page.mobe_sign_up_button.click()
            try:
                page.wait_for_selector("#onetrust-accept-btn-handler", timeout=10000).click()
                framework_logger.info("Privacy banner accepted")
            except Exception as e:
                framework_logger.debug(f"Privacy banner not found or already accepted: {e}")
            landing_page.hpid_page.wait_for(state='visible', timeout=50000)
            if callback: callback("signup_function", page, screenshot_only=True)
            framework_logger.info("Sign Up Now Function is working fine on Landing Page")

            # Return to Customer Landing Page
            page.goto("https://instantink-stage1.hpconnectedstage.com/us/en/l/v2", timeout=120000)
            try:
                page.wait_for_selector("#onetrust-accept-btn-handler", timeout=10000).click()
                framework_logger.info("Privacy banner accepted")
            except Exception as e:
                framework_logger.debug(f"Privacy banner not found or already accepted: {e}")
            landing_page.mobe_menu_button.wait_for(state='visible', timeout=200000)
            landing_page.mobe_menu_button.click()

            # How It Works section
            landing_page.mobe_how_it_works_tab.wait_for(state='visible', timeout=50000)
            landing_page.mobe_how_it_works_tab.click()
            time.sleep(5)  # Wait for scroll to the section
            landing_page.how_it_works_section.wait_for(state='visible', timeout=50000)
            if LandingPageHelper.verify_section_is_in_viewport(page, landing_page.elements.how_it_works_section):
                framework_logger.info(
                    "How It Works Function is working fine on Landing Page and is in the viewport after click")
            else:
                framework_logger.error("How It Works section is not in the viewport after clicking How It Works link")
            if callback: callback("howitworks", page, screenshot_only=True)

            # Instant Paper Plan section
            landing_page.mobe_menu_button.wait_for(state='visible', timeout=200000)
            landing_page.mobe_menu_button.click()
            landing_page.mobe_instant_paper_tab.wait_for(state='visible', timeout=50000)
            landing_page.mobe_instant_paper_tab.click()
            time.sleep(5)  # Wait for scroll to the section
            landing_page.mobe_instant_paper_section.wait_for(state='visible', timeout=50000)
            if LandingPageHelper.verify_section_is_in_viewport(page, landing_page.elements.mobe_instant_paper_section):
                framework_logger.info(
                    "Instant Paper Plan Function is working fine on Landing Page and is in the viewport after click")
            else:
                framework_logger.error(
                    "Instant Paper Plan section is not in the viewport after clicking Instant Paper Plan link")
            if callback: callback("instant_paper", page, screenshot_only=True)

            # Plans section
            landing_page.mobe_menu_button.wait_for(state='visible', timeout=200000)
            landing_page.mobe_menu_button.click()
            landing_page.mobe_plans_tab.wait_for(state='visible', timeout=50000)
            landing_page.mobe_plans_tab.click()
            time.sleep(5)  # Wait for scroll to the section
            landing_page.plans_section.wait_for(state='visible', timeout=50000)
            if LandingPageHelper.verify_section_is_in_viewport(page, landing_page.elements.plans_section):
                framework_logger.info(
                    "Plans Function is working fine on Landing Page and is in the viewport after click")
            else:
                framework_logger.error("Plans section is not in the viewport after clicking Plans section")
            if callback: callback("plans", page, screenshot_only=True)

            # FAQs section
            landing_page.mobe_menu_button.wait_for(state='visible', timeout=200000)
            landing_page.mobe_menu_button.click()
            landing_page.mobe_faqs_tab.wait_for(state='visible', timeout=50000)
            landing_page.mobe_faqs_tab.click()
            time.sleep(5)  # Wait for scroll to the section
            landing_page.mobe_faqs_section.wait_for(state='visible', timeout=50000)
            if LandingPageHelper.verify_section_is_in_viewport(page, landing_page.elements.mobe_faqs_section):
                framework_logger.info(
                    "FAQs Function is working fine on Landing Page and is in the viewport after click")
            else:
                framework_logger.error("FAQs section is not in the viewport after clicking FAQs section")
            if callback: callback("faqs", page, screenshot_only=True)
        except Exception as e:
            framework_logger.error(f'ERROR in consumer_landing_page method: {e}')

    @staticmethod
    def validate_never_worry_section_oobe(page, callback=None):
        landing_page = LandingPage(page)
        try:
            # Never worry about running out of ink again section
            landing_page.never_worry_section.wait_for(state='visible', timeout=50000)
            landing_page.never_worry_section.scroll_into_view_if_needed(timeout=50000)
            framework_logger.info("Never worry about running out of ink again section is visible on Landing Page")
            if callback: callback("never_worry", page, screenshot_only=True)
        except Exception as e:
            framework_logger.error(f"ERROR in never_worry_section method: {e}")

    @staticmethod
    def validate_never_worry_section_mobe(page, callback=None):
        landing_page = LandingPage(page)
        try:
            # Never worry about running out of ink again section
            landing_page.mobe_never_work_section.wait_for(state='visible', timeout=50000)
            landing_page.mobe_never_work_section.scroll_into_view_if_needed(timeout=50000)
            framework_logger.info("Never worry about running out of ink again section is visible on Landing Page")
            if callback: callback("never_worry", page, screenshot_only=True)
        except Exception as e:
            framework_logger.error(f"ERROR in never_worry_section method: {e}")

    @staticmethod
    def hyperlinks_validation(page, callback=None):
        landing_page = LandingPage(page)
        try:
            # HP.com link
            landing_page.footer_hp_link.wait_for(state='visible', timeout=50000)
            landing_page.footer_hp_link.scroll_into_view_if_needed(timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_hp_link.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/home.html"), timeout=60000)
            framework_logger.info("HP.com hyperlink is working fine on Landing Page")
            if callback: callback("hpcom", new_page, screenshot_only=True)
            new_page.close()

            # Privacy Statement link
            landing_page.footer_privacy_statement.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_privacy_statement.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("load", timeout=60000)
            time.sleep(5) # Wait for full page load for screenshot
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/privacy/privacy.html"), timeout=60000)
            framework_logger.info("Privacy Statement hyperlink is working fine on Landing Page")
            if callback: callback("privacy_statement", new_page, screenshot_only=True)
            new_page.close()

            # HP Connected Terms of Use
            landing_page.footer_terms_of_use.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_terms_of_use.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hpsmart.com/us/en/tou"), timeout=60000)
            framework_logger.info("HP Connected Terms of Use hyperlink is working fine on Landing Page")
            if callback: callback("terms_of_use", new_page, screenshot_only=True)
            new_page.close()

            # cookie setting
            landing_page.footer_cookies.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_cookies.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("load", timeout=60000)
            time.sleep(5)  # Wait for full page load for screenshot
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/privacy/use-of-cookies.html"), timeout=60000)
            framework_logger.info("Cookie Settings hyperlink is working fine on Landing Page")
            if callback: callback("cookie_settings", new_page, screenshot_only=True)
            new_page.close()

            # Your Privacy Choices
            landing_page.footer_privacy_choice.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_privacy_choice.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/privacy/your-privacy-choices.html"), timeout=60000)
            framework_logger.info("Your Privacy Choices hyperlink is working fine on Landing Page")
            if callback: callback("privacy_choices", new_page, screenshot_only=True)
            new_page.close()

            # Instant Ink Terms of Service
            landing_page.footer_iitos.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_iitos.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://instantink-stage1.hpconnectedstage.com/us/en/terms"), timeout=60000)
            framework_logger.info("Instant Ink Terms of Service hyperlink is working fine on Landing Page")
            if callback: callback("instant_ink_terms", new_page, screenshot_only=True)
            new_page.close()
        except Exception as e:
            framework_logger.error(f"ERROR in hyperlink method: {e}")

    @staticmethod
    def hyperlinks_validation_mobe(page, callback=None):
        landing_page = LandingPage(page)
        try:
            # HP.com link
            landing_page.footer_hp_link.wait_for(state='visible', timeout=50000)
            landing_page.footer_hp_link.scroll_into_view_if_needed(timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_hp_link.click()
            new_page = new_page_info.value
            new_page.set_viewport_size({"width": 400, "height": 740})
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/home.html"), timeout=60000)
            framework_logger.info("HP.com hyperlink is working fine on Landing Page")
            if callback: callback("hpcom", new_page, screenshot_only=True)
            new_page.close()

            # Privacy Statement link
            landing_page.footer_privacy_statement.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_privacy_statement.click()
            new_page = new_page_info.value
            new_page.set_viewport_size({"width": 400, "height": 740})
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/privacy/privacy.html"), timeout=60000)
            framework_logger.info("Privacy Statement hyperlink is working fine on Landing Page")
            if callback: callback("privacy_statement", new_page, screenshot_only=True)
            new_page.close()

            # HP Connected Terms of Use
            landing_page.footer_terms_of_use.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_terms_of_use.click()
            new_page = new_page_info.value
            new_page.set_viewport_size({"width": 400, "height": 740})
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hpsmart.com/us/en/tou"), timeout=60000)
            framework_logger.info("HP Connected Terms of Use hyperlink is working fine on Landing Page")
            if callback: callback("terms_of_use", new_page, screenshot_only=True)
            new_page.close()

            # cookie setting
            landing_page.footer_cookies.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_cookies.click()
            new_page = new_page_info.value
            new_page.set_viewport_size({"width": 400, "height": 740})
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/privacy/use-of-cookies.html"),
                                         timeout=60000)
            framework_logger.info("Cookie Settings hyperlink is working fine on Landing Page")
            if callback: callback("cookie_settings", new_page, screenshot_only=True)
            new_page.close()

            # Your Privacy Choices
            landing_page.footer_privacy_choice.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_privacy_choice.click()
            new_page = new_page_info.value
            new_page.set_viewport_size({"width": 400, "height": 740})
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/privacy/your-privacy-choices.html"),
                                         timeout=60000)
            framework_logger.info("Your Privacy Choices hyperlink is working fine on Landing Page")
            if callback: callback("privacy_choices", new_page, screenshot_only=True)
            new_page.close()

            # Instant Ink Terms of Service
            landing_page.footer_iitos.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_iitos.click()
            new_page = new_page_info.value
            new_page.set_viewport_size({"width": 400, "height": 740})
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://instantink-stage1.hpconnectedstage.com/us/en/terms"),
                                         timeout=60000)
            framework_logger.info("Instant Ink Terms of Service hyperlink is working fine on Landing Page")
            if callback: callback("instant_ink_terms", new_page, screenshot_only=True)
            new_page.close()
        except Exception as e:
            framework_logger.error(f"ERROR in hyperlink method: {e}")

    @staticmethod
    def cookies_settings_oobe(page, callback=None):
        landing_page = LandingPage(page)
        try:
            # Cookie Settings link
            landing_page.footer_cookies.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_cookies.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/privacy/use-of-cookies.html"), timeout=60000)
            framework_logger.info("Cookie Settings hyperlink is working fine on Landing Page")

            new_page.locator(landing_page.elements.cookies_preference).scroll_into_view_if_needed(timeout=50000)
            new_page.locator(landing_page.elements.cookies_preference).wait_for(state='visible', timeout=50000)
            new_page.locator(landing_page.elements.cookies_preference).click()
            framework_logger.info("Cookie preference button clicked successfully")
            time.sleep(5)  # Wait for the cookie preference modal to appear
            cp_title = new_page.locator(landing_page.elements.cookies_preference_title).text_content()
            if cp_title == "Privacy Preference Center":
                framework_logger.info("Cookie Preferences title is displayed correctly")
            else:
                framework_logger.error(f"Cookie Preferences title is incorrect. Found: '{cp_title}'")
            new_page.locator(landing_page.elements.cookies_preference_close).wait_for(state='visible', timeout=50000)
            if callback: callback("cookie_preferences", new_page, screenshot_only=True)
            new_page.locator(landing_page.elements.cookies_preference_close).click()
            framework_logger.info("Cookie preference closed successfully")
            new_page.close()
        except Exception as e:
            framework_logger.error(f"ERROR in cookies_setting method: {e}")

    @staticmethod
    def cookies_settings_mobe(page, callback=None):
        landing_page = LandingPage(page)
        try:
            # Cookie Settings link
            landing_page.footer_cookies.wait_for(state='visible', timeout=50000)
            with page.context.expect_page(timeout=100000) as new_page_info:
                landing_page.footer_cookies.click()
            new_page = new_page_info.value
            new_page.set_viewport_size({"width": 400, "height": 740})
            new_page.wait_for_load_state("load", timeout=60000)
            expect(new_page).to_have_url(re.compile(r"https://www.hp.com/us-en/privacy/use-of-cookies.html"),
                                         timeout=60000)
            framework_logger.info("Cookie Settings hyperlink is working fine on Landing Page")

            new_page.locator(landing_page.elements.cookies_preference).scroll_into_view_if_needed(timeout=50000)
            new_page.locator(landing_page.elements.cookies_preference).wait_for(state='visible', timeout=50000)
            new_page.locator(landing_page.elements.cookies_preference).click()
            framework_logger.info("Cookie preference button clicked successfully")
            time.sleep(5)  # Wait for the cookie preference modal to appear
            cp_title = new_page.locator(landing_page.elements.cookies_preference_title).text_content()
            if cp_title == "Privacy Preference Center":
                framework_logger.info("Cookie Preferences title is displayed correctly")
            else:
                framework_logger.error(f"Cookie Preferences title is incorrect. Found: '{cp_title}'")
            new_page.locator(landing_page.elements.cookies_preference_close).wait_for(state='visible', timeout=50000)
            if callback: callback("cookie_preferences", new_page, screenshot_only=True)
            new_page.locator(landing_page.elements.cookies_preference_close).click()
            framework_logger.info("Cookie preference closed successfully")
            new_page.close()
        except Exception as e:
            framework_logger.error(f"ERROR in cookies_setting method: {e}")
        expect(raf_footnote).to_be_visible(timeout=30000)  

    @staticmethod
    def validate_faq_links(page):
        landing_page = LandingPage(page)
        original_url = page.url

        landing_page.faqs_section.scroll_into_view_if_needed()
        expect(landing_page.faqs_section).to_be_visible()

        faq_sections = [
            ("General", "section-general"),
            ("Monthly plans", "section-monthly-plans"),
            ("Yearly plans", "section-yearly-plans"),
            ("Pay As You Print plans", "section-pay-as-you-print-plans")
        ]

        for section_name, section_id in faq_sections:
            try:
                framework_logger.info(f"=== Validating {section_name} ===")
    
                if page.url != original_url:
                    page.goto(original_url)
                    page.wait_for_load_state("networkidle")                    
        
                section_tab = page.locator(f"[data-testid='accordion'] [aria-controls='{section_id}']")
                section_tab.click()
                page.wait_for_timeout(500)
            
                show_more = page.locator(f"#{section_id} [data-testid='show-more-button'], #{section_id} button:has-text('Show more')")
                if show_more.count() > 0:
                    show_more.first.click()
                    page.wait_for_timeout(500)

                questions = page.locator(f"#{section_id} button[aria-controls*='item-']")
                questions_count = questions.count()

                for i in range(questions_count):                   
                    questions = page.locator(f"#{section_id} button[aria-controls*='item-']")
                    if i >= questions.count():
                        break
                        
                    question = questions.nth(i)
                    question.click()
                    page.wait_for_timeout(300)

                    controls_id = question.get_attribute("aria-controls")
                    if not controls_id:
                        continue
                 
                    answer = page.locator(f"#{section_id} #{controls_id}")
                    expect(answer).to_be_visible(timeout=3000)
                    
                    links = answer.locator("a")
                    links_count = links.count()
            
                    for j in range(links_count):                        
                        answer = page.locator(f"#{section_id} #{controls_id}")
                        links = answer.locator("a")
                        
                        if j >= links.count():
                            break
                            
                        link = links.nth(j)
                        link_href = link.get_attribute("href")
                        
                        if not link_href or link_href.startswith(('mailto:', 'tel:')):
                            continue

                        try:
                            link.click()
                            page.wait_for_timeout(2000)                       
                            all_pages = page.context.pages
                            last_page = all_pages[-1]
                            last_page.bring_to_front()
                            last_page.wait_for_load_state("networkidle", timeout=35000)       
                            try:
                                expect(last_page.locator('[data-testid="branding-image-light-theme"]')).to_be_visible(timeout=3000)
                                framework_logger.info("HP text found on page")                                 
                                last_page.close()
                            except Exception:    
                                expect(last_page).to_have_url(re.compile(r'/terms'), timeout=30000)
                                framework_logger.info("Terms of service page found")                                  
                                last_page.close()                                      
                             
                                page.goto(original_url)
                                page.wait_for_load_state("domcontentloaded")                                
                                section_tab.click()
                                page.wait_for_timeout(300)
                                
                                if show_more.count() > 0:
                                    show_more.first.click()
                                    page.wait_for_timeout(300)
                                
                                questions = page.locator(f"#{section_id} button[aria-controls*='item-']")
                                if i < questions.count():
                                    questions.nth(i).click()
                                    page.wait_for_timeout(300)
                                    
                        except Exception as e:
                            framework_logger.warning(f"Failed link: {e}")
                            continue
                 
                    try:
                        questions = page.locator(f"#{section_id} button[aria-controls*='item-']")
                        if i < questions.count():
                            questions.nth(i).click()
                            page.wait_for_timeout(200)
                    except:
                        pass

            except Exception as e:
                framework_logger.warning(f"Failed section {section_name}: {e}")
                continue

        if page.url != original_url:
            page.goto(original_url)
            page.wait_for_load_state("domcontentloaded")

    @staticmethod
    def select_country(page, country="United States"):
        landing_page = LandingPage(page)
        landing_page.flag_icon.click()
        locale_map = load_locale_data()
        languages = locale_map[country]["languages"]
        short_code = locale_map[country]["code"].lower()      
        language = languages[0]  
         
        locale_code = f"{language}-{short_code}"
        
        page.locator(f"[data-testid='{locale_code}-selector']").click()

   
    @staticmethod
    def validate_new_emergency_banner(page, country="United States"):        
        landing_page = LandingPage(page)       
        banner_element = landing_page.emergency_banner.locator("..")
        banner_data = common.get_font_details(banner_element)
        detected_color = banner_data['background-color']
        
        framework_logger.info(f"Detected color: {detected_color}")
        
        # Country configurations
        country_configs = {
             'Finland': {
                'name': 'Red Minus Banner',
                'expected_color': 'rgb(190, 19, 19)',
                'expected_icon_path': 'M3.37957 11.5159C3.20996 11.5567 3.06121 11.7055 3.01585 11.8796C2.99862 11.9458 2.99862 12.0547 3.01585 12.1209C3.06121 12.2969 3.21087 12.4447 3.38411 12.4855C3.43581 12.4973 4.40452 12.4991 12 12.4991C19.5138 12.4991 20.5651 12.4973 20.6149 12.4855C20.7891 12.4447 20.9379 12.2978 20.9841 12.1218C21.0521 11.8597 20.8807 11.5776 20.6149 11.515C20.5306 11.4951 3.46211 11.496 3.37957 11.5159Z'
            },
            'Bulgaria': {
                'name': 'Orange Alert Banner',
                'expected_color': 'rgb(208, 103, 2)',
                'expected_icon_path': None
            },
            'Portugal': {
                'name': 'Green Done Banner',
                'expected_color': 'rgb(28, 122, 23)',
                'expected_icon_path': 'M20.3719 6.01731C20.312 6.03455 20.2685 6.0545 20.2204 6.08715C20.1959 6.10257 17.6617 8.63046 14.5877 11.7044L8.99772 17.2926L6.39273 14.6885C4.01541 12.3121 3.7814 12.0817 3.7297 12.0563C3.39137 11.8912 3.00226 12.1289 3.00226 12.5008C3.00226 12.5842 3.0204 12.6559 3.06303 12.7384C3.09387 12.7992 3.25985 12.967 5.86756 15.5765C7.39228 17.1021 8.66575 18.3701 8.6984 18.3946C8.85986 18.5171 9.05033 18.5316 9.24353 18.4355C9.28435 18.4146 10.2086 17.4949 15.0939 12.6105C19.0467 8.65858 20.9043 6.79464 20.9243 6.76289C20.9905 6.65223 21.015 6.50439 20.985 6.38557C20.9397 6.20688 20.8018 6.06357 20.6304 6.01822C20.566 6.00189 20.4299 6.00189 20.3719 6.01731Z'
            },   
            'Australia': {
                'name': 'Blue Done Banner',
                'expected_color': 'rgb(2, 122, 174)',
                'expected_icon_path': 'M20.3719 6.01731C20.312 6.03455 20.2685 6.0545 20.2204 6.08715C20.1959 6.10257 17.6617 8.63046 14.5877 11.7044L8.99772 17.2926L6.39273 14.6885C4.01541 12.3121 3.7814 12.0817 3.7297 12.0563C3.39137 11.8912 3.00226 12.1289 3.00226 12.5008C3.00226 12.5842 3.0204 12.6559 3.06303 12.7384C3.09387 12.7992 3.25985 12.967 5.86756 15.5765C7.39228 17.1021 8.66575 18.3701 8.6984 18.3946C8.85986 18.5171 9.05033 18.5316 9.24353 18.4355C9.28435 18.4146 10.2086 17.4949 15.0939 12.6105C19.0467 8.65858 20.9043 6.79464 20.9243 6.76289C20.9905 6.65223 21.015 6.50439 20.985 6.38557C20.9397 6.20688 20.8018 6.06357 20.6304 6.01822C20.566 6.00189 20.4299 6.00189 20.3719 6.01731Z'
            },
             'Norway': {
                'name': 'White Done Banner',
                'expected_color': 'rgb(255, 255, 255)',
                'expected_icon_path': 'M20.3719 6.01731C20.312 6.03455 20.2685 6.0545 20.2204 6.08715C20.1959 6.10257 17.6617 8.63046 14.5877 11.7044L8.99772 17.2926L6.39273 14.6885C4.01541 12.3121 3.7814 12.0817 3.7297 12.0563C3.39137 11.8912 3.00226 12.1289 3.00226 12.5008C3.00226 12.5842 3.0204 12.6559 3.06303 12.7384C3.09387 12.7992 3.25985 12.967 5.86756 15.5765C7.39228 17.1021 8.66575 18.3701 8.6984 18.3946C8.85986 18.5171 9.05033 18.5316 9.24353 18.4355C9.28435 18.4146 10.2086 17.4949 15.0939 12.6105C19.0467 8.65858 20.9043 6.79464 20.9243 6.76289C20.9905 6.65223 21.015 6.50439 20.985 6.38557C20.9397 6.20688 20.8018 6.06357 20.6304 6.01822C20.566 6.00189 20.4299 6.00189 20.3719 6.01731Z'
            },
            'Poland': {
                'name': 'Grey Done Banner',
                'expected_color': 'rgb(64, 64, 64)',
                'expected_icon_path': 'M20.3719 6.01731C20.312 6.03455 20.2685 6.0545 20.2204 6.08715C20.1959 6.10257 17.6617 8.63046 14.5877 11.7044L8.99772 17.2926L6.39273 14.6885C4.01541 12.3121 3.7814 12.0817 3.7297 12.0563C3.39137 11.8912 3.00226 12.1289 3.00226 12.5008C3.00226 12.5842 3.0204 12.6559 3.06303 12.7384C3.09387 12.7992 3.25985 12.967 5.86756 15.5765C7.39228 17.1021 8.66575 18.3701 8.6984 18.3946C8.85986 18.5171 9.05033 18.5316 9.24353 18.4355C9.28435 18.4146 10.2086 17.4949 15.0939 12.6105C19.0467 8.65858 20.9043 6.79464 20.9243 6.76289C20.9905 6.65223 21.015 6.50439 20.985 6.38557C20.9397 6.20688 20.8018 6.06357 20.6304 6.01822C20.566 6.00189 20.4299 6.00189 20.3719 6.01731Z'
            },
            'Estonia': {
                'name': 'Black Done Banner',
                'expected_color': 'rgb(33, 33, 33)',
                'expected_icon_path': 'M20.3719 6.01731C20.312 6.03455 20.2685 6.0545 20.2204 6.08715C20.1959 6.10257 17.6617 8.63046 14.5877 11.7044L8.99772 17.2926L6.39273 14.6885C4.01541 12.3121 3.7814 12.0817 3.7297 12.0563C3.39137 11.8912 3.00226 12.1289 3.00226 12.5008C3.00226 12.5842 3.0204 12.6559 3.06303 12.7384C3.09387 12.7992 3.25985 12.967 5.86756 15.5765C7.39228 17.1021 8.66575 18.3701 8.6984 18.3946C8.85986 18.5171 9.05033 18.5316 9.24353 18.4355C9.28435 18.4146 10.2086 17.4949 15.0939 12.6105C19.0467 8.65858 20.9043 6.79464 20.9243 6.76289C20.9905 6.65223 21.015 6.50439 20.985 6.38557C20.9397 6.20688 20.8018 6.06357 20.6304 6.01822C20.566 6.00189 20.4299 6.00189 20.3719 6.01731Z'
            },
        }
        
        # Get config for target country
        config = country_configs[country]
        framework_logger.info(f"Testing: {country} - {config['name']}")
        
        assert detected_color == config['expected_color'], f"Color mismatch: expected {config['expected_color']}, got {detected_color}"
        framework_logger.info(f"Color validated: {detected_color}")
        
        if config['expected_icon_path']:
            # Countries with SVG path (Portugal, Finland, United States)
            svg_path = landing_page.emergency_banner.locator('svg path').get_attribute('d')
            assert svg_path == config['expected_icon_path'], f"SVG path mismatch for {country}"
            framework_logger.info(f"SVG path validated for {country}")
        else:
            # Bulgaria - validate orange banner icon exists
            orange_icon = page.locator('[class="orangeBannerIcon"]')
            assert orange_icon.count() > 0, f"Orange banner icon not found for {country}"
            framework_logger.info(f"Orange banner icon found for {country}")
        
        framework_logger.info(f"{config['name']} validation successful")