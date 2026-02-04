# test_flows/CreateIISubscription/create_ii_subscription.py

import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState
from core.settings import framework_logger
from helper.dashboard_helper import DashboardHelper
from helper.gemini_ra_helper import GeminiRAHelper
from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from pages.overview_page import OverviewPage
from pages.thank_you_page import ThankYouPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def apply_code_for_the_printer_without_any_benefits(stage_callback):
    framework_logger.info("=== C52081684 - Apply code for the printer without any benefits flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # 1) HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer and add address
        common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        try:
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            price = None
            try:
                price = EnrollmentHelper.get_total_price_by_plan_card(page)
            except Exception:
                framework_logger.info(f"Failed to get price from plan card")

            # billing
            EnrollmentHelper.add_billing(page, plan_value=price)
            framework_logger.info(f"Billing added")
            offer = common.get_offer(GlobalState.country_code)
            identifier = offer.get("identifier")
            if not identifier:
                raise ValueError(f"No identifier found for region: {GlobalState.country_code}")

            # Apply Ek code
            ek_code = common.offer_request(identifier)
            months = offer.get("months")
            EnrollmentHelper.apply_and_validate_ek_code(page, ek_code, months)
            framework_logger.info(f"Apply Ek code successfully: {ek_code}")
            # Validate redeemed months and credits
            EnrollmentHelper.validate_benefits_header(page, months)
            framework_logger.info(f"Validated benefits header with {months} months")

            # Click continue button on confirmation page
            confirmation_page = ConfirmationPage(page)
            confirmation_page.wait.continue_enrollment_button().click()
            framework_logger.info(f"Clicked continue button on confirmation page ")
            
            # Sees 700 waiver pages on disclaimer modal
            EnrollmentHelper.verify_waiver_pages_on_disclaimer_modal(page, "700")
            framework_logger.info(f"Verified 700 waiver modal")

            # Click terms of service checkbox option and confirm button
            confirmation_page = ConfirmationPage(page)
            confirmation_page.terms_agreement_checkbox.wait_for(state="visible", timeout=60000)
            confirmation_page.terms_agreement_checkbox.check(force=True)
            confirmation_page.enroll_button.click()
            thank_you_page = ThankYouPage(page)
            thank_you_page.continue_button.wait_for(state="visible", timeout=60000)
            framework_logger.info(f"Click terms of service checkbox option and confirm button")

            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)
            GeminiRAHelper.subscription_to_subscribed(page)

            DashboardHelper.first_access(page, tenant_email)
            framework_logger.info("Dashboard first access completed successfully")
            overview_page = OverviewPage(page)
            body_text = overview_page.status_card_body.inner_text()
            assert "700" not in body_text, f"Text '700' found in body: {body_text}"
            framework_logger.info("Verified that 700 pages are not displayed on the status card")

            framework_logger.info("=== C52081684 - Apply code for the printer without any benefits flow finished ===")   
            return tenant_email
        except Exception as e:
            framework_logger.error(f"An error occurred during the enrollment: {e}\n{traceback.format_exc()}")
            raise e
