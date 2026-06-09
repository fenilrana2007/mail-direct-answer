import os
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from googleapiclient.discovery import build
from gmail_oauth import get_gmail_credentials

load_dotenv()

def send_gmail_api_email(creds, recipient_email: str, subject: str, body: str) -> tuple[bool, str]:
    """
    Send an email using the official Google Gmail REST API.
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        
        # Build MIME Message
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Encode message in URL-safe base64 string
        raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        
        # Dispatch via users.messages.send
        service.users().messages().send(userId='me', body={'raw': raw_msg}).execute()
        return True, "Email sent successfully via Gmail REST API"
        
    except Exception as e:
        return False, f"Gmail API Dispatch Error: {str(e)}"

def send_email(recipient_email: str, subject: str, body: str, dry_run: bool = None) -> tuple[bool, str]:
    """
    Dual routing email dispatch engine:
    1. Authenticates & sends via Gmail REST API if OAuth credentials exist.
    2. Falls back to smtplib secure TLS connection if OAuth is unavailable.
    """
    # Safety Dry Run Check
    if dry_run is None:
        dry_run_str = os.getenv("DRY_RUN", "true").lower()
        dry_run = dry_run_str == "true" or dry_run_str == "1"
    
    sender_name = os.getenv("SENDER_NAME", "Job Seeker")
    sender_email = os.getenv("SMTP_USER", "")
    
    if dry_run:
        print("\n" + "-" * 50)
        print("[DRY RUN ACTIVE] (No email will be actually dispatched)")
        print(f"To: {recipient_email}")
        print(f"From: {sender_name} <{sender_email or 'dry-run@example.com'}>")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("-" * 50 + "\n")
        return True, "Dry run completed successfully (email not sent)"

    # Route 1: Google OAuth REST API (Preferred)
    creds = get_gmail_credentials()
    if creds:
        return send_gmail_api_email(creds, recipient_email, subject, body)
        
    # Route 2: SMTP Fallback
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port_str = os.getenv("SMTP_PORT", "587")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    if not sender_email or not smtp_password:
        return False, "Configuration Error: No OAuth token.json detected, and SMTP_USER/SMTP_PASSWORD are missing from .env."
        
    try:
        smtp_port = int(smtp_port_str)
    except ValueError:
        return False, f"Configuration Error: Invalid SMTP_PORT '{smtp_port_str}' configured in .env"
        
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(sender_email, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        
        return True, "Email sent successfully via SMTP"
    except Exception as e:
        return False, f"SMTP Error: {str(e)}"
