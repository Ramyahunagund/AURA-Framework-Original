from core.playwright_manager import PlaywrightManager
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage
import traceback
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
import re

def landing_page(stage_callback):
    framework_logger.info("=== Landing page flow started ===")
    common.setup()
    timeout_ms = 120000

    with PlaywrightManager() as page:
        privacy_banner_page = PrivacyBannerPage(page)
        landing_page = LandingPage(page)
        try:
            url = common._instantink_url + f"/{GlobalState.country_code.lower()}/{GlobalState.language.lower()}"
            page.goto(url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()

            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)
            expect(landing_page.flag_icon).to_be_visible(timeout=timeout_ms)
            expect(landing_page.sign_in_button).to_be_visible(timeout=timeout_ms)
            expect(landing_page.sign_up_header_button).to_be_visible(timeout=timeout_ms)
            expect(landing_page.get_started_button).to_be_visible(timeout=timeout_ms)
            expect(landing_page.virtual_agent).to_be_visible(timeout=timeout_ms)
            expect(landing_page.support_phone_number).to_be_visible(timeout=timeout_ms)
            expect(landing_page.how_it_works).to_be_visible(timeout=timeout_ms)
            expect(landing_page.how_it_works_never_run_out).to_be_visible(timeout=timeout_ms)
            expect(landing_page.how_it_works_save_time_money).to_be_visible(timeout=timeout_ms)
            expect(landing_page.when_we_save).to_be_visible(timeout=timeout_ms)
            expect(landing_page.ink_plans_tab).to_be_visible(timeout=timeout_ms)
            expect(landing_page.faqs_section).to_be_visible(timeout=timeout_ms)
            expect(landing_page.go_green_section).to_be_visible(timeout=timeout_ms)
            expect(landing_page.go_green_learn_more).to_be_visible(timeout=timeout_ms)
            expect(landing_page.footnotes_section).to_be_visible(timeout=timeout_ms)
            expect(landing_page.footer_section).to_be_visible(timeout=timeout_ms)
            expect(landing_page.footer_hp_link).to_be_visible(timeout=timeout_ms)
            expect(landing_page.footer_privacy_statement).to_be_visible(timeout=timeout_ms)
            expect(landing_page.footer_terms_of_use).to_be_visible(timeout=timeout_ms)
            expect(landing_page.footer_copyright).to_be_visible(timeout=timeout_ms)
            expectedPlans = [10, 50, 100, 300, 700]
            plans_elements = landing_page.ink_plans_tab_content.element_handles()
            plan_count = len(plans_elements)
            assert plan_count==len(expectedPlans), f"Expected {len(expectedPlans)} plans, but found {plan_count}."
            for i in range(plan_count):
                plan_text = landing_page.ink_plans_tab_pages(i).text_content()
                plan_number = int(re.search(r'\d+', plan_text).group())
                assert plan_number in expectedPlans, f"Plan {plan_number} not found in expected plans {expectedPlans}."

            framework_logger.info("=== Landing Page flow ended ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Landing Page test: {e}\n{traceback.format_exc()}")
            raise e