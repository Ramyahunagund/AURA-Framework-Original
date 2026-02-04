from datetime import timedelta
import datetime
import json
import time
import test_flows_common.test_flows_common as common

class RABaseHelper:

    @staticmethod
    def wait_page_to_load(page, page_title, timeout=60000):
        page.wait_for_selector(f"h1:has-text('Details for {page_title}')", timeout=timeout)

    @staticmethod
    def access_resque(page, base_url):
        page.goto(base_url + "/resque/schedule")

    @staticmethod
    def run_job(page, base_url, job_name):
        row_selector = f"tr:has(td:text-is('{job_name}'))"
        button_selector = f"{row_selector} input[value='Queue now']"
        page.wait_for_selector(button_selector, state="visible").click()
        page.wait_for_selector("h1.wi:has-text('Queues')")
        page.goto(base_url + "/resque/working")
        RABaseHelper.wait_for_job_to_disappear(page, f"{job_name}")

    @staticmethod
    def complete_jobs(page, base_url, jobs=[]):
        for job in jobs:
            RABaseHelper.access_resque(page, base_url)
            RABaseHelper.run_job(page, base_url, job)

    @staticmethod
    def wait_for_job_to_disappear(page, job_name: str, timeout: int = 60):
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                page.wait_for_selector("table.workers", timeout=5000)
                
                table_rows = page.locator("table.workers tbody tr:not(:first-child)")
                
                job_found = False
                for i in range(table_rows.count()):
                    row = table_rows.nth(i)
                    queue_cell = row.locator("td.queues")
                    queue_text = queue_cell.text_content()
                    
                    if queue_text and job_name in queue_text:
                        job_found = True
                        break
                
                if not job_found:
                    return 
                
                page.wait_for_timeout(2000) 
                page.reload()
                page.wait_for_load_state("networkidle")
                
            except Exception as e:
                return

        raise RuntimeError(f"Timeout: Job '{job_name}' is still present after {timeout} seconds")

    @staticmethod
    def access_page(page, page_name):
        page.locator(f'//a[@class="nav-link" and normalize-space(text())="{page_name}"]').click()    

    @staticmethod
    def access_menu_of_page(page, menu):
        page.wait_for_selector(f"[class^='nav-item']:has-text('{menu}')").click(timeout=120000)

    @staticmethod
    def get_item_by_title(page, title):
        combined_selector = f"div.card:has(h5.card-header:text-is('{title}'), h5.card-header a:text-is('{title}'))"
        card = page.locator(combined_selector)
        
        if card.count() == 0:
            page.wait_for_selector(combined_selector, timeout=10000)
        if card.count() == 0:
            raise ValueError(f"Field with title '{title}' not found.")
        
        return card.locator("div.card-body")
    
    @staticmethod
    def get_links_by_title(page, title):
        items = RABaseHelper.get_item_by_title(page, title)
        links = items.locator("a")

        if links.count() == 0:
            raise ValueError(f"links field with title'{title}' not found.")
        return links
    
    @staticmethod
    def get_link_urls_by_title(page, title):
        links = RABaseHelper.get_links_by_title(page, title)
        return [links.nth(i).get_attribute("href") for i in range(links.count())]
    
    @staticmethod
    def get_field_text_by_title(page, title):
        field = RABaseHelper.get_item_by_title(page, title)
        return field.inner_text().strip()
    
    @staticmethod
    def access_link_by_title(page, link_text, title):
        links = RABaseHelper.get_links_by_title(page, title)
        clicked = False

        for i in range(links.count()):
            link = links.nth(i)
            link_text_content = link.inner_text().strip()
            
            if link_text in link_text_content:
                link.click()
                clicked = True
                break
        
        assert clicked, f"Link with text '{link_text}' not found in section '{title}'"
        return True
        
    @staticmethod
    def get_boolean_value_by_title(page, title):
        field = RABaseHelper.get_item_by_title(page, title)
        bool_field = field.locator("span").nth(1).get_attribute("class")
        if "fa-check" in bool_field:
            return True
        if "fa-times" in bool_field:
            return False
        return None

    def get_links_with_text_by_title(page, title, text_filter):
        all_links = RABaseHelper.get_links_by_title(page, title)
        
        filtered_links = []
        for i in range(all_links.count()):
            link = all_links.nth(i)
            link_text = link.inner_text()
            if text_filter in link_text:
                filtered_links.append(link)
        return filtered_links

    @staticmethod
    def validate_template_data(page, current_date, final_bill_date):
        text = page.locator('[class="page-content"] pre').text_content()
        data = json.loads(text)

        timezone = timedelta(hours=3)

        cancel_initiate_date = data['cancel_initiate_date']
        epoch_cancel_initiate_date = datetime.datetime.fromtimestamp(cancel_initiate_date) + timezone

        final_charge_date_start = data['final_charge_date_start']
        epoch_date_time_start = datetime.datetime.fromtimestamp(final_charge_date_start) + timezone

        if isinstance(current_date, str):
            current_date = datetime.datetime.strptime(current_date, '%b %d, %Y')
        if isinstance(final_bill_date, str):
            final_bill_date = datetime.datetime.strptime(final_bill_date, '%b %d, %Y')

        assert epoch_cancel_initiate_date.strftime('%b %d, %Y') == current_date.strftime('%b %d, %Y'), \
            f"Cancel initiate date does not match: {epoch_cancel_initiate_date} != {current_date}"

        assert epoch_date_time_start.strftime('%b %d, %Y') == final_bill_date.strftime('%b %d, %Y'), \
            f"Final charge date does not match: {epoch_date_time_start} != {final_bill_date}"
    
    @staticmethod
    def access_link_by_title_with_retry(page, link_text, title, max_attempts=12, delay=10):
        common.retry_operation(
            lambda: RABaseHelper.access_link_by_title(page, link_text, title),
            link_text,
            max_attempts,
            delay,
            on_retry=page.reload
        )