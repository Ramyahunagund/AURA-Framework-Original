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
from test_flows.EnrollmentInkWeb.enrollment_ink_web import enrollment_ink_web
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def billing_purchase(stage_callback):
    framework_logger.info("=== Billing Purchase flow started ===")
    tenant_email = enrollment_ink_web(stage_callback)
    with PlaywrightManager() as page:
        try:
            page.goto(common._instantink_url + common._gemini_rails_admin_login_url)

            page.wait_for_load_state("networkidle"); page.wait_for_load_state("load")

            page.locator("#admin_email, #admin_user_email").fill(common._rails_admin_user)
            page.locator("#admin_password, #admin_user_password").fill(common._rails_admin_password),

            page.locator("[name='commit']").click()

            page.goto(common._instantink_url + common._gemini_fetch_tenant_url)
            page.locator("#email").fill(tenant_email)
            page.locator("input[type='submit']").click()
            page.wait_for_selector("[class^='table'] a", timeout=180000).click()
            page.wait_for_selector("[class^='card-body'] a:has-text('Subscription')")
            links = page.locator("[class^='card-body'] a:has-text('Subscription')")

            assert links.count() > 0, "No subscription  found"

            links.first.click()

            if not page.wait_for_selector("div[class='card-body']:has-text('subscribed')").is_visible():
                page.wait_for_selector("nav-item:has-text('Edit') a").click()    
                dropdown = page.locator("#subscription_state_event")
                dropdown.select_option("event_hise_pens_inserted")

                save_button = page.locator("[class='btn btn-primary']")
                save_button.scroll_into_view_if_needed()
                save_button.click()
            page.wait_for_selector("li.nav-item:has-text('One Time Charge') a").click() 
            page.wait_for_selector("h1:has-text('Create a One Time Charge')", timeout=180000)
            page.locator("#charge_amount_cents_price").fill("199")
            page.locator("input[type='submit'][value=\"Generate One Time Charge\"]").click()
            page.wait_for_selector("input[type='submit'][value=\"Yes, I'm very sure\"]").click()

            page.wait_for_selector("[class^='card-body'] a:has-text('Subscription')")
            links = page.locator("[class^='card-body'] a:has-text('Subscription')")

            assert links.count() > 0, "No subscription  found"
            links.first.click()

            page.wait_for_selector(f"ul.nav.nav-tabs li.nav-item:has-text('View Billing Summary') a").click()  
            
            page.wait_for_selector("table") 
            first_row = page.locator("table.table-striped.table-bordered tbody tr:nth-of-type(3)")

            billable_type = first_row.locator("td.type").inner_text() == "BillingPurchase"
            charge_complete = first_row.locator("td.charge-complete span.badge-success").is_visible()
            status_code = first_row.locator("td.status-code").inner_text() == "CPT-100"
            page_tally = first_row.locator("td.page-tally").inner_text() == "-"
            plan_pages = first_row.locator("td.plan-pages").inner_text() == "-"

            assert billable_type and charge_complete and status_code and page_tally and plan_pages, "Incorrect data found"

            page.close()
            framework_logger.info("Billing Enrollment completed successfully")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Billing Enrollment: {e}\n{traceback.format_exc()}")
            raise e
