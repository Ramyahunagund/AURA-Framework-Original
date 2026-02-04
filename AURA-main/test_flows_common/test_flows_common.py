#test_flows_common.py

import os
import time
from datetime import datetime
import string
import random
import traceback
import uuid
import base64
import json
import requests
import struct
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from playwright.sync_api import expect
from tenacity import retry, stop_after_attempt, wait_fixed
from core.settings import GlobalState, framework_logger
from core.utils import load_json_file

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))
DEFAULT_FIRSTNAME   = "InstantInk"
DEFAULT_LASTNAME    = "User"
DEFAULT_PASSWORD    = "Test@123"
REDIRECT_URI        = "http://localhost:8080/test"
PROXY_URL           = os.getenv("HTTP_PROXY")
GMAIL_SCOPE         = ["https://www.googleapis.com/auth/gmail.readonly"]
GMAIL_CLIENT_ID     = os.getenv("GMAIL_CLIENT_ID")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
GMAIL_REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN")
STRATUS_CLIENT_ID   = os.getenv("STRATUS_CLIENT_ID")
UCDE_CLIENT_ID      = os.getenv("UCDE_CLIENT_ID")
GEMINI_CLIENT_ID    = os.getenv("GEMINI_CLIENT_ID")

# MongoDB and storage configuration
MONGODB_URI       = os.getenv("MONGODB_URI")
MONGODB_DB_NAME   = os.getenv("MONGODB_DB_NAME")
S3_ENDPOINT       = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY     = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY     = os.getenv("S3_SECRET_KEY")
S3_BUCKET         = os.getenv("S3_BUCKET")
S3_REGION         = os.getenv("S3_REGION")
S3_SECURE         = os.getenv("S3_SECURE", "false").lower() == "true"

framework_logger.debug(f"Loaded STRATUS_CLIENT_ID={STRATUS_CLIENT_ID[:8]}...")
framework_logger.debug(f"Loaded UCDE_CLIENT_ID={UCDE_CLIENT_ID[:8]}...")
framework_logger.debug(f"Loaded GEMINI_CLIENT_ID={GEMINI_CLIENT_ID[:8]}...")
session = requests.Session()
session.verify = False 
session.proxies = {"http": PROXY_URL, "https": PROXY_URL}
framework_logger.debug(f"Configured HTTP_PROXY={PROXY_URL}")

# Common Rails admin configuration for all stacks
RAILS_ADMIN_CONFIG = {
    "gemini_rails_admin_endpoint": "/admins/sign_in?automation=1",
    "agena_cps_and_fulfillment_rails_admin_endpoint": "/admin_user/sign_in?automation=1",
    "fetch_tenant_endpoint": "/admin/fetch_tenant",
    "rails_admin_user": os.getenv("RAILS_ADMIN_USER"),
    "rails_admin_password": os.getenv("RAILS_ADMIN_PASSWORD")
}

STACK_CONFIG = {
    "pie": {
        "instantink_url":         "https://instantink-pie1.hpconnectedpie.com",
        "instantink_v3_url":      "https://instantink-pie1.hpconnectedpie.com/enroll/start_v3_web",
        "agena_url":              "https://agena-pie1.services.hpconnectedpie.com",
        "cartridgepacker_url":    "https://cartridgepacker-pie1.instantink.com",
        "fulfillmentservice_url": "https://fulfillmentservice-pie1.instantink.com",
        "fulfillmentsimulator_url": "https://fulfillmentsimulator.hp-instantink.com",
        "portalshell":            "https://consumer.pie.portalshell.int.hp.com",
        "onboarding_center_url":  "https://onboardingcenter.pie.portalshell.int.hp.com/us/en/instantink-oobe-test-setup",
        "oss_url":                "https://oss.hpconnectedpie.com/emulate/v9",
        "hpid_url":               "https://myaccount.stg.cd.id.hp.com",
        "stratus_authz":  "https://authz-stratus.api.itg-thor-ue1.hpip-internal.com",
        "stratus_tropos": "https://stratus.api.itg-thor-ue1.hpip-internal.com",
        "usermgt":        "https://usermgt-stratus.api.itg-thor-ue1.hpip-internal.com",
        "ucde_authz":     "https://authz.pie.api.ws-hp.com",
        "ucde_tropos":    "https://ucde-ucde.api.itg-thor-ue1.hpip-internal.com",
        "ucde_server":    "https://pie-us1.api.ws-hp.com/ucde/ucde",
        "client_secrets": {
            "stratus": os.getenv("PIE_STRATUS_CLIENT_SECRET"),
            "ucde":    os.getenv("PIE_UCDE_CLIENT_SECRET"),
            "gemini":  os.getenv("PIE_GEMINI_CLIENT_SECRET"),
        },
        **RAILS_ADMIN_CONFIG
    },
    "stage": {
        "instantink_url":         "https://instantink-stage1.hpconnectedstage.com",
        "instantink_v3_url":      "https://instantink-stage1.hpconnectedstage.com/enroll/start_v3_web",
        "agena_url":              "https://agena-stage1.services.hpconnectedstage.com",
        "cartridgepacker_url":    "https://cartridgepacker-stage1.instantink.com",
        "fulfillmentservice_url": "https://fulfillmentservice-stage1.instantink.com",
        "fulfillmentsimulator_url": "https://fulfillmentsimulator.hp-instantink.com",
        "portalshell":            "https://consumer.stage.portalshell.int.hp.com",
        "onboarding_center_url":  "https://onboardingcenter.stage.portalshell.int.hp.com/us/en/instantink-oobe-test-setup",
        "oss_url":                "https://oss.hpconnectedstage.com/emulate/v9",
        "hpid_url":               "https://myaccount.stg.cd.id.hp.com",
        "stratus_authz":  "https://authz-stratus.api.stg-thor-ue1.hpip-internal.com",
        "stratus_tropos": "https://stratus.api.stg-thor-ue1.hpip-internal.com",
        "usermgt":        "https://usermgt-stratus.api.stg-thor-ue1.hpip-internal.com",
        "ucde_authz":     "https://authz.stage.api.ws-hp.com",
        "ucde_tropos":    "https://ucde-ucde.api.stg-thor-ue1.hpip-internal.com",
        "ucde_server":    "https://stage-us1.api.ws-hp.com/ucde/ucde",
        "client_secrets": {
            "stratus": os.getenv("STAGE_STRATUS_CLIENT_SECRET"),
            "ucde":    os.getenv("STAGE_UCDE_CLIENT_SECRET"),
            "gemini":  os.getenv("STAGE_GEMINI_CLIENT_SECRET"),
        },
        **RAILS_ADMIN_CONFIG
    },
    "production": {
        "instantink_url":         "https://instantink.hpconnected.com",
        "instantink_v3_url":      "https://instantink.hpconnected.com/enroll/start_v3_web",
        "agena_url":              "",
        "cartridgepacker_url":    "",
        "fulfillmentservice_url": "",
        "fulfillmentsimulator_url": "",
        "portalshell":            "",
        "onboarding_center_url":  "",
        "oss_url":                "",
        "hpid_url":               "",
        "stratus_authz":          "",
        "stratus_tropos":         "",
        "usermgt":                "",
        "ucde_authz":             "",
        "ucde_tropos":            "",
        "ucde_server":            "",
        "client_secrets": {
            "stratus": "",
            "ucde":    "",
            "gemini":  "",
        }
    }
}
_stack                        = None
_profile                      = None
_derivative_model             = None
_biz_model                    = None
_tenant_country               = None
_tenant_country_short         = None
_tenant_country_language_code = None
_tenant_address               = None
_tenant_email                 = None
_headless                     = True
_target                       = None
_simulator_platform           = ""
_target_width                 = 1920
_target_height                = 1080
_stratus_authz   = None
_stratus_tropos  = None
_usermgt         = None
_ucde_authz      = None
_ucde_tropos     = None
_ucde_server     = None
_instantink_url          = None
_instantink_v3_url       = None
_portalshell_url   = None
_onboarding_center_url = None
_oss_url         = None
_hpid_url        = None
_agena_url      = None
_cartridgepacker_url = None
_fulfillmentservice_url = None
_fulfillmentsimulator_url = None
_gemini_rails_admin_login_url = None
_gemini_fetch_tenant_url = None
_agena_cps_and_fulfillment_rails_admin_login_url = None
_rails_admin_user = None
_rails_admin_password = None
_client_secrets  = {}
_stratus_client_id = None
_ucde_client_id    = None
_gemini_client_id  = None
_supplyvariant = None
_card_payment_gateway = None
_payment_method = None
_printer_created = []
_mongodb_uri = None
_mongodb_db_name = None
_s3_endpoint = None
_s3_access_key = None
_s3_secret_key = None
_s3_bucket = None
_s3_region = None
_s3_secure = None

def set_globals(args: dict):
    global _stack, _profile, _derivative_model, _biz_model, _tenant_country, _tenant_country_short, _tenant_country_language_code, _tenant_address, _headless, _target, _simulator_platform, _target_width, _target_height, _instantink_url, _gemini_rails_admin_login_url, _gemini_fetch_tenant_url, _agena_cps_and_fulfillment_rails_admin_login_url, _rails_admin_user, _rails_admin_password, _mongodb_uri, _mongodb_db_name, _s3_endpoint, _s3_access_key, _s3_secret_key, _s3_bucket, _s3_region, _s3_secure, _instantink_v3_url, _portalshell_url, _onboarding_center_url, _agena_url, _cartridgepacker_url, _fulfillmentservice_url, _fulfillmentsimulator_url, _oss_url, _hpid_url, _stratus_authz, _stratus_tropos, _usermgt, _ucde_authz, _ucde_tropos, _ucde_server, _client_secrets, _stratus_client_id, _ucde_client_id, _gemini_client_id, _supplyvariant, _card_payment_gateway, _payment_method, _printer_created
    _stack                        = args.get("stack")
    _profile                      = args.get("profile")
    _derivative_model             = args.get("derivative_model")
    _biz_model                    = args.get("biz_model", "Flex")
    _tenant_country               = args.get("tenant_country")
    _tenant_country_short         = args.get("tenant_country_short")
    _tenant_country_language_code = args.get("tenant_country_language_code")
    _tenant_address               = args.get("tenant_address")
    _headless                     = args.get("headless", True)
    _target                       = args.get("target")
    _simulator_platform           = args.get("simulator_platform", "")
    _target_width                 = int(args.get("target_width", 1920))
    _target_height                = int(args.get("target_height", 1080))
    _supplyvariant                = args.get("supplyvariant")
    _card_payment_gateway          = args.get("card_payment_gateway")
    _payment_method               = args.get("payment_method", "credit_card")
    framework_logger.info(f"set_globals → stack={_stack} profile={_profile} biz_model={_biz_model} supplyvariant={_supplyvariant} card_payment_gateway={_card_payment_gateway}")
    framework_logger.debug(f"set_globals → tenant={_tenant_country} ({_tenant_country_short}), language_code={_tenant_country_language_code}")
    framework_logger.debug(f"set_globals → headless={_headless} tenant_address={json.dumps(_tenant_address)}")
    framework_logger.debug(f"set_globals → target={_target} simulator_platform={_simulator_platform} target_width={_target_width} target_height={_target_height}")
    cfg = STACK_CONFIG.get(_stack)
    if not cfg:
        raise ValueError(f"Unknown stack: {_stack}")
    _instantink_url           = cfg["instantink_url"]
    _gemini_rails_admin_login_url   = cfg["gemini_rails_admin_endpoint"]
    _gemini_fetch_tenant_url = cfg["fetch_tenant_endpoint"]
    _agena_cps_and_fulfillment_rails_admin_login_url = cfg["agena_cps_and_fulfillment_rails_admin_endpoint"]
    _rails_admin_user        = cfg["rails_admin_user"]
    _rails_admin_password    = cfg["rails_admin_password"]
    _instantink_v3_url       = cfg["instantink_v3_url"]
    _portalshell_url         = cfg["portalshell"]
    _onboarding_center_url   = cfg["onboarding_center_url"]
    _agena_url               = cfg["agena_url"]
    _cartridgepacker_url     = cfg["cartridgepacker_url"]
    _fulfillmentservice_url  = cfg["fulfillmentservice_url"]
    _fulfillmentsimulator_url= cfg["fulfillmentsimulator_url"]
    _oss_url                 = cfg["oss_url"]
    _hpid_url                = cfg["hpid_url"]
    _stratus_authz           = cfg["stratus_authz"]
    _stratus_tropos          = cfg["stratus_tropos"]
    _usermgt                 = cfg["usermgt"]
    _ucde_authz              = cfg["ucde_authz"]
    _ucde_tropos             = cfg["ucde_tropos"]
    _ucde_server             = cfg["ucde_server"]
    _stratus_client_id       = STRATUS_CLIENT_ID
    _ucde_client_id          = UCDE_CLIENT_ID
    _gemini_client_id        = GEMINI_CLIENT_ID
    _client_secrets          = cfg["client_secrets"]
    # Initialize DB and Storage configuration
    _mongodb_uri              = MONGODB_URI
    _mongodb_db_name           = MONGODB_DB_NAME
    _s3_endpoint              = S3_ENDPOINT
    _s3_access_key            = S3_ACCESS_KEY
    _s3_secret_key            = S3_SECRET_KEY
    _s3_bucket                = S3_BUCKET
    _s3_region                = S3_REGION
    _s3_secure                = S3_SECURE

    framework_logger.debug(f"Endpoints loaded for stack={_stack}:")
    framework_logger.debug(f"  instantink_url={_instantink_url}")
    framework_logger.debug(f"  instantink_v3_url={_instantink_v3_url}")
    framework_logger.debug(f"  portalshell_url={_portalshell_url}")
    framework_logger.debug(f"  onboarding_center_url={_onboarding_center_url}")
    framework_logger.debug(f"  agena_url={_agena_url}")
    framework_logger.debug(f"  cartridgepacker_url={_cartridgepacker_url}")
    framework_logger.debug(f"  fulfillmentservice_url={_fulfillmentservice_url}")
    framework_logger.debug(f"  fulfillmentsimulator_url={_fulfillmentsimulator_url}")
    framework_logger.debug(f"  oss_url={_oss_url}")
    framework_logger.debug(f"  hpid_url={_hpid_url}")
    framework_logger.debug(f"  gemini_rails_admin_login_url={_gemini_rails_admin_login_url}")
    framework_logger.debug(f"  gemini_fetch_tenant_url={_gemini_fetch_tenant_url}")
    framework_logger.debug(f"  agena_and_fulfillment_rails_admin_login_url={_agena_cps_and_fulfillment_rails_admin_login_url}")
    framework_logger.debug(f"  rails_admin_user={_rails_admin_user}")
    framework_logger.debug(f"  rails_admin_password={'***' if _rails_admin_password else None}")
    framework_logger.debug(f"  stratus_authz={_stratus_authz}")
    framework_logger.debug(f"  stratus_tropos={_stratus_tropos}")
    framework_logger.debug(f"  usermgt={_usermgt}")
    framework_logger.debug(f"  ucde_authz={_ucde_authz}")
    framework_logger.debug(f"  ucde_tropos={_ucde_tropos}")
    framework_logger.debug(f"  ucde_server={_ucde_server}")
    framework_logger.debug(f"Common Client IDs: stratus={_stratus_client_id[:8]}..., ucde={_ucde_client_id[:8]}..., gemini={_gemini_client_id[:8]}...")
    framework_logger.debug(f"Client secrets loaded for stack={_stack}: " + json.dumps({k: (v[:8] + '...') if isinstance(v, str) and len(v) > 8 else v for k, v in _client_secrets.items()}))
    framework_logger.debug(f"MongoDB configuration loaded:")
    framework_logger.debug(f"  mongodb_uri={_mongodb_uri}")
    framework_logger.debug(f"  mongodb_db_name={_mongodb_db_name}")
    framework_logger.debug(f"Storage (S3/MinIO) configuration loaded:")
    framework_logger.debug(f"  s3_bucket={_s3_bucket}")
    framework_logger.debug(f"  s3_region={_s3_region}")
    framework_logger.debug(f"  s3_secure={_s3_secure}")
    framework_logger.debug(f"  s3_endpoint={_s3_endpoint}")
    framework_logger.debug(f"  s3_access_key={_s3_access_key[:8] + '...' if _s3_access_key else None}")
    framework_logger.debug(f"  s3_secret_key={'***' if _s3_secret_key else None}")

def setup():
    set_globals({
        "stack": GlobalState.stack,
        "profile": GlobalState.printer_profile,
        "derivative_model": getattr(GlobalState, "derivative_model", None),
        "biz_model": getattr(GlobalState, "biz_model", "Flex"),
        "supplyvariant": getattr(GlobalState, "supplyvariant", None),
        "tenant_country": GlobalState.country,
        "tenant_country_short": GlobalState.country_code,
        "tenant_country_language_code": GlobalState.language_code,
        "tenant_address": GlobalState.address_payload,
        "headless": GlobalState.headless,
        "target": getattr(GlobalState, "target"),
        "simulator_platform": getattr(GlobalState, "simulator_platform", ""),
        "card_payment_gateway": getattr(GlobalState, "card_payment_gateway", None),
        "payment_method": getattr(GlobalState, "payment_method") or "credit_card_master",
    })

    TEMP_DIR = "temp"
    os.makedirs(TEMP_DIR, exist_ok=True)
    framework_logger.debug(f"Created temp directory: {TEMP_DIR}")

def generate_tenant_email() -> str:
    global _tenant_email
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    _tenant_email = f"hello.instantink+{suffix}@gmail.com"
    framework_logger.info(f"Generated tenant_email={_tenant_email}")
    return _tenant_email

def authenticate_gmail():
    creds = Credentials(
        None,
        refresh_token=GMAIL_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GMAIL_CLIENT_ID,
        client_secret=GMAIL_CLIENT_SECRET,
        scopes=GMAIL_SCOPE,
    )
    try:
        creds.refresh(Request())
    except Exception as e:
        framework_logger.error(f"Gmail refresh token failed: {e}")
        if "invalid_grant" in str(e) or "invalid_request" in str(e):
            raise RuntimeError("Gmail refresh token is invalid or expired. Please update your GMAIL_REFRESH_TOKEN.")
        raise
    return build("gmail", "v1", credentials=creds)

def extract_verification_code(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    el = soup.find("p", class_="code")
    if not el:
        raise RuntimeError("Verification code element not found in email HTML")
    code = el.get_text(strip=True)
    framework_logger.debug(f"Extracted verification code: {code}")
    return code

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def fetch_verification_code(tenant_email: str) -> str:
    framework_logger.info(f"Fetching verification code for {tenant_email}")
    service = authenticate_gmail()
    q       = f"to:{tenant_email} newer_than:5m"
    res     = service.users().messages().list(userId="me", q=q).execute()
    msgs    = res.get("messages", [])
    if not msgs:
        raise RuntimeError(f"No recent messages found for {tenant_email}")
    full    = service.users().messages().get(
        userId="me", id=msgs[0]["id"], format="full"
    ).execute()
    framework_logger.debug(f"Fetched raw email payload for message {msgs[0]['id']}")
    parts   = full["payload"].get("parts", [])
    data    = (
        full["payload"].get("body", {}).get("data")
        or next((p["body"]["data"] for p in parts if p.get("mimeType")=="text/html"), None)
    )
    if not data:
        raise RuntimeError("Email HTML body not found")
    html    = base64.urlsafe_b64decode(data).decode("utf-8")
    return extract_verification_code(html)

def create_hpid(page, callback=None, email=None):
    if email == None:
        email = _tenant_email
    framework_logger.info(f"Signing up HPID for {email}")
    page.goto(_hpid_url)
    page.set_viewport_size({"width":1366,"height":768})
    page.wait_for_selector("#sign-up", timeout=2000000).click()
    page.fill("#firstName",DEFAULT_FIRSTNAME)
    page.fill("#lastName",DEFAULT_LASTNAME)
    page.fill("#email", email)
    page.fill("#password",DEFAULT_PASSWORD)
    page.click("#sign-up-submit")
    page.wait_for_load_state("load")
    if callback:
       callback()

    start_time = time.time()

    while time.time() - start_time < 60:
        if safe_check(lambda: page.locator("#submit-code").count() > 0):
            confirm_code_by_onboarding_center(page)
            break
        
        if safe_check(lambda: "myaccount" in page.url):
            confirm_code_by_my_account(page)
            break
        
        time.sleep(2)

    framework_logger.info("HPID created successfully")
    return page

def safe_check(check_func):
    try:
        return check_func()
    except Exception:
        return False

def confirm_code_by_my_account(page):
    page.locator("li[id='security']").click()
    page.get_by_role("button", name="Verify").click()
    code = get_verification_code()
    page.get_by_role("textbox", name="Enter 6-digit numeric code").fill(code)
    page.get_by_role("button", name="Verify").click()

def confirm_code_by_onboarding_center(page):
    code = get_verification_code()
    page.fill("#code", code)
    page.click("#submit-code")
    page.wait_for_selector("#countryResidence", timeout=20000).click()
    page.locator(f"[data-value='{_tenant_country_short}']").click()
    page.click("#continue-button")
    framework_logger.info("HPID created successfully")

def get_verification_code():
    code = None
    for attempt in range(1,4):
        try:
            code = fetch_verification_code(_tenant_email)
            break
        except Exception as e:
            framework_logger.warning(f"Attempt {attempt}/3: no code yet ({e}), retrying…")
            time.sleep(5)
    if not code:
        raise RuntimeError("Failed to retrieve verification code after 3 attempts")
    framework_logger.info(f"Using verification code: {code}")
    return code

def create_ii_v2_account(page):
    framework_logger.info(f"Signing up HPID for {_tenant_email}")
    page.goto(_instantink_url, timeout=1200000)
    try:
        page.wait_for_selector("#onetrust-accept-btn-handler", timeout=100000).click()
        framework_logger.debug("Privacy banner accepted")
    except Exception as e:
        framework_logger.debug(f"Privacy banner not found or already accepted: {e}")
    
    sign_up_button = page.locator("[data-testid='header-sign-up-button'], [data-testid='plans-sign-up-button'], [data-testid='origami-intro-enroll-starter-kit-button'], [data-testid='i_ink-plan-type-card-select-button']").first
    create_account_button = page.locator("[data-testid='create-account-button']")
    sign_in = page.locator("#sign-in")

    expect(sign_up_button).to_be_visible(timeout=3000000)
    sign_up_button.click()
    expect(create_account_button).to_be_visible(timeout=300000)
    create_account_button.click()
    expect(sign_in).to_be_visible(timeout=300000)
    
    page.fill("#firstName",DEFAULT_FIRSTNAME)
    page.fill("#lastName",DEFAULT_LASTNAME)
    page.fill("#email",_tenant_email)
    page.fill("#password",DEFAULT_PASSWORD)
    page.click("#market")
    page.click("#sign-up-submit")
    page.wait_for_selector("#submit-code",timeout=50000)
    code = None
    for attempt in range(1,4):
        try:
            code = fetch_verification_code(_tenant_email)
            break
        except Exception as e:
            framework_logger.warning(f"Attempt {attempt}/3: no code yet ({e}), retrying…")
            time.sleep(5)
    if not code:
        raise RuntimeError("Failed to retrieve verification code after 3 attempts")
    framework_logger.info(f"Using verification code: {code}")
    page.fill("#code", code)
    page.click("#submit-code")
    page.locator("[data-testid='stepper']").wait_for(state="visible", timeout=1200000)
    framework_logger.info("HPID account created successfully")
    page.goto(_portalshell_url, timeout=60000)
    page.wait_for_timeout(60000)
    try:
        page.locator(".vn-side-menu__toggle").click()
    except Exception:
        pass
    page.locator('[data-testid="jarvis-react-consumer-layout__side-menu-item-HP Instant Ink"]').click(timeout=120000)
    return page

def login_ii_v2_account(page, username=None, oobe=False):
    framework_logger.info(f"Signing up HPID for {_tenant_email}")
    page.goto(_instantink_url, timeout=120000)
    try:
        page.wait_for_selector("#onetrust-accept-btn-handler", timeout=10000).click()
        framework_logger.debug("Privacy banner accepted")
    except Exception as e:
        framework_logger.debug(f"Privacy banner not found or already accepted: {e}")
    page.locator("[data-testid='header-sign-up-button'], [data-testid='plans-sign-up-button'], [data-testid='origami-intro-enroll-starter-kit-button'], [data-testid='i_ink-plan-type-card-select-button']").first.click()
    time.sleep(5)
    page.wait_for_selector("[data-testid='sign-in-button']").click()
    page.fill("#username",username)
    page.locator("//*[text()='Use password']").click()
    page.fill("#password",DEFAULT_PASSWORD)
    page.click("#sign-in")
    if oobe:
        page.locator('[data-index="0"]').wait_for(state="visible", timeout=180000)
        page.locator('[data-index="0"] span').click()
        page.locator('[data-testid="continue-button"]').wait_for(state="visible", timeout=8000)
        page.locator('[data-testid="continue-button"]').click()
    return page


def onboard_hpid_to_ucde(page):
    framework_logger.info("Onboarding HPID to UCDE")
    guid = str(uuid.uuid4())
    authz_url = (
        f"{_ucde_authz}/openid/v1/authorize"
        f"?scope=openid+email+profile"
        f"&response_type=code"
        f"&state={guid}"
        f"&client_id={_ucde_client_id}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    framework_logger.debug(f"UCDE authorize URL: {authz_url}")
    page.goto(authz_url, timeout=60000)
    page.wait_for_load_state("load")
    time.sleep(5)
    final = page.url
    framework_logger.info(f"Final: {final}")
    if "code=" not in final:
        raise RuntimeError(f"OAuth code not found in redirect URI: {final}")
    code = final.split("code=")[1].split("&")[0]
    framework_logger.info(f"OAuth code retrieved: {code}")
    token_url = f"{_ucde_authz}/openid/v1/token"
    basic = base64.b64encode(
        f"{_ucde_client_id}:{_client_secrets['ucde']}".encode()
    ).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {basic}"
    }
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    framework_logger.debug(f"Token exchange POST to {token_url} with Basic auth")
    token_response = session.post(token_url, headers=headers, data=body, timeout=30)
    framework_logger.debug(f"Token exchange response: {token_response.status_code} {token_response.text[:128]}{'... (truncated)' if len(token_response.text) > 128 else ''}")
    token_response.raise_for_status()
    access_token = token_response.json().get("access_token")
    id_token     = token_response.json().get("id_token")
    if not access_token or not id_token:
        raise RuntimeError("Missing access_token or id_token in token response")
    framework_logger.info("access_token and id_token retrieved")
    onboard_url = f"{_ucde_server}/v2/ecosystem/accountmgtsvc/accounts"
    acct_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    acct_body = {
        "countrySet": [_tenant_country_short],
        "idToken":    id_token,
        "language":   _tenant_country_language_code
    }
    framework_logger.debug(f"Account creation POST to {onboard_url}")
    acct_response = session.post(onboard_url, headers=acct_headers, json=acct_body, timeout=300)
    framework_logger.debug(f"Account creation response: {acct_response.status_code} {acct_response.text}")
    acct_response.raise_for_status()
    framework_logger.info(
        f"HPID onboarded to UCDE on {_stack.upper()} "
        f"for {_tenant_country_short}_{_tenant_country_language_code}"
    )
    return page

def get_token_gemini_client():
    token_url = f"{_stratus_authz}/openid/v1/token"
    basic_gemini = base64.b64encode(
        f"{_gemini_client_id}:{_client_secrets['gemini']}".encode()
    ).decode()
    response = session.post(
        token_url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_gemini}"
        },
        data={"grant_type": "client_credentials"}
    )
    response.raise_for_status()
    token0 = response.json()["access_token"]
    return token0

def get_org_aware_token(email=None):
    if email == None:
        email = _tenant_email
    token_url = f"{_stratus_authz}/openid/v1/token"
    token0 = get_token_gemini_client()
    framework_logger.info(f"[1/4] Gemini token obtained: {token0[:8]}…")
    response = session.get(
        f"{_usermgt}/v3/usermgtsvc/users?email={email}",
        headers={"Authorization": f"Bearer {token0}"}
    )
    response.raise_for_status()
    user = response.json()["resourceList"][0]
    user_res = user["resourceId"]
    hp_id    = user.get("idpId")
    framework_logger.info(f"[2/4] Found userResourceId={user_res}, idpId={hp_id}")
    response = session.get(
        f"{_usermgt}/v3/usermgtsvc/usertenantdetails?userResourceId={user_res}",
        headers={"Authorization": f"Bearer {token0}"}
    )
    response.raise_for_status()
    tenant_id = response.json()["resourceList"][0]["tenantResourceId"]
    framework_logger.info(f"[3/4] Resolved tenantResourceId={tenant_id}")
    basic_stratus = base64.b64encode(f"{_stratus_client_id}:{_client_secrets['stratus']}".encode()).decode()
    response = session.post(
        token_url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_stratus}"
        },
        data={"grant_type": "client_credentials"}
    )
    response.raise_for_status()
    token1 = response.json()["access_token"]
    framework_logger.info(f"[4/4] Stratus client token obtained: {token1[:8]}…")
    response = session.post(
        token_url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_stratus}"
        },
        data={
            "grant_type":                 "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token":              token1,
            "subject_token_type":         "urn:ietf:params:oauth:token-type:access_token",
            "requested_user_type":        "hp:authz:params:oauth:user-id-type:stratusid",
            "requested_user":             user_res,
            "tenant_id":                  tenant_id
        }
    )
    response.raise_for_status()
    org_token = response.json()["access_token"]
    framework_logger.info(f"[Done] Org-Aware user token obtained: {org_token[:8]}…")
    return org_token, tenant_id

class PrinterData(tuple):
    def __new__(cls, entity_id, model_number, device_uuid, cloud_id, postcard, fingerprint):
        return super().__new__(cls, (entity_id, model_number, device_uuid, cloud_id, postcard, fingerprint))
    
    def __init__(self, entity_id, model_number, device_uuid, cloud_id, postcard, fingerprint):
        self.entity_id = entity_id
        self.model_number = model_number
        self.device_uuid = device_uuid
        self.cloud_id = cloud_id
        self.postcard = postcard
        self.fingerprint = fingerprint

def retry_operation(operation, operation_name="Operation", max_attempts=5, delay=2, on_retry=None):
    for attempt in range(1, max_attempts + 1):
        try:
            framework_logger.info(f"{operation_name} - attempt {attempt}/{max_attempts}")
            result = operation()
            framework_logger.info(f"{operation_name} successful")
            return result

        except Exception as e:
            framework_logger.warning(f"{operation_name} failed: {e}")
            if attempt == max_attempts:
                framework_logger.error(f"All {max_attempts} attempts failed for {operation_name}")
                raise

            if on_retry:
                try:
                    on_retry()
                except Exception as retry_e:
                    framework_logger.warning(f"on_retry failed: {retry_e}")

            framework_logger.info(f"Retrying in {delay}s...")
            time.sleep(delay)

def create_virtual_printer():
    global _printer_created
    def make_request(method, url, **kwargs):
        """Helper para fazer requests HTTP"""
        response = session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    
    # Step 1: Create printer
    def step_create_printer():
        url = "https://g2sim.wpp.api.hp.com/wpp/simulator/printers"
        body = {
            "stack": _stack,
            "profile": _profile,
            "biz_model": _biz_model,
            "offer": 1,
            "fipsflag": "true",
            "derivative_model": _derivative_model
        }
        framework_logger.info(f"Creating virtual printer with body: {json.dumps(body)}")
        response = make_request("POST", url, json=body)
        return response.json()
    
    data = retry_operation(step_create_printer, "Create virtual printer", max_attempts=5)
    
    entity_id = data["entity_id"]
    model_number = data["model_number"]
    device_uuid = data["uuid"]
    framework_logger.info(f"Virtual printer created: serialnumber = {entity_id}, model={model_number}, uuid={device_uuid}")
    
    # Step 2: Register printer
    def step_register_printer():
        url = f"https://g2sim.wpp.api.hp.com/wpp/simulator/printers/{entity_id}/register"
        response = make_request("POST", url)
        return response.json().get("cloud_id")
    
    cloud_id = retry_operation(step_register_printer, f"Register printer {entity_id}", max_attempts=5)
    framework_logger.info(f"Printer registered, cloud_id={cloud_id}")
    
    # Step 3: Get claim postcard
    def step_get_postcard():
        url = f"https://g2sim.wpp.api.hp.com/wpp/simulator/printers/{entity_id}/claimpostcard"
        response = make_request("POST", url)
        text = response.text.strip()
        return (base64.b64encode(text.encode()).decode()
                if text.startswith('{') else text.replace('"',''))
    
    postcard = retry_operation(step_get_postcard, f"Get postcard for {entity_id}", max_attempts=3)
    
    # Step 4: Get device fingerprint
    def step_get_fingerprint():
        url = f"https://g2sim.wpp.api.hp.com/wpp/simulator/printers/{entity_id}/devicefingerprint"
        response = make_request("GET", url)
        text = response.text.strip()
        return (base64.b64encode(text.encode()).decode()
                if text.startswith('{') else text.replace('"',''))
    
    fingerprint = retry_operation(step_get_fingerprint, f"Get fingerprint for {entity_id}", max_attempts=3)
    
    printer_created = PrinterData(entity_id, model_number, device_uuid, cloud_id, postcard, fingerprint)
    _printer_created.append(printer_created)
    return printer_created

def claim_virtual_printer(org_token, tenant_id, model_number, device_uuid, postcard, fingerprint):
    framework_logger.info(f"Claiming printer {model_number} under tenant {tenant_id}")
    payload = {
        "autoClaimRequest": {
            "productNumber":    model_number,
            "uuid":             device_uuid,
            "claimPostcard":    postcard,
            "fingerprint":      fingerprint,
            "selectedBizModel": _biz_model
        }
    }
    framework_logger.debug(f"Claim payload: {json.dumps(payload)[:180]}...")
   
    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            framework_logger.info(f"Claim attempt {attempt}/{max_attempts}")
            response = session.post(
                f"{_ucde_tropos}/v2/ecosystem/accountmgtsvc/accounts/{tenant_id}/devices",
                headers={
                    "Accept":"application/json",
                    "Content-Type":"application/json",
                    "Authorization":f"Bearer {org_token}"
                },
                json=payload
            )
 
            framework_logger.debug(f"Claim response: {response.status_code} {response.text}")
            response.raise_for_status()
            framework_logger.info("Printer claimed successfully")
            return  # Exit function on success
           
        except Exception as e:
            framework_logger.warning(f"Claim attempt {attempt}/{max_attempts} failed: {e}")
            if attempt == max_attempts:
                framework_logger.error(f"All {max_attempts} claim attempts failed")
                raise
            framework_logger.info(f"Retrying claim... ({attempt + 1}/{max_attempts})")
            time.sleep(2)

def add_address_to_tenant(org_token, tenant_id):
    framework_logger.info(f"Adding address to tenant {tenant_id}")
      
    if isinstance(_tenant_address, list):
       address_data = _tenant_address[0]
    else:
        address_data = _tenant_address
    
    address_payload = {k: v for k, v in address_data.items() if not k.startswith("fullState")}
    framework_logger.debug(f"Address payload: {json.dumps(address_payload)}")
    response = session.post(
        f"{_instantink_url}/api/comfe/v1/shipping/addresses/?tenantId={tenant_id}",
        headers={
            "Content-Type":"application/json",
            "Authorization":f"Bearer {org_token}"
        },
        json=address_payload
    )
    framework_logger.debug(f"Address POST response: {response.status_code} {response.text}")
    if response.status_code != 201:
        raise RuntimeError(f"Failed to add address: HTTP {response.status_code}")
    framework_logger.info("Address added successfully")

def create_and_claim_virtual_printer():
    org_token, tenant_id = get_org_aware_token()
    framework_logger.info(f"Obtained org_token and tenant_id")
    
    printer = create_virtual_printer()
    entity_id, model_number, device_uuid, cloud_id, postcard, fingerprint = printer
    framework_logger.info(f"Printer details: serialnumber={entity_id}, model={model_number}, uuid={device_uuid}, cloud_id={cloud_id}, postcard={postcard[:8]}..., fingerprint={fingerprint[:8]}...")
    
    claim_virtual_printer(org_token, tenant_id, model_number, device_uuid, postcard, fingerprint)
    framework_logger.info("Virtual printer created and claimed successfully")
    
    return printer

def create_and_claim_virtual_printer_and_add_address():
    org_token, tenant_id = get_org_aware_token()
    framework_logger.info(f"Obtained org_token and tenant_id")
    
    printer = create_virtual_printer()
    entity_id, model_number, device_uuid, cloud_id, postcard, fingerprint = printer
    framework_logger.info(f"Printer details: serialnumber={entity_id}, model={model_number}, uuid={device_uuid}, cloud_id={cloud_id}, postcard={postcard[:8]}..., fingerprint={fingerprint[:8]}...")
    
    claim_virtual_printer(org_token, tenant_id, model_number, device_uuid, postcard, fingerprint)
    framework_logger.info("Virtual printer created and claimed successfully")

    add_address_to_tenant(org_token, tenant_id)
    framework_logger.info("Address added to tenant successfully using comfe API")
    
    return printer

def get_payment_method_data(payment_type: str = None) -> dict:
    if payment_type is None:
        payment_type = _payment_method or "credit_card_master"
    payment_file = os.path.join(os.path.dirname(__file__), "payment_method_data.json")
    data = load_json_file(payment_file)    
    if payment_type not in data:
        available_types = list(data.keys())
        raise ValueError(f"Payment type '{payment_type}' not found. Available: {available_types}") 
    payment_data = data[payment_type].copy()
    if "expiration_year" in payment_data:
        exp_year_value = payment_data["expiration_year"]
        if isinstance(exp_year_value, str) and exp_year_value.startswith("+"):
            from datetime import datetime
            current_year = datetime.now().year
            years_to_add = int(exp_year_value[1:])
            payment_data["expiration_year"] = str(current_year + years_to_add)
    return payment_data

def create_oobe_registration_record(org_token, entity_id, model_number):
    payload = {
        "model_number": model_number,
        "serial_number": entity_id,
        "country": _tenant_country_short,
        "sku": "",
        "ink_declaration": "",
        "supply_types": "",
        "supply_levels": "",
        "supply_states": "",
        "unenrolled_pages": "",
        "ui_phase": "",
        "enrollment_kit": "",
        "jump_id": "",
        "ip_address": ""
    }
    url = f"{_agena_url}/oobe_registrations"
    headers = {
        "Version": "HTTP/1.0",
        "Authorization": f"Bearer {org_token}",
        "Accept": "application/vnd.agena+json;version=2",
        "Content-Type": "application/json"
    }
    framework_logger.debug(f"POST OOBE registration to {url} with payload: {json.dumps(payload)}")
    response = session.post(url, headers=headers, json=payload)
    framework_logger.info(f"OOBE registration response: {response.status_code} {response.text}")
    response.raise_for_status()
    return response

def find_card_body_by_header(page, header_text: str):
    header_locator = page.locator(f".card-header:text-is('{header_text}')")
    assert header_locator.count() > 0, f"Header '{header_text}' not found"
    return header_locator.locator("..").locator(".card-body")

def find_field_text_by_header(page, header_text: str) -> str:
    card_body_locator = find_card_body_by_header(page, header_text)
    return card_body_locator.inner_text().strip()

def find_field_link_list_by_header(page, header_text: str) -> list:
    card_body_locator = find_card_body_by_header(page, header_text)
    links_locator = card_body_locator.locator("a")
    return [link.get_attribute("href") for link in links_locator.all()]

def last_number_from_url(page):
    url = page.url
    numbers = re.findall(r'\d+', url)
    return numbers[-1] if numbers else None

def extract_numbers_from_text(text: str) -> list:
    if not text: return []
    
    text = text.strip()
    matches = re.findall(r"\d+\.\d+|\d+", text)

    return matches if matches else []

def send_rtp_devicestatus(entity_id, cloud_id, device_uuid):
    bizmodelFlag = 1409286144
    lastValidConfigSeqNum = 1
    lastReceivedConfigSeqNum = 1
    lastValidCredentialSeqNum = 1
    supplyInsertionCount = 1
    totalImpressionCount = 0
    bizlogicImpressionCount = 0
    internalReportImpressionCount = 0
    snapshotCountersSum = 0
    unique_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    crsSessionData_template = (
        "AAAABFoXAAAAIwAXAQEAAAAAAAAA70ozEoLnTKPYcmv3RjNMcKCyX3g3RtkoAAJhEQAGAAAAB8AAAAUWIBQAJAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFFiBcACQAJQBiMTBhNzJlZC04YmQyLTQ2NDgtOTNmNy1mZWI5NjhjODU2MzEABRYIPwAEAAUAAAAAZgAFFiAQAAQABQBUAAAAAAUWIgQABAAFAAAAAAIABRYiCAAEAAUAAAAAAAAFFiIMAAQABQAAAAABAAUWIhAABAAFAAAAAAMABRYiFAAEAAUAAAAAAAAFFgYrABAAEQDYcmv3RjNMcKCyX3g3RtkoAAUWH+8AIAAhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUWIiQABAAFAAAAAAsABRYiIAAEAAUAAAAAAAAFFiIcAAQABQAAAAAAAAUWIiwABAAFAAAAAAAABRYgpAABAAIAAAABWA=="
    )
    field_map = {
        'totalImpressionCount':      (66, 4,  '<I'),
        'bizlogicImpressionCount':   (120, 4, '<I'),
        'internalReportImpressionCount': (162, 4, '<I'),
        'snapshotCountersSum':       (201, 4, '<I'),
        'manufacturingDeviceUuid':   (20, 36, 'str'),
    }
    data = bytearray(base64.b64decode(crsSessionData_template))

    def set_field(offset, length, fmt, value):
        if fmt == 'str':
            value_bytes = value.encode('ascii')
            value_bytes = value_bytes.ljust(length, b'\x00')[:length]
            data[offset:offset+length] = value_bytes
        else:
            data[offset:offset+length] = struct.pack(fmt, value)

    set_field(*field_map['totalImpressionCount'], totalImpressionCount)
    set_field(*field_map['bizlogicImpressionCount'], bizlogicImpressionCount)
    set_field(*field_map['internalReportImpressionCount'], internalReportImpressionCount)
    set_field(*field_map['snapshotCountersSum'], snapshotCountersSum)
    set_field(*field_map['manufacturingDeviceUuid'], device_uuid)
    crsSessionData = base64.b64encode(bytes(data)).decode('ascii')

    # DEBUG: decode the freshly-packed crsSessionData and log values
    def decode_crssession(data_bytes):
        result = {}
        result['totalImpressionCount'] = struct.unpack('<I', data_bytes[66:70])[0]
        result['bizlogicImpressionCount'] = struct.unpack('<I', data_bytes[120:124])[0]
        result['internalReportImpressionCount'] = struct.unpack('<I', data_bytes[162:166])[0]
        result['snapshotCountersSum'] = struct.unpack('<I', data_bytes[201:205])[0]
        result['manufacturingDeviceUuid'] = data_bytes[20:56].decode('ascii').rstrip('\x00')
        return result

    decoded = decode_crssession(data)
    framework_logger.debug("crsSessionData (decoded): " + json.dumps(decoded, indent=2))
    framework_logger.debug(
        f"crsSessionData (base64): {crsSessionData[:32]}...{crsSessionData[-32:]}"
    )

    replacements = {
        "cloud_id": cloud_id,
        "uuid": device_uuid,
        "crsSessionData": crsSessionData,
        "totalImpressionCount": totalImpressionCount,
        "bizlogicImpressionCount": bizlogicImpressionCount,
        "internalReportImpressionCount": internalReportImpressionCount,
        "snapshotCountersSum": snapshotCountersSum,
        "lastValidConfigSeqNum": lastValidConfigSeqNum,
        "lastReceivedConfigSeqNum": lastReceivedConfigSeqNum,
        "lastValidCredentialSeqNum": lastValidCredentialSeqNum,
        "supplyInsertionCount": supplyInsertionCount,
        "bizmodelFlag": bizmodelFlag,
        "UniqueTimestamp": unique_timestamp,
        "manufacturingDeviceUuid": device_uuid,
    }
    framework_logger.debug("RTP Device Status replacements: " + json.dumps(replacements, indent=2))

    payload_path = os.path.join(os.path.dirname(__file__), f"RTPDS-PayLoad-{_supplyvariant}.json")
    if not os.path.exists(payload_path):
        raise FileNotFoundError(f"Payload file not found: {payload_path}")
    with open(payload_path, "r", encoding="utf-8") as f:
        template = f.read()
    for key, value in replacements.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    payload = json.loads(template)

    numeric_keys = {
        "totalImpressionCount",
        "bizlogicImpressionCount",
        "internalReportImpressionCount",
        "snapshotCountersSum",
        "lastValidConfigSeqNum",
        "lastReceivedConfigSeqNum",
        "lastValidCredentialSeqNum",
        "supplyInsertionCount",
        "bizmodelFlag",
    }
    def coerce_numerics(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in numeric_keys and isinstance(v, str) and v.isdigit():
                    obj[k] = int(v)
                else:
                    coerce_numerics(v)
        elif isinstance(obj, list):
            for item in obj:
                coerce_numerics(item)
    coerce_numerics(payload)

    framework_logger.debug("RTP Device Status request payload: " + json.dumps(payload, indent=2))
    url = f"https://g2sim.wpp.api.hp.com/wpp/simulator/printers/{entity_id}/rtpdevicestatustriggers"
    framework_logger.info(f"Sending RTP Device Status for entity_id={entity_id} with supplyvariant={_supplyvariant}")
    response = session.put(
        url,
        headers={"Content-Type": "application/json"},
        json=payload
    )
    framework_logger.debug(f"RTP Device Status raw response: {response.status_code} {response.text}")
    framework_logger.info(f"RTP Device Status response: {response.status_code} {response.text}")
    response.raise_for_status()
    return response

def offer_request(identifier_code):
    org_token, _ = get_org_aware_token()
    url = f"{_agena_url}/codes/{identifier_code}"
    headers = {
        "Version": "HTTP/1.0",
        "Authorization": f"Bearer {org_token}",
        "Accept": "application/vnd.agena+json;version=1",
        "Content-Type": "application/json"
    }
    framework_logger.debug(f"Generating token {url}")
    response = session.post(url, headers=headers)
    framework_logger.info(f"Generated offer response: {response.status_code} {response.text}")
    response.raise_for_status()
    
    response_data = response.json()
    code = response_data["posaCodes"][0]["code"]
    framework_logger.info(f"Generated offer code: {code}")
    
    return code

_OFFERS_FILE = os.path.join(os.path.dirname(__file__), "offers.json")
with open(_OFFERS_FILE, 'r') as file: OFFERS_DATA = json.load(file)

def get_offer(region: str, type: str = "free", amount_equal: int = None, amount_greater: int = None, amount_less: int = None) -> dict:

    if not region:
        raise ValueError("Region is required to fetch an offer.")

    if region not in OFFERS_DATA:
        raise ValueError(f"No offers found for region: {region}")

    region_offers = OFFERS_DATA[region]

    for offer in region_offers:
        if offer.get("type") != type:
            continue

        # If no amount filters, return the first matching offer
        if not any([amount_equal, amount_greater, amount_less]):
            return offer

        # Ensure amount is available and an int
        amount = offer.get("amountCents")
        if amount is None:
            continue
        try:
            amount_int = int(amount) if isinstance(amount, str) else amount
        except (ValueError, TypeError):
            framework_logger.warning(f"Could not convert amount '{amount}' to int, skipping offer")
            continue

        # Filtering conditions
        if (amount_equal and amount_int != amount_equal or
            amount_greater and amount_int <= amount_greater or 
            amount_less and amount_int >= amount_less):
            continue

        return offer

    # Build error message with only the values that were passed
    filter_parts = []
    if amount_equal is not None:
        filter_parts.append(f"amount_equal: {amount_equal}")
    if amount_greater is not None:
        filter_parts.append(f"amount_greater: {amount_greater}")
    if amount_less is not None:
        filter_parts.append(f"amount_less: {amount_less}")
    filter_str = ", ".join(filter_parts) if filter_parts else "no filters"
    raise ValueError(
        f"No matching offer found for region: {region}, type: {type or 'free'}, {filter_str}"
    )


def get_offer_code(offer_type: str = "free", amount_equal: int = None, amount_greater: int = None, amount_less: int = None) -> str:

    region = getattr(GlobalState, "country_code", None)
    if not region:
        raise ValueError("GlobalState.country_code is not set. Cannot fetch offer.")

    offer = get_offer(region, offer_type, amount_equal, amount_greater, amount_less)
    identifier = offer.get("identifier")
    if not identifier:
        raise ValueError(f"No identifier found for region: {region} and offer_type: {offer_type}")

    code = offer_request(identifier)
    framework_logger.info(f"Generated {offer_type} code: {code} for region: {region}")
    return code

def user_info_from_dashboard(page):  
    framework_logger.info("Waiting for /v3/usermgtsvc/users/me request...")
    
    try:
        with page.expect_response("**/v3/usermgtsvc/users/me", timeout=120000) as response_info:
            framework_logger.info("Reloading page...")
            page.reload()
        
        response = response_info.value
        request = response.request
        
        try:
            response_data = response.json()
        except Exception as e:
            framework_logger.warning(f"Failed to parse JSON: {e}")
            response_data = {"error": "Could not parse response as JSON"}
        
        captured_data = {
            'request': {
                'method': request.method,
                'url': request.url,
                'headers': dict(request.headers),
                'body': request.post_data
            },
            'response': {
                'status': response.status,
                'status_text': response.status_text,
                'headers': dict(response.headers),
                'data': response_data
            }
        }       

        print(captured_data)
        return captured_data
        
    except Exception as e:
        framework_logger.warning(f"No request to /v3/usermgtsvc/users/me was captured: {e}")
        return None

def request_me_by_dashboard(page):
    user_data = user_info_from_dashboard(page)
    print(user_data)
    token = user_data['request']['headers'].get('authorization', '').replace('Bearer ', '')
    url = f"{_instantink_url}/api/users/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    framework_logger.debug(f"Getting {url}, {headers}")
    response = session.get(url, headers=headers)
    framework_logger.info(f"Response: {response.status_code} {response.text}")
    response.raise_for_status()
    
    response_data = response.json()
    return response_data

def subscription_data_from_gemini(id):
    token = get_token_gemini_client()
    url = f"{_instantink_url}/api/users/subscriptions/{id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    framework_logger.debug(f"Getting {url}")
    response = session.get(url, headers=headers)
    framework_logger.info(f"Response: {response.status_code} {response.text}")
    response.raise_for_status()
    
    response_data = response.json()
    return response_data

def get_subscription_state(id):
    sub_data = subscription_data_from_gemini(id)
    try:
        subscription_state = sub_data['userSubInfo']['subscriptionInfo']['minSubInfo']['subscriptionState']
        return subscription_state
    except KeyError as e:
        return None

def get_subscription_state_by_me_from_dashboard(page):
    user_data = request_me_by_dashboard(page)
    try:
        subscription_state = user_data['userMinSubInfo']['minSubInfo'][0]['subscriptionState']
        return subscription_state
    except KeyError as e:
        return None

def validate_subscription_state(sub_id, expected_state):
    start_time = time.time()
    while time.time() - start_time < 60:
        state = get_subscription_state(sub_id)

        if state == expected_state:
            framework_logger.info(f"Subscription state is {expected_state}")
            break

        time.sleep(1)

    assert state == expected_state, f"Expected subscription state '{expected_state}', but got '{state}'"

def validate_subscription_state_by_me(page, expected_state):
    start_time = time.time()
    while time.time() - start_time < 60:
        state = get_subscription_state_by_me_from_dashboard(page)

        if state == expected_state:
            framework_logger.info(f"Subscription state is {expected_state}")
            break

        time.sleep(1)

    assert state == expected_state, f"Expected subscription state '{expected_state}', but got '{state}'"

def remove_printer_webservices(entity_id):
    framework_logger.info(f"Removing printer webservices for {entity_id}")
    url = f"https://g2sim.wpp.api.hp.com/wpp/simulator/printers/{entity_id}/webservices"
    response = session.delete(url)
    framework_logger.debug(f"Webservices removal response: {response.status_code} {response.text}")
    
    if response.status_code != 200:
        raise RuntimeError(f"Failed to remove webservices: HTTP {response.status_code}")
    framework_logger.info("Printer webservices removed successfully")

def enable_printer_webservices(entity_id):
    framework_logger.info(f"Enabling printer webservices for {entity_id}")
    url = f"https://g2sim.wpp.api.hp.com/wpp/simulator/printers/{entity_id}/webservices"
    response = session.put(url)
    framework_logger.debug(f"Webservices enabling response: {response.status_code} {response.text}")

    if response.status_code != 200:
        raise RuntimeError(f"Failed to enable webservices: HTTP {response.status_code}")
    framework_logger.info("Printer webservices enabled successfully")

def printer_colors():
    if _supplyvariant == "IPH":
        colors = ["CMY", "K"]
    elif _supplyvariant == "IIC":
        colors = ["K", "C", "M", "Y"]
    return colors

def parse_flexible_date(date_string):
    date_formats = [
        "%b %d, %Y, %I:%M:%S %p",     # Sep 14, 2025, 2:41:11 PM
        "%Y/%m/%d %I:%M:%S %p",       # 2025/09/14 02:41:13 PM  
        "%d %b %Y, %H:%M:%S",         # 14 Sep 2025, 14:41:13
        "%d/%m/%Y %H:%M:%S",          # 14/09/2025 14:41:13
        "%m/%d/%Y %I:%M:%S %p",       # 09/14/2025 2:41:11 PM
        "%B %d, %Y, %I:%M:%S %p",     # September 14, 2025, 2:41:11 PM
    ]
    
    for date_format in date_formats:
        try:
            return datetime.strptime(date_string, date_format)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: '{date_string}'")

def extract_date_from_text(text: str):
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    
    date_patterns = [
        r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)',  # Sep 14, 2025, 2:41:11 PM
        r'(\d{1,2}\s+[A-Za-z]{3}\s+\d{4},\s+\d{1,2}:\d{2}:\d{2})',           # 14 Sep 2025, 14:41:13
        r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)',            # 09/14/2025 2:41:11 PM
        r'(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)',            # 2025/09/14 02:41:13 PM
        r'([A-Za-z]{3,}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)', # September 14, 2025, 2:41:11 PM
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            date_string = match.group(1)
            framework_logger.info(f"Extracted date string: '{date_string}'")
            return parse_flexible_date(date_string)
    
    raise ValueError(f"Date not found in text: {cleaned_text}")

def get_plans_data():
    url = f"{_agena_url}/plans?country={_tenant_country_short}&program=i_ink&obsolete=false"
    token = get_token_gemini_client()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.agena+json;version=3",
        "Content-Type": "application/json"
    }
    framework_logger.debug(f"Getting plans {url}")
    response = session.get(url, headers=headers)
    response.raise_for_status()
    
    response_data = response.json()
    return response_data

def get_filtered_plan_data(key="pages", value=100):
    data = get_plans_data()
    value = int(value)
    matching = [p for p in data if p.get(key) == value]
    
    if not matching:
        raise ValueError(f"No {key} found with {value} pages")
    
    return matching

def billing_status_code():
    status = None
    if "credit_card" in _payment_method:
        status = "CPT-100"
        if  _card_payment_gateway == "2CO":
            status = "STRATUS-PAYMENT-COMPLETE"
    if "direct_debit" in _payment_method:
        status = "DIRECT-DEBIT-SUCCESS"
    if "paypal" in _payment_method:
        status = "PAY-PAL-SUCCESS"
    if "prepaid" in _payment_method:
        status = "PEGASUS-SUCCESS"
    return status

def request_event_response_status(full=False):
    refund_status_code = {
        "credit_card": {"full": "PAYMENT-GATEWAY-REFUNDED", "partial": "PAYMENT-GATEWAY-PARTIAL-REFUNDED"},
        "direct_debit": {"full": "DIRECT-DEBIT-REFUND-SUCCESS", "partial": "DIRECT-DEBIT-PARTIAL-REFUND-SUCCESS"},
        "paypal": {"full": "PAY-PAL-REFUNDED", "partial": "PAY-PAL-REFUND-PARTIAL"},
        "prepaid_only": {"full": "PEGASUS-REFUNDED", "partial": "PEGASUS-PARTIAL-REFUNDED"},
    }

    key = _payment_method
    if key.startswith("credit_card"):
        key = "credit_card"
    elif key.startswith("direct_debit"):
        key = "direct_debit"
    elif key.startswith("paypal"):
        key = "paypal"
    elif key.startswith("prepaid_only"):
        key = "prepaid_only"

    refund_by_payment_method = refund_status_code[key]
    if full:
        return refund_by_payment_method["full"]
    else:
        return refund_by_payment_method["partial"]

def refund_status(full=False):
    refund_status_code = {
        "credit_card": {"full": "FULL-REFUND", "partial": "PARTIAL-REFUND"},
        "direct_debit": {"full": "DIRECT-DEBIT-REFUND", "partial": "PARTIAL-REFUNDED"},
        "paypal": {"full": "PAY-PAL-REFUND", "partial": "PARTIAL-REFUND"},
        "prepaid_only": {"full": "PEGASUS-REFUNDED", "partial": "PARTIAL-REFUND"},
    }

    key = _payment_method
    if key.startswith("credit_card"):
        key = "credit_card"
    elif key.startswith("direct_debit"):
        key = "direct_debit"
    elif key.startswith("paypal"):
        key = "paypal"
    elif key.startswith("prepaid_only"):
        key = "prepaid_only"

    refund_by_payment_method = refund_status_code[key]
    if full:
        return refund_by_payment_method["full"]
    else:
        return refund_by_payment_method["partial"]

def payment_engine():
    payment_engine = None
    if "credit_card" in _payment_method:
        payment_engine = "payment_gateway"
        if  _card_payment_gateway == "2CO":
            payment_engine = "stratus"
    if "direct_debit" in _payment_method:
        payment_engine = "pgs_direct_debit"
    if "paypal" in _payment_method:
        payment_engine = "pgs_pay_pal"
    if "prepaid_only" in _payment_method:
        payment_engine = "pegasus"
    return payment_engine

def countries_without_states_mandate():
    countries =  ["Austria", "Belgium", "Denmark", "Finland", "France", "Germany", "Luxembourg", "Netherlands", 
                  "New Zealand", "Norway", "Portugal", "Puerto Rico", "Singapore", "Sweden", "Switzerland"]
    return countries

def countries_with_direct_debit():
    countries =  ["Belgium", "Denmark", "France", "Germany", "Italy",
                  "Netherlands", "Spain"]
    return countries

def is_element_actionable(page, locator):
    try:
        bounding_box = locator.bounding_box()
        if not bounding_box:
            return False

        center_x = bounding_box['x'] + bounding_box['width'] / 2
        center_y = bounding_box['y'] + bounding_box['height'] / 2

        is_top_element = page.evaluate(
            """([element, x, y]) => {
                const elementAtPoint = document.elementFromPoint(x, y);
                return element && (element === elementAtPoint || element.contains(elementAtPoint));
            }""",
            [locator.element_handle(), center_x, center_y]
        )

        return is_top_element

    except Exception:
        return False

def parse_json_string(json_string):
    try:
        return json.loads(json_string)
    except Exception as e:
        framework_logger.error(f"Failed to parse JSON string: {e}")
        raise

def printer_data():
    url = f"{_agena_url}/printer_skus/{_tenant_country_short}/{_derivative_model}"
    token = get_token_gemini_client()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.agena+json;version=3",
        "Content-Type": "application/json"
    }
    framework_logger.debug(f"Getting printer data {url}")
    response = session.get(url, headers=headers)
    response.raise_for_status()
    
    response_data = response.json()
    return response_data

def get_font_details(element):
    font_details = element.evaluate("""
        (element) => {
            const styles = window.getComputedStyle(element);
            return {
                'font-family': styles.getPropertyValue('font-family'),
                'font-size': styles.getPropertyValue('font-size'),
                'font-weight': styles.getPropertyValue('font-weight'),
                'font-style': styles.getPropertyValue('font-style'),
                'line-height': styles.getPropertyValue('line-height'),
                'letter-spacing': styles.getPropertyValue('letter-spacing'),
                'text-decoration': styles.getPropertyValue('text-decoration'),
                'text-transform': styles.getPropertyValue('text-transform'),
                'color': styles.getPropertyValue('color'),
                'font-variant': styles.getPropertyValue('font-variant'),
                'background-color': styles.getPropertyValue('background-color')
            };
        }
    """)      
    return font_details