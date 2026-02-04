# test_flows/EnrollNonFlipOOBE/enroll_non_flip_oobe.py

import os
import time
import random
import string
import base64
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from core.settings import GlobalState
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def enroll_non_flip_oobe(stage_callback):
    framework_logger.info("=== EnrollNonFlipOOBE flow started ===")
    # 1) Bootstrap globals
    common.setup()

    os.makedirs(TEMP_DIR, exist_ok=True)

    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # 2) HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
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
            page = common.create_hpid(page)
            time.sleep(5)
            framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
            page = common.onboard_hpid_to_ucde(page)
        finally:
            context.close()
            browser.close()

    # 3) Create virtual printer
    entity_id, model_number, device_uuid, cloud_id, postcard, postcard_encoded, fingerprint, fingerprint_encoded = common.create_virtual_printer()
    framework_logger.info(f"Printer details: serialnumber={entity_id}, model={model_number}, uuid={device_uuid}, cloud_id={cloud_id}, postcard={postcard_encoded[:8]}..., fingerprint={fingerprint_encoded[:8]}...")

    # 4) Launch Playwright and drive Instant Ink OOBE flow
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
        framework_logger.info(f"Launching Playwright browser with headless={GlobalState.headless}, locale={GlobalState.language_code}")
        page = context.new_page()
        try:
            page.set_viewport_size({"width": GlobalState.target_width, "height": GlobalState.target_height})
            page.goto(common._oss_url)
            page.wait_for_load_state("networkidle"); page.wait_for_load_state("load")
            page.click("//a[normalize-space(text())='Dev']")
            page.click("#oss-hpid-login")
            page.click("#sign-in")
            page.fill("#username", tenant_email)
            page.click("#user-name-form-submit")
            page.fill("#password", "Test@123")
            page.click("#sign-in")
            page.click("#novelli")
            time.sleep(3)
            page.wait_for_selector("#serial-number").fill(entity_id)
            page.wait_for_selector("#sku").fill(model_number)
            page.wait_for_selector("#uuid").fill(device_uuid)
            page.fill("//input[@ng-model='device.cloudID']", base64.b64decode(postcard_encoded).decode('utf-8'))
            page.fill("//input[@id='cdm-printer-fingerprint']", base64.b64decode(fingerprint_encoded).decode('utf-8'))
            page.locator("#registration-state").select_option("registered")
            page.locator("#usage-tracking-consent").select_option("optedin")
            page.locator("#language-config").select_option("completed")
            page.locator("#country-config").select_option("completed")
            page.locator("#load-main-tray").select_option("completed")
            page.locator("#insert-ink").select_option("completed")
            page.locator("#calibration").select_option("completed")
            page.get_by_role('link', name='App/Post-OOBE/Agreements/').click()
            page.get_by_label('App Type').select_option(getattr(GlobalState, 'ossplatform', 'GothamDesktop'))
            page.click("#start-flow-button")
            # page.click("#actions-button")
            page.wait_for_load_state("networkidle"); page.wait_for_load_state("load")
            page.click("#consent-accept-all-button")
            if getattr(GlobalState, "biz_model", "Flex") in ["Flex"]:
                page.wait_for_load_state("networkidle"); page.wait_for_load_state("load")
                page.get_by_role("button", name="Continue").click()
                page.wait_for_selector("#btn-ok").click()
            page.wait_for_function("document.URL.includes('instantink')", timeout=180000)
            page.wait_for_selector("[data-testid='next-button']:enabled", timeout=180000).click()

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
            framework_logger.info(f"Card Payment Method for this flow: {common._card_payment_gateway}")
            if common._card_payment_gateway == "PGS":
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
            if GlobalState.ossplatform in ["GothamDesktop", "GothamMac", "HpxWindows", "HpxMac"]:
                page.wait_for_load_state("networkidle"); page.wait_for_load_state("load")
                page.click("[data-testid='focused-paper-addon-section'] button:has-text('Skip Paper')", timeout=180000)
            page.wait_for_selector("[data-testid='oobe-enroll-continue-button']:enabled", timeout=180000).click()
            page.wait_for_selector("[data-testid='terms-agreement']", state="visible").click(force=True)
            page.wait_for_selector("[data-testid='redeem-button']:enabled").click()
            page.wait_for_selector("[data-testid='continue-button']:enabled", timeout=120000).click()
            page.wait_for_function("document.URL.includes('spinner') || document.URL.includes('firmware')", timeout=60000)
            page.close()
            framework_logger.info("OSS Enrollment completed successfully")
        except Exception as e:
            framework_logger.error(f"An error occurred during the OSS Enrollment: {e}\n{traceback.format_exc()}")
        finally:
            common.send_rtp_devicestatus(entity_id, cloud_id, device_uuid)
            context.close()
            browser.close()