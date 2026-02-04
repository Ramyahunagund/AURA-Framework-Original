from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class LandingPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.sign_in_button = "[data-testid='sign-in-button']"
        self.elements.sign_up_header_button = "[data-testid='header-sign-up-button']"
        self.elements.header_logo = "[class^='globalHeader-module_newIiLogo']"
        self.elements.header_plan = "[class^='globalHeader-module_plans']"
        self.elements.flag_icon = "[class*='flag-icon']"
        self.elements.hero_section = "#intro"
        self.elements.get_started_button = "[data-testid='origami-intro-enroll-starter-kit-button']"
        self.elements.virtual_agent = "[data-testid='virtual-agent-button']"
        self.elements.virtual_agent_fixed_button = "[data-testid='virtual-agent-fixed-button']"
        self.elements.support_section = "#support"
        self.elements.support_phone_number = "[data-testid='support-phone-link']"
        self.elements.how_it_works = "[data-testid='how-it-works-title-v2']"
        self.elements.how_it_works = '[class="v4HowItWorks"]'
        self.elements.how_it_works_never_run_out = '[class="v4HowItWorks"] .steps:has(.stepsImage.never_run_out) .titleSmall'
        self.elements.how_it_works_save_time_money = '[class="v4HowItWorks"] .steps:has(.stepsImage.save_time_and_money) .titleSmall'
        self.elements.plan_banner = "#plan-banner"
        self.elements.plan_section = "#plan"
        self.elements.ink_plans_tab = "[data-testid='i_ink-plans-tab']"
        self.elements.landing_page_plans_container = "#plan-section"
        self.elements.faqs_section = "#faqs-section"
        self.elements.show_more_button = "[data-testid='show-more-button']"
        self.elements.go_green_section = "#go-green"
        self.elements.go_green_learn_more = "[data-testid='learn-more-go-green']"
        self.elements.raf_section = "#raf"
        self.elements.raf_learn_more = "[data-testid='learn-more-button']"
        self.elements.footnotes_section = "#disclaimers"
        self.elements.footer_section = "[class='v3-global-footer']"
        self.elements.footer_hp_link = "[data-testid='hpDotCom']"
        self.elements.footer_privacy_statement = "[data-testid='privacyStatement']"
        self.elements.footer_terms_of_use = "[data-testid='termsOfUse']"
        self.elements.footer_cookies = "[data-testid='cookieSettings']"
        self.elements.footer_copyright = "[data-testid='footer-copyright']"
        self.elements.footer_privacy_choice = "[data-testid='privacyChoices']"
        self.elements.footer_iitos = "[data-testid='iiTOS']"
        self.elements.terms_of_service_page = "[class^='page-content terms']"
        self.elements.how_it_works_plan = "#how-it-works > div > div.stepsContainer > div:nth-child(2) > div.stepsContent > div.titleSmall"
        self.elements.how_it_works_ship = "#how-it-works > div > div.stepsContainer > div:nth-child(4) > div.stepsContent > div.titleSmall"
        self.elements.how_it_works_flexibility = "#how-it-works > div > div.stepsContainer > div:nth-child(6) > div.stepsContent > div.titleSmall"
        self.elements.need_more_plan_info = "[data-testid='more-plans-info']"
        self.elements.plans_info_modal = "[class^='planSection-module_infoModal']"
        self.elements.plans_info_modal_signin_link = "//div/p[4]/a"
        self.elements.modal_close = "[class^='vn-modal__close']"
        self.elements.check_printer_eligibility_link = "[data-linkid='check_device_eligibility']"
        self.elements.how_it_works_never_run_out = "#how-it-works > div > div.stepsContainer > div:nth-child(1) > div.steps-image-container-v4 > div"
        self.elements.how_it_works_save = "#how-it-works > div > div.stepsContainer > div:nth-child(3) > div.steps-image-container-v4 > div"
        self.elements.when_we_save = "[data-testid='when-we-save-title'], [class^='saveSection-module_title']"
        self.elements.ink_plans_tab_content = "[data-testid='landing-page-plans-container'] [data-testid^='lp-plans-plan-card-'] [class^='styles__PagesContainer-']"
        self.elements.eligibility_search_modal = "[data-testid='eligibile-checker-title']"
        self.elements.plan_sign_up_now_button = "[data-testid='plans-sign-up-button']"
        self.elements.raf_banner = '[class^="legacyBanner-module_bannerMessage"]'
        self.elements.raf_footnote = '[data-testid="refer-a-friend-footnote"]'
        self.elements.ink_plans_card_right_arrow = '#ink [data-testid="landing-page-plans-arrow-button-right"] svg'
        self.elements.ink_plans_card_left_arrow = '#ink [data-testid="landing-page-plans-arrow-button-left"] svg'
        self.elements.instant_ink_for_business_section = "[data-testid='instant-ink-for-business-section']"
        self.elements.paper_delivery_section = "#paper"
        self.elements.paper_delivery_title = "[class^='saveMorePaper-module_heading']"
        self.elements.paper_delivery_description = "[class^='saveMorePaper-module_description']"
        self.elements.paper_delivery_image = "[class^='saveMorePaper-module_imageWrapper']"
        self.elements.paper_delivery_learn_more_link = "[data-testid='learn-more-about-pricing']"
        self.elements.paper_delivery_superscript = "[class^='saveMorePaper-module_label'] sup"
        self.elements.combined_savings_footnote = "[data-testid='combined-savings-footnote']"
        # Header elements
        self.elements.header_logo = "[class^='globalHeader-module_newIiLogo']"
        self.elements.header_section = "[id='consumerGlobalHeader']"
        self.elements.country_picker = "[data-testid='country-picker']"
        self.elements.sign_in_button = "[data-testid='sign-in-button']"
        self.elements.manage_account_button = "[data-testid='manage-account-button']"
        self.elements.mobile_sign_in_link = "[data-testid='sign-in-menu-link']"
        self.elements.mobile_sign_up_link = "[data-testid='sign-up-menu-link']"
        self.elements.mobile_how_it_works_link = "[data-testid='how-it-works-menu-link']"
        self.elements.mobile_instant_paper_link = "[data-testid='paper-add-on-menu-link']"
        self.elements.mobile_plans_link = "[data-testid='plans-menu-link']"
        self.elements.mobile_faqs_link = "[data-testid='faqs-menu-link']"
        self.elements.sign_up_header_button = "[data-testid='header-sign-up-button']"
        self.elements.hamburger_menu = "[class^='globalHeader-module_menu']"
        # Country selector elements
        self.elements.country_selector_modal = "[class='supported-countries']"
        self.elements.country_selector_title = "[class='supported-countries']"
        self.elements.country_selector_items = "[class='country-link']"

         # FAQ section elements 
        self.elements.faq_general_tab = "[data-testid='accordion'] [aria-controls='section-general']"
        self.elements.faq_monthly_plans_tab = "[data-testid='accordion'] [aria-controls='section-monthly-plans']"
        self.elements.faq_yearly_plans_tab = "[data-testid='accordion'] [aria-controls='section-yearly-plans']"
        self.elements.faq_pay_as_you_print_tab = "[data-testid='accordion'] [aria-controls='section-pay-as-you-print-plans']"

         # Alert banner selectors
        self.elements.alert_banner = '#banner [class="v3-banner"]'
        self.elements.alert_banner_container = '[class^="legacyBanner-module_banner"]'
        self.elements.alert_banner_icon = '[class^="legacyBanner-module_bannerIcon"]'
        self.elements.alert_banner_content = '[class^="legacyBanner-module_bannerContent"]'
        self.elements.alert_banner_link = '[class^="legacyBanner-module_bannerLink"]'
        self.elements.alert_banner_close = '[class^="legacyBanner-module_closeButton"]'
        self.elements.emergency_banner_header = '[data-testid="banner-header"]'
        # Alert Banner Interactive Elements
        self.elements.alert_banner_title = '[data-testid="banner-heading"]'
        self.elements.alert_banner_subtitle = '[data-testid="banner-subtitle"]'
        self.elements.alert_banner_body = '[data-testid="banner-content"]'
        self.elements.alert_banner_hide_link = '[data-testid="emergency_banner_collapse_expand"]'
        self.elements.alert_banner_show_link = '[data-testid="emergency_banner_collapse_expand"]'
        self.elements.alert_banner_dismiss_button = '[data-testid="emergency_banner_dismiss"]'
        # Enrolment kit Banner Interactive Elements
        self.elements.ek_banner = "[id='enrollment-kit']"
        self.elements.ek_banner_content = "#enrollment-kit [class*='banners-module_bannerContentContainer']"
        self.elements.ek_message_container = "#enrollment-kit [class*='banners-module_bannerMessageContainer']"
        self.elements.ek_banner_message = "#enrollment-kit [data-testid='origami-banner-message']"
        self.elements.ek_signup_link = "[data-testid='enrollment-kit-banner']"

    
    def ink_plans_tab_pages(self, card):
        return self.page.locator(f"[data-testid='landing-page-plans-container'] [data-testid^='lp-plans-plan-card-{card}'] [class^='styles__PagesContainer-']")
    
    def ink_plans_card(self, card):
        return self.page.locator(f"[data-testid='landing-page-plans-container'] [data-testid='lp-plans-plan-card-{card}'] [class^='styles__PagesContainer-']")

    @property
    def flag_icon(self):
        return self.page.locator(self.elements.flag_icon).first

    
    @property
    def go_green_section(self):
        return self.page.locator(self.elements.go_green_section).first