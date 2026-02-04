from datetime import datetime, timedelta
from core.settings import framework_logger
from helper.ra_base_helper import RABaseHelper
import re
import test_flows_common.test_flows_common as common
import time
import re


class GeminiRAHelper():

    @staticmethod
    def access(page):
        page.goto(common._instantink_url + common._gemini_rails_admin_login_url, timeout=120000)
        page.wait_for_load_state("networkidle"); page.wait_for_load_state("load")

        alert_locator = page.locator("div.alert-warning.alert.alert-dismissible")
        if alert_locator.is_visible():
            framework_logger.info("[GeminiRAHelper] Already signed in to Gemini Rails Admin. Skipping login.")
            return

        page.locator("#admin_email, #admin_user_email").type(common._rails_admin_user)
        page.locator("#admin_password, #admin_user_password").type(common._rails_admin_password)
        page.locator("#admin_submit, input[type='submit']").click()

    def fill_and_assert_email(page, tenant_email):
            page.locator("#email").fill("")  # Clear first, just in case
            page.locator("#email").type(tenant_email)
            email_value = page.locator("#email").input_value()
            assert email_value == tenant_email, f"Expected email input value to be '{tenant_email}', but got '{email_value}'"
            return True

    @staticmethod
    def access_tenant_page(page, tenant_email: str):
        page.goto(common._instantink_url + common._gemini_fetch_tenant_url, timeout=120000)

        common.retry_operation(
            lambda: GeminiRAHelper.fill_and_assert_email(page, tenant_email),
            operation_name="Fill email input"
        )

        page.locator("input[type='submit']").click()
        page.wait_for_selector("[class^='table'] a", timeout=180000).click()
        RABaseHelper.wait_page_to_load(page, "Tenant")
        return common.last_number_from_url(page)

    @staticmethod
    def access_subscription_by_tenant(page, index=0):
        links = RABaseHelper.get_links_by_title(page, "Subscriptions")
        links.nth(index).click()
        RABaseHelper.wait_page_to_load(page, "Subscription")
        return common.last_number_from_url(page)

    @staticmethod
    def access_subscription(page):
        links = RABaseHelper.get_links_by_title(page, "Subscription")
        links.first.click()
        RABaseHelper.wait_page_to_load(page, "Subscription")
        return common.last_number_from_url(page)
    
    @staticmethod
    def access_stratus_tenant_info(page):
        RABaseHelper.access_menu_of_page(page, "Stratus Tenant Info")    
       
    @staticmethod
    def remove_free_months(page):
        RABaseHelper.access_menu_of_page(page, "Award Subscription Months")
        
        def remove_months_operation():
            dropdown = page.locator("#free_month_amount").last
            dropdown.select_option("-12")
            page.locator("#remove_months").first.click()
            page.locator("#remove_months").first.click()
            
            page_content = page.content()
            if "Current remaining_prepaid_months: 0" not in page_content:
                raise Exception("Free months not yet removed, retrying...")
            return True
        
        common.retry_operation(
            remove_months_operation,
            operation_name="Remove free months",
            max_attempts=10,
            delay=2
        )
        
        page.locator('a', has_text="<< Back to Subscription").click()
        RABaseHelper.wait_page_to_load(page, "Subscription")
    
    @staticmethod
    def subscription_to_subscribed(page):
        if RABaseHelper.get_field_text_by_title(page, "State") != "subscribed":
            RABaseHelper.access_menu_of_page(page, "Edit")
            dropdown = page.locator("#subscription_state_event")
            try:
                dropdown.select_option("event_hise_pens_inserted")
            except Exception as e:
                framework_logger.error(f"Error selecting dropdown option: {e}")

            save_button = page.locator("[class='btn btn-primary']")
            save_button.scroll_into_view_if_needed()
            save_button.click()

        RABaseHelper.wait_page_to_load(page, "Subscription")
        assert RABaseHelper.get_field_text_by_title(page, "State") == "subscribed"

    @staticmethod
    def force_subscription_to_obsolete(page):
        RABaseHelper.access_menu_of_page(page, "Obsolete It")
        obsolete_link = page.locator('a:nth-child(7)')
        obsolete_link.click()
        assert RABaseHelper.get_field_text_by_title(page, "State") == "obsolete"

    @staticmethod
    def update_subscription_rpl(page):
        RABaseHelper.access_menu_of_page(page, "Update Subscription RPL")
        page.locator("#rpl_state").select_option("CLEAR")
        page.locator('[value="Update"]').click()
        page.locator('a', has_text="<< Back to Subscription").click()
        RABaseHelper.wait_page_to_load(page, "Subscription")

    @staticmethod
    def ship_cartridge(page, kit_type="welcome", colors=None):
        RABaseHelper.access_menu_of_page(page, "Ship it")
        
        assert kit_type in ["welcome", "replenishment"], "Invalid kit type"
        page.locator(f'#{kit_type}').set_checked(True)

        if colors:
            for color in colors:
                assert color in ["K", "CMY", "C", "M", "Y"], "Invalid color"
                page.locator(f'#{color.lower()}_supply').set_checked(True)

        page.locator('input[type=submit][value="Ship Ink Now"]').click()

        alert_text = page.locator("p.alert").inner_text()
        match = re.search(r"trigger id (\w+)", alert_text)
        trigger_id = match.group(1) if match else ""
        return trigger_id
    
    @staticmethod
    def click_calculate_retention(page):
        RABaseHelper.access_menu_of_page(page, "Calculate retention")
        page.wait_for_selector('.alert-success', timeout=120000)
        assert page.is_visible('.alert-success')
    
    @staticmethod
    def process_new_kit(page, tenant_email=None, kit_type="welcome"):
        if tenant_email != None:
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)

        # GRA subscription move to subscribed
        GeminiRAHelper.subscription_to_subscribed(page)

        # GRA subscription Update Subscription RPL
        GeminiRAHelper.update_subscription_rpl(page)

        # GRA subscription ship it
        colors = common.printer_colors()
        trigger_id = GeminiRAHelper.ship_cartridge(page, kit_type, colors)
        return trigger_id
    
    @staticmethod
    def replenishment_kit_shipped_with_colors(page, colors):
        RABaseHelper.access_menu_of_page(page, "Replenishment Kit Shipped")
        page.locator("#replenishment_kit_colors").fill(colors)
        page.locator("[value='Ship']").click()
        page.wait_for_selector('.alert-success', timeout=120000)
        assert "Replenishment kit shipped successfully" in page.inner_text('.alert-success')
        framework_logger.info(f"Replenishment kit shipped with colors: {colors}")
    
    @staticmethod
    def verify_notification_events(page, notification, tenant_email=None):
        if tenant_email != None:
            GeminiRAHelper.access(page)
            GeminiRAHelper.access_tenant_page(page, tenant_email)
            GeminiRAHelper.access_subscription_by_tenant(page)

        link_urls = RABaseHelper.get_link_urls_by_title(page, "Notification events")
        event_found = False
        
        for link_url in link_urls:
            page.goto(common._instantink_url + link_url)
            try:
                field_value = RABaseHelper.get_field_text_by_title(page, "Event variant")
                assert notification in field_value, f"Expected '{notification}' in 'Event variant', but got '{field_value}'"
                event_found = True
                break
            except AssertionError:
                continue

        if not event_found:
            raise AssertionError(f"Event variant '{notification}' not found in notification events.")

    @staticmethod    
    def get_access_token(page):   
        access_token = page.evaluate("""
            async () => await window.Shell.v1.authProvider.getAccessToken()
        """)
        return access_token

    @staticmethod
    def stratus_register_device(page, access_token, postcard, fingerprint, model_number, device_uuid):
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            page.locator(".stratus_register_device_member_link").click(timeout=120000)
            page.locator("#access_token").fill(access_token)
            page.locator("#claim_postcard").fill(postcard)
            page.locator("#fingerprint").fill(fingerprint)
            page.locator("#product_number").fill(model_number)
            page.locator("#uuid").fill(device_uuid)
            page.locator("[value='Register Device']").click()
            result_message = page.locator("div.alert").text_content(timeout=120000)
            if "Registered device successfully" in result_message:
                break
            elif attempt == max_attempts:
                raise AssertionError("Failed to register device after multiple attempts: " + str(result_message))

    @staticmethod
    def event_shift(page, event_shift, force_billing=True):
        RABaseHelper.access_menu_of_page(page, "Edit")
        page.fill('#subscription_rollback', event_shift)
        page.wait_for_selector("#subscription_create_billing_cycle_after_rollback")
        if force_billing:
            page.locator("#subscription_create_billing_cycle_after_rollback").click()
            page.wait_for_selector("#subscription_create_billing_cycle_after_rollback").is_checked()
        page.wait_for_selector(".btn.btn-primary", timeout=120000).click()
        page.wait_for_selector('.alert-success', timeout=10000)
        assert page.is_visible('.alert-success')

    @staticmethod
    def access_first_billing_cycle(page):
        RABaseHelper.access_menu_of_page(page, 'View Billing Summary')
        page.wait_for_selector(".table.table-striped.table-bordered > tbody > tr:nth-child(3) > .id", timeout=120000).click()

    @staticmethod
    def access_second_billing_cycle(page, status_code=None):
        start_time = time.time()
        
        while time.time() - start_time < 1800:
            try:
                RABaseHelper.access_menu_of_page(page, 'View Billing Summary')
                                
                row = page.locator(".table.table-striped.table-bordered > tbody > tr:nth-child(4)")

                if status_code and row:
                    current_status = row.locator(".status-code").inner_text().strip()
                    if current_status != status_code:
                        continue
                
                row.locator(".id a").click()
                break
                
            except Exception as e:
                framework_logger.warning(f"Attempt failed: {str(e)}")
                
                try:
                    page.locator(".table.table-striped.table-bordered > tbody > tr:nth-child(1) a").click(timeout=1000)
                except Exception:
                    pass
            
    @staticmethod
    def access_third_billing_cycle(page):
        RABaseHelper.access_menu_of_page(page, 'View Billing Summary')
        page.wait_for_selector(".table.table-striped.table-bordered > tbody > tr:nth-child(5) > .id", timeout=30000).click()

    @staticmethod
    def calculate_and_define_page_tally(page, tally):
        try:
            GeminiRAHelper.calculate_page_tally(page)
        except Exception as e:
            pass
        GeminiRAHelper.define_page_tally(page, tally)

    @staticmethod
    def calculate_page_tally(page):
        RABaseHelper.access_menu_of_page(page, 'Calculate page tally')
        page.wait_for_selector('.alert-success', timeout=150000)
        assert "Successfully calculated page tally" in page.inner_text('.alert-success')
    
    @staticmethod
    def define_page_tally(page, tally):
        RABaseHelper.access_menu_of_page(page, 'Edit')
        page.fill('#billing_cycle_page_tally', str(tally))
        page.wait_for_selector(".btn.btn-primary", timeout=120000).click()
        page.wait_for_selector('.alert-success', timeout=120000)
        assert "Billing cycle successfully" in page.inner_text('.alert-success')

    @staticmethod
    def submit_charge(page):
        RABaseHelper.access_menu_of_page(page, 'Submit Charge')
        page.wait_for_selector(".btn.btn-warning", timeout=120000).click()
        page.wait_for_selector('.alert-success', timeout=150000)
        assert "Billing cycle has been charged" in page.inner_text('.alert-success')

    @staticmethod
    def billing_cycle_data(page, plan, tally, status, charge_complete, billable_type):
        page.wait_for_selector('//a[starts-with(text(), "Subscription #")]', timeout=120000)
        page.locator('//a[starts-with(text(), "Subscription #")]').click()
        RABaseHelper.access_menu_of_page(page, "View Billing Summary")

        page.wait_for_selector('//a[starts-with(text(), "Subscription #")]')
        rows = page.locator('tr[id^="bc-"]')
        count = rows.count()
        found = False

        for i in range(count):
            row = rows.nth(i)
            plan_val = row.locator('.plan-pages').inner_text().strip()
            tally_val = row.locator('.page-tally').inner_text().strip()
            status_val = row.locator('.status-code').inner_text().strip()
            billable_type_val = row.locator('.type').inner_text().strip()
            charge_complete_val = row.locator('.charge-complete span').inner_text().strip() == "✓"

            if (plan_val == plan and tally_val == tally and status_val == status and
                billable_type_val == billable_type and str(charge_complete_val).lower() == str(charge_complete).lower()):
                print(f"Plan: {plan_val}, Tally: {tally_val}, Status: {status_val}, Billable Type: {billable_type_val}, Charge Complete: {charge_complete_val}")
                found = True
                break

        assert found, "Billing cycle with expected data not found"

    @staticmethod
    def add_free_pages_visible(page, free_pages: str):
        RABaseHelper.access_menu_of_page(page, "Edit")
        page.fill('#billing_cycle_free_pages_visible', free_pages)
        page.locator(".btn.btn-primary").click()
        assert "Billing cycle successfully" in page.inner_text('.alert-success')

    @staticmethod
    def set_printed_pages(page, tally: str):
        RABaseHelper.access_menu_of_page(page, "Edit")
        page.fill('#billing_cycle_page_tally', tally)
        page.locator(".btn.btn-primary").click()
        assert "Billing cycle successfully" in page.inner_text('.alert-success')
    
    @staticmethod
    def verify_rails_admin_info(page, title, value, retry=True):
        def operation():
            field_title = RABaseHelper.get_field_text_by_title(page, title)
            assert field_title == value, f"Expected '{value}', got '{field_title}'"
            framework_logger.info(f"Verified {title} is '{value}' on the page.")
            return True

        def on_retry():
            framework_logger.info(f"Retrying verification of {title}, reloading page...")
            page.reload()
            page.wait_for_load_state("load")

        max_attempts = 12 if retry else 1
        common.retry_operation(
            operation,
            operation_name=f"Verify {title} info",
            max_attempts=max_attempts,
            delay=10,
            on_retry=on_retry if retry else None
        )

    @staticmethod
    def verify_rails_admin_info_contains(page, title, expected_text, retry=True): 
        def operation(): 
            field_text = RABaseHelper.get_field_text_by_title(page, title)
            assert expected_text in field_text, f"Expected '{expected_text}' to be contained in '{field_text}'"
            framework_logger.info(f"Verified {title} contains '{expected_text}' in text: '{field_text}'")
            return True
        
        def on_retry():
            page.reload()

        max_attempts = 12 if retry else 1
        common.retry_operation(
            operation,
            operation_name=f"Verify {title} info",
            max_attempts=max_attempts,
            delay=10,
            on_retry=on_retry
        )

    @staticmethod
    def click_billing_cycle_by_status(page, status_code):
        RABaseHelper.access_menu_of_page(page, "View Billing Summary")
        page.wait_for_selector('table.table-striped.table-bordered', timeout=30000)

        rows = page.locator('tr[id^="bc-"]')
        row_count = rows.count()

        for i in range(row_count - 1, -1, -1):
            row = rows.nth(i)
            current_status = row.locator('.status-code').inner_text().strip()

            if current_status == status_code:
                billing_id_link = row.locator('.id a')
                billing_id_link.click()
                return

        raise ValueError(f"No billing cycle found with status code '{status_code}'")
        
    @staticmethod
    def check_printer_offline_message(page, offline_message, timeout=30000):
        RABaseHelper.check_printer_offline_message(page, '[class^="connectivityBanner__connectivity-banner"]')    
        try:
            element = page.locator(offline_message)
            element.wait_for(state="visible", timeout=timeout)
            print("\tWARNING: Printer is already offline!")
        except Exception:
            pass

    @staticmethod
    def set_printer_offline(page, printer_serial):
        RABaseHelper.access_menu_of_page(page, "Printers")

        page.locator(f'tr[data-testid="printer-selector"]').click()
        page.wait_for_selector('.alert-success', timeout=10000)
        assert "Printer set to offline" in page.inner_text('.alert-success')
        print(f"Printer {printer_serial} set to offline successfully.")

    @staticmethod
    def manual_retry_until_complete(page, max_attempts=10):
        framework_logger.info("Starting manual retry process...")
        retry_count = 0

        while retry_count < max_attempts:
            try:
                manual_retry_button = page.locator('.nav-item.icon.manual_retry_member_link')

                if manual_retry_button.is_visible(timeout=2000):
                    framework_logger.info(f"Manual retry button found, attempt {retry_count + 1}")
                    manual_retry_button.click()
                    framework_logger.info("Clicked on manual retry button")

                    try:
                        confirm_button = page.locator('input[value="Yes, I\'m very sure"], button:has-text("Yes, I\'m very sure")')
                        confirm_button.wait_for(state="visible", timeout=5000)
                        confirm_button.click()
                        framework_logger.info("Clicked 'Yes, I'm very sure' confirmation button")

                        page.wait_for_timeout(2000)

                    except Exception as e:
                        framework_logger.warning(f"Confirmation button not found or clickable: {e}")
                        break

                    retry_count += 1

                else:
                    framework_logger.info("Manual retry button no longer visible, process complete")
                    break

            except Exception as e:
                framework_logger.info(f"Manual retry process failed: {e}")

    def click_link_by_text_on_rails_admin(page, link_text, section_header):
        try:
            item_title = page.locator("[class^='card-header'] a", has_text=section_header).locator("xpath=../..")
            if not item_title.is_visible():
                raise Exception
        except Exception:
            item_title = page.locator("[class='card'] span", has_text=section_header).locator("xpath=..")

        item_links = item_title.locator("[class^='card-body'] a")
        count = item_links.count()
        clicked = False

        for i in range(count):
            if link_text in item_links.nth(i).inner_text():
                item_links.nth(i).click()
                clicked = True
                break
        assert clicked, f"Link with text '{link_text}' not found in section '{section_header}'"

    @staticmethod
    def get_billing_cycle_times(page):
        start_time = RABaseHelper.get_field_text_by_title(page, "Start time")
        end_time = RABaseHelper.get_field_text_by_title(page, "End time")
        return start_time, end_time

    @staticmethod
    def update_to_payment_problem(page):
        RABaseHelper.access_menu_of_page(page, 'Edit')
        page.locator('.btn.btn-info.dropdown-toggle').nth(3).click()
        page.locator('li.ui-menu-item').nth(2).click()
        page.locator('.btn.btn-primary').first.click()

    @staticmethod
    def set_pgs_override_response_successfully(page):
        RABaseHelper.access_menu_of_page(page, 'Edit')
        page.locator('.btn.btn-info.dropdown-toggle').nth(3).click()
        page.locator('li.ui-menu-item').nth(1).click()
        page.locator('.btn.btn-primary').first.click()

    @staticmethod
    def set_status_code(page, status_code):
        RABaseHelper.access_menu_of_page(page, 'Edit')
        page.fill('#billing_cycle_status_code', status_code)
        page.locator('.btn.btn-primary').first.click()
        page.wait_for_selector('.alert-success', timeout=10000)
        assert "Billing cycle successfully" in page.inner_text('.alert-success')
        
    @staticmethod
    def add_pages_by_rtp(page, additional_pages: str):
        links = RABaseHelper.get_links_by_title(page, "Printer")
        links.first.click()
        RABaseHelper.wait_page_to_load(page, "Printer")
        RABaseHelper.access_menu_of_page(page, "Stratus Page Count")
        page.fill('#pages_printed', additional_pages)
        page.locator('.btn.btn-primary').click()
        RABaseHelper.wait_page_to_load(page, "Printer")

    @staticmethod
    def set_expire_information(page, expire_month, expire_year):
        RABaseHelper.access_menu_of_page(page, 'Edit')
        page.fill('#charger_models_pgs_credential_expire_month', expire_month)
        page.fill('#charger_models_pgs_credential_expire_year', expire_year)
        page.locator('.btn.btn-primary').first.click()
        page.wait_for_selector('.alert-success', timeout=10000)
        assert "Pgs credential successfully updated" in page.inner_text('.alert-success')

    @staticmethod
    def set_almost_expired_credit_card(page):
        now = datetime.now()
        expire_month = f"{now.month:02d}"
        expire_year = str(now.year)

        RABaseHelper.access_menu_of_page(page, 'Edit')
        page.fill('#charger_models_pgs_credential_expire_month', expire_month)
        page.fill('#charger_models_pgs_credential_expire_year', expire_year)
        page.locator('.btn.btn-primary').first.click()
        page.wait_for_selector('.alert-success', timeout=10000)
        assert "Pgs credential successfully updated" in page.inner_text('.alert-success')
    
    @staticmethod
    def make_refund_option(page, refund_option, blocks=None):
        for attempt in range(60):
            try:
                RABaseHelper.access_menu_of_page(page, "Refund Payment")
                page.locator("#refund-option").click()
                page.locator("#refund-option").select_option(refund_option)
                
                if refund_option == "Instant Ink Overage Blocks":
                    page.locator("#overage_amount").fill(str(blocks))
                    page.locator('#overage_amount').press("NumpadEnter")
                    page.locator("#showIIOverageOptions > div > form > input.btn.btn-warning").click()
                else:
                    page.get_by_role("button", name="Submit").click()
                
                page.locator(".btn.btn-warning.one-click-only").click()
                
                # Wait for success message
                page.wait_for_selector('.alert-success', timeout=10000)
                message = page.inner_text('.alert-success')
                assert page.is_visible('.alert-success')
                
                framework_logger.info(f"Refund successful: {message}")
                return
                
            except Exception as e:
                if attempt == 59:  # Last attempt
                    framework_logger.error(f"Refund failed after 60 attempts: {e}")
                    raise
                framework_logger.warning(f"Refund attempt {attempt + 1}/60 failed, retrying...")
                time.sleep(2)
                page.reload()

    def complete_jobs(page, jobs=[]):
        RABaseHelper.complete_jobs(page, common._instantink_url, jobs)

    @staticmethod
    def verify_charge_complete(page):
        GeminiRAHelper.verify_field_is_true(page, "Charge complete")

    @staticmethod
    def verify_field_is_true(page, title):
        timeout = time.time() + 1800
        while time.time() < timeout:
            field_complete = RABaseHelper.get_boolean_value_by_title(page, title)
            if field_complete:
                break
            time.sleep(10)
            page.reload()
        assert field_complete is True, f"'{title}' is not True, got {field_complete}"
        framework_logger.info(f"'{title}' is true")

    @staticmethod
    def verify_field_is_false(page, title):
        timeout = time.time() + 1800
        while time.time() < timeout:
            field_complete = RABaseHelper.get_boolean_value_by_title(page, title)
            if field_complete is False:
                break
            time.sleep(10)
            page.reload()
        assert field_complete is False, f"'{title}' is not False, got {field_complete}"
        framework_logger.info(f"'{title}' is false")

    @staticmethod
    def verify_field_is_positive(page, title):
        field_text = RABaseHelper.get_field_text_by_title(page, title)
        
        try:
            field_value = int(field_text)
        except ValueError:
            raise AssertionError(f"Field '{title}' value '{field_text}' is not a valid integer")
        
        assert field_value >= 1, f"Expected field '{title}' to be positive (>= 1), but got {field_value}"
        framework_logger.info(f"Verified {title} is positive: {field_value}")

    @staticmethod
    def verify_field_is_negative(page, title):
        field_text = RABaseHelper.get_field_text_by_title(page, title)
        
        try:
            field_value = int(field_text)
        except ValueError:
            raise AssertionError(f"Field '{title}' value '{field_text}' is not a valid integer")

        assert field_value < 0, f"Expected field '{title}' to be negative (< 0), but got {field_value}"
        framework_logger.info(f"Verified {title} is negative: {field_value}")

    @staticmethod
    def one_time_charge(page, value: str):
        RABaseHelper.access_menu_of_page(page, "One Time Charge")
        page.fill('#charge_amount_cents_price', value)
        page.locator('[value="Generate One Time Charge"]').click()
        page.locator('[value="Yes, I\'m very sure"]').click()
        page.wait_for_selector('.alert-success', timeout=30000)

    @staticmethod
    def pgs_direct_debit_credential_edit(page, value):
            direct_debit_credential = RABaseHelper.get_links_by_title(page, "Pgs direct debit credential")
            direct_debit_credential.click()
            token = RABaseHelper.get_field_text_by_title(page, "Token")
            page.wait_for_selector(".nav-item.icon.edit_record_member_link", timeout=120000).click()
            page.fill('#charger_models_pgs_direct_debit_credential_token', str(value))
            
            if value == "token":
                page.fill('#charger_models_pgs_direct_debit_credential_token', token)

            page.locator("[class='btn btn-primary']").click()
            page.wait_for_selector('.alert-success', timeout=30000)

    @staticmethod
    def pgs_paypal_credential_edit(page, value):
            paypal_credential = RABaseHelper.get_links_by_title(page, "Pgs pay pal credential")
            paypal_credential.click()
            
            agreement_identifier =  RABaseHelper.get_field_text_by_title(page, "Agreement identifier")
            token = RABaseHelper.get_field_text_by_title(page, "Token")
            
            page.wait_for_selector(".nav-item.icon.edit_record_member_link", timeout=120000).click()
            page.fill('#charger_models_pgs_pay_pal_credential_agreement_identifier', str(value))
            page.fill('#charger_models_pgs_pay_pal_credential_token', str(value))
            
            if value == "token":
                page.fill('#charger_models_pgs_direct_debit_credential_token', token)
                page.fill('#charger_models_pgs_pay_pal_credential_agreement_identifier', agreement_identifier)

            page.locator("[class='btn btn-primary']").click()
            page.wait_for_selector('.alert-success', timeout=30000)

    @staticmethod
    def updates_pgs_override(page, status):
        RABaseHelper.access_menu_of_page(page, 'Edit')
        page.locator("div[data-input-for=billing_cycle_pgs_direct_debit_override] > span > label").click()
        page.fill('div[data-input-for="billing_cycle_pgs_direct_debit_override"] > input', status)
        page.wait_for_selector(".btn.btn-primary", timeout=120000).click()
        page.locator('li[class=ui-menu-item]').click()
        page.locator("[class='btn btn-primary']").click()

    @staticmethod
    def verify_refund_complete(page):
        timeout = time.time() + 1800
        while time.time() < timeout:
            refund_complete = RABaseHelper.get_boolean_value_by_title(page, "Refund complete")
            if refund_complete:
                break               
            time.sleep(10)
            page.reload()
        assert refund_complete is True, f"Refund complete is not True, got {refund_complete}"
        framework_logger.info("Refund complete")
 
    @staticmethod
    def billing_purchase_refund_total_payment(page):
        RABaseHelper.access_menu_of_page(page, 'Refund Payment')
        page.locator('input[value="Refund Total Payment"]').click()       
        page.locator('input[value="OK"]').click()
        page.wait_for_selector('.alert-success', timeout=60000)
        
    @staticmethod
    def update_direct_debit_status(page):
        RABaseHelper.wait_page_to_load(page, "Billing cycle")
        billing_page = page.url
        status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
        if (status_code in ["DIRECT-DEBIT-PENDING", "DIRECT-DEBIT-RETRYABLE"]):
            RABaseHelper.access_menu_of_page(page, 'Edit')
            page.locator("#billing_cycle_pgs_direct_debit_override").select_option("SETTLED", force=True)
            page.wait_for_selector(".btn.btn-primary", timeout=120000).click()
            RABaseHelper.get_links_by_title(page, "Subscription").click()
            RABaseHelper.wait_page_to_load(page, "Subscription")
            GeminiRAHelper.event_shift(page, "8", False)
            GeminiRAHelper.complete_jobs(page, ["TransitionBillingCycleStateDispatcherJob"])
            page.goto(billing_page)
            RABaseHelper.wait_page_to_load(page, "Billing cycle")
            GeminiRAHelper.verify_rails_admin_info(page, "Status code", "DIRECT-DEBIT-SUCCESS", True)
            framework_logger.info("Direct debit status updated")
        else:
            framework_logger.info("it was not necessary to update the status")

    @staticmethod
    def update_direct_debit_status_after_refund(page):
        RABaseHelper.wait_page_to_load(page, "Billing cycle")
        status_code = RABaseHelper.get_field_text_by_title(page, "Status code")
        if (status_code == "DIRECT-DEBIT-REFUND-PENDING"):
            RABaseHelper.access_menu_of_page(page, 'Edit')
            page.locator("#billing_cycle_pgs_direct_debit_override").select_option("REFUNDED", force=True)
            page.wait_for_selector(".btn.btn-primary", timeout=120000).click()
            framework_logger.info("Direct debit status updated")
        else:
            framework_logger.info("it was not necessary to update the status")

    @staticmethod
    def get_template_data(page, key):
        template_data = page.locator('[class="page-content"] pre').inner_text()
        json_data = common.parse_json_string(template_data)
        return json_data.get(key, None)

    @staticmethod
    def perform_billing_cycle(page, tenant_email, days, tally):
        GeminiRAHelper.access_tenant_page(page, tenant_email)
        GeminiRAHelper.access_subscription_by_tenant(page)
        GeminiRAHelper.event_shift(page, days)
        GeminiRAHelper.access_second_billing_cycle(page, "-")
        GeminiRAHelper.calculate_and_define_page_tally(page, tally)
        GeminiRAHelper.submit_charge(page)
        framework_logger.info(f"Submitted charge for 100 pages")

    @staticmethod
    def click_on_welcome_kit_and_fetch_trigger_id(page):
        page.locator("xpath=//a[contains(text(), 'WelcomeKitShipment')]").scroll_into_view_if_needed()
        page.locator("xpath=//a[contains(text(), 'WelcomeKitShipment')]").click()
        trigger_id = page.locator("xpath=//*[contains(text(), 'Agena trigger' )]//..//div[@class='card-body']").inner_text()
        return trigger_id
    
    @staticmethod
    def flip_approval_date(page):
        page.locator("xpath=//a[contains(text(), 'FlipTheModelSubscription')]").scroll_into_view_if_needed()
        page.locator("xpath=//a[contains(text(), 'FlipTheModelSubscription')]").click()
        approval_date = page.locator("xpath=//*[contains(text(), 'Flip approval date' )]//..//div[@class='card-body']").inner_text()
        return approval_date

    @staticmethod
    def run_ship_supplies_job(page):
        # Scroll to and click the Gemini Resque link, which opens a new window/tab
        gemini_resque = page.locator("xpath=//*[contains(text(), 'Gemini Resque')]")
        gemini_resque.scroll_into_view_if_needed()
        with page.expect_popup() as popup_info:
            gemini_resque.click()
        new_page = popup_info.value
        new_page.wait_for_load_state()

        # Click the 'Schedule' link in the new window/tab
        schedule_link = new_page.locator("xpath=//a[text()='Schedule']")
        schedule_link.scroll_into_view_if_needed()
        schedule_link.click()

        # Scroll to and click the 'Queue now' button for ShipSuppliesDispatcherJob
        target = new_page.locator("xpath=//input[@value='ShipSuppliesDispatcherJob']//..//input[@value='Queue now']")
        target.scroll_into_view_if_needed()
        target.click()
        framework_logger.info("Clicked 'Queue now' for ShipSuppliesDispatcherJob")
        new_page.close()
        page.bring_to_front()
        time.sleep(300)  # Wait for 5 minutes to allow the job to complete
        framework_logger.info("Waited 5 minutes for job to complete and get trigger id")

    @staticmethod
    def activate_pilot(page):
        if RABaseHelper.get_field_text_by_title(page, "State") != "active":
            RABaseHelper.access_menu_of_page(page, "Edit")
   
            page.locator('#pilot_subscription_activation_date_field [class="input-group"]').click()
            page.locator(".flatpickr-prev-month").first.click()
            page.wait_for_timeout(500)
            target_date = datetime.now() - timedelta(days=31)
            target_day = target_date.day
            day_selector = f".flatpickr-day:not(.flatpickr-disabled):has-text('{target_day}')"
            try:
                page.locator(day_selector).first.click()
                framework_logger.info(f"Selected day {target_day} from previous month")
            except Exception as e:
                framework_logger.error(f"Error selecting day {target_day}: {e}")

            page.click('body', position={'x': 50, 'y': 50})

            dropdown = page.locator("#pilot_subscription_state_event")
            try:
                dropdown.select_option("event_activated")
            except Exception as e:
                framework_logger.error(f"Error selecting dropdown option: {e}")

            save_button = page.locator("[class='btn btn-primary']")
            save_button.scroll_into_view_if_needed()
            save_button.click()

        RABaseHelper.wait_page_to_load(page, "Pilot subscription")
        assert RABaseHelper.get_field_text_by_title(page, "State") == "active"
