from pages.hpid_page import HPIDPage
import test_flows_common.test_flows_common as common
from core.settings import GlobalState, framework_logger

class HPIDHelper:

    @staticmethod
    def dismiss_select_country(page):
        hpid_page = HPIDPage(page)
        try:
            hpid_page.country_selector_button.first.click()
        except Exception as _e:
            pass
       
    @staticmethod
    def sign_in(page, email, password):
        hpid_page = HPIDPage(page)
        hpid_page.username.fill(email)
        hpid_page.user_name_form_submit.click()
        hpid_page.password.fill(password)
        hpid_page.sign_in.click()

    @staticmethod
    def complete_sign_in(page, email, password):
        HPIDHelper.dismiss_select_country(page)
        hpid_page = HPIDPage(page)
        hpid_page.wait.sign_in_option(timeout=20000).click()
        HPIDHelper.sign_in(page, email, password)

    @staticmethod
    def sign_up(page, email, password):
        hpid_page = HPIDPage(page)
        hpid_page.firstName.fill("InstantInk")
        hpid_page.lastName.fill("User")
        hpid_page.email.fill(email)
        hpid_page.password.fill(password)
        hpid_page.market.click()
        hpid_page.create_account_button.click()

    @staticmethod
    def confirm_account_code(page, email): 
        hpid_page = HPIDPage(page)
        hpid_page.wait.submit_code(timeout=20000)
        retries = 3
        wait_time = 10
        verification_code = None
        for attempt in range(retries):
            try:
                page.wait_for_timeout(wait_time * 1000)
                verification_code = common.fetch_verification_code(email)
                if verification_code:
                    hpid_page.code.fill(verification_code)
                    hpid_page.submit_code.click()
                    framework_logger.info(
                        f"{email} user Onboarded to {GlobalState.stack.upper()}/{GlobalState.country_code}_{GlobalState.language_code}.")
                    break
            except Exception as ex:
                framework_logger.warning(f"Attempt {attempt+1}/{retries}: Verification code not found ({ex}), retrying…")
        if not verification_code:
            framework_logger.error("Verification failed after all retries.")
            return
        page.wait_for_load_state("load")

    @staticmethod
    def complete_sign_up(page, tenant_email):
        HPIDHelper.dismiss_select_country(page)
        hpid_page = HPIDPage(page)
        hpid_page.wait.create_account_button_data(timeout=20000).click()
        HPIDHelper.sign_up(page, tenant_email, common.DEFAULT_PASSWORD)
        HPIDHelper.confirm_account_code(page, tenant_email)       
