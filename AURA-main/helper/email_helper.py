import base64
import time
from datetime import datetime, timedelta
import test_flows_common.test_flows_common as common

class EmailHelper:
    @staticmethod
    def sees_email_with_subject(tenant_email: str, subject: str, timeout: int = 240, poll_interval: int = 10):
        EmailHelper.email_by_subject(tenant_email, subject, timeout, poll_interval)

    
    @staticmethod
    def email_by_subject(tenant_email: str, subject: str, timeout: int = 240, poll_interval: int = 10):
        service = common.authenticate_gmail()
        end_time = datetime.now() + timedelta(seconds=timeout)
        query = f'to:{tenant_email} subject:"{subject}"'
        while datetime.now() < end_time:
            try:
                res = service.users().messages().list(userId="me", q=query).execute()
                msgs = res.get("messages", [])
                if msgs:
                    message_id = msgs[0]['id']
                    message = service.users().messages().get(userId="me", id=message_id).execute()
                    return message
            except Exception as e:
                pass
            time.sleep(poll_interval)
        raise RuntimeError(f"No emails were received with the subject '{subject}' for {tenant_email}")

    @staticmethod
    def extract_email_details(tenant_email: str, subject: str, timeout: int = 240, poll_interval: int = 10):
        message = EmailHelper.email_by_subject(tenant_email, subject, timeout, poll_interval)

        headers = message.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
        pre_header = next((h["value"] for h in headers if h["name"].lower() == "x-preheader-text"), "")

        def find_html_part(payload):
            if payload.get("mimeType") == "text/html":
                return payload.get("body", {}).get("data")
            for part in payload.get("parts", []):
                html = find_html_part(part)
                if html:
                    return html
            return None

        html_data = find_html_part(message.get("payload", {}))
        html_body = ""
        if html_data:
            html_body = base64.urlsafe_b64decode(html_data.encode("UTF-8")).decode("UTF-8")

        return {
            "subject": subject,
            "pre_header": pre_header,
            "html_body": html_body
        }
