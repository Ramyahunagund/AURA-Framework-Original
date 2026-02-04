# test_flows/BillingCycle/billing_cycle.py

import os
import time
import random
import string
import base64
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState
from core.settings import framework_logger
from helper.gemini_ra_helper import GeminiRAHelper
from pages.sign_in_page import SignInPage
from test_flows.CreateIISubscription.create_ii_subscription import create_ii_subscription
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

# C1234567
def billing_cycle(stage_callback):
    tenant_email = create_ii_subscription(stage_callback)
    framework_logger.info("=== Billing Cycle flow started ===")

    with PlaywrightManager() as page:
        try:
            # Access Rails Admin
            GeminiRAHelper.access(page)
            framework_logger.info("Login on Gemini Rails Admin")

            GeminiRAHelper.perform_billing_cycle(page, tenant_email, "32", "100")

            #Billing Cycle Data
            GeminiRAHelper.billing_cycle_data(page, plan="100", tally="100", status="NO-CHARGE", charge_complete="true", billable_type="BillingCycle")          
            framework_logger.info("=== BillingCycle flow completed ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the Billing Enrollment: {e}\n{traceback.format_exc()}")
            raise e
