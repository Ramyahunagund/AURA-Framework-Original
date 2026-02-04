# test_flows/CreateV3Account/create_v3_account.py

import os
import time
import base64
from playwright.sync_api import sync_playwright
from core.settings import GlobalState
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def create_v3_account(stage_callback) -> None:
    framework_logger.info("=== CreateV3Account flow started ===")
    # 1) Bootstrap globals
    common.set_globals({
        "stack": GlobalState.stack,
        "profile": GlobalState.printer_profile,
        "derivative_model":             getattr(GlobalState, "derivative_model", None),
        "biz_model":                    getattr(GlobalState, "biz_model", "Flex"),
        "supplyvariant":                getattr(GlobalState, "supplyvariant", None),
        "tenant_country":               GlobalState.country,
        "tenant_country_short":         GlobalState.country_code,
        "tenant_country_language_code": GlobalState.language_code,
        "tenant_address":               GlobalState.address_payload,
        "headless":                     GlobalState.headless,
        "card_payment_method":          getattr(GlobalState, "card_payment_method", None),
    })

    os.makedirs(TEMP_DIR, exist_ok=True)

    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    with sync_playwright() as p:
        launch_args = {"headless": GlobalState.headless}
        context_args = {
            "locale": f"{GlobalState.language_code}",
            "viewport": {"width": GlobalState.target_width, "height": GlobalState.target_height}
        }
        if common.PROXY_URL:
            launch_args["proxy"] = {"server": common.PROXY_URL}
            context_args["proxy"] = {"server": common.PROXY_URL}

        browser = p.chromium.launch(**launch_args)
        context = browser.new_context(**context_args)
        page = context.new_page()
        try:
            # Step 1: Load Instant Ink Landing page and accept cookies
            page.goto(common._instantink_url)
            page.wait_for_load_state("load")
            page.wait_for_selector("#onetrust-accept-btn-handler").click()
            if page.is_visible("[data-testid='emergency_banner_dismiss']"):
                page.click("[data-testid='emergency_banner_dismiss']")

            if page.is_visible("a.legacyBanner-module_closeButton__RmbK8"):
                page.click("a.legacyBanner-module_closeButton__RmbK8")

            time.sleep(10)

            stage_callback("landing_page", page)

            # Step 2: Sign Up
            page.wait_for_selector("[data-testid='header-sign-up-button']").click()
            page.wait_for_load_state("load")
            time.sleep(5)
            if page.is_visible("[data-testid='country-selector-modal']", timeout=2000):
                page.wait_for_selector("[data-testid='country-selector-modal'] button:has-text('Cancel')").click()
            page.wait_for_selector("[data-testid='create-account-button']").click()
            page.fill("#firstName", "InstantInk")
            page.fill("#lastName", "User")
            page.fill("#email", tenant_email)
            page.fill("#password", "Test@123")
            page.click("#market")
            page.click("#sign-up-submit")
            page.wait_for_selector("#submit-code", timeout=20000)
            retries = 3
            wait_time = 10
            verification_code = None
            for attempt in range(retries):
                try:
                    page.wait_for_timeout(wait_time * 1000)
                    verification_code = common.fetch_verification_code(tenant_email)
                    if verification_code:
                        page.fill("#code", verification_code)
                        page.click("#submit-code")
                        framework_logger.info(
                            f"User Onboarded to {GlobalState.stack.upper()}/{GlobalState.country_code}_{GlobalState.language_code} is '{tenant_email}' with Password 'Test@123'")
                        break
                except Exception as ex:
                    framework_logger.warning(f"Attempt {attempt+1}/{retries}: Verification code not found ({ex}), retrying…")
            if not verification_code:
                framework_logger.error("Verification failed after all retries.")
                return
            page.wait_for_load_state("load")

            # Step 3: Plan selection 
            if GlobalState.country in ["United States", "France", "Germany", "United Kingdom"]:
                page.wait_for_selector("[data-testid='select-plan-ink-only']:enabled", timeout=180000)
                stage_callback("plan_selection", page)
                page.locator("[data-testid='select-plan-ink-only']").click()
                # stage_callback("plan_selection", page, sub_context="plan_selected")

            # Step 4: Continue after plan
            page.wait_for_selector("[data-testid='btn-continue']", timeout=120000).click()

            for _ in range(int(30 / 5)):
                if page.is_visible("[data-testid='choose-HP-checkout']") and page.is_enabled("[data-testid='choose-HP-checkout']"):
                    page.click("[data-testid='choose-HP-checkout']")
                    break
                time.sleep(5)

            # Step 5: Add Shipping
            page.wait_for_selector("[data-testid='add-shipping']").click()
            page.wait_for_selector("[data-testid='street1']", timeout=120000).fill(GlobalState.address_payload.get("street1", ""))
            page.wait_for_selector("[data-testid='street2']").fill(GlobalState.address_payload.get("street2", ""))
            if GlobalState.country not in ["Hong Kong", "Singapore"]:
                page.wait_for_selector("[data-testid='city']").fill(GlobalState.address_payload.get("city", ""))
            if GlobalState.country not in ["Austria", "Belgium", "Denmark", "Finland", "France", "Germany", "Luxembourg", "Netherlands", "New Zealand", "Norway", "Portugal", "Puerto Rico", "Singapore", "Sweden", "Switzerland"]:
                page.wait_for_selector("#state").click()
                page.get_by_role("option", name=GlobalState.address_payload.get("fullState", GlobalState.address_payload.get(f"fullState_{GlobalState.language_code}"))).click()
            if GlobalState.country not in ["Hong Kong"]:
                page.wait_for_selector("[data-testid='zip-code']").fill(GlobalState.address_payload.get("zipCode", ""))
            page.wait_for_selector("[data-testid='phoneNumberSmall']").fill(GlobalState.address_payload.get("phoneNumber1", ""))
            page.wait_for_selector("[data-testid='save-button']").click()
            for _ in range(int(15 / 5)):
                if page.is_visible("div[data-testid='suggested-address-modal']") and page.is_visible("button[data-testid='ship-to-address-button']") and page.is_enabled("button[data-testid='ship-to-address-button']"):
                    page.click("button[data-testid='ship-to-address-button']")
                    break
                time.sleep(5)
            # Step 6: Add Billing
            page.wait_for_selector("[data-testid='add-billing']:enabled").click()
            framework_logger.info(f"Card Payment Method for this flow: {common._card_payment_method}")
            if common._card_payment_method == "PGS":
                if GlobalState.country in ["Italy"]:
                    page.locator("#tax-id").wait_for(state="visible")
                    page.fill("#tax-id", "MRTMTT91D08F205J")
                else:
                    page.wait_for_selector("[data-testid='use-shipping-address'] input:checked", timeout=120000)
                page.wait_for_selector("[data-testid='continue-button']").click()
                page.frame_locator("#pgs-iframe").locator("#txtCardNumber").wait_for(state="visible")
                page.frame_locator("#pgs-iframe").locator("#txtCardNumber").fill("5555555555554444")
                page.frame_locator("#pgs-iframe").locator("#drpExpMonth").wait_for(state="visible")
                page.frame_locator("#pgs-iframe").locator("#drpExpMonth").select_option("12")
                page.frame_locator("#pgs-iframe").locator("#drpExpYear").wait_for(state="visible")
                page.frame_locator("#pgs-iframe").locator("#drpExpYear").select_option("2034")
                page.frame_locator("#pgs-iframe").locator("#txtCVV").wait_for(state="visible")
                page.frame_locator("#pgs-iframe").locator("#txtCVV").type("123")
                time.sleep(5)
                if page.frame_locator("#pgs-iframe").locator("#btn_pgs_card_add").count() > 0:
                    page.frame_locator("#pgs-iframe").locator("#btn_pgs_card_add").click()
                else:
                    page.frame_locator("#pgs-iframe").locator("#btn_pgs_3dcard_add").click()
                    challenge_frame = page.frame_locator("#pgs-iframe").frame_locator("#challengeFrame")
                    challenge_frame.locator("#selectAuthResult").wait_for(state="visible")
                    challenge_frame.locator("#selectAuthResult").select_option("AUTHENTICATED")
                    challenge_frame.locator("#acssubmit").wait_for(state="visible")
                    challenge_frame.locator("#acssubmit").click()
            else:
                page.frame_locator("#cart-iframe").locator("button.continue-to-billing").wait_for(state="visible")
                page.frame_locator("#cart-iframe").locator("button.continue-to-billing").click()
                page.frame_locator("#cart-iframe").locator("button.continue-to-payment").wait_for(state="visible")
                page.frame_locator("#cart-iframe").locator("button.continue-to-payment").click()
                page.frame_locator("#cart-iframe").locator("input[name='name']").wait_for(state="attached", timeout=3000)
                if page.frame_locator("#cart-iframe").locator("input[name='name']").is_visible():
                    page.frame_locator("#cart-iframe").locator("input[name='name']").fill("John Doe")
                else:
                    page.frame_locator("#cart-iframe").locator("input[name='firstName']").wait_for(state="visible")
                    page.frame_locator("#cart-iframe").locator("input[name='firstName']").type("John")
                    page.keyboard.press("Tab")
                    page.frame_locator("#cart-iframe").locator("input[name='lastName']").wait_for(state="visible")
                    page.frame_locator("#cart-iframe").locator("input[name='lastName']").type("Doe")
                page.keyboard.press("Tab")
                page.frame_locator("#cart-iframe").locator("input[name='card']").wait_for(state="visible")
                page.frame_locator("#cart-iframe").locator("input[name='card']").type("5555555555554444")
                page.keyboard.press("Tab")
                page.frame_locator("#cart-iframe").locator("input[name='date']").type("12/34")
                page.keyboard.press("Tab")
                page.frame_locator("#cart-iframe").locator("input[name='cvv']").type("123")
                time.sleep(5)
                page.frame_locator("#cart-iframe").locator("button.place-order").wait_for(state="visible")
                page.frame_locator("#cart-iframe").locator("button.place-order").click()

            # Step 7: Preenrollment Continue and Connect Later
            page.wait_for_selector("[data-testid='preenroll-continue-button']:enabled", timeout=90000)

            stage_callback("enroll_summary_page", page)

            page.wait_for_selector("[data-testid='preenroll-continue-button']").click()
            page.wait_for_load_state("load")
            page.wait_for_selector("[data-testid='connect-later-button']", timeout=30000)

            stage_callback("connect_later_and_back", page)
            
            page.click("[data-testid='connect-later-button']")
            page.wait_for_selector("[data-testid='go-back-button']").click()
            framework_logger.info("V3 enrollment completed successfully")

        except Exception as e:
            framework_logger.error(f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
        finally:
            context.close()
            browser.close()

    framework_logger.info("=== CreateV3Account flow completed ===")
