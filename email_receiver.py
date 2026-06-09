import imaplib
import email
import base64
from email.header import decode_header
from email.utils import parsedate_to_datetime
import os
import re
import html
from dotenv import load_dotenv
from googleapiclient.discovery import build
from gmail_oauth import get_gmail_credentials

load_dotenv()

def strip_html_tags(html_str: str) -> str:
    """
    Remove HTML tags, script, and style blocks from a string and unescape HTML entities.
    """
    if not html_str:
        return ""
    # Remove script and style tags and their contents
    html_str = re.sub(r'<(script|style).*?>.*?</\1>', '', html_str, flags=re.DOTALL | re.IGNORECASE)
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]*>', '', html_str)
    # Decode HTML entities (e.g., &amp; -> &, &lt; -> <)
    text = html.unescape(text)
    # Clean up whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def fetch_gmail_api_emails(creds, limit=100, folder="INBOX", timeframe="All") -> dict:
    """
    Fetch latest emails from a specific folder/label using the official Google Gmail REST API.
    Uses batch requests for high-performance retrieval.
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        
        folder = folder.upper()
        label_ids = [folder]
        q = ""
        
        if folder == "INBOX":
            label_ids = ["INBOX"]
            q = ""  # Fetch both read and unread messages in the inbox
        elif folder == "RECENT_GMAIL":
            label_ids = ["INBOX"]
            q = "is:unread"  # Fetch only unread messages in the inbox
            if timeframe == "Last 24 Hours":
                q += " newer_than:1d"
            elif timeframe == "Last 2 Days":
                q += " newer_than:2d"
            elif timeframe == "Last 7 Days":
                q += " newer_than:7d"
        elif folder == "STARRED":
            label_ids = ["STARRED"]
        elif folder == "SNOOZED":
            label_ids = []  # Snoozed might not be a system label, search is safer
            q = "label:snoozed"
        elif folder == "SENT":
            label_ids = ["SENT"]
        elif folder == "DRAFT":
            label_ids = ["DRAFT"]
        elif folder == "ALL_MAIL":
            label_ids = None  # Fetch all mail by omitting label restriction
            q = ""
            
        # Search messages
        results = service.users().messages().list(
            userId="me", 
            labelIds=label_ids if label_ids else None, 
            q=q if q else None, 
            maxResults=limit
        ).execute()
        
        messages = results.get("messages", [])
        if not messages:
            return {"success": True, "emails": []}
            
        emails_list = []
        
        # Batch callback
        def batch_callback(request_id, response, exception):
            if exception is not None:
                # Handle error
                print(f"Error fetching message {request_id}: {exception}")
                return
            
            msg_id = response.get("id")
            headers = response["payload"].get("headers", [])
            
            subject = "No Subject"
            from_sender = "Unknown Sender"
            to_recipient = "Unknown Recipient"
            date = ""
            
            for h in headers:
                if h["name"].lower() == "subject":
                    subject = h["value"]
                elif h["name"].lower() == "from":
                    from_sender = h["value"]
                elif h["name"].lower() == "to":
                    to_recipient = h["value"]
                elif h["name"].lower() == "date":
                    date = h["value"]
            
            # Parse date to timestamp for sorting
            timestamp = 0
            if date:
                try:
                    dt = parsedate_to_datetime(date)
                    timestamp = int(dt.timestamp())
                except Exception:
                    pass
                    
            # Parse out body payload securely
            body = ""
            html_body = ""
            parts = [response["payload"]]
            while parts:
                part = parts.pop(0)
                if part.get("parts"):
                    parts.extend(part["parts"])
                
                mime_type = part.get("mimeType")
                if mime_type == "text/plain":
                    data = part.get("body", {}).get("data")
                    if data:
                        padding = len(data) % 4
                        if padding:
                            data += '=' * (4 - padding)
                        body = base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="ignore")
                elif mime_type == "text/html":
                    data = part.get("body", {}).get("data")
                    if data:
                        padding = len(data) % 4
                        if padding:
                            data += '=' * (4 - padding)
                        html_body = base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="ignore")
            
            body_cleaned = body.strip()
            if not body_cleaned and html_body:
                body_cleaned = strip_html_tags(html_body)
                
            # If no plain text or html decoding yields text, fall back to snippet
            if not body_cleaned:
                body_cleaned = response.get("snippet", "[No Plain Text Content Available]")
                
            # Check if message is unread based on presence of UNREAD label
            is_unread = "UNREAD" in response.get("labelIds", [])
            
            emails_list.append({
                "id": msg_id,
                "from": from_sender,
                "to": to_recipient,
                "subject": subject,
                "date": date,
                "timestamp": timestamp,
                "body": body_cleaned,
                "folder": folder,
                "is_unread": is_unread
            })
            
        # Execute batch requests in chunks of 100 (Google API batch request limit is 100)
        for k in range(0, len(messages), 100):
            chunk = messages[k:k+100]
            batch = service.new_batch_http_request(callback=batch_callback)
            for msg in chunk:
                batch.add(service.users().messages().get(userId="me", id=msg["id"], format="full"))
            batch.execute()
        
        # Sort messages to preserve the order returned by users.messages.list
        msg_id_order = {msg["id"]: idx for idx, msg in enumerate(messages)}
        emails_list.sort(key=lambda x: msg_id_order.get(x["id"], 9999))
        
        return {"success": True, "emails": emails_list}
        
    except Exception as e:
        return {"success": False, "error": f"Gmail API Error: {str(e)}"}

def fetch_incoming_emails(limit=100, folder="INBOX", timeframe="All") -> dict:
    """
    Dual routing email ingestion engine:
    1. Authenticates & fetches via official Gmail REST API if OAuth creds exist.
    2. Falls back to lightweight IMAP SSL protocol if OAuth is unavailable.
    """
    creds = get_gmail_credentials()
    if creds:
        return fetch_gmail_api_emails(creds, limit, folder, timeframe)
        
    # IMAP Fallback
    imap_host = "imap.gmail.com"
    imap_port = 993
    username = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    
    if not username or not password:
        return {
            "success": False, 
            "error": "Configuration Error: No OAuth token.json detected, and SMTP_USER/SMTP_PASSWORD are missing from .env."
        }
        
    try:
        mail = imaplib.IMAP4_SSL(imap_host, imap_port)
        mail.login(username, password)
        
        # Map selected folder to IMAP system mailboxes
        mailbox_map = {
            "INBOX": "inbox",
            "RECENT_GMAIL": "inbox",
            "STARRED": '"[Gmail]/Starred"',
            "SNOOZED": '"[Gmail]/Snoozed"',
            "SENT": '"[Gmail]/Sent Mail"',
            "DRAFT": '"[Gmail]/Drafts"',
            "ALL_MAIL": '"[Gmail]/All Mail"'
        }
        mailbox = mailbox_map.get(folder.upper(), "inbox")
        
        try:
            mail.select(mailbox)
        except Exception:
            mail.select("inbox")
            
        search_query = "ALL"
        if folder.upper() == "RECENT_GMAIL":
            if timeframe == "Last 24 Hours":
                from datetime import datetime, timedelta
                since_date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
                search_query = f"UNSEEN SINCE {since_date}"
            elif timeframe == "Last 2 Days":
                from datetime import datetime, timedelta
                since_date = (datetime.now() - timedelta(days=2)).strftime("%d-%b-%Y")
                search_query = f"UNSEEN SINCE {since_date}"
            elif timeframe == "Last 7 Days":
                from datetime import datetime, timedelta
                since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
                search_query = f"UNSEEN SINCE {since_date}"
            else:
                search_query = "UNSEEN"
            
        status, messages = mail.search(None, search_query)
        if status != "OK":
            return {"success": False, "error": "IMAP Search Command failed."}
            
        message_ids = messages[0].split()
        if not message_ids:
            return {"success": True, "emails": []}
            
        latest_ids = message_ids[-limit:]
        latest_ids.reverse()
        
        emails_list = []
        for msg_id in latest_ids:
            # Check flags to see if unread
            is_unread = True
            try:
                status_flags, flag_data = mail.fetch(msg_id, "(FLAGS)")
                if status_flags == "OK" and flag_data and flag_data[0]:
                    flags_str = flag_data[0].decode("utf-8", errors="ignore")
                    if "\\Seen" in flags_str:
                        is_unread = False
            except Exception:
                pass

            status, data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
                
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject_header = msg["Subject"]
            subject = "No Subject"
            if subject_header:
                decoded_header = decode_header(subject_header)[0]
                subject_content = decoded_header[0]
                encoding = decoded_header[1]
                if isinstance(subject_content, bytes):
                    subject = subject_content.decode(encoding or "utf-8", errors="ignore")
                else:
                    subject = str(subject_content)
                    
            from_header = msg["From"]
            from_sender = "Unknown Sender"
            if from_header:
                decoded_header = decode_header(from_header)[0]
                from_content = decoded_header[0]
                encoding = decoded_header[1]
                if isinstance(from_content, bytes):
                    from_sender = from_content.decode(encoding or "utf-8", errors="ignore")
                else:
                    from_sender = str(from_content)
                    
            date = msg["Date"]
            
            body = ""
            html_body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except Exception:
                            pass
                    elif content_type == "text/html" and "attachment" not in content_disposition:
                        try:
                            html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except Exception:
                            pass
            else:
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                elif content_type == "text/html":
                    try:
                        html_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except Exception:
                        pass
            
            body_cleaned = body.strip()
            if not body_cleaned and html_body:
                body_cleaned = strip_html_tags(html_body)
                
            if not body_cleaned:
                body_cleaned = "[No Plain Text Content Available]"
                
            timestamp = 0
            if date:
                try:
                    dt = parsedate_to_datetime(date)
                    timestamp = int(dt.timestamp())
                except Exception:
                    pass
                
            emails_list.append({
                "id": msg_id.decode("utf-8"),
                "from": from_sender,
                "subject": subject,
                "date": date,
                "timestamp": timestamp,
                "body": body_cleaned,
                "is_unread": is_unread
            })
            
        mail.close()
        mail.logout()
        return {"success": True, "emails": emails_list}
        
    except Exception as e:
        return {"success": False, "error": f"IMAP Error: {str(e)}"}

def mark_email_as_read(mail_id: str) -> bool:
    """
    Mark an email as read using Gmail REST API or IMAP.
    """
    creds = get_gmail_credentials()
    if creds:
        try:
            service = build("gmail", "v1", credentials=creds)
            service.users().messages().batchModify(
                userId="me",
                body={
                    "ids": [mail_id],
                    "removeLabelIds": ["UNREAD"]
                }
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking message as read via Gmail API: {e}")
            return False

    # IMAP Fallback
    imap_host = "imap.gmail.com"
    imap_port = 993
    username = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    
    if not username or not password:
        return False
        
    try:
        mail = imaplib.IMAP4_SSL(imap_host, imap_port)
        mail.login(username, password)
        mail.select("inbox")
        # IMAP mail_id was decoded to string, so encode it back for IMAP store command.
        mail.store(mail_id.encode("utf-8"), '+FLAGS', '\\Seen')
        mail.close()
        mail.logout()
        return True
    except Exception as e:
        print(f"Error marking message as read via IMAP: {e}")
        return False

